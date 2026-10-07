"""Offline configuration/launcher tests. Never calls a real model."""
import copy
import unittest
from unittest.mock import patch

import loop
import luna


MODEL = {'id': luna.MODEL, 'model': luna.MODEL,
         'supportedReasoningEfforts': [{'reasoningEffort': 'max'}],
         'inputModalities': ['text', 'image']}


class CatalogRPC:
    def __init__(self, pages=None, config=None):
        self.pages = pages or [{'data': [copy.deepcopy(MODEL)], 'nextCursor': None}]
        self.config = config if config is not None else {'model': luna.MODEL, 'model_reasoning_effort': 'max'}
        self.calls = []
        self.index = 0

    def request(self, method, params):
        self.calls.append((method, params))
        if method == 'config/read':
            return {'config': self.config}
        if method == 'model/list':
            page = self.pages[self.index]
            self.index += 1
            return page
        raise AssertionError('Unexpected inference or mutation call: ' + method)


class LunaTests(unittest.TestCase):
    def test_supported_selection_does_not_start_turn(self):
        rpc = CatalogRPC()
        result = luna.verify_selection(rpc, require_images=True)
        self.assertEqual(result['model'], luna.MODEL)
        self.assertFalse(result['inference_started'])
        self.assertEqual([m for m, _ in rpc.calls], ['config/read', 'model/list'])

    def test_wrong_effective_model_or_effort_stops(self):
        for config in [{'model': 'gpt-6-sol', 'model_reasoning_effort': 'max'},
                       {'model': luna.MODEL, 'model_reasoning_effort': 'low'}, {}]:
            with self.subTest(config=config), self.assertRaises(loop.Stop):
                luna.verify_selection(CatalogRPC(config=config))

    def test_missing_model_does_not_fallback(self):
        with self.assertRaises(loop.Stop):
            luna.verify_selection(CatalogRPC(pages=[{'data': [], 'nextCursor': None}]))

    def test_missing_max_stops(self):
        row = copy.deepcopy(MODEL)
        row['supportedReasoningEfforts'] = [{'reasoningEffort': 'high'}]
        with self.assertRaises(loop.Stop):
            luna.verify_selection(CatalogRPC(pages=[{'data': [row]}]))

    def test_image_requirement(self):
        row = copy.deepcopy(MODEL)
        row['inputModalities'] = ['text']
        with self.assertRaises(loop.Stop):
            luna.verify_selection(CatalogRPC(pages=[{'data': [row]}]), True)
        self.assertEqual(luna.verify_selection(CatalogRPC(pages=[{'data': [row]}]), False)['model'], luna.MODEL)

    def test_missing_modalities_follow_documented_compatibility(self):
        row = copy.deepcopy(MODEL)
        del row['inputModalities']
        self.assertIn('image', luna.verify_selection(CatalogRPC(pages=[{'data': [row]}]), True)['input_modalities'])

    def test_catalog_pagination(self):
        rpc = CatalogRPC(pages=[{'data': [], 'nextCursor': 'second'}, {'data': [MODEL], 'nextCursor': None}])
        luna.verify_selection(rpc)
        self.assertEqual(rpc.calls[-1][1]['cursor'], 'second')

    def test_repeated_cursor_stops(self):
        rpc = CatalogRPC(pages=[{'data': [], 'nextCursor': 'same'}, {'data': [], 'nextCursor': 'same'}])
        with self.assertRaises(loop.Stop):
            luna.verify_selection(rpc)

    def test_invalid_catalog_shape_stops(self):
        with self.assertRaises(loop.Stop):
            luna.verify_selection(CatalogRPC(pages=[{'data': None}]))

    def test_pinned_command_and_restoration(self):
        calls = []
        def fake(*args, **kwargs):
            calls.append(kwargs)
            return 'candidate'
        with patch.object(loop, 'native_goal', fake):
            with luna.pinned_goals():
                self.assertEqual(loop.native_goal('unused'), 'candidate')
            self.assertIs(loop.native_goal, fake)
        self.assertEqual(calls[0]['command'], luna.COMMAND)
        self.assertIn('model_reasoning_effort="max"', calls[0]['command'])

    def test_restoration_on_exception(self):
        original = loop.native_goal
        with self.assertRaises(RuntimeError):
            with luna.pinned_goals():
                raise RuntimeError('test')
        self.assertIs(loop.native_goal, original)


if __name__ == '__main__':
    unittest.main()
