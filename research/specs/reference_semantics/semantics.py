"""Synthetic specification reference, not a scientific evidence validator.

Certificate IDs are assumed to refer to independently validated, same-scope
proofs. The module does NOT validate their contents or infer real applicability.
It implements only the v0.2 evidence-state and bounded composition contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class State(str, Enum):
    UNKNOWN = "UNKNOWN"
    APPLIES = "APPLIES"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    CONFLICTING = "CONFLICTING"


class ClaimTarget(str, Enum):
    REPORTED_SETUP = "REPORTED_SETUP"
    DOCUMENTED_PROCEDURE = "DOCUMENTED_PROCEDURE"
    EXECUTION_LINKED_ARTIFACT = "EXECUTION_LINKED_ARTIFACT"


def evidence_state(presence_supported: bool, absence_supported: bool) -> State:
    """Missing support means insufficient evidence, NOT scientific falsity."""
    if type(presence_supported) is not bool or type(absence_supported) is not bool:
        raise TypeError("Support flags must be bool, not scores or strings.")
    return {
        (False, False): State.UNKNOWN,
        (True, False): State.APPLIES,
        (False, True): State.NOT_APPLICABLE,
        (True, True): State.CONFLICTING,
    }[(presence_supported, absence_supported)]


@dataclass(frozen=True)
class ScopeAssessment:
    evaluation_id: str
    issue_id: str
    scope_id: str
    snapshot_id: str
    claim_target: ClaimTarget
    presence_certificate_ids: tuple[str, ...] = ()
    absence_certificate_ids: tuple[str, ...] = ()
    correction_complete: bool = False
    correction_certificate_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value in (self.evaluation_id, self.issue_id, self.scope_id, self.snapshot_id):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Nonempty identifiers are required.")
        if not isinstance(self.claim_target, ClaimTarget):
            raise TypeError("claim_target must be an explicit ClaimTarget.")
        if type(self.correction_complete) is not bool:
            raise TypeError("correction_complete must be bool.")
        for ids in (
            self.presence_certificate_ids,
            self.absence_certificate_ids,
            self.correction_certificate_ids,
        ):
            if not isinstance(ids, tuple):
                raise TypeError("Certificate IDs must be an immutable tuple.")
            if any(not isinstance(x, str) or not x.strip() for x in ids):
                raise ValueError("Certificate identifiers must be nonempty strings.")
            if len(set(ids)) != len(ids):
                raise ValueError("Duplicate certificate IDs are not allowed.")
        if self.correction_complete and (
            not self.absence_certificate_ids or not self.correction_certificate_ids
        ):
            raise ValueError("Complete correction requires negative and correction evidence.")

    @property
    def state(self) -> State:
        return evidence_state(
            bool(self.presence_certificate_ids), bool(self.absence_certificate_ids)
        )

    @property
    def display(self) -> str:
        if self.state is State.NOT_APPLICABLE and self.correction_complete:
            return "MITIGATED"
        return self.state.value


@dataclass(frozen=True)
class Summary:
    state: State
    boundary_label: str
    inventory_complete_for_boundary: bool
    applicable_scope_ids: tuple[str, ...]
    unknown_scope_ids: tuple[str, ...]
    conflicting_scope_ids: tuple[str, ...]
    negative_scope_ids: tuple[str, ...]
    mitigated_scope_ids: tuple[str, ...]
    all_scopes: tuple[ScopeAssessment, ...]


def summarize(
    scopes: Sequence[ScopeAssessment], *, inventory_complete: bool, boundary_label: str
) -> Summary:
    """Conservative summary; never certifies undisclosed/real-world inventory.

    A clean positive witness can justify a localized warning. A conflicted
    witness alone cannot. Global negative summaries require nonempty, fully
    assessed scope inventory. An empty query is always UNKNOWN here; independent
    proof of an empty inventory is intentionally not implemented.
    """
    if type(inventory_complete) is not bool:
        raise TypeError("inventory_complete must be bool.")
    if not isinstance(boundary_label, str) or not boundary_label.strip():
        raise ValueError("An explicit completeness boundary is required.")
    records = tuple(scopes)
    if any(not isinstance(x, ScopeAssessment) for x in records):
        raise TypeError("All inputs must be ScopeAssessment records.")
    contexts = {(x.evaluation_id, x.issue_id, x.snapshot_id, x.claim_target) for x in records}
    if len(contexts) > 1:
        raise ValueError("Cannot combine different evaluations/issues/snapshots/claim targets.")
    if len({x.scope_id for x in records}) != len(records):
        raise ValueError("Assess each distinct scope once; merge its evidence explicitly first.")
    ids = {s: tuple(x.scope_id for x in records if x.state is s) for s in State}
    if ids[State.APPLIES]:
        result = State.APPLIES
    elif ids[State.CONFLICTING]:
        result = State.CONFLICTING
    elif not records or not inventory_complete or ids[State.UNKNOWN]:
        result = State.UNKNOWN
    else:
        result = State.NOT_APPLICABLE
    return Summary(
        state=result,
        boundary_label=boundary_label,
        inventory_complete_for_boundary=inventory_complete,
        applicable_scope_ids=ids[State.APPLIES],
        unknown_scope_ids=ids[State.UNKNOWN],
        conflicting_scope_ids=ids[State.CONFLICTING],
        negative_scope_ids=ids[State.NOT_APPLICABLE],
        mitigated_scope_ids=tuple(x.scope_id for x in records if x.display == "MITIGATED"),
        all_scopes=records,
    )
