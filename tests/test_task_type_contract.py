from __future__ import annotations

import importlib.util
import sys
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


navigator_scope = load("tailtrail_task_contract_scope_test", "scripts/navigator_scope.py")


class EditablePathsForTaskTypesTests(unittest.TestCase):
    def test_qa_keeps_tests_only(self):
        result = navigator_scope.editable_paths_for_task_types(
            ["tests/test_x.py", "src/work.py", "navigator.legacy.py"], ["qa"])
        self.assertEqual(result["editable"], ["tests/test_x.py"])
        self.assertEqual(result["inspection"], ["navigator.legacy.py", "src/work.py"])
        self.assertTrue(result["contract"]["restricted"])

    def test_doc_keeps_docs_only(self):
        result = navigator_scope.editable_paths_for_task_types(
            ["docs/guide.md", "src/work.py"], ["documentation"])
        self.assertEqual(result["editable"], ["docs/guide.md"])
        self.assertEqual(result["inspection"], ["src/work.py"])

    def test_implementation_stays_broad(self):
        result = navigator_scope.editable_paths_for_task_types(
            ["tests/test_x.py", "src/work.py"], ["implementation"])
        self.assertEqual(result["editable"], ["src/work.py", "tests/test_x.py"])
        self.assertEqual(result["inspection"], [])
        self.assertFalse(result["contract"]["restricted"])

    def test_multi_type_unions(self):
        result = navigator_scope.editable_paths_for_task_types(
            ["tests/test_x.py", "docs/guide.md", "src/work.py"], ["qa", "doc"])
        self.assertEqual(result["editable"], ["docs/guide.md", "tests/test_x.py"])
        self.assertEqual(result["inspection"], ["src/work.py"])

    def test_unmappable_types_impose_nothing(self):
        result = navigator_scope.editable_paths_for_task_types(
            ["src/work.py"], ["security"])
        self.assertEqual(result["editable"], ["src/work.py"])
        self.assertFalse(result["contract"]["restricted"])

    def test_empty_types_impose_nothing(self):
        result = navigator_scope.editable_paths_for_task_types(["src/work.py"], [])
        self.assertEqual(result["editable"], ["src/work.py"])


def _sealed_evidence(owners):
    document = {
        "schema_version": "2",
        "type": "tailtrail-navigator-scope-evidence",
        "state": "resolved",
        "requirements": [{
            "requirement_id": "req-1",
            "display_id": "REQ-01",
            "scope_state": "resolved",
            "implementation_owners": list(owners),
            "inspection_paths": [],
            "proof_paths": ["tests/test_x.py"],
            "query_terms": [],
        }],
        "candidates": [],
        "edges": [],
        "investigation": {"state": "resolved"},
    }
    document["decision_fingerprint"] = navigator_scope.fingerprint(
        navigator_scope._fingerprintable_document(document))
    return document


def _binding_report(owners, task_types, resolution=None):
    navigator = {
        "scope_evidence": _sealed_evidence(owners),
        "requirement_matrix": [{
            "requirement_uid": "req-1", "display_id": "REQ-01",
            "statement": "Do the thing.",
            "validation_contract": {"state": "required", "tiers": ["unit"]},
        }],
        "task_types": list(task_types),
    }
    report: dict = {
        "navigator": navigator,
        "aidlc_mode": {"mode": "lite"},
    }
    if resolution is not None:
        report["task_type_resolution"] = dict(resolution)
    return report


class ScopeBindingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from workflow_runtime import start_integration
        cls.binding = start_integration

    def test_qa_binding_narrows_to_tests(self):
        report = _binding_report(
            ["tests/test_x.py", "src/work.py", "navigator.legacy.py"], ["qa"])
        bound = self.binding.scope_binding(report)
        self.assertEqual(bound["editable_paths"], ["tests/test_x.py"])
        self.assertEqual(
            bound["implementation_paths"], ["tests/test_x.py"])
        self.assertIn("src/work.py", bound["inspection_paths"])
        self.assertIn("navigator.legacy.py", bound["inspection_paths"])
        self.assertTrue(bound["task_type_contract"]["restricted"])

    def test_resolved_override_wins_over_classifier(self):
        report = _binding_report(
            ["tests/test_x.py", "src/work.py"], ["qa"],
            {"status": "resolved", "task_type": "implementation"})
        bound = self.binding.scope_binding(report)
        self.assertEqual(
            bound["editable_paths"], ["src/work.py", "tests/test_x.py"])

    def test_implementation_binding_unchanged(self):
        report = _binding_report(
            ["tests/test_x.py", "src/work.py"], ["implementation"])
        bound = self.binding.scope_binding(report)
        self.assertEqual(
            bound["editable_paths"], ["src/work.py", "tests/test_x.py"])
        self.assertFalse(bound["task_type_contract"]["restricted"])


if __name__ == "__main__":
    unittest.main()
