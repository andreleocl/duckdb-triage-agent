"""Offline checks for model metadata and both compiled model jobs."""

import json
import os
import subprocess
import sys
import tempfile
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

    def test_detector_timeout_patch_and_dependency_drift(self):
        workflow = (ROOT / '.github/workflows/issue-triage.md').read_text(encoding='utf-8')
        script = workflow.split("python - <<'PY'\n", 1)[1].split('          PY', 1)[0]
        script = '\n'.join(line[10:] for line in script.splitlines())
        old = 'const AWF_MODELS_URL_TIMEOUT_MS = 3000;'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'gh-aw/actions/awf_reflect.cjs'
            path.parent.mkdir(parents=True)
            for source, expected in ((old, 0), ('changed implementation', 1), (old + '\n' + old, 1)):
                with self.subTest(source=source):
                    path.write_text(source, encoding='utf-8')
                    result = subprocess.run([sys.executable, '-c', script],
                                            env={**os.environ, 'RUNNER_TEMP': directory},
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected)
                    self.assertEqual(path.read_text(encoding='utf-8'),
                                     source.replace('3000', '15000') if expected == 0 else source)
        lock = (ROOT / '.github/workflows/issue-triage.lock.yml').read_text(encoding='utf-8')
        detection = lock.split('\n  detection:\n', 1)[1].split('\n  conclusion:\n', 1)[0]
        self.assertLess(detection.index('name: Extend detector model lookup timeout'),
                        detection.index('name: Execute threat detection'))
        self.assertIn('const AWF_MODELS_URL_TIMEOUT_MS = 15000;', detection)
        self.assertIn('GH_AW_DETECTION_CONTINUE_ON_ERROR: "false"', detection)

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
