from __future__ import annotations

import importlib.util
import json
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


impact = load("tailtrail_verify_impact_test", "scripts/requirement-impact-map.py")
completion = load("tailtrail_verify_completion_test", "scripts/requirement-completion.py")
ledger = load("tailtrail_verify_ledger_test", "scripts/run-ledger.py")


def _anchor(root: Path, run_id: str, contracts: dict | None = None) -> None:
    contracts = contracts or {}
    directory = root / ".tailtrail" / "runs" / run_id / "anchors"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "approved-v1.json").write_text(json.dumps({
        "schema_version": "1", "type": "tailtrail-change-intent-anchor",
        "run_id": run_id, "status": "approved",
        "requirements": [{
            "requirement_uid": "req-1", "display_id": "REQ-01", "kind": "change",
            "statement": "Do the thing.", "acceptance_criteria": ["Done."],
            "preserve_rules": [], "likely_paths": ["src/work.py"],
            "evidence_plan": ["Run unit proof."],
            "validation_contract": contracts or {"state": "required", "tiers": ["unit"]},
            "status": "approved",
        }],
    }), encoding="utf-8")


class ImpactMapTests(unittest.TestCase):
    def test_maps_changed_to_callers_and_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src").mkdir()
            (root / "src" / "work.py").write_text("def build():\n    return 1\n", encoding="utf-8")
            (root / "app.py").write_text("from src.work import build\nprint(build())\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_work.py").write_text("from src.work import build\nbuild()\n", encoding="utf-8")
            ledger.init_run(root, "run-1", "do the thing")
            _anchor(root, "run-1")
            mapped = impact.map_impact(root, "run-1", ["src/work.py"])
        req = mapped["requirements"][0]
        self.assertEqual(req["classification"], "mapped")
        self.assertIn("src/work.py", [entry["path"] for entry in req["symbols"]])
        self.assertTrue(any(entry["path"] == "app.py" for entry in req["callers"]))
        self.assertTrue(any(entry["path"] == "tests/test_work.py" for entry in req["tests"]))
        self.assertIn("completion-review", req["selected_controls"])

    def test_unrelated_change_is_new_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src").mkdir()
            (root / "src" / "work.py").write_text("X = 1\n", encoding="utf-8")
            (root / "other.py").write_text("Y = 2\n", encoding="utf-8")
            ledger.init_run(root, "run-2", "do the thing")
            _anchor(root, "run-2")
            mapped = impact.map_impact(root, "run-2", ["other.py"])
        self.assertEqual(mapped["requirements"][0]["classification"], "new-drift")


class CompletionGateTests(unittest.TestCase):
    def _receipts(self, root: Path, items: list) -> Path:
        path = root / "receipts.json"
        path.write_text(json.dumps({"receipts": items}), encoding="utf-8")
        return path

    def _pass(self, quality="trusted"):
        return {"requirement_uids": ["req-1"], "tiers": ["unit"],
                "outcome": "pass", "evidence_quality": quality}

    def test_trusted_pass_completes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger.init_run(root, "run-1", "do the thing")
            _anchor(root, "run-1")
            gate = completion.gate(
                root, "run-1", self._receipts(root, [self._pass()]), record=False)
        self.assertTrue(gate["complete"])
        self.assertEqual(gate["findings"], [])

    def test_declared_pass_does_not_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger.init_run(root, "run-2", "do the thing")
            _anchor(root, "run-2")
            gate = completion.gate(
                root, "run-2", self._receipts(root, [self._pass("declared")]), record=False)
        self.assertFalse(gate["complete"])
        self.assertEqual(gate["findings"][0]["state"], "unverified")

    def test_authoritative_fail_dominates_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ledger.init_run(root, "run-3", "do the thing")
            _anchor(root, "run-3")
            gate = completion.gate(root, "run-3", self._receipts(root, [
                self._pass(),
                {"requirement_uids": ["req-1"], "tiers": ["unit"],
                 "outcome": "fail", "evidence_quality": "trusted"},
            ]), record=False)
        self.assertFalse(gate["complete"])
        self.assertEqual(gate["findings"][0]["state"], "fail")


if __name__ == "__main__":
    unittest.main()
