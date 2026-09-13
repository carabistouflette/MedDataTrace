"""Synthetic gold-admission guardrails, not a scientific evidence validator.

This module encodes only benchmark bookkeeping distinctions from the specification:
- a gold reference requires an inspectable evaluation-to-artifact derivation;
- a reproducibly justified UNKNOWN can be gold;
- inability to construct a reliable reference is REFERENCE_UNSCORABLE.

It does not determine whether any real source actually supports a linkage or issue claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from semantics import State


class Referenceability(StrEnum):
    ARTIFACT_GOLD = "ARTIFACT_GOLD"
    SILVER_ONLY = "SILVER_ONLY"
    REFERENCE_UNSCORABLE = "REFERENCE_UNSCORABLE"
    EXPERT_REQUIRED = "EXPERT_REQUIRED"
    INACCESSIBLE = "INACCESSIBLE"


class GoldBasis(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    EXPLICIT_UNKNOWN = "EXPLICIT_UNKNOWN"
    REPRODUCIBLE_CONFLICT = "REPRODUCIBLE_CONFLICT"


@dataclass(frozen=True)
class AdmissionInput:
    evaluation_identified: bool
    artifact_linkage_supported: bool
    artifacts_pinned: bool
    identity_basis_supported: bool
    computation_reproducible: bool
    domain_judgment_required: bool = False
    inaccessible: bool = False
    gold_basis: GoldBasis | None = None


@dataclass(frozen=True)
class AdmissionResult:
    referenceability: Referenceability
    gold_state: State | None


def admit(inp: AdmissionInput) -> AdmissionResult:
    """Apply only the explicit benchmark-admission bookkeeping contract."""
    if not isinstance(inp, AdmissionInput):
        raise TypeError("inp must be AdmissionInput")
    for name in (
        "evaluation_identified",
        "artifact_linkage_supported",
        "artifacts_pinned",
        "identity_basis_supported",
        "computation_reproducible",
        "domain_judgment_required",
        "inaccessible",
    ):
        if type(getattr(inp, name)) is not bool:
            raise TypeError(f"{name} must be bool")

    if inp.inaccessible:
        return AdmissionResult(Referenceability.INACCESSIBLE, None)
    if inp.domain_judgment_required:
        return AdmissionResult(Referenceability.EXPERT_REQUIRED, None)

    complete_chain = all(
        (
            inp.evaluation_identified,
            inp.artifact_linkage_supported,
            inp.artifacts_pinned,
            inp.identity_basis_supported,
            inp.computation_reproducible,
        )
    )
    if not complete_chain or inp.gold_basis is None:
        return AdmissionResult(Referenceability.REFERENCE_UNSCORABLE, None)

    state = {
        GoldBasis.POSITIVE: State.APPLIES,
        GoldBasis.NEGATIVE: State.NOT_APPLICABLE,
        GoldBasis.EXPLICIT_UNKNOWN: State.UNKNOWN,
        GoldBasis.REPRODUCIBLE_CONFLICT: State.CONFLICTING,
    }[inp.gold_basis]
    return AdmissionResult(Referenceability.ARTIFACT_GOLD, state)
