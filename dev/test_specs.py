"""Specification consistency checks, not tests of the unimplemented product."""
import json
from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SpecificationTests(unittest.TestCase):
    def test_model_and_budget_configuration(self):
        plan = json.loads((ROOT / 'dev/plan.json').read_text())
        config = tomllib.loads((ROOT / '.codex/config.toml').read_text())
        self.assertEqual(plan['spec_revision'], '0.3')
        self.assertEqual(config['model'], plan['preferred_model'])
        self.assertEqual(config['model_reasoning_effort'], plan['preferred_effort'])
        self.assertEqual(plan['limits']['builder_tokens'], 40000)
        self.assertEqual(plan['limits']['validator_tokens'], 12000)
        self.assertFalse(config['features']['multi_agent'])

    def test_each_goal_has_read_list_and_checks(self):
        plan = json.loads((ROOT / 'dev/plan.json').read_text())
        for key, lane in plan['lanes'].items():
            text = (ROOT / lane['doc']).read_text()
            for goal in lane['goals']:
                with self.subTest(goal=goal['id']):
                    self.assertIn('/goal Complete ' + goal['id'], text)
                    self.assertIn('Read ', text)
                    for check_id in goal['checks']:
                        self.assertIn(check_id, text)
            self.assertIn('journals/' + key + '.md', lane['owned'])

    def test_retained_and_new_acceptance_coverage(self):
        text = (ROOT / 'docs/FEATURE_MATRIX.md').read_text()
        for prefix, count in [('AC', 14), ('UI', 5), ('MON', 5), ('COST', 5)]:
            for number in range(1, count + 1):
                self.assertIn(f'{prefix}-{number:02}', text)

    def test_computer_example_is_not_live_evidence(self):
        fixture = json.loads((ROOT / 'contracts/examples/computer.json').read_text())
        self.assertTrue(fixture['fixture_only'])
        self.assertEqual(fixture['contract_revision'], '1.1')
        for key in ['manifest_response', 'diff_response', 'log_response']:
            self.assertEqual(fixture[key]['v'], 1)
        rows = fixture['diff_response']['rows']
        self.assertEqual({r['kind'] for r in rows}, {'file_header', 'hunk_header', 'add', 'remove'})
        self.assertTrue(any(f['binary'] for f in fixture['manifest_response']['files']))
        self.assertTrue(any(f['status'] == 'renamed' for f in fixture['manifest_response']['files']))

    def test_mermaid_blocks_are_closed(self):
        for path in (ROOT / 'docs').glob('*.md'):
            text = path.read_text()
            blocks = re.findall(r'^```.*$', text, flags=re.MULTILINE)
            self.assertEqual(len(blocks) % 2, 0, str(path))
            self.assertNotIn('```mermaid\n```', text)


if __name__ == '__main__':
    unittest.main()
