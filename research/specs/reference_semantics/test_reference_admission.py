"""Synthetic admission tests; not validation of real DM-H01 artifacts."""

import unittest

from reference_admission import AdmissionInput, GoldBasis, Referenceability, admit
from semantics import State


def base(**kw):
    data = dict(
        evaluation_identified=True,
        artifact_linkage_supported=True,
        artifacts_pinned=True,
        identity_basis_supported=True,
        computation_reproducible=True,
        gold_basis=GoldBasis.POSITIVE,
    )
    data.update(kw)
    return AdmissionInput(**data)


class AdmissionTests(unittest.TestCase):
    def test_positive_gold_requires_full_chain(self):
        out = admit(base())
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.APPLIES)

    def test_ambiguous_evaluation_to_artifact_link_is_unscorable(self):
        out = admit(base(artifact_linkage_supported=False))
        self.assertIs(out.referenceability, Referenceability.REFERENCE_UNSCORABLE)
        self.assertIsNone(out.gold_state)

    def test_reproducible_unknown_can_be_gold(self):
        out = admit(base(gold_basis=GoldBasis.EXPLICIT_UNKNOWN))
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.UNKNOWN)

    def test_missing_reference_basis_is_not_gold_unknown(self):
        out = admit(base(gold_basis=None))
        self.assertIs(out.referenceability, Referenceability.REFERENCE_UNSCORABLE)
        self.assertIsNone(out.gold_state)

    def test_reproducible_conflict_can_be_gold(self):
        out = admit(base(gold_basis=GoldBasis.REPRODUCIBLE_CONFLICT))
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.CONFLICTING)

    def test_domain_judgment_required_is_non_gold(self):
        out = admit(base(domain_judgment_required=True))
        self.assertIs(out.referenceability, Referenceability.EXPERT_REQUIRED)
        self.assertIsNone(out.gold_state)

    def test_inaccessible_is_non_gold(self):
        out = admit(base(inaccessible=True))
        self.assertIs(out.referenceability, Referenceability.INACCESSIBLE)
        self.assertIsNone(out.gold_state)


if __name__ == "__main__":
    unittest.main()
