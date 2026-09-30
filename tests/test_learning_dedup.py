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


refresh = load("tailtrail_learning_dedup_refresh_test", "scripts/learning-refresh.py")
receipts = load("tailtrail_learning_dedup_receipts_test", "scripts/learning-use-receipt.py")
v3 = load("tailtrail_learning_dedup_v3_test", "scripts/learning-v3.py")


def _capture(root: Path, learning_id: str, advice: str, tags=None) -> dict:
    import hashlib
    digest = hashlib.sha256(learning_id.encode()).hexdigest()
    record = v3.build_record(
        root, learning_id=learning_id, learning_class="positive-pattern",
        summary=f"Summary {learning_id}", advice=advice,
        source_kind="test", source_ref="test", source_fingerprint=f"sha256:{digest}",
        captured_by="test", tags=list(tags or ["t"]),
    )
    return v3.append_record(root, record)




class ExactDuplicateCollapseTests(unittest.TestCase):
    def test_execute_merge_supersedes_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = _capture(root, "lrn-aaa", "Do not declare victory early.", ["a"])
            _capture(root, "lrn-bbb", "Do not declare victory early.", ["a"])
            _capture(root, "lrn-ccc", "Something entirely different here.", ["b"])
            groups = refresh.exact_duplicate_v3_groups(
                list(v3.latest_records(v3.read_records(root)).values()))
            self.assertEqual(len(groups), 1)
            key = next(iter(groups))
            self.assertEqual(sorted(groups[key]), ["lrn-aaa", "lrn-bbb"])
            result = refresh.execute_merge_group(
                root, "lrn-aaa", ["lrn-bbb"], "approved exact-duplicate collapse", True)
            self.assertEqual(result["superseded"], ["lrn-bbb"])
            latest = v3.latest_records(v3.read_records(root))
            self.assertEqual(latest["lrn-bbb"]["freshness"]["status"], "superseded")
            self.assertEqual(
                latest["lrn-bbb"]["lifecycle"]["replacement_learning_id"], "lrn-aaa")
            self.assertEqual(latest["lrn-aaa"]["freshness"]["status"], "current")
            self.assertEqual(latest["lrn-ccc"]["freshness"]["status"], "current")

    def test_execute_merge_requires_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "--approved"):
                refresh.execute_merge_group(
                    Path(temp), "lrn-aaa", ["lrn-bbb"], "reason", False)

    def test_terminal_records_excluded_from_groups(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _capture(root, "lrn-aaa", "Same advice twice.", ["a"])
            _capture(root, "lrn-bbb", "Same advice twice.", ["a"])
            refresh.execute_merge_group(
                root, "lrn-aaa", ["lrn-bbb"], "collapse", True)
            groups = refresh.exact_duplicate_v3_groups(
                list(v3.latest_records(v3.read_records(root)).values()))
            # latest_records returns the superseded version of lrn-bbb, whose
            # status is terminal, so no group reforms around it.
            self.assertNotIn("lrn-bbb", [item for ids in groups.values() for item in ids])


class NearDuplicateProposalTests(unittest.TestCase):
    def _record(self, learning_id, advice, tags):
        return {
            "learning_id": learning_id,
            "freshness": {"status": "current"},
            "content": {"advice": advice},
            "applicability": {"tags": list(tags)},
        }

    def test_related_records_proposed(self):
        records = [
            self._record("lrn-1", "Do not declare completion while drift remains open", ["closure"]),
            self._record("lrn-2", "Do not declare completion while drift remains unresolved", ["closure"]),
            self._record("lrn-3", "Prefer greenfield modules for new endpoints", ["design"]),
        ]
        proposals = refresh.near_duplicate_proposals(records)
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0]["status"], "proposed")
        self.assertIn("closure", proposals[0]["shared_tags"])

    def test_exact_pairs_not_reproposed(self):
        records = [
            self._record("lrn-1", "Identical advice text here", ["a"]),
            self._record("lrn-2", "Identical advice text here", ["a"]),
        ]
        self.assertEqual(refresh.near_duplicate_proposals(records), [])

    def test_unrelated_records_silent(self):
        records = [
            self._record("lrn-1", "Alpha beta gamma delta epsilon", ["a"]),
            self._record("lrn-2", "Zebra yak xray wolf violet", ["b"]),
        ]
        self.assertEqual(refresh.near_duplicate_proposals(records), [])


class ProofOfLifeTouchTests(unittest.TestCase):
    def test_touch_advances_applied_record(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            before = _capture(root, "lrn-use", "Useful advice here.", ["a"])
            result = receipts.touch_on_use(root, "lrn-use", "run-1", "rid-1", "applied")
            self.assertEqual(result["status"], "touched")
            latest = v3.latest_records(v3.read_records(root))["lrn-use"]
            self.assertNotEqual(latest["record_id"], before["record_id"])
            self.assertEqual(latest["content"]["advice"], "Useful advice here.")

    def test_non_use_decisions_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _capture(root, "lrn-use", "Useful advice here.", ["a"])
            result = receipts.touch_on_use(root, "lrn-use", "run-1", "rid-1", "ignored")
            self.assertEqual(result["status"], "not-applicable")
            latest = v3.latest_records(v3.read_records(root))["lrn-use"]
            self.assertEqual(latest["utility"]["use_count"], 0)

    def test_missing_record_fails_gracefully(self):
        with tempfile.TemporaryDirectory() as temp:
            result = receipts.touch_on_use(Path(temp), "lrn-nope", "run-1", "rid-1", "applied")
            self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main()
