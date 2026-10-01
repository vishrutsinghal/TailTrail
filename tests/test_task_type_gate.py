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


task_start = load("tailtrail_task_type_gate_start_test", "scripts/task-start.py")


class PathKindTests(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(task_start._task_type_path_kind("tests/test_x.py"), "test")
        self.assertEqual(task_start._task_type_path_kind("src/mod/test_helper.py"), "test")
        self.assertEqual(task_start._task_type_path_kind("docs/guide.md"), "doc")
        self.assertEqual(task_start._task_type_path_kind("README.md"), "doc")
        self.assertEqual(task_start._task_type_path_kind(".github/workflows/ci.yml"), "infra")
        self.assertEqual(task_start._task_type_path_kind("Dockerfile"), "infra")
        self.assertEqual(task_start._task_type_path_kind("infra/main.tf"), "infra")
        self.assertEqual(task_start._task_type_path_kind("src/service.py"), "src")
        self.assertEqual(task_start._task_type_path_kind("scripts/task-start.py"), "src")


class AssessTaskTypeTests(unittest.TestCase):
    def test_default_implementation_resolves(self):
        decision = task_start.assess_task_type("Do something", ["implementation"], [], [], [], None)
        self.assertEqual((decision["status"], decision["task_type"]), ("resolved", "implementation"))

    def test_corroborated_qa_singleton_resolves(self):
        decision = task_start.assess_task_type(
            "Add tests", ["qa"], ["tests/test_x.py"], [], ["tests/test_x.py"], None,
        )
        self.assertEqual((decision["status"], decision["task_type"]), ("resolved", "qa"))

    def test_thin_singleton_asks(self):
        decision = task_start.assess_task_type(
            "Record commands from focused validation", ["qa"], [], ["scripts/task-start.py"], [], None,
        )
        self.assertEqual(decision["status"], "question")
        self.assertEqual(decision["question"]["question_id"], "TASK-Q1")
        self.assertEqual(len(decision["question"]["options"]), 4)

    def test_single_supported_type_among_many_resolves(self):
        decision = task_start.assess_task_type(
            "Add feature", ["qa", "implementation"], ["src/a.py"], ["src/a.py"], [], None,
        )
        self.assertEqual((decision["status"], decision["task_type"]), ("resolved", "implementation"))

    def test_tied_supported_types_ask(self):
        decision = task_start.assess_task_type(
            "Add feature with tests", ["qa", "implementation"],
            ["src/a.py", "tests/test_a.py"], ["src/a.py"], ["tests/test_a.py"], None,
        )
        self.assertEqual(decision["status"], "question")

    def test_unsupported_multi_asks(self):
        decision = task_start.assess_task_type(
            "Do review and qa", ["qa", "review"], [], [], [], None,
        )
        self.assertEqual(decision["status"], "question")

    def test_declared_agreement_resolves(self):
        decision = task_start.assess_task_type(
            "Add tests", ["qa"], ["tests/test_x.py"], [], [], "qa",
        )
        self.assertEqual(
            (decision["status"], decision["task_type"], decision["resolution"]),
            ("resolved", "qa", "declared-agreement"),
        )

    def test_declared_settles_uncertain(self):
        decision = task_start.assess_task_type(
            "Record commands", ["qa"], [], ["scripts/task-start.py"], [], "implementation",
        )
        self.assertEqual(
            (decision["status"], decision["task_type"], decision["resolution"]),
            ("resolved", "implementation", "declared-settles-uncertain"),
        )

    def test_declared_vs_strong_evidence_conflicts(self):
        decision = task_start.assess_task_type(
            "Add tests everywhere", ["qa"], ["tests/a.py", "tests/b.py"], [], ["tests/a.py"],
            "doc",
        )
        self.assertEqual(decision["status"], "conflict")
        self.assertIn("declared-doc-vs-evidenced-qa", decision["resolution"])

    def test_declared_vs_weak_evidence_settles(self):
        decision = task_start.assess_task_type(
            "Update tests", ["qa"], [], ["scripts/task-start.py"], [], "implementation",
        )
        # Only src-path support for implementation (1 signal < 2 needed for
        # a strong qa conflict) — but qa itself has no support either, so the
        # declaration settles the uncertain verdict.
        self.assertEqual(decision["status"], "resolved")
        self.assertEqual(decision["task_type"], "implementation")

    def test_implementation_family_maps_without_question(self):
        for tasks in (["feature"], ["bug"], ["refactor"]):
            with self.subTest(tasks=tasks):
                decision = task_start.assess_task_type(
                    "Do the thing", tasks, [], ["src/a.py"], [], None,
                )
                self.assertEqual(decision["status"], "resolved")
                self.assertEqual(decision["task_type"], "implementation")

    def test_unmappable_types_pass_through(self):
        decision = task_start.assess_task_type(
            "Audit dependencies", ["security"], [], [], [], None,
        )
        self.assertEqual(decision["status"], "resolved")
        self.assertEqual(decision["resolution"], "passthrough-unmapped-types")


class PostAnswerDeescalationTests(unittest.TestCase):
    def _report(self, owners, selection="scope-complexity-standard", mode="standard",
                edge_specs=None, state="resolved"):
        candidates = []
        edges = []
        for index, owner in enumerate(owners):
            candidate_id = f"cand-{index}"
            edge_ids = []
            for edge_index, (kind, strength) in enumerate(edge_specs or []):
                edge_id = f"e-{index}-{edge_index}"
                edge_ids.append(edge_id)
                edges.append({
                    "edge_id": edge_id, "strength": strength, "kind": kind,
                    "from_candidate_id": candidate_id, "to_candidate_id": candidate_id,
                })
            candidates.append({
                "path": owner, "candidate_id": candidate_id,
                "role": "implementation-owner", "status": "included",
                "confidence": "high", "reason_codes": [], "evidence_edge_ids": edge_ids,
            })
        return {
            "navigator": {
                "scope_evidence": {
                    "state": state,
                    "requirements": [{
                        "requirement_id": "req-1", "display_id": "REQ-01",
                        "scope_state": state, "implementation_owners": list(owners),
                        "inspection_paths": [], "proof_paths": [],
                    }],
                    "candidates": candidates,
                    "edges": edges,
                },
                "scope_quality": {},
            },
            "aidlc_mode": {"mode": mode, "selection": selection},
        }

    def test_thin_narrowed_scope_deescalates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(
                ["scripts/a.py", "scripts/b.py"],
                edge_specs=[("defines symbol", "strong")],
            )
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None)
        self.assertEqual(mode, "lite")
        self.assertEqual(report["aidlc_mode"]["selection"], "post-answer-de-escalation")

    def test_deep_narrowed_scope_keeps_standard(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(
                ["scripts/a.py", "scripts/b.py"],
                edge_specs=[("defines symbol", "strong"), ("calls function", "strong")],
            )
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None)
        self.assertIsNone(mode)
        self.assertEqual(report["aidlc_mode"]["mode"], "standard")

    def test_explicit_selection_never_deescalates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(["scripts/a.py"], selection="explicit-flag")
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None)
        self.assertIsNone(mode)

    def test_official_authority_blocks_deescalation(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(["scripts/a.py"])
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None, official_authority_present=True)
        self.assertIsNone(mode)

    def test_unresolved_evidence_never_deescalates(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(["scripts/a.py"], state="ambiguous")
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None)
        self.assertIsNone(mode)

    def test_nonstandard_mode_untouched(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            report = self._report(["scripts/a.py"], mode="lite")
            mode = task_start.post_answer_deescalation(
                report, Path(temp), None)
        self.assertIsNone(mode)


if __name__ == "__main__":
    unittest.main()
