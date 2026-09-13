"""Deterministic DM-H01 reference computation from pinned CSV artifacts.

The generator consumes only the split and recorded-identity columns needed by the
DM-H01 contract. It does not infer biological or patient identity, perform visual
matching, compute transitive closure, or decide whether a source artifact belongs
to a reported evaluation. Those provenance and identity qualifications remain
inputs to gold admission.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

GENERATOR_VERSION = "DM-H01-reference-generator-0.1.0"
_ALLOWED_PARTITIONS = frozenset(("train", "val", "test"))


@dataclass(frozen=True, slots=True)
class Membership:
    """One source-image membership in a named partition."""

    image_id: str
    partition: str
    index: int


@dataclass(frozen=True, slots=True)
class Witness:
    """One oriented direct witness derived from a shared recorded identity."""

    pair_key: str
    from_image_id: str
    from_partition: str
    to_image_id: str
    to_partition: str
    recorded_identity: str


@dataclass(frozen=True, slots=True)
class ReferenceResult:
    """Deterministic issue result and non-sensitive computation statistics."""

    generator_version: str
    split_sha256: str
    identity_sha256: str
    witness_registry_sha256: str
    witness_count: int
    development_count: int
    test_count: int
    matching_witness_count: int
    reference_state: str


def _path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _required_columns(path: Path, required: Sequence[str]) -> Iterable[tuple[int, tuple[str, ...]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"empty CSV artifact: {path}") from exc

        positions: list[int] = []
        for name in required:
            matches = [index for index, column in enumerate(header) if column == name]
            if len(matches) != 1:
                raise ValueError(f"CSV must contain exactly one {name!r} column: {path}")
            positions.append(matches[0])

        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(f"ragged CSV row {line_number}: {path}")
            yield line_number, tuple(row[index] for index in positions)


def _exact_nonempty(value: str, field: str, line_number: int, path: Path) -> str:
    if not value or value != value.strip():
        raise ValueError(f"invalid {field} at CSV row {line_number}: {path}")
    return value


def read_memberships(path_value: str | Path) -> tuple[Membership, ...]:
    """Read and validate split/index/image_id without retaining other columns."""
    path = _path(path_value)
    memberships: dict[str, Membership] = {}
    seen_indices: set[tuple[str, int]] = set()

    for line_number, (partition, index_text, image_id) in _required_columns(
        path, ("split", "index", "image_id")
    ):
        partition = _exact_nonempty(partition, "split", line_number, path)
        image_id = _exact_nonempty(image_id, "image_id", line_number, path)
        if partition not in _ALLOWED_PARTITIONS:
            raise ValueError(f"unsupported partition {partition!r}: {path}")
        try:
            index = int(index_text)
        except ValueError as exc:
            raise ValueError(f"invalid index at CSV row {line_number}: {path}") from exc
        if index < 0:
            raise ValueError(f"negative index at CSV row {line_number}: {path}")
        if image_id in memberships:
            raise ValueError(f"duplicate image_id {image_id!r}: {path}")
        if (partition, index) in seen_indices:
            raise ValueError(f"duplicate partition/index {(partition, index)!r}: {path}")

        memberships[image_id] = Membership(image_id, partition, index)
        seen_indices.add((partition, index))

    if not memberships:
        raise ValueError(f"CSV has no memberships: {path}")
    return tuple(
        sorted(memberships.values(), key=lambda item: (item.partition, item.index, item.image_id))
    )


def read_recorded_identities(
    path_value: str | Path, expected_image_ids: set[str]
) -> dict[str, str]:
    """Read only image_id and recorded lesion_id from an identity artifact."""
    path = _path(path_value)
    identities: dict[str, str] = {}

    for line_number, (recorded_identity, image_id) in _required_columns(
        path, ("lesion_id", "image_id")
    ):
        recorded_identity = _exact_nonempty(recorded_identity, "lesion_id", line_number, path)
        image_id = _exact_nonempty(image_id, "image_id", line_number, path)
        if image_id in identities:
            raise ValueError(f"duplicate image_id {image_id!r}: {path}")
        identities[image_id] = recorded_identity

    actual_image_ids = set(identities)
    if actual_image_ids != expected_image_ids:
        missing = sorted(expected_image_ids - actual_image_ids)
        extra = sorted(actual_image_ids - expected_image_ids)
        raise ValueError(
            f"identity/membership image set mismatch; missing={missing[:3]}, extra={extra[:3]}"
        )
    return identities


def _witness_sort_key(witness: Witness) -> tuple[str, str, str]:
    return (witness.pair_key, witness.from_image_id, witness.to_image_id)


def _build_witnesses(
    memberships: tuple[Membership, ...], identities: dict[str, str]
) -> tuple[Witness, ...]:
    by_image = {membership.image_id: membership for membership in memberships}
    by_identity: dict[str, list[str]] = {}
    for membership in memberships:
        by_identity.setdefault(identities[membership.image_id], []).append(membership.image_id)

    witnesses: list[Witness] = []
    for recorded_identity in sorted(by_identity):
        image_ids = sorted(by_identity[recorded_identity])
        for left_index, left_image_id in enumerate(image_ids):
            for right_image_id in image_ids[left_index + 1 :]:
                left = by_image[left_image_id]
                right = by_image[right_image_id]
                if left.partition == right.partition:
                    continue
                pair_key = f"{recorded_identity}|{left_image_id}|{right_image_id}"
                witnesses.extend(
                    (
                        Witness(
                            pair_key,
                            left.image_id,
                            left.partition,
                            right.image_id,
                            right.partition,
                            recorded_identity,
                        ),
                        Witness(
                            pair_key,
                            right.image_id,
                            right.partition,
                            left.image_id,
                            left.partition,
                            recorded_identity,
                        ),
                    )
                )

    return tuple(sorted(witnesses, key=_witness_sort_key))


def build_witnesses(split_path: str | Path, identity_path: str | Path) -> tuple[Witness, ...]:
    """Build direct cross-partition pairs and both symmetric orientations."""
    memberships = read_memberships(split_path)
    identities = read_recorded_identities(identity_path, {item.image_id for item in memberships})
    return _build_witnesses(memberships, identities)


def _canonical_witness_bytes(witnesses: Sequence[Witness]) -> bytes:
    records = [
        {
            "pair_key": witness.pair_key,
            "from_image_id": witness.from_image_id,
            "from_partition": witness.from_partition,
            "to_image_id": witness.to_image_id,
            "to_partition": witness.to_partition,
            "recorded_identity": witness.recorded_identity,
        }
        for witness in sorted(witnesses, key=_witness_sort_key)
    ]
    return (
        json.dumps(records, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def witness_registry_sha256(witnesses: Sequence[Witness]) -> str:
    """Hash the canonical ordered oriented witness registry."""
    return hashlib.sha256(_canonical_witness_bytes(witnesses)).hexdigest()


def _partitions(value: Sequence[str], field: str) -> frozenset[str]:
    if isinstance(value, str):
        raise TypeError(f"{field} must be a sequence of partition names")
    result = frozenset(value)
    if not result or not result <= _ALLOWED_PARTITIONS:
        raise ValueError(f"{field} must be a nonempty subset of {_ALLOWED_PARTITIONS}")
    return result


def compute_reference(
    split_path: str | Path,
    identity_path: str | Path,
    *,
    development_partitions: Sequence[str] = ("train", "val"),
    test_partitions: Sequence[str] = ("test",),
) -> ReferenceResult:
    """Compute Q_H01 for complete, exact source memberships.

    The recorded identity is used only as the explicitly named identity basis.
    Every emitted pair is made directly from two source rows sharing that value;
    no visual, alias, ancestor, or transitive relationship is added.
    """
    split = _path(split_path)
    identity = _path(identity_path)
    memberships = read_memberships(split)
    identities = read_recorded_identities(identity, {item.image_id for item in memberships})
    witnesses = _build_witnesses(memberships, identities)

    development = _partitions(development_partitions, "development_partitions")
    test = _partitions(test_partitions, "test_partitions")
    if development & test:
        raise ValueError("development and test partitions must be disjoint")

    development_ids = {item.image_id for item in memberships if item.partition in development}
    test_ids = {item.image_id for item in memberships if item.partition in test}
    matching_count = sum(
        witness.from_image_id in development_ids and witness.to_image_id in test_ids
        for witness in witnesses
    )

    return ReferenceResult(
        generator_version=GENERATOR_VERSION,
        split_sha256=_raw_sha256(split),
        identity_sha256=_raw_sha256(identity),
        witness_registry_sha256=witness_registry_sha256(witnesses),
        witness_count=len(witnesses),
        development_count=len(development_ids),
        test_count=len(test_ids),
        matching_witness_count=matching_count,
        reference_state="APPLIES" if matching_count else "NOT_APPLICABLE",
    )
