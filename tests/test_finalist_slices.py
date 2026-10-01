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


mapper = load("tailtrail_finalist_slices_mapper_test", "scripts/code-graph-mapper.py")


def _section():
    return {
        "schema_version": 1,
        "root": ".",
        "scope": ["b.py"],
        "source_files": {"b.py": {"sha256": "x"}},
        "graph": {
            "symbols": [{"name": "help", "kind": "function", "file": "b.py", "line": 1}],
            "references": [
                {
                    "target": "b",
                    "referring_file": "a.py",
                    "reference_type": "import",
                    "module_resolution": {"state": "resolved", "resolved_targets": ["b.py"]},
                },
                {
                    "target": "b",
                    "referring_file": "tests/test_b.py",
                    "reference_type": "import",
                    "module_resolution": {"state": "resolved", "resolved_targets": ["b.py"]},
                },
            ],
        },
    }


class FinalistSliceSummaryTests(unittest.TestCase):
    def test_splits_callers_tests_relations_symbols(self):
        summary = mapper.finalist_slice_summary(_section(), "b.py")
        self.assertEqual(summary["callers"], ["a.py"])
        self.assertEqual(summary["tests"], ["tests/test_b.py"])
        self.assertIn("import", summary["relations"])
        self.assertEqual(summary["symbols"], [{"name": "help", "kind": "function", "line": 1}])

    def test_unknown_shape_yields_empties(self):
        summary = mapper.finalist_slice_summary(None, "b.py")
        self.assertEqual(summary["callers"], [])
        self.assertEqual(summary["tests"], [])
        self.assertEqual(summary["symbols"], [])


class ExpandFinalistSlicesTests(unittest.TestCase):
    def _repo(self, root: Path) -> None:
        (root / "helper.py").write_text("def help():\n    return 1\n", encoding="utf-8")
        (root / "main.py").write_text("from helper import help\nprint(help())\n", encoding="utf-8")
        tests = root / "tests"
        tests.mkdir(exist_ok=True)
        (tests / "test_main.py").write_text("from main import *\n", encoding="utf-8")

    def test_expand_then_reuse_fresh(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._repo(root)
            cache = root / "cache.json"
            first = mapper.expand_finalist_slices(root, ["helper.py"], cache_override=cache)
            self.assertEqual(first["helper.py"]["status"], "expanded")
            self.assertIn("main.py", first["helper.py"]["callers"])
            self.assertTrue(cache.is_file())
            second = mapper.expand_finalist_slices(root, ["helper.py"], cache_override=cache)
            self.assertEqual(second["helper.py"]["status"], "fresh")

    def test_stale_file_reexpands(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._repo(root)
            cache = root / "cache.json"
            mapper.expand_finalist_slices(root, ["helper.py"], cache_override=cache)
            (root / "helper.py").write_text("def help():\n    return 2\n", encoding="utf-8")
            second = mapper.expand_finalist_slices(root, ["helper.py"], cache_override=cache)
            self.assertEqual(second["helper.py"]["status"], "expanded")

    def test_cap_defers_excess_finalists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._repo(root)
            cache = root / "cache.json"
            paths = ["helper.py", "main.py", "tests/test_main.py", "a.py", "b.py", "c.py"]
            summaries = mapper.expand_finalist_slices(root, paths, cache_override=cache)
            self.assertEqual(summaries["c.py"]["status"], "deferred")
            self.assertNotEqual(summaries["helper.py"]["status"], "deferred")

    def test_missing_file_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summaries = mapper.expand_finalist_slices(
                root, ["nope.py"], cache_override=root / "cache.json")
            self.assertEqual(summaries["nope.py"]["status"], "missing")

    def test_empty_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(
                mapper.expand_finalist_slices(root, [], cache_override=root / "cache.json"), {})


if __name__ == "__main__":
    unittest.main()
