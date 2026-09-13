"""Synthetic admission tests; not validation of real DM-H01 artifacts."""

import unittest

from reference_admission import AdmissionInput, GoldBasis, Referenceability, admit
from semantics import State


def base(
    *,
    evaluation_identified: bool = True,
    artifact_linkage_supported: bool = True,
    artifacts_pinned: bool = True,
    identity_basis_supported: bool = True,
    computation_reproducible: bool = True,
    domain_judgment_required: bool = False,
    inaccessible: bool = False,
    gold_basis: GoldBasis | None = GoldBasis.POSITIVE,
) -> AdmissionInput:
    return AdmissionInput(
        evaluation_identified=evaluation_identified,
        artifact_linkage_supported=artifact_linkage_supported,
        artifacts_pinned=artifacts_pinned,
        identity_basis_supported=identity_basis_supported,
        computation_reproducible=computation_reproducible,
        domain_judgment_required=domain_judgment_required,
        inaccessible=inaccessible,
        gold_basis=gold_basis,
    )


class AdmissionTests(unittest.TestCase):
    def test_positive_gold_requires_full_chain(self) -> None:
        out = admit(base())
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.APPLIES)

    def test_ambiguous_evaluation_to_artifact_link_is_unscorable(self) -> None:
        out = admit(base(artifact_linkage_supported=False))
        self.assertIs(out.referenceability, Referenceability.REFERENCE_UNSCORABLE)
        self.assertIsNone(out.gold_state)

    def test_reproducible_unknown_can_be_gold(self) -> None:
        out = admit(base(gold_basis=GoldBasis.EXPLICIT_UNKNOWN))
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.UNKNOWN)

    def test_missing_reference_basis_is_not_gold_unknown(self) -> None:
        out = admit(base(gold_basis=None))
        self.assertIs(out.referenceability, Referenceability.REFERENCE_UNSCORABLE)
        self.assertIsNone(out.gold_state)

    def test_reproducible_conflict_can_be_gold(self) -> None:
        out = admit(base(gold_basis=GoldBasis.REPRODUCIBLE_CONFLICT))
        self.assertIs(out.referenceability, Referenceability.ARTIFACT_GOLD)
        self.assertIs(out.gold_state, State.CONFLICTING)

    def test_domain_judgment_required_is_non_gold(self) -> None:
        out = admit(base(domain_judgment_required=True))
        self.assertIs(out.referenceability, Referenceability.EXPERT_REQUIRED)
        self.assertIsNone(out.gold_state)

    def test_inaccessible_is_non_gold(self) -> None:
        out = admit(base(inaccessible=True))
        self.assertIs(out.referenceability, Referenceability.INACCESSIBLE)
        self.assertIsNone(out.gold_state)


if __name__ == "__main__":
    unittest.main()
