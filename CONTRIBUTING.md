# Contributing to MedDataTrace

MedDataTrace is a public research foundation. Keep changes reproducible, synthetic where
appropriate, and within the boundary described by the authoritative specification. The code
must make evidence boundaries, uncertainty, and reproducibility visible. A green check proves
conformance to repository contracts; it does not validate medical evidence or scientific
conclusions.

## Workflow

1. Create a feature branch from `main`.
2. Keep a pull request focused and describe the change and its evidence.
3. Run the exact checks below before requesting review.
4. Review staged paths for secrets, restricted source material, patient data, populated
   held-out answers, reviewer identities, and unsupported claims.

```text
uv sync --locked
uv run --locked python scripts/tasks.py format
uv run --locked python scripts/tasks.py check
```

`scripts/tasks.py` is the cross-platform task entry point and works in PowerShell, Command
Prompt, and Unix shells. On Unix, `make setup`, `make check`, `make format`, `make typecheck`,
and `make spec` remain optional convenience aliases. Use the task runner's `format` task for
Ruff formatting and import-order fixes. Use the `typecheck` task when iterating on annotations.
When native TeX prerequisites are installed, run
`uv run --locked python scripts/tasks.py spec` and inspect the generated PDF. Without them,
the GitHub Actions `Specification` job is the supported build route.

## Python quality standard

Ruff is the single formatting and linting authority. Do not hand-format around it or introduce
a second formatter. Follow these rules when designing code:

- Use Python `3.14`, four spaces, a 100-character line limit, and import grouping handled by
  Ruff.
- Use explicit type annotations for every function and method, including test helpers. Keep
  mypy strict; avoid `Any`. If a test intentionally passes an invalid runtime type, isolate
  that cast at the call site and explain the runtime contract in the test.
- Prefer standard-library types from `collections.abc` and modern syntax such as `X | None`.
  Use `enum.StrEnum` for string-valued enums.
- Prefer immutable, explicit records (`@dataclass(frozen=True, slots=True)` where appropriate)
  over unstructured dictionaries in Python APIs. Validate inputs at the boundary and fail
  closed.
- Raise a specific exception with a useful message. Preserve the original exception as the
  cause when translating errors. Do not catch broad exceptions to hide malformed evidence or
  I/O failure.
- Keep deterministic code deterministic: sort unordered inputs before emitting output, pin or
  hash external artifacts, and never use ambient time, random state, or network access in core
  logic.
- Keep provenance separate from interpretation. A recorded identifier, citation, or model score
  must not silently become a scientific identity or conclusion.
- Avoid hidden filesystem, network, model, or global-state dependencies in functions that can
  be pure. Pass paths, policies, and boundaries explicitly.

## Tests

Tests defend observable behavior, boundaries, invariants, and failure modes. They must be:

- deterministic and isolated;
- independent of downloaded data, network access, credentials, and machine-specific paths;
- focused on a plausible regression rather than implementation details; and
- updated when a public contract intentionally changes.

Use the existing `unittest` convention unless a different framework is justified by a real need.
Do not add tests that merely assert a value is nonempty, an exception is not raised, or a mock
forwarded an argument. For evidence and reference code, test conservative behavior: incomplete
inputs remain unresolved, unsupported identity inferences are rejected, and canonical output
does not depend on input row order.

## Research boundaries

- Reference semantics and tests are synthetic bookkeeping conformance, not medical validation
  or a usefulness claim.
- Preserve the separation between source artifacts, reference semantics, pilot templates, and
  operational actions.
- Keep the six-study pilot unactivated until its operating records are frozen. Do not add
  acquired sources, raw images, populated reference labels, reviewer identities, patient
  records, or unreviewed results.
- Never execute downloaded research code or fetch images as part of repository tooling.
- Update the single authoritative specification in
  `research/specs/meddatatrace_specification.tex` in place for actual protocol, architecture,
  pilot, or policy changes. Do not create competing specification files.

Never commit any of the following:

- raw images or patient data;
- demographic, diagnostic, or other unnecessary clinical metadata;
- populated withheld reference states or labels;
- reviewer identities, signatures, or invented human judgments;
- downloaded-code execution output; or
- acquired source captures unless the task explicitly requires a public-safe, rights-reviewed
  artifact and its provenance is recorded.

Use exact versions, source locators, and hashes for permissible artifacts. Read only the fields
required by the contract. Keep withheld reference outputs outside this checkout and unavailable
to evaluated methods.

See `README.md` for the public-safe content policy and `SECURITY.md` for reporting security
concerns.

## Pull requests

A pull request should be narrow, reviewable, and reproducible. Its description must state:

- what changed and which contracts are affected;
- the exact commands run and their results;
- what remains intentionally unverified; and
- the publication-safety and data-boundary decision.

Before opening a pull request:

- run `uv run --locked python scripts/tasks.py format`;
- run `uv run --locked python scripts/tasks.py check`;
- inspect `git diff --check` and the staged file list;
- do not include generated TeX files or local research artifacts; and
- update relevant README, specification, and template text when behavior or workflow changes.

CI is authoritative for the locked environment. Workflow actions are pinned to full commit
SHAs, workflow permissions stay least-privilege, and pull-request code is never executed
through a privileged `pull_request_target` workflow.

## References

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python Developer's Guide](https://devguide.python.org/)
- [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
- [Ruff integrations and CI](https://docs.astral.sh/ruff/integrations/)
- [uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [mypy configuration](https://mypy.readthedocs.io/en/stable/config_file.html)
- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)
