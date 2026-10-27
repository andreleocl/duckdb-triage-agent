"""Invented proposals exercise validation, not model decision quality."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / '.claude/skills/duckdb-triage/scripts/validate_output.py'
spec = importlib.util.spec_from_file_location('validate_output', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class OutputValidation(unittest.TestCase):
    def request(self, **changes):
        return dict(label='needs reproducible example', comment='Could you share a generated input?',
                    rationale='The input used by the command is absent.', **changes)

    def check(self, proposal):
        return validator.validate(proposal, validator.REPOSITORY, 7)

    def test_allowed_decisions(self):
        for label in validator.LABELS:
            proposal = self.request()
            proposal['label'] = label
            self.assertEqual(self.check(proposal), proposal)
        self.check(dict(label=None, comment=None, rationale='Complete supplied example.'))

    def test_wrong_shapes_and_extra_actions(self):
        invalid = [[], {}, self.request(close_issue=True), self.request(repository='other/repo')]
        for field, values in {'label': ['bug', [], False], 'comment': [None, '', '  ', []],
                              'rationale': ['', None, 3]}.items():
            for value in values:
                invalid.append({**self.request(), field: value})
        invalid.append(dict(label=None, comment='Unnecessary question', rationale='No gap.'))
        for proposal in invalid:
            with self.subTest(proposal=proposal), self.assertRaises(ValueError):
                self.check(proposal)

    def test_comment_boundary(self):
        self.check({**self.request(), 'comment': '\U0001f986' * 1200})
        with self.assertRaises(ValueError):
            self.check({**self.request(), 'comment': '\U0001f986' * 1201})

    def test_notification_references_rejected(self):
        for comment in ['Ask @someone', '@team/maintainers', 'See #123', 'other/repo#42',
                        '[source](https://github.com/other/repo/issues/42)', 'DUCKDB/DUCKDB']:
            with self.subTest(comment=comment), self.assertRaises(ValueError):
                self.check({**self.request(), 'comment': comment})

    def test_target_from_caller(self):
        for repository, issue in [('other/repo', 7), (validator.REPOSITORY, 0),
                                  (validator.REPOSITORY, -1), (validator.REPOSITORY, True),
                                  (validator.REPOSITORY, '7')]:
            with self.subTest(repository=repository, issue=issue), self.assertRaises(ValueError):
                validator.validate(self.request(), repository, issue)

    def test_contract_matches_frozen_limits(self):
        limits = json.loads((ROOT / 'evals/golden/thresholds.json').read_text(encoding='utf-8'))
        self.assertEqual(list(validator.LABELS), limits['labels'])
        self.assertEqual(validator.MAX_COMMENT_CHARS, limits['max_comment_chars'])
        self.assertEqual((limits['max_labels'], limits['max_comments']), (1, 1))

    def test_cli_accepts_valid_and_rejects_bad_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'proposal.json'
            command = [sys.executable, str(SCRIPT), str(path), '--repository',
                       validator.REPOSITORY, '--issue', '7']
            path.write_text(json.dumps(self.request()), encoding='utf-8')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), self.request())
            for content in ['{', '{"label":null,"label":"bug","comment":null,"rationale":"x"}',
                            json.dumps(self.request(close_issue=True))]:
                path.write_text(content, encoding='utf-8')
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, '')
            path.unlink()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)


if __name__ == '__main__':
    unittest.main()
