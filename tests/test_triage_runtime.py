"""Offline workflow tests: fabricated reports and a mocked GitHub API only."""

import copy
import hashlib
import importlib.util
import json
import io
import os
import tempfile
from pathlib import Path
import re
import shutil
import subprocess
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
        fields = dict(self.proposal if proposal is None else proposal)
        if fields.get('label') is None and fields.get('comment') is None:
            fields.update(label='no_action', comment='no_action')
        return dict(items=[dict(type='submit_triage', **fields)])

    def publish(self, output=None):
        return runtime.publish(self.client, 7, self.snapshot, output or self.output(), 'trusted-sha')

    def test_preparation_exposes_only_opening_text_and_skill(self):
        self.assertEqual(set(self.snapshot['issue']), {'title', 'body'})
        self.assertEqual(self.snapshot['input_sha256'], runtime.fingerprint(self.snapshot['issue']))
        self.assertIn('name: duckdb-triage', self.skill)
        self.assertFalse(self.client.writes)

    def test_practice_preparation_preserves_report_and_current_skill_without_answers(self):
        # Input-delivery regression only; no model judgment is evaluated here.
        cases = json.loads((ROOT / 'tests/fixtures/essential_information_practice.json').read_text(encoding='utf-8'))
        # Fixture coverage only: these are authored expectations, not model results.
        expected_labels = {
            'practice-ui-complete': None,
            'practice-notebook-complete': None,
            'practice-input-missing': 'needs reproducible example',
            'practice-version-conflict': 'needs more info',
            'practice-ui-environment-missing': 'needs more info',
            'practice-diagnostic-enhancement': None,
            'practice-parameter-enhancement': None,
            'practice-parameter-regression': 'needs reproducible example',
            'practice-enhancement-and-crash': 'needs reproducible example',
        }
        self.assertEqual(len(cases), len(expected_labels))
        self.assertEqual({case['id']: case['expected']['label'] for case in cases}, expected_labels)
        skill = runtime.SKILL.read_text(encoding='utf-8')
        for case in cases:
            with self.subTest(case=case['id']):
                client = FakeGitHub()
                client.issue.update(case['issue'])
                client.issue['expected'] = case['expected']
                snapshot, delivered_skill = runtime.prepare(client, 7, 'practice-sha')
                self.assertEqual(snapshot['issue'], case['issue'])
                self.assertEqual(snapshot['input_sha256'], runtime.fingerprint(case['issue']))
                self.assertEqual(delivered_skill, skill)
                self.assertEqual(snapshot['skill_sha256'], hashlib.sha256(skill.encode()).hexdigest())
                self.assertNotIn(case['expected']['reason'], json.dumps(snapshot) + delivered_skill)
                self.assertFalse(client.writes)

    def test_target_disabled_wrong_repo_event_branch_host_or_number(self):
        env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true', GITHUB_SERVER_URL='https://github.com')
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
        receipt = self.publish(self.output(no_action))
        self.assertEqual(receipt['status'], 'no_action')
        self.assertEqual(receipt['proposal'], no_action)
        self.assertEqual(receipt['actions'], [])
        self.assertFalse(self.client.writes)
        self.assertEqual(self.publish()['actions'], ['add_comment', 'add_label'])
        self.assertEqual(self.publish()['status'], 'already_triaged')
        self.assertEqual(len(self.client.writes), 2)
        body = self.client.history[0]['body']
        self.assertLessEqual(len(body), 1200)
        self.assertIn('Automated triage suggestion.', body)
        self.assertNotIn(self.proposal['rationale'], body)

    def test_publisher_preserves_plain_arrows_and_comparisons(self):
        for text in ('VARCHAR->NULL', 'x > 10', 'x < 10', 'x <= 10',
                     'x < y', 'x > y', 'x &gt; 10', 'x &lt; 10'):
            with self.subTest(text=text):
                self.client = FakeGitHub()
                comment = f'Could you share sample input triggering `{text}`?'
                receipt = self.publish(self.output({**self.proposal, 'comment': comment}))
                self.assertEqual(receipt['actions'], ['add_comment', 'add_label'])
                self.assertTrue(self.client.history[0]['body'].startswith(comment + '\n\n'))
                self.assertEqual(receipt['proposal']['comment'], comment)

    def test_publisher_blocks_html_and_encoded_prohibited_content_without_writes(self):
        for text in ('<b>sample</b>', '</div>', '<br/>', '<IMG src="x">',
                     '<a\nhref="relative">sample</a>', '<!-- comment -->',
                     '<!DOCTYPE html>', '<?instruction?>',
                     '&lt;b&gt;sample&lt;/b&gt;', '%3Cb%3Esample%3C/b%3E',
                     '%26lt%3Bb%26gt%3Bsample%26lt%3B/b%26gt%3B',
                     '%40someone', '&#64;someone', '%23' + '42',
                     'https%3A%2F%2Fexample.invalid', 'www.example.invalid'):
            with self.subTest(text=text):
                self.client = FakeGitHub()
                with self.assertRaises(ValueError):
                    self.publish(self.output({**self.proposal, 'comment': f'Please share {text}.'}))
                self.assertFalse(self.client.writes)

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

    def test_separate_fields_preserve_quotes_backslashes_newlines_and_unicode(self):
        comment = 'Could you share input triggering "unexpected token"?\nThe example uses `C:\\temp\\sample.csv` and caf\u00e9.'
        proposal = {**self.proposal, 'comment': comment,
                    'rationale': 'The report says "parse failed"; sample input is missing.'}
        output = json.loads(json.dumps(self.output(proposal)), object_pairs_hook=runtime.validator.unique_fields)
        self.assertEqual(runtime.proposal_from_output(output), proposal)
        receipt = self.publish(output)
        self.assertEqual(receipt['proposal'], proposal)
        self.assertTrue(self.client.history[0]['body'].startswith(comment + '\n\n'))
        self.assertEqual(receipt['actions'], ['add_comment', 'add_label'])

    def test_separate_fields_reject_legacy_missing_extra_and_wrong_types(self):
        valid = self.output()['items'][0]
        invalid = [dict(type='submit_triage', proposal=json.dumps(self.proposal)),
                   dict(type='submit_triage', proposal='{broken JSON'),
                   {**valid, 'issue_number': 8}, {**valid, 'repository': 'other/repo'},
                   {**valid, 'type': 'close_issue'}]
        for field in ('label', 'comment', 'rationale'):
            invalid.append({k: v for k, v in valid.items() if k != field})
            for value in (None, False, 0, [], {}):
                invalid.append({**valid, field: value})
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                self.publish(dict(items=[item]))
        self.assertFalse(self.client.writes)

    def test_no_action_requires_exact_sentinel_pair_and_nonempty_rationale(self):
        for changes in (dict(label=''), dict(comment=''), dict(label='', comment=''),
                        dict(label=' ', comment=' '), dict(label='no_action'),
                        dict(comment='no_action'), dict(label='no_action', comment=''),
                        dict(label='', comment='no_action'), dict(label='null', comment='null'),
                        dict(label=' no_action ', comment='no_action'),
                        dict(label='no_action', comment='no_action '),
                        dict(label='NO_ACTION', comment='NO_ACTION'),
                        dict(label='no_action', comment='no_action', rationale=' ')):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.publish(self.output({**self.proposal, **changes}))
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
                   GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true',
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

    def test_publish_entry_point_blocks_malformed_and_duplicate_json_fields(self):
        env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true',
                   GITHUB_SERVER_URL='https://github.com', GH_TOKEN='fake-token',
                   TRIAGE_AGENT_RESULT='success', GH_AW_DETECTION_CONCLUSION='success',
                   GITHUB_EVENT_PATH='event.json', GH_AW_AGENT_OUTPUT='output.json',
                   GITHUB_SHA='trusted-sha', GITHUB_RUN_ID='123')
        event = json.dumps(dict(inputs=dict(issue_number='7')))
        bad_outputs = ['{"items":', '{"items": [], "items": []}',
                       '{"items": [{"type": "submit_triage", "label": "", "label": "bug", '
                       '"comment": "", "rationale": "No gap."}]}']
        self.client.operations = []
        for output in bad_outputs:
            with self.subTest(output=output), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch.dict(os.environ, env, clear=True), patch.object(runtime, 'ROOT', root), \
                        patch.object(runtime.sys, 'argv', ['triage_runtime.py', 'publish']), \
                        patch.object(runtime.sys, 'stderr', io.StringIO()), \
                        patch.object(runtime, 'GitHub', return_value=self.client), \
                        patch.object(Path, 'read_text', side_effect=[event, json.dumps(self.snapshot), output]):
                    self.assertEqual(runtime.main(), 1)
                receipt = json.loads((root / '.triage/receipt.json').read_text(encoding='utf-8'))
                self.assertEqual(receipt['status'], 'error')
                self.assertEqual(receipt['api_operations'], [])
                self.assertFalse(self.client.writes)

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
                       GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true',
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


class RunAdmission(unittest.TestCase):
    def setUp(self):
        self.now = runtime.datetime(2026, 10, 30, 12, tzinfo=runtime.timezone.utc)
        self.current = dict(id=100, workflow_id=7, path=runtime.WORKFLOW_PATH,
                            event='workflow_dispatch', repository=dict(full_name=runtime.REPOSITORY),
                            created_at='2026-10-30T11:59:00Z', run_attempt=1,
                            head_branch='main', head_sha='trusted-sha')

    def admit(self, runs, total=None, links=None, payload=None):
        body = payload if payload is not None else json.dumps(dict(
            total_count=len(runs) if total is None else total, workflow_runs=runs)).encode()
        response = io.BytesIO(body)
        response.headers = {'Link': links} if links else {}
        with patch.object(runtime.urllib.request.OpenerDirector, 'open', return_value=response) as opened:
            result = runtime.admit_run('fake-token', '100', 'trusted-sha', self.now)
        self.request = opened.call_args[0][0]
        self.assertEqual(opened.call_count, 1)
        return result

    def test_fifth_allowed_sixth_blocked_across_actors_and_conclusions(self):
        runs = [{**self.current, 'id': 100 + i, 'actor': {'login': actor},
                 'conclusion': conclusion, 'updated_at': self.current['created_at']}
                for i, (actor, conclusion) in enumerate([
                    ('andreleocl', None), ('andreleocl', 'cancelled'), ('other', 'failure'),
                    ('andreleocl', 'skipped'), ('other', 'success')])]
        result = self.admit(runs)
        self.assertEqual(result['count'], 5)
        self.assertEqual(result['run_ids'], [100, 101, 102, 103, 104])
        with self.assertRaisesRegex(runtime.AdmissionDenied, 'limit reached'):
            self.admit(runs + [{**self.current, 'id': 105}])

    def test_current_run_must_be_present_and_is_counted_once(self):
        self.assertEqual(self.admit([self.current])['count'], 1)
        for runs in ([], [{**self.current, 'id': 101}], [self.current, self.current]):
            with self.subTest(runs=runs), self.assertRaises(runtime.AdmissionDenied):
                self.admit(runs)

    def test_incomplete_or_truncated_history_never_allows(self):
        for total, links in ((2, None), (1001, None), (True, None), ('1', None), (1, '<next>; rel="next"')):
            with self.subTest(total=total, links=links), self.assertRaises(runtime.AdmissionDenied):
                self.admit([self.current], total=total, links=links)
        for body in (b'{}', b'[]', b'{"total_count":1,"workflow_runs":null}',
                     b'{"total_count":0,"total_count":1,"workflow_runs":[]}'):
            with self.subTest(body=body), self.assertRaises(runtime.AdmissionDenied):
                self.admit([], payload=body)

    def test_malformed_or_wrong_scope_records_never_allow(self):
        for changes in ({'created_at': 'bad'}, {'created_at': None}, {'id': True},
                        {'workflow_id': None}, {'run_attempt': 0}, {'event': 'push'},
                        {'path': 'other.yml'}, {'repository': None},
                        {'repository': {'full_name': 'duckdb/duckdb'}}):
            with self.subTest(changes=changes), self.assertRaises(runtime.AdmissionDenied):
                self.admit([{**self.current, **changes}])
        for field in self.current:
            with self.subTest(missing=field), self.assertRaises(runtime.AdmissionDenied):
                self.admit([{k: v for k, v in self.current.items() if k != field}])
        with self.assertRaises(runtime.AdmissionDenied):
            self.admit([self.current, {**self.current, 'id': 101, 'workflow_id': 8}])

    def test_queued_run_and_inclusive_hour_boundary(self):
        at_boundary = {**self.current, 'created_at': '2026-10-30T11:00:00Z'}
        self.assertEqual(self.admit([at_boundary])['count'], 1)
        for timestamp in ('2026-10-30T10:59:59Z', '2026-10-30T12:00:01Z'):
            with self.subTest(timestamp=timestamp), self.assertRaises(runtime.AdmissionDenied):
                self.admit([{**self.current, 'created_at': timestamp}])
        self.assertEqual(self.admit([{**self.current, 'created_at': '2026-10-30T11:30:00Z'}])['count'], 1)

    def test_current_run_must_match_first_attempt_branch_and_commit(self):
        for changes in ({'run_attempt': 2}, {'head_branch': 'other'}, {'head_sha': 'other-sha'}):
            with self.subTest(changes=changes), self.assertRaises(runtime.AdmissionDenied):
                self.admit([{**self.current, **changes}])

    def test_request_is_read_only_and_fixed_to_sandbox_workflow(self):
        self.admit([self.current])
        from urllib.parse import urlsplit, parse_qs
        url = urlsplit(self.request.full_url)
        self.assertEqual(self.request.get_method(), 'GET')
        self.assertEqual(url.scheme, 'https')
        self.assertEqual(url.netloc, 'api.github.com')
        self.assertEqual(url.path, '/repos/andreleocl/duckdb-triage-agent/actions/workflows/issue-triage.lock.yml/runs')
        self.assertEqual(parse_qs(url.query), dict(event=['workflow_dispatch'],
                         created=['2026-10-30T11:00:00Z..2026-10-30T12:00:00Z'],
                         per_page=['100'], page=['1'], exclude_pull_requests=['true']))
        self.assertIsNone(self.request.data)

    def test_http_timeout_redirect_and_json_errors_fail_closed(self):
        for error in (TimeoutError(), runtime.urllib.error.HTTPError('url', 503, '', {}, None),
                      ValueError('Unexpected GitHub redirect')):
            with self.subTest(error=type(error).__name__), \
                    patch.object(runtime.urllib.request.OpenerDirector, 'open', side_effect=error) as opened, \
                    self.assertRaisesRegex(runtime.AdmissionDenied, 'unavailable or invalid'):
                runtime.admit_run('fake-token', '100', 'trusted-sha', self.now)
            self.assertEqual(opened.call_count, 1)
        with self.assertRaises(runtime.AdmissionDenied):
            self.admit([], payload=b'not json')

    def test_successful_preparation_checks_admission_before_reading_issue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = root / 'event.json'
            event.write_text(json.dumps(dict(inputs=dict(issue_number='7'))), encoding='utf-8')
            env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                       GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true',
                       GITHUB_SERVER_URL='https://github.com', GH_TOKEN='fake-token', GITHUB_RUN_ID='100',
                       GITHUB_SHA='trusted-sha', GITHUB_EVENT_PATH=str(event), GITHUB_OUTPUT=str(root / 'outputs'))
            skill = root / '.claude/skills/duckdb-triage/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text(runtime.SKILL.read_text(encoding='utf-8'), encoding='utf-8')
            order = []
            issue = FakeGitHub().issue
            def admit(*args):
                order.append('admission')
                return dict(status='allowed', count=1)
            def read_issue(*args):
                order.append('issue')
                return issue
            with patch.dict(os.environ, env, clear=True), patch.object(runtime, 'ROOT', root), \
                    patch.object(runtime, 'SKILL', skill), \
                    patch.object(runtime.sys, 'argv', ['triage_runtime.py', 'prepare']), \
                    patch.object(runtime.sys, 'stdout', io.StringIO()), \
                    patch.object(runtime, 'admit_run', side_effect=admit), \
                    patch.object(runtime.GitHub, 'call', side_effect=read_issue):
                self.assertEqual(runtime.main(), 0)
            self.assertEqual(order, ['admission', 'issue'])
            snapshot = json.loads((root / '.triage/input.json').read_text(encoding='utf-8'))
            self.assertEqual(snapshot['configuration_sha'], 'trusted-sha')
            self.assertEqual(snapshot['issue'], dict(title=issue['title'], body=issue['body']))
            self.assertNotIn('admission', (root / 'outputs').read_text(encoding='utf-8'))

    def test_denied_admission_and_reruns_never_read_issue_or_publish(self):
        env = dict(GITHUB_REPOSITORY=runtime.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_RUN_ATTEMPT='1', TRIAGE_ENABLED='true',
                   GITHUB_SERVER_URL='https://github.com', GH_TOKEN='fake-token', GITHUB_RUN_ID='100',
                   GITHUB_SHA='trusted-sha', GITHUB_EVENT_PATH='event.json')
        event = json.dumps(dict(inputs=dict(issue_number='7')))
        for mode, attempt in (('prepare', '1'), ('prepare', '2'), ('publish', '2')):
            with self.subTest(mode=mode, attempt=attempt), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                with patch.dict(os.environ, {**env, 'GITHUB_RUN_ATTEMPT': attempt}, clear=True), \
                        patch.object(runtime, 'ROOT', root), \
                        patch.object(runtime.sys, 'argv', ['triage_runtime.py', mode]), \
                        patch.object(runtime.sys, 'stderr', io.StringIO()), \
                        patch.object(Path, 'read_text', return_value=event), \
                        patch.object(runtime, 'admit_run', side_effect=runtime.AdmissionDenied('Limit reached')) as admit, \
                        patch.object(runtime.GitHub, 'call', side_effect=AssertionError('Network forbidden')) as call:
                    self.assertEqual(runtime.main(), 1)
                    call.assert_not_called()
                    self.assertEqual(admit.call_count, 1 if attempt == '1' else 0)
                self.assertFalse((root / '.triage/input.json').exists())


class CompiledWorkflow(unittest.TestCase):
    def assert_job_condition(self, name, cases):
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        jobs = dict(re.findall(r'^  ([a-z_]+):\n(.*?)(?=^  [a-z_]+:\n|\Z)',
                               lock.split('\njobs:\n', 1)[1], re.M | re.S))
        match = re.search(r'^    if: (?:>\n((?:^      [^\n]+\n)+)|([^\n]+))', jobs[name], re.M)
        self.assertIsNotNone(match, f'{name} must have an explicit job condition')
        condition = ' '.join((match[1] or match[2]).split())
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for compiled condition checks')
        # These generated conditions use the shared JS/Actions boolean syntax.
        # This checks their truth table, not GitHub scheduling or process cancellation.
        script = """
const {condition, cases} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const check = new Function('needs', 'cancelled', 'always', 'contains', 'github', 'vars',
                          'return (' + condition + ');');
process.stdout.write(JSON.stringify(cases.map(c => check(
    c.needs, () => c.cancelled, () => true, (value, part) => value.includes(part),
    {run_attempt: c.attempt ?? 1, repository: 'andreleocl/duckdb-triage-agent', ref: 'refs/heads/main'},
    {TRIAGE_ENABLED: 'true'}))));
"""
        result = subprocess.run([node, '-e', script], input=json.dumps(dict(condition=condition, cases=cases)),
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        for case, actual in zip(cases, json.loads(result.stdout), strict=True):
            with self.subTest(job=name, case=case):
                self.assertIs(actual, case['expected'])

    def test_detection_requires_successful_dependencies_and_no_cancellation(self):
        cases = []
        for cancelled in (False, True):
            for activation in ('success', 'failure', 'cancelled', 'skipped'):
                for agent in ('success', 'failure', 'cancelled', 'skipped'):
                    cases.append(dict(cancelled=cancelled,
                                      needs=dict(activation=dict(result=activation), agent=dict(result=agent)),
                                      expected=not cancelled and activation == agent == 'success'))
        self.assert_job_condition('detection', cases)

    def test_publication_remains_blocked_without_detection_or_after_cancellation(self):
        cases = []
        for cancelled in (False, True):
            for detection in ('success', 'failure', 'cancelled', 'skipped'):
                for output_types in ('submit_triage', ''):
                    cases.append(dict(cancelled=cancelled,
                                      needs=dict(agent=dict(result='success', outputs=dict(output_types=output_types)),
                                                 detection=dict(result=detection)),
                                      expected=not cancelled and detection == 'success' and bool(output_types)))
        self.assert_job_condition('submit_triage', cases)

    def test_every_paid_or_publishing_job_rejects_reruns(self):
        needs = dict(pre_activation=dict(outputs=dict(activated='true')),
                     activation=dict(result='success'),
                     agent=dict(result='success', outputs=dict(output_types='submit_triage')),
                     detection=dict(result='success'))
        for job in ('activation', 'agent', 'detection', 'submit_triage'):
            self.assert_job_condition(job, [dict(cancelled=False, needs=needs, attempt=attempt,
                                                  expected=attempt == 1) for attempt in (1, 2, 3)])

    def test_admission_precedes_inference_and_concurrency_is_preserved(self):
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        jobs = dict(re.findall(r'^  ([a-z_]+):\n(.*?)(?=^  [a-z_]+:\n|\Z)',
                               lock.split('\njobs:\n', 1)[1], re.M | re.S))
        self.assertIn('run: python scripts/triage_runtime.py prepare', jobs['activation'])
        self.assertIn('actions: read', jobs['activation'])
        self.assertIn('needs: activation', jobs['agent'])
        self.assertNotIn('continue-on-error: true', jobs['activation'].split('id: prepare', 1)[1].split('      - ', 1)[0])
        self.assertIn('concurrency:\n  cancel-in-progress: false\n  group: duckdb-triage', lock)
        self.assertNotIn('check_rate_limit.cjs', lock)

    def test_compiled_submission_schema_uses_three_required_strings(self):
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        block = lock.split('GH_AW_TOOLS_META_JSON: |\n', 1)[1].split('          GH_AW_VALIDATION_JSON:', 1)[0]
        metadata = json.loads(block)
        tool = next(t for t in metadata['dynamic_tools'] if t['name'] == 'submit_triage')
        schema = tool['inputSchema']
        fields = {'label', 'comment', 'rationale'}
        self.assertEqual(set(schema['properties']), fields)
        self.assertEqual(set(schema['required']), fields)
        self.assertIs(schema['additionalProperties'], False)
        self.assertTrue(all(p['type'] == 'string' for p in schema['properties'].values()))

    def test_pinned_framework_required_fields_accept_sentinel_and_reject_empty_pair(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node.js is required for the pinned framework validation check')
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        metadata = json.loads(lock.split('# gh-aw-metadata: ', 1)[1].splitlines()[0])
        self.assertEqual(metadata['compiler_version'], 'v0.93.5')
        block = lock.split('GH_AW_TOOLS_META_JSON: |\n', 1)[1].split('          GH_AW_VALIDATION_JSON:', 1)[0]
        schema = next(t['inputSchema'] for t in json.loads(block)['dynamic_tools']
                      if t['name'] == 'submit_triage')
        fixture = (ROOT / 'tests/fixtures/gh_aw_v0_93_5_required_fields.js').read_text(encoding='utf-8')
        function = fixture[fixture.index('function validateRequiredFields('):]
        self.assertEqual(hashlib.sha256(function.encode()).hexdigest(),
                         'f42da12482b6d67796fe88473984af8f68704fdb936bd9b8befd717d6fddb06b')
        no_action = dict(label='no_action', comment='no_action', rationale='No essential gap.')
        request = dict(label='needs more info', comment='Which build produced "parse failed"?',
                       rationale='The build is missing.')
        cases = [no_action, request, {**no_action, 'label': '', 'comment': ''},
                 {**no_action, 'label': ' ', 'comment': '\t'}, {**no_action, 'rationale': ''},
                 {**no_action, 'label': None}, {k: v for k, v in no_action.items() if k != 'comment'}]
        script = fixture + """
const {schema, cases} = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(cases.map(args => validateRequiredFields(args, schema))));
"""
        result = subprocess.run([node, '-e', script], input=json.dumps(dict(schema=schema, cases=cases)),
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([sorted(missing) for missing in json.loads(result.stdout)],
                         [[], [], ['comment', 'label'], ['comment', 'label'], ['rationale'],
                          ['label'], ['comment']])
        for args in (no_action, request):
            proposal = runtime.proposal_from_output(dict(items=[dict(type='submit_triage', **args)]))
            runtime.validator.validate(proposal, runtime.REPOSITORY, 7)
        self.assertEqual(runtime.proposal_from_output(dict(items=[dict(type='submit_triage', **no_action)])),
                         dict(label=None, comment=None, rationale='No essential gap.'))

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
