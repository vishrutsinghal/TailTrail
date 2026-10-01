from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


task_start = load("tailtrail_complexity_corroboration_start_test", "scripts/task-start.py")
# Canonical import: task-start.py resolves `from metrics_extractor import ...`
# locally at call time, so patches must land on this exact module object.
import metrics_extractor  # noqa: E402


def _complexity(**overrides):
    base = {
        "source": "scope_evidence",
        "available": True,
        "affected_files": 0,
        "changed_lines_estimate": 0,
        "cross_layer_edges": 0,
        "call_chain_depth_stddev": 0.0,
        "module_resolution_ambiguous": 0,
        "new_external_deps": 0,
        "behavior_chain_incomplete": False,
        "thresholds": dict(metrics_extractor.DEFAULT_THRESHOLDS),
    }
    base.update(overrides)
    return base


# File-count breadth only: the lexical-noise case (twenty candidates, one edit).
_FILE_COUNT_ONLY = _complexity(affected_files=25, changed_lines_estimate=200)

# Corroborated: file count plus a second witness.
_CORROBORATED = _complexity(affected_files=25, changed_lines_estimate=200, cross_layer_edges=3)

_QUIET = _complexity()


class CorroboratedScopeSignalTests(unittest.TestCase):
    def test_file_count_only_is_uncorroborated(self):
        corroborated, fired = task_start._corroborated_scope_signal(_FILE_COUNT_ONLY)
        self.assertFalse(corroborated)
        self.assertEqual(fired, [])

    def test_each_witness_corroborates(self):
        for key, value in (
            ("cross_layer_edges", 2),
            ("call_chain_depth_stddev", 3.0),
            ("module_resolution_ambiguous", 3),
            ("new_external_deps", 1),
            ("behavior_chain_incomplete", True),
        ):
            with self.subTest(witness=key):
                corroborated, fired = task_start._corroborated_scope_signal(_complexity(**{key: value}))
                self.assertTrue(corroborated)
                self.assertIn(key, fired)

    def test_missing_thresholds_reports_uncorroborated(self):
        plain = _complexity(cross_layer_edges=9)
        del plain["thresholds"]
        corroborated, fired = task_start._corroborated_scope_signal(plain)
        self.assertFalse(corroborated)
        self.assertEqual(fired, [])

    def test_non_dict_reports_uncorroborated(self):
        self.assertEqual(task_start._corroborated_scope_signal(None), (False, []))


class ModeSelectionCorroborationTests(unittest.TestCase):
    def setUp(self):
        self._orig_compute = metrics_extractor.compute_complexity
        self._orig_navigator = task_start.navigator_standard_evidence
        bridge = task_start.official_aidlc_bridge
        self._orig_preflight = bridge.preflight
        bridge.preflight = lambda root, mode, manifest=None: {
            "mode": mode, "state": "test-preflight", "requested_mode": mode,
        }
        task_start.navigator_standard_evidence = lambda goal, plan: {
            "selected": False, "signals": [], "reason": "test: no routing signal",
        }
        self._complexity = _QUIET

        def _fake_compute(likely, scope_ev, root):
            return self._complexity

        metrics_extractor.compute_complexity = _fake_compute

    def tearDown(self):
        metrics_extractor.compute_complexity = self._orig_compute
        task_start.navigator_standard_evidence = self._orig_navigator
        task_start.official_aidlc_bridge.preflight = self._orig_preflight

    def _select(self, goal="Refactor the retry helper", **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            return task_start.aidlc_mode_selection(
                goal, None, Path(temp), {"likely_impacted_files": []}, None, **kwargs
            )

    def test_file_count_only_stays_lite(self):
        self._complexity = _FILE_COUNT_ONLY
        selected = self._select()
        self.assertEqual(selected["mode"], "lite")
        self.assertEqual(selected["selection"], "scope-complexity-uncorroborated")

    def test_corroborated_signal_escalates_standard(self):
        self._complexity = _CORROBORATED
        selected = self._select()
        self.assertEqual(selected["mode"], "standard")
        self.assertEqual(selected["selection"], "scope-complexity-standard")

    def test_quiet_stays_lite_default(self):
        selected = self._select()
        self.assertEqual(selected["mode"], "lite")
        self.assertEqual(selected["selection"], "default")

    def test_declared_complex_escalates_one_notch(self):
        self._complexity = _QUIET
        selected = self._select(declared_complexity="complex")
        self.assertEqual(selected["mode"], "standard")
        self.assertEqual(selected["selection"], "declared-complexity-escalation")

    def test_declared_complex_escalates_uncorroborated_breadth(self):
        self._complexity = _FILE_COUNT_ONLY
        selected = self._select(declared_complexity="complex")
        self.assertEqual(selected["mode"], "standard")
        self.assertEqual(selected["selection"], "declared-complexity-escalation")

    def test_declared_simple_cannot_deescalate_corroborated_evidence(self):
        self._complexity = _CORROBORATED
        selected = self._select(declared_complexity="simple")
        self.assertEqual(selected["mode"], "standard")
        self.assertEqual(selected["selection"], "scope-complexity-standard")
        self.assertIn("complexity_disagreement", selected)

    def test_declared_simple_agrees_with_quiet_lite(self):
        self._complexity = _QUIET
        selected = self._select(declared_complexity="simple")
        self.assertEqual(selected["mode"], "lite")
        self.assertNotIn("complexity_disagreement", selected)

    def test_invalid_declared_complexity_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                task_start.aidlc_mode_selection(
                    "Refactor the retry helper", None, Path(temp),
                    {"likely_impacted_files": []}, None,
                    declared_complexity="enormous",
                )


if __name__ == "__main__":
    unittest.main()
