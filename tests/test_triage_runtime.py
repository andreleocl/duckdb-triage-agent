"""Offline workflow tests: fabricated reports and a mocked GitHub API only."""

import copy
import importlib.util
import json
import io
import os
import tempfile
from pathlib import Path
import re
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('triage_runtime', ROOT / 'scripts/triage_runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class FakeGitHub:
    def __init__(self):
        self.issue = dict(number=7, state='open', title='CSV import error',
                          body='The import fails; no input file is supplied.', labels=[])
        self.history = []
        self.writes = []
        self.fail_label = False

    def call(self, method, suffix='', data=None):
        if method == 'GET':
            return copy.deepcopy(self.issue)
        self.writes.append((suffix, data))
        if suffix == '/comments':
            self.history.append(dict(body=data['body'], user=dict(login=runtime.BOT, type='Bot')))
        elif suffix == '/labels':
            if self.fail_label:
                raise ValueError('Simulated label failure')
            self.issue['labels'].extend({'name': label} for label in data['labels'])
        else:
            raise AssertionError('Unexpected mutation')
        return {}

    def comments(self):
        return copy.deepcopy(self.history)


class WorkflowBehavior(unittest.TestCase):
    def setUp(self):
        self.client = FakeGitHub()
        self.snapshot, self.skill = runtime.prepare(self.client, 7, 'trusted-sha')
        self.proposal = dict(label='needs reproducible example', comment='Could you share generated sample input?',
                             rationale='The input file is missing.')

    def output(self, proposal=None):
        return dict(items=[dict(type='submit_triage', proposal=json.dumps(proposal or self.proposal))])

    def publish(self, output=None):
        return runtime.publish(self.client, 7, self.snapshot, output or self.output(), 'trusted-sha')

    def test_preparation_exposes_only_opening_text_and_skill(self):
        self.assertEqual(set(self.snapshot['issue']), {'title', 'body'})
        self.assertEqual(self.snapshot['input_sha256'], runtime.fingerprint(self.snapshot['issue']))
        self.assertIn('name: duckdb-triage', self.skill)
        self.assertFalse(self.client.writes)

    def test_target_disabled_wrong_repo_event_branch_host_or_number(self):
        env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_EVENT_NAME='workflow_dispatch', TRIAGE_ENABLED='true', GITHUB_SERVER_URL='https://github.com')
        event = dict(inputs=dict(issue_number='7'))
        self.assertEqual(runtime.target(event, env), 7)
        for field in env:
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.target(event, {**env, field: 'wrong'})
        for number in ['0', '-1', '1; echo injected', '1.5', True, 7, None, '12345678901']:
            with self.subTest(number=number), self.assertRaises(ValueError):
                runtime.target(dict(inputs=dict(issue_number=number)), env)

    def test_no_action_and_idempotent_publication(self):
        no_action = dict(label=None, comment=None, rationale='No essential gap.')
        self.assertEqual(self.publish(self.output(no_action))['status'], 'no_action')
        self.assertFalse(self.client.writes)
        self.assertEqual(self.publish()['actions'], ['add_comment', 'add_label'])
        self.assertEqual(self.publish()['status'], 'already_triaged')
        self.assertEqual(len(self.client.writes), 2)
        body = self.client.history[0]['body']
        self.assertLessEqual(len(body), 1200)
        self.assertIn('Automated triage suggestion.', body)
        self.assertNotIn(self.proposal['rationale'], body)

    def test_retry_after_label_failure_does_not_duplicate_comment(self):
        self.client.fail_label = True
        with self.assertRaises(ValueError):
            self.publish()
        self.client.fail_label = False
        self.assertEqual(self.publish()['actions'], ['add_label'])
        self.assertEqual(len(self.client.history), 1)

    def test_rejects_multiple_outputs_extra_actions_bad_labels_and_public_text(self):
        invalid = [dict(items=[]), dict(items=self.output()['items'] * 2),
                   dict(items=[dict(type='close_issue', proposal='{}')]),
                   dict(items=[dict(type='submit_triage', proposal='{}', issue_number=8)])]
        for changes in [dict(label='bug'), dict(close_issue=True), dict(comment='x' * 1200),
                        dict(comment='Ask @someone'), dict(comment='See #42'),
                        dict(comment='Visit https://example.invalid/upload'),
                        dict(comment='Ask &#64;someone'), dict(comment='Ask %40someone'),
                        dict(comment='<img src=x>'),
                        dict(comment='Please share 5â€“20 rows of sample data.')]:
            invalid.append(self.output({**self.proposal, **changes}))
        for output in invalid:
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.publish(output)
        self.assertFalse(self.client.writes)

    def test_closed_pr_changed_and_wrong_snapshot_fail_without_writes(self):
        for changes in [dict(state='closed'), dict(pull_request={}), dict(body='Edited report')]:
            old = copy.deepcopy(self.client.issue)
            self.client.issue.update(changes)
            with self.assertRaises(ValueError):
                self.publish()
            self.client.issue = old
        for field in ['repository', 'number', 'configuration_sha', 'input_sha256']:
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.publish(self.client, 7, {**self.snapshot, field: 'wrong'}, self.output(), 'trusted-sha')
        self.assertFalse(self.client.writes)

    def test_change_during_comment_inspection_fails(self):
        def comments():
            self.client.issue['body'] = 'Changed during analysis'
            return []
        self.client.comments = comments
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse(self.client.writes)

    def test_existing_labels_and_older_bot_response_are_not_overwritten(self):
        self.client.issue['labels'] = [dict(name='needs more info')]
        self.assertEqual(self.publish()['status'], 'existing_triage_label')
        self.client.issue['labels'] = []
        self.client.history = [dict(body='<!-- duckdb-triage:v1 old -->', user=dict(login=runtime.BOT, type='Bot'))]
        self.assertEqual(self.publish()['status'], 'already_triaged')
        self.assertFalse(self.client.writes)

    def test_reporter_cannot_forge_bot_marker(self):
        self.publish()
        self.client.history[0]['user'] = dict(login='reporter', type='User')
        self.client.issue['labels'] = []
        self.assertEqual(self.publish()['actions'], ['add_comment', 'add_label'])

    def test_read_retries_transient_failures_then_succeeds(self):
        client = runtime.GitHub('fake-token', 7)
        failures = [runtime.urllib.error.URLError(runtime.socket.gaierror(runtime.socket.EAI_AGAIN, 'private detail')),
                    runtime.urllib.error.HTTPError('private-url', 503, 'private detail', {}, None)]
        with patch.object(client.opener, 'open', side_effect=failures + [io.BytesIO(b'{"ok": true}')]) as opened, \
                patch.object(runtime.time, 'sleep') as sleep, patch('sys.stderr', new_callable=io.StringIO) as log:
            self.assertEqual(client.call('GET'), {'ok': True})
            self.assertEqual(opened.call_count, 3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], [1, 3])
            self.assertNotIn('private', log.getvalue())
            self.assertNotIn('fake-token', log.getvalue())
        self.assertEqual([x['status'] for x in client.operations], ['failed', 'failed', 'succeeded'])

    def test_read_stops_after_three_timeouts(self):
        client = runtime.GitHub('fake-token', 7)
        with patch.object(client.opener, 'open', side_effect=TimeoutError('private detail')) as opened, \
                patch.object(runtime.time, 'sleep') as sleep, patch('sys.stderr', new_callable=io.StringIO):
            with self.assertRaisesRegex(ValueError, 'attempts=3'):
                client.call('GET')
            self.assertEqual(opened.call_count, 3)
            self.assertEqual(sleep.call_count, 2)

    def test_permanent_read_errors_do_not_retry(self):
        errors = [runtime.urllib.error.HTTPError('private-url', code, 'private', {}, None)
                  for code in (400, 401, 403, 404, 429)]
        errors += [runtime.urllib.error.URLError(runtime.ssl.SSLCertVerificationError('private')),
                   runtime.urllib.error.URLError(runtime.socket.gaierror(runtime.socket.EAI_NONAME, 'private')),
                   runtime.urllib.error.URLError('unclassified failure')]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                client = runtime.GitHub('fake-token', 7)
                with patch.object(client.opener, 'open', side_effect=error) as opened, \
                        patch.object(runtime.time, 'sleep') as sleep, patch('sys.stderr', new_callable=io.StringIO):
                    with self.assertRaises(ValueError):
                        client.call('GET')
                    self.assertEqual(opened.call_count, 1)
                    sleep.assert_not_called()

    def test_writes_never_retry_transient_errors(self):
        for suffix in ('/comments', '/labels'):
            for error in (TimeoutError(), runtime.urllib.error.HTTPError('url', 503, '', {}, None)):
                client = runtime.GitHub('fake-token', 7)
                with patch.object(client.opener, 'open', side_effect=error) as opened, \
                        patch.object(runtime.time, 'sleep') as sleep, patch('sys.stderr', new_callable=io.StringIO):
                    with self.assertRaises(ValueError):
                        client.call('POST', suffix, {})
                    self.assertEqual(opened.call_count, 1)
                    sleep.assert_not_called()

    def test_invalid_json_does_not_retry(self):
        client = runtime.GitHub('fake-token', 7)
        with patch.object(client.opener, 'open', return_value=io.BytesIO(b'not json')) as opened, \
                patch.object(runtime.time, 'sleep') as sleep:
            with self.assertRaises(ValueError):
                client.call('GET')
            self.assertEqual(opened.call_count, 1)
            sleep.assert_not_called()

    def test_transport_cannot_call_other_endpoints_or_follow_redirects(self):
        client = runtime.GitHub('fake-token', 7)
        with patch.object(client.opener, 'open', side_effect=AssertionError('Network forbidden')):
            for method, suffix in [('PATCH', ''), ('DELETE', ''), ('POST', '/assignees'),
                                   ('GET', '/../../other/issues/1'), ('GET', 'https://example.invalid')]:
                with self.subTest(method=method, suffix=suffix), self.assertRaises(ValueError):
                    client.call(method, suffix)
        with self.assertRaises(ValueError):
            runtime.NoRedirect().redirect_request(None, None, 302, None, None, 'https://example.invalid')

    def test_publish_entry_point_requires_detection_and_refuses_staged_mode(self):
        env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_EVENT_NAME='workflow_dispatch', TRIAGE_ENABLED='true',
                   GITHUB_SERVER_URL='https://github.com', GH_TOKEN='fake-token',
                   TRIAGE_AGENT_RESULT='success')
        for flags in [{}, {'GH_AW_DETECTION_CONCLUSION': 'failure'},
                      {'GH_AW_DETECTION_CONCLUSION': 'success', 'TRIAGE_AGENT_RESULT': 'failure'},
                      {'GH_AW_DETECTION_CONCLUSION': 'success', 'TRIAGE_AGENT_RESULT': ''},
                      {'GH_AW_DETECTION_CONCLUSION': 'success', 'GH_AW_SAFE_OUTPUTS_STAGED': 'true'}]:
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                event = root / 'event.json'
                event.write_text(json.dumps(dict(inputs=dict(issue_number='7'))), encoding='utf-8')
                with patch.dict(os.environ, {**env, **flags, 'GITHUB_EVENT_PATH': str(event)}, clear=True), \
                        patch.object(runtime, 'ROOT', root), \
                        patch.object(runtime.sys, 'argv', ['triage_runtime.py', 'publish']), \
                        patch.object(runtime.sys, 'stderr', io.StringIO()), \
                        patch.object(runtime.GitHub, 'call', side_effect=AssertionError('Network forbidden')):
                    self.assertEqual(runtime.main(), 1)
                receipt = json.loads((root / '.triage/receipt.json').read_text(encoding='utf-8'))
                self.assertEqual(receipt['status'], 'error')
                self.assertEqual(receipt['api_operations'], [])

    def test_publish_entry_point_records_successful_validated_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.triage').mkdir()
            event = root / 'event.json'
            event.write_text(json.dumps(dict(inputs=dict(issue_number='7'))), encoding='utf-8')
            (root / '.triage/input.json').write_text(json.dumps(self.snapshot), encoding='utf-8')
            output = root / 'output.json'
            output.write_text(json.dumps(self.output()), encoding='utf-8')
            env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                       GITHUB_EVENT_NAME='workflow_dispatch', TRIAGE_ENABLED='true',
                       GITHUB_SERVER_URL='https://github.com', GH_TOKEN='fake-token',
                       TRIAGE_AGENT_RESULT='success', GH_AW_DETECTION_CONCLUSION='success',
                       GITHUB_EVENT_PATH=str(event), GH_AW_AGENT_OUTPUT=str(output),
                       GITHUB_SHA='trusted-sha', GITHUB_RUN_ID='123')
            self.client.operations = []
            with patch.dict(os.environ, env, clear=True), patch.object(runtime, 'ROOT', root), \
                    patch.object(runtime.sys, 'argv', ['triage_runtime.py', 'publish']), \
                    patch.object(runtime, 'GitHub', return_value=self.client):
                self.assertEqual(runtime.main(), 0)
            receipt = json.loads((root / '.triage/receipt.json').read_text(encoding='utf-8'))
            self.assertEqual(receipt['status'], 'published')
            self.assertEqual(receipt['actions'], ['add_comment', 'add_label'])
            self.assertEqual(receipt['input_sha256'], self.snapshot['input_sha256'])
            self.assertEqual(receipt['run_id'], '123')
            self.assertEqual(len(self.client.writes), 2)

    def test_comment_pagination_fails_closed_at_limit(self):
        client = runtime.GitHub('fake-token', 7)
        with patch.object(client, 'call', side_effect=[[{}] * 100, []]) as call:
            self.assertEqual(len(client.comments()), 100)
            self.assertEqual(call.call_count, 2)
        with patch.object(client, 'call', return_value=[{}] * 100), self.assertRaises(ValueError):
            client.comments()


class CompiledWorkflow(unittest.TestCase):
    def test_compiled_capability_boundary(self):
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        manifest = json.loads(next(line.split(': ', 1)[1] for line in lock.splitlines()
                                   if line.startswith('# gh-aw-manifest:')))
        self.assertEqual(manifest['mcp_servers'], [dict(name='safeoutputs', tools=['report_incomplete', 'submit_triage'])])
        for action in manifest['actions']:
            self.assertRegex(action['sha'], r'^[0-9a-f]{40}$')
        jobs = dict(re.findall(r'^  ([a-z_]+):\n(.*?)(?=^  [a-z_]+:\n|\Z)', lock.split('\njobs:\n', 1)[1], re.M | re.S))
        writers = []
        for name, body in jobs.items():
            permissions = re.search(r'^    permissions:\n((?:^      [^\n]*\n)+)', body, re.M)
            if permissions and ': write' in permissions[1]:
                writers.append(name)
                self.assertEqual(permissions[1].strip().splitlines()[-1].strip(), 'issues: write')
        self.assertEqual(writers, ['submit_triage'])
        self.assertNotIn('actions/checkout@', jobs['agent'])
        self.assertIn("needs.detection.result == 'success'", jobs['submit_triage'])
        self.assertIn('TRIAGE_AGENT_RESULT: ${{ needs.agent.result }}', jobs['submit_triage'])
        self.assertIn("vars.TRIAGE_ENABLED == 'true'", jobs['activation'])
        self.assertIn('issues: read', jobs['activation'])
        self.assertIn('timeout-minutes: 15', jobs['agent'])
        self.assertNotIn('pull_request_target:', lock)
        self.assertNotIn('schedule:', lock)


if __name__ == '__main__':
    unittest.main()
