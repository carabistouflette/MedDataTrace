"""Tests for deterministic DM-H01 computation, not source validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dmh01 import build_witnesses, compute_reference, witness_registry_sha256

_SPLIT = """split,index,image_id
train,0,A
train,1,B
val,0,C
test,0,D
test,1,E
"""
_IDENTITY = """lesion_id,image_id,dx
L1,A,ignored
L1,B,ignored
L1,D,ignored
L2,C,ignored
L2,E,ignored
"""


class GeneratorTests(unittest.TestCase):
    def _artifacts(self, split: str = _SPLIT, identity: str = _IDENTITY):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        split_path = root / "split.csv"
        identity_path = root / "identity.csv"
        split_path.write_text(split, encoding="utf-8", newline="")
        identity_path.write_text(identity, encoding="utf-8", newline="")
        self.addCleanup(directory.cleanup)
        return split_path, identity_path

    def test_computes_symmetric_direct_witnesses(self):
        split_path, identity_path = self._artifacts()

        witnesses = build_witnesses(split_path, identity_path)
        result = compute_reference(split_path, identity_path)

        self.assertEqual(len(witnesses), 6)
        self.assertEqual(result.witness_count, 6)
        self.assertEqual(result.development_count, 3)
        self.assertEqual(result.test_count, 2)
        self.assertEqual(result.matching_witness_count, 3)
        self.assertEqual(result.reference_state, "APPLIES")
        self.assertEqual(
            {(w.from_image_id, w.to_image_id) for w in witnesses},
            {
                ("A", "D"),
                ("D", "A"),
                ("B", "D"),
                ("D", "B"),
                ("C", "E"),
                ("E", "C"),
            },
        )

    def test_order_of_source_rows_does_not_change_registry(self):
        split_path, identity_path = self._artifacts()
        split_lines = _SPLIT.rstrip().splitlines()
        identity_lines = _IDENTITY.rstrip().splitlines()
        reversed_split = "\n".join([split_lines[0], *split_lines[:0:-1]]) + "\n"
        reversed_identity = "\n".join([identity_lines[0], *identity_lines[:0:-1]]) + "\n"
        reversed_split_path, reversed_identity_path = self._artifacts(
            reversed_split, reversed_identity
        )

        witnesses = build_witnesses(split_path, identity_path)
        reversed_witnesses = build_witnesses(reversed_split_path, reversed_identity_path)
        self.assertEqual(
            witness_registry_sha256(witnesses), witness_registry_sha256(reversed_witnesses)
        )
        self.assertEqual(
            witness_registry_sha256(witnesses), witness_registry_sha256(witnesses[::-1])
        )

    def test_missing_identity_and_duplicate_membership_are_rejected(self):
        split_path, identity_path = self._artifacts(
            identity=_IDENTITY.replace("L2,E,ignored\n", "")
        )
        with self.assertRaises(ValueError):
            build_witnesses(split_path, identity_path)

        duplicate_split = _SPLIT.replace("test,1,E\n", "test,1,E\ntest,1,F\n")
        duplicate_split_path, duplicate_identity_path = self._artifacts(duplicate_split)
        with self.assertRaises(ValueError):
            build_witnesses(duplicate_split_path, duplicate_identity_path)

        extra_identity = _IDENTITY + "L3,F,ignored\n"
        extra_identity_path = self._artifacts(identity=extra_identity)[1]
        with self.assertRaises(ValueError):
            build_witnesses(split_path, extra_identity_path)

        ragged_split = _SPLIT.replace("train,1,B\n", "train,1,B,extra\n")
        ragged_split_path, ragged_identity_path = self._artifacts(ragged_split)
        with self.assertRaises(ValueError):
            build_witnesses(ragged_split_path, ragged_identity_path)

    def test_development_and_test_partitions_must_be_disjoint(self):
        split_path, identity_path = self._artifacts()
        with self.assertRaises(ValueError):
            compute_reference(
                split_path,
                identity_path,
                development_partitions=("train", "test"),
                test_partitions=("test",),
            )


if __name__ == "__main__":
    unittest.main()
