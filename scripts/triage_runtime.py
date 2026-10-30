"""Trusted workflow preparation and publication; never executes issue text."""

from datetime import datetime, timedelta, timezone
import errno
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import unquote, urlencode

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / '.claude/skills/duckdb-triage/SKILL.md'
VALIDATOR = ROOT / '.claude/skills/duckdb-triage/scripts/validate_output.py'
spec = importlib.util.spec_from_file_location('validate_output', VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
REPOSITORY = validator.REPOSITORY
BOT = 'github-actions[bot]'
WORKFLOW_PATH = '.github/workflows/issue-triage.lock.yml'
MAX_RUNS = 5


def target(event, environment):
    if (environment.get('GITHUB_REPOSITORY') != REPOSITORY
            or environment.get('GITHUB_REF') != 'refs/heads/main'
            or environment.get('GITHUB_EVENT_NAME') != 'workflow_dispatch'
            or environment.get('GITHUB_RUN_ATTEMPT') != '1'
            or environment.get('TRIAGE_ENABLED') != 'true'
            or environment.get('GITHUB_SERVER_URL') != 'https://github.com'):
        raise ValueError('Triage requires a fresh enabled manual dispatch on the assignment main branch')
    number = event.get('inputs', {}).get('issue_number')
    if not isinstance(number, str) or not re.fullmatch(r'[1-9][0-9]{0,9}', number):
        raise ValueError('Invalid selected issue number')
    return int(number)


def fingerprint(issue):
    return hashlib.sha256(json.dumps(issue, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def report(issue, number):
    if issue.get('number') != number or 'pull_request' in issue or issue.get('state') != 'open':
        raise ValueError('Target must be the selected open issue, not a pull request')
    title, body = issue.get('title'), issue.get('body')
    if not isinstance(title, str) or not title.strip() or not isinstance(body, str) or not body.strip():
        raise ValueError('Missing report title or body')
    if len(title) + len(body) > 40000:
        raise ValueError('Report exceeds 40000 characters; do not silently truncate')
    return dict(title=title, body=body)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected GitHub redirect')


class AdmissionDenied(ValueError):
    """A fixed, safe-to-log explanation for refusing a paid run."""


def admit_run(token, run_id, sha, now=None):
    # Count dispatch attempts, including blocked/cancelled runs, across all actors.
    # The UTC window is measured at admission; a dispatch older than it must restart.
    if not isinstance(run_id, str) or not re.fullmatch(r'[1-9][0-9]*', run_id):
        raise AdmissionDenied('Missing or invalid current run ID')
    now = (now or datetime.now(timezone.utc)).replace(microsecond=0)
    start = now - timedelta(hours=1)
    stamp = lambda value: value.strftime('%Y-%m-%dT%H:%M:%SZ')
    query = urlencode(dict(event='workflow_dispatch', created=f'{stamp(start)}..{stamp(now)}',
                           per_page=100, page=1, exclude_pull_requests='true'))
    url = f'https://api.github.com/repos/{REPOSITORY}/actions/workflows/issue-triage.lock.yml/runs?{query}'
    request = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'duckdb-triage-agent'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            history = json.load(response, object_pairs_hook=validator.unique_fields)
            links = response.headers.get('Link')
    except (ValueError, OSError) as error:
        if isinstance(error, urllib.error.HTTPError):
            error.close()
        raise AdmissionDenied('GitHub run history unavailable or invalid; refusing inference') from None
    total = history.get('total_count') if isinstance(history, dict) else None
    runs = history.get('workflow_runs') if isinstance(history, dict) else None
    if type(total) is not int or total < 1 or not isinstance(runs, list):
        raise AdmissionDenied('Run history is missing or malformed')
    if total > MAX_RUNS:
        raise AdmissionDenied('Five-dispatch hourly limit reached; blocked attempts also count')
    # Any allowable result fits on one page. Never allow from truncated history.
    if links or len(runs) != total:
        raise AdmissionDenied('Run history is incomplete; refusing inference')
    seen, workflow_ids, current = set(), set(), None
    for run in runs:
        if (not isinstance(run, dict) or type(run.get('id')) is not int or run['id'] < 1
                or type(run.get('workflow_id')) is not int or run['workflow_id'] < 1
                or type(run.get('run_attempt')) is not int or run['run_attempt'] < 1
                or run.get('path') != WORKFLOW_PATH or run.get('event') != 'workflow_dispatch'
                or not isinstance(run.get('repository'), dict)
                or run['repository'].get('full_name') != REPOSITORY):
            raise AdmissionDenied('Unexpected run identity in history')
        try:
            created = datetime.strptime(run['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            raise AdmissionDenied('Missing or invalid run timestamp') from None
        if not start <= created <= now or run['id'] in seen:
            raise AdmissionDenied('Out-of-window or duplicate run in history')
        seen.add(run['id'])
        workflow_ids.add(run['workflow_id'])
        if run['id'] == int(run_id):
            current = run
    if len(workflow_ids) != 1 or current is None:
        raise AdmissionDenied('Current run absent or inconsistent history; dispatch must be within the last hour')
    if current['run_attempt'] != 1 or current.get('head_branch') != 'main' or current.get('head_sha') != sha:
        raise AdmissionDenied('Current run does not match this fresh main-branch dispatch')
    return dict(status='allowed', checked_at=stamp(now), window_start=stamp(start),
                max_dispatches=MAX_RUNS, count=len(seen), run_ids=sorted(seen))


class GitHub:
    def __init__(self, token, number):
        self.token, self.number = token, number
        self.operations = []
        self.opener = urllib.request.build_opener(NoRedirect)

    def call(self, method, suffix='', data=None):
        # Callers cannot supply a repository, host, issue number or arbitrary endpoint.
        permitted = (method == 'GET' and (suffix == '' or re.fullmatch(r'/comments\?per_page=100&page=[1-9][0-9]*', suffix)))
        permitted = permitted or (method == 'POST' and suffix in ('/comments', '/labels'))
        if not permitted:
            raise ValueError('Operation is not allowed')
        url = f'https://api.github.com/repos/{REPOSITORY}/issues/{self.number}{suffix}'
        request = urllib.request.Request(url, method=method,
            data=None if data is None else json.dumps(data).encode(),
            headers={'Authorization': f'Bearer {self.token}', 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'User-Agent': 'duckdb-triage-agent'})
        attempts = 3 if method == 'GET' else 1
        for attempt in range(1, attempts + 1):
            operation = dict(method=method, endpoint=suffix, status='attempted', attempt=attempt)
            self.operations.append(operation)
            try:
                with self.opener.open(request, timeout=30) as response:
                    result = json.load(response)
                    operation['status'] = 'succeeded'
                    return result
            except urllib.error.HTTPError as error:
                category = f'HTTP {error.code}'
                retryable = error.code in (500, 502, 503, 504)
                error.close()
            except (urllib.error.URLError, OSError) as error:
                reason = error.reason if isinstance(error, urllib.error.URLError) else error
                if isinstance(reason, ssl.SSLError):
                    category, retryable = 'TLS error', False
                elif isinstance(reason, socket.gaierror):
                    category, retryable = 'DNS error', reason.errno == socket.EAI_AGAIN
                elif isinstance(reason, TimeoutError):
                    category, retryable = 'timeout', True
                else:
                    category = 'connection error'
                    retryable = isinstance(reason, OSError) and reason.errno in (
                        errno.ECONNRESET, errno.ECONNREFUSED, errno.ECONNABORTED,
                        errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ETIMEDOUT, errno.EPIPE)
            operation.update(status='failed', error_category=category)
            print(f'GitHub {method} attempt {attempt}/{attempts} failed: {category}', file=sys.stderr)
            if not retryable or attempt == attempts:
                raise ValueError(f'GitHub {method} failed: {category}; attempts={attempt}') from None
            time.sleep((1, 3)[attempt - 1])

    def comments(self):
        comments = []
        for page in range(1, 11):
            batch = self.call('GET', f'/comments?per_page=100&page={page}')
            if not isinstance(batch, list):
                raise ValueError('Invalid comment response')
            comments.extend(batch)
            if len(batch) < 100:
                return comments
        raise ValueError('Comment history exceeds inspection limit')


def prepare(client, number, sha):
    issue = report(client.call('GET'), number)
    skill = SKILL.read_text(encoding='utf-8')
    return dict(repository=REPOSITORY, number=number, issue=issue, input_sha256=fingerprint(issue),
                configuration_sha=sha, skill_path=str(SKILL.relative_to(ROOT)),
                skill_sha256=hashlib.sha256(skill.encode()).hexdigest()), skill


def proposal_from_output(output):
    items = output.get('items') if isinstance(output, dict) else None
    if not isinstance(items, list) or len(items) != 1:
        raise ValueError('Exactly one safe-output item is required')
    item = items[0]
    fields = ('label', 'comment', 'rationale')
    if (not isinstance(item, dict) or set(item) != {'type', *fields}
            or item['type'] != 'submit_triage'
            or any(not isinstance(item[field], str) for field in fields)):
        raise ValueError('Unexpected safe-output action or fields')
    proposal = {field: item[field] for field in fields}
    if proposal['label'] == 'no_action' or proposal['comment'] == 'no_action':
        if proposal['label'] != 'no_action' or proposal['comment'] != 'no_action':
            raise ValueError('No action requires the exact sentinel pair')
        proposal.update(label=None, comment=None)
    return proposal


def publish(client, number, snapshot, output, sha):
    if (snapshot.get('repository') != REPOSITORY or snapshot.get('number') != number
            or snapshot.get('configuration_sha') != sha
            or snapshot.get('input_sha256') != fingerprint(snapshot.get('issue'))):
        raise ValueError('Input artifact does not match trusted dispatch')
    proposal = proposal_from_output(output)
    validator.validate(proposal, REPOSITORY, number)
    live = client.call('GET')
    if report(live, number) != snapshot['issue']:
        raise ValueError('Report changed after preparation; select a fresh run')
    if proposal['label'] is None:
        return dict(status='no_action', proposal=proposal, actions=[])
    label = proposal['label']
    decoded = html.unescape(unquote(proposal['comment']))
    if re.search(r'@|https?://|www\.|github\.com|#\d+|<(?:/?[a-z][^<>]*>|!|\?)',
                 decoded, re.IGNORECASE):
        raise ValueError('Public questions must not include links, mentions, HTML or issue references')
    marker = f"<!-- duckdb-triage:v1 {snapshot['input_sha256']} {label} -->"
    body = proposal['comment'] + '\n\nAutomated triage suggestion.\n' + marker
    validator.validate({**proposal, 'comment': body}, REPOSITORY, number)
    labels = {entry['name'] for entry in live.get('labels', [])}
    existing = [c for c in client.comments() if c.get('user', {}).get('login') == BOT
                and c.get('user', {}).get('type') == 'Bot'
                and '<!-- duckdb-triage:v1 ' in (c.get('body') or '')]
    matching = [c for c in existing if marker in c['body']]
    if existing and not matching:
        return dict(status='already_triaged', proposal=proposal, actions=[])
    if labels.intersection(validator.LABELS) - {label}:
        return dict(status='existing_triage_label', proposal=proposal, actions=[])
    if not matching and labels.intersection(validator.LABELS):
        return dict(status='existing_triage_label', proposal=proposal, actions=[])
    current = client.call('GET')
    if report(current, number) != snapshot['issue'] or current.get('labels', []) != live.get('labels', []):
        raise ValueError('Issue changed before publication')
    actions = []
    if not matching:
        client.call('POST', '/comments', {'body': body})
        actions.append('add_comment')
    # A retry after successful comment creation repairs only a missing label.
    if label not in labels:
        client.call('POST', '/labels', {'labels': [label]})
        actions.append('add_label')
    return dict(status='published' if actions else 'already_triaged', proposal=proposal, actions=actions)


def main():
    receipt = dict(status='error')
    client = None
    directory = ROOT / '.triage'
    try:
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        number = target(event, os.environ)
        client = GitHub(os.environ['GH_TOKEN'], number)
        mode = sys.argv[1]
        if mode == 'prepare':
            admission = admit_run(os.environ['GH_TOKEN'], os.environ['GITHUB_RUN_ID'], os.environ['GITHUB_SHA'])
            print('Admission: ' + json.dumps(admission, sort_keys=True))
            snapshot, skill = prepare(client, number, os.environ['GITHUB_SHA'])
            directory.mkdir(exist_ok=True)
            (directory / 'input.json').write_text(json.dumps(snapshot, ensure_ascii=True), encoding='utf-8')
            with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
                # Single-line JSON prevents issue text from injecting Actions output keys.
                output.write('issue=' + json.dumps(snapshot['issue'], ensure_ascii=True) + '\n')
                output.write('skill=' + json.dumps(skill, ensure_ascii=True) + '\n')
        elif mode == 'publish':
            if os.environ.get('TRIAGE_AGENT_RESULT') != 'success':
                raise ValueError('Successful agent completion is required')
            if os.environ.get('GH_AW_DETECTION_CONCLUSION') != 'success':
                raise ValueError('Successful threat detection is required')
            if os.environ.get('GH_AW_SAFE_OUTPUTS_STAGED') == 'true':
                raise ValueError('Custom publisher does not implement staged mode; refusing writes')
            snapshot = json.loads((directory / 'input.json').read_text(encoding='utf-8'))
            output = json.loads(Path(os.environ['GH_AW_AGENT_OUTPUT']).read_text(encoding='utf-8'),
                                object_pairs_hook=validator.unique_fields)
            receipt = publish(client, number, snapshot, output, os.environ['GITHUB_SHA'])
            receipt.update(run_id=os.environ['GITHUB_RUN_ID'], configuration_sha=os.environ['GITHUB_SHA'],
                           input_sha256=snapshot['input_sha256'])
        else:
            raise ValueError('Expected prepare or publish')
    except (ValueError, KeyError, OSError, IndexError) as error:
        # Do not echo arbitrary API response bodies or report content into Actions logs.
        receipt['error_type'] = type(error).__name__
        detail = str(error) if isinstance(error, AdmissionDenied) else type(error).__name__
        print(f'Triage stopped: {detail}', file=sys.stderr)
        return 1
    finally:
        if len(sys.argv) > 1 and sys.argv[1] == 'publish':
            receipt['api_operations'] = client.operations if client else []
            directory.mkdir(exist_ok=True)
            (directory / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=True, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
