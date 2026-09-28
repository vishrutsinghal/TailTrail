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


if __name__ == "__main__":
    unittest.main()
