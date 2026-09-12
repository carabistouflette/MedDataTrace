"""Contract conformance on synthetic records; not real-world validation."""

import unittest
from dataclasses import replace
from itertools import product

from semantics import ClaimTarget, ScopeAssessment, State, evidence_state, summarize


def make(state: State, scope: str = "scope-1", corrected: bool = False) -> ScopeAssessment:
    return ScopeAssessment(
        evaluation_id="synthetic-eval",
        issue_id="synthetic-issue",
        scope_id=scope,
        snapshot_id="synthetic-snapshot",
        claim_target=ClaimTarget.REPORTED_SETUP,
        presence_certificate_ids=("p:" + scope,)
        if state in (State.APPLIES, State.CONFLICTING)
        else (),
        absence_certificate_ids=("n:" + scope,)
        if state in (State.NOT_APPLICABLE, State.CONFLICTING)
        else (),
        correction_complete=corrected,
        correction_certificate_ids=("c:" + scope,) if corrected else (),
    )


def summary(*records, complete=True):
    return summarize(records, inventory_complete=complete, boundary_label="documented inputs only")


class ContractTests(unittest.TestCase):
    def test_truth_table(self):
        expected = (
            (False, False, State.UNKNOWN),
            (True, False, State.APPLIES),
            (False, True, State.NOT_APPLICABLE),
            (True, True, State.CONFLICTING),
        )
        for p, n, state in expected:
            with self.subTest(p=p, n=n):
                self.assertIs(evidence_state(p, n), state)

    def test_all_two_scope_compositions(self):
        # Explicit expected tables independent of the implementation branches.
        # Order: UNKNOWN, APPLIES, NOT_APPLICABLE, CONFLICTING.
        U, A, N, C = State.UNKNOWN, State.APPLIES, State.NOT_APPLICABLE, State.CONFLICTING
        order = (U, A, N, C)
        complete_table = ((U, A, U, C), (A, A, A, A), (U, A, N, C), (C, A, C, C))
        incomplete_table = ((U, A, U, C), (A, A, A, A), (U, A, U, C), (C, A, C, C))
        for complete, i, j in product((False, True), range(4), range(4)):
            with self.subTest(complete=complete, i=i, j=j):
                table = complete_table if complete else incomplete_table
                result = summary(make(order[i], "a"), make(order[j], "b"), complete=complete)
                self.assertIs(result.state, table[i][j])

    def test_unknown_is_not_negative(self):
        self.assertIs(make(State.UNKNOWN).state, State.UNKNOWN)

    def test_mitigation_is_reason_for_negative(self):
        r = make(State.NOT_APPLICABLE, corrected=True)
        self.assertIs(r.state, State.NOT_APPLICABLE)
        self.assertEqual(r.display, "MITIGATED")

    def test_incomplete_correction_evidence_is_not_complete(self):
        with self.assertRaises(ValueError):
            replace(
                make(State.UNKNOWN), correction_complete=True, correction_certificate_ids=("c",)
            )

    def test_missing_correction_certificate_rejected(self):
        with self.assertRaises(ValueError):
            replace(make(State.NOT_APPLICABLE), correction_complete=True)

    def test_conflicting_correction_not_displayed_mitigated(self):
        self.assertEqual(make(State.CONFLICTING, corrected=True).display, "CONFLICTING")

    def test_corrected_plus_unknown_is_unknown(self):
        out = summary(make(State.NOT_APPLICABLE, "a", True), make(State.UNKNOWN, "b"))
        self.assertIs(out.state, State.UNKNOWN)
        self.assertEqual(out.mitigated_scope_ids, ("a",))

    def test_clean_positive_is_localized(self):
        out = summary(make(State.APPLIES, "a"), make(State.CONFLICTING, "b"), complete=False)
        self.assertIs(out.state, State.APPLIES)
        self.assertEqual(out.applicable_scope_ids, ("a",))
        self.assertEqual(out.conflicting_scope_ids, ("b",))
        self.assertFalse(out.inventory_complete_for_boundary)

    def test_contested_witness_is_not_clean_positive(self):
        out = summary(make(State.CONFLICTING, "a"), make(State.UNKNOWN, "b"))
        self.assertIs(out.state, State.CONFLICTING)
        self.assertFalse(out.applicable_scope_ids)

    def test_all_negative_in_incomplete_inventory_unknown(self):
        self.assertIs(summary(make(State.NOT_APPLICABLE), complete=False).state, State.UNKNOWN)

    def test_all_negative_in_complete_boundary_negative(self):
        out = summary(make(State.NOT_APPLICABLE, "a"), make(State.NOT_APPLICABLE, "b", True))
        self.assertIs(out.state, State.NOT_APPLICABLE)
        self.assertEqual(out.mitigated_scope_ids, ("b",))
        self.assertEqual(len(out.all_scopes), 2)

    def test_empty_query_never_negative(self):
        for complete in (True, False):
            self.assertIs(summary(complete=complete).state, State.UNKNOWN)

    def test_mixed_snapshots_rejected(self):
        with self.assertRaises(ValueError):
            summary(
                make(State.UNKNOWN, "a"), replace(make(State.UNKNOWN, "b"), snapshot_id="other")
            )

    def test_mixed_issue_rejected(self):
        with self.assertRaises(ValueError):
            summary(make(State.UNKNOWN, "a"), replace(make(State.UNKNOWN, "b"), issue_id="other"))

    def test_mixed_evaluation_rejected(self):
        with self.assertRaises(ValueError):
            summary(
                make(State.UNKNOWN, "a"), replace(make(State.UNKNOWN, "b"), evaluation_id="other")
            )

    def test_mixed_claim_target_rejected(self):
        with self.assertRaises(ValueError):
            summary(
                make(State.UNKNOWN, "a"),
                replace(make(State.UNKNOWN, "b"), claim_target=ClaimTarget.DOCUMENTED_PROCEDURE),
            )

    def test_duplicate_scopes_rejected(self):
        with self.assertRaises(ValueError):
            summary(make(State.APPLIES), make(State.NOT_APPLICABLE))

    def test_empty_boundary_rejected(self):
        with self.assertRaises(ValueError):
            summarize([], inventory_complete=True, boundary_label="")

    def test_nonboolean_support_rejected(self):
        with self.assertRaises(TypeError):
            evidence_state(0.95, False)

    def test_blank_identifier_rejected(self):
        with self.assertRaises(ValueError):
            replace(make(State.UNKNOWN), scope_id=" ")

    def test_duplicate_certificates_rejected(self):
        with self.assertRaises(ValueError):
            replace(make(State.UNKNOWN), presence_certificate_ids=("p", "p"))

    def test_no_empty_certificate_ids(self):
        with self.assertRaises(ValueError):
            replace(make(State.UNKNOWN), absence_certificate_ids=("",))

    def test_no_untyped_target(self):
        with self.assertRaises(TypeError):
            replace(make(State.UNKNOWN), claim_target="REPORTED_SETUP")


if __name__ == "__main__":
    unittest.main()
