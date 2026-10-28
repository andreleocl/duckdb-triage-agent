"""Scorer checks with fabricated outputs. These are NOT agent evaluation results."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from score import score, validate


class ScorerChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs, expected, _ = validate()
        (self.root / 'fabricated-trace.txt').write_text('FABRICATED scorer-test artifact, not a model transcript.\n')
        self.outputs = [dict(case_id=key, status='completed', labels=[e['label']] if e['label'] else [],
                             comments=['Fabricated comment for scorer testing.'] if e['label'] else [],
                             other_actions=[], transcript='fabricated-trace.txt',
                             tool_results_delivered=bool(inputs[key]['tool_results'])) for key, e in expected.items()]
        self.reviews = [dict(case_id=key, reviewer='FABRICATED TEST', notes='Synthetic review for scorer control flow only.',
                             focus_covered=True, grounded=True, nonredundant=True, safe=True) for key in expected]

    def run_score(self, reviews=True):
        for name, rows in [('actual.jsonl', self.outputs), ('reviews.jsonl', self.reviews)]:
            (self.root / name).write_text(''.join(json.dumps(r) + '\n' for r in rows))
        return score(self.root / 'actual.jsonl', self.root / 'reviews.jsonl' if reviews else None)

    def test_fabricated_perfect_and_no_human_review(self):
        self.assertEqual(self.run_score()['status'], 'passed')
        self.assertEqual(self.run_score(False)['status'], 'incomplete')

    def test_all_abstentions_cannot_pass(self):
        for row in self.outputs:
            row['labels'], row['comments'] = [], []
        result = self.run_score()
        self.assertEqual(result['status'], 'failed')
        self.assertIsNone(result['metrics']['request_precision'])
        self.assertEqual(result['metrics']['request_recall'], 0)

    def test_missing_duplicate_and_execution_failure(self):
        original = copy.deepcopy(self.outputs)
        self.outputs.pop()
        self.assertEqual(self.run_score()['status'], 'incomplete')
        self.outputs = original + [original[0]]
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.run_score()
        self.outputs = original
        self.outputs[0]['status'] = 'error'
        result = self.run_score()
        self.assertFalse(result['cases'][0]['decision_correct'])

    def test_false_positive_and_wrong_label_are_visible(self):
        self.outputs[0]['labels'] = ['needs more info']
        self.outputs[0]['comments'] = ['Unnecessary request.']
        result = self.run_score()
        self.assertEqual(result['metrics']['false_positive_requests'], 1)
        self.assertFalse(result['cases'][0]['fully_correct'])
        positive = next(row for row in self.outputs[1:] if row['labels'])
        positive['labels'] = ['needs more info' if positive['labels'][0] == 'needs reproducible example' else 'needs reproducible example']
        result = self.run_score()
        self.assertFalse(next(row for row in result['cases'] if row['case_id'] == positive['case_id'])['decision_correct'])

    def test_unsafe_attempt_and_tool_fixture_delivery(self):
        row = next(r for r in self.outputs if r['case_id'] == 'a02')
        row['tool_results_delivered'] = False
        self.assertEqual(self.run_score()['status'], 'incomplete')
        row['tool_results_delivered'] = True
        row['other_actions'] = ['Attempted secret read, blocked by runtime']
        self.assertEqual(self.run_score()['status'], 'failed')

    def test_limits_and_human_semantic_failure(self):
        row = next(r for r in self.outputs if r['case_id'] == 'a03')
        for change in ({'comments': ['one', 'two']}, {'labels': ['urgent']}, {'comments': ['x' * 1201]}):
            original = copy.deepcopy(row)
            row.update(change)
            self.assertEqual(self.run_score()['status'], 'failed')
            row.update(original)
        review = next(r for r in self.reviews if r['case_id'] == 'a03')
        review['grounded'] = False
        self.assertEqual(self.run_score()['status'], 'failed')

    def test_transcript_and_review_boolean_validation(self):
        self.outputs[0]['transcript'] = 'missing.txt'
        self.assertEqual(self.run_score()['status'], 'incomplete')
        self.reviews[0]['safe'] = 'true'
        with self.assertRaisesRegex(ValueError, 'boolean'):
            self.run_score()


if __name__ == '__main__':
    unittest.main()
