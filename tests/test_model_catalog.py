"""Offline checks for model metadata and both compiled model jobs."""

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'gpt-5-mini'
CATALOG_PATH = '/tmp/gh-aw/model-catalog/model-catalog.json'


class ModelCatalogue(unittest.TestCase):
    def test_catalogue_preserves_alias_and_tool_boundary(self):
        catalog = json.loads((ROOT / '.github/codex/model-catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(catalog['models']), 1)
        model = catalog['models'][0]
        self.assertEqual(model['slug'], MODEL)
        self.assertTrue(model['supported_in_api'])
        self.assertEqual(['minimal', 'low', 'medium', 'high'],
                         [level['effort'] for level in model['supported_reasoning_levels']])
        self.assertEqual(model['context_window'], 272000)
        self.assertIsNone(model['upgrade'])
        self.assertFalse(model['supports_parallel_tool_calls'])
        self.assertIsNone(model['apply_patch_tool_type'])

    def test_both_jobs_receive_catalogue_without_changing_proxy(self):
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        jobs = dict(re.findall(r'^  ([a-z_]+):\n(.*?)(?=^  [a-z_]+:\n|\Z)', lock.split('\njobs:\n', 1)[1], re.M | re.S))
        agent, detection = jobs['agent'], jobs['detection']
        self.assertIn(CATALOG_PATH, agent)
        for job in (agent, detection):
            self.assertIn('name: codex-model-catalog', job)
            self.assertIn(MODEL, job)
        self.assertLess(agent.index('name: codex-model-catalog'), agent.index('name: Execute Codex CLI'))
        self.assertLess(detection.index('name: Configure detector model catalogue'), detection.index('name: Execute threat detection'))
        self.assertIn('CODEX_HOME: /tmp/gh-aw/detection-codex-home', detection)
        config = (ROOT / '.github/codex/detection-config.toml').read_text(encoding='utf-8')
        self.assertIn('model_catalog_json = "' + CATALOG_PATH + '"', config)
        for setting in ('model_provider = "openai-proxy"', 'base_url = "http://172.30.0.30:10000"',
                        'env_key = "CODEX_API_KEY"', 'wire_api = "responses"',
                        'requires_openai_auth = false', 'supports_websockets = false'):
            self.assertIn(setting, config)
            self.assertIn(setting, detection)
        self.assertNotIn('actions/checkout@', agent)


if __name__ == '__main__':
    unittest.main()
