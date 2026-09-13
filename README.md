# MedDataTrace

MedDataTrace is a public, research-only foundation for evidence-qualified review of
dataset issues in medical-imaging evaluations. The repository currently contains the
research specification, synthetic reference semantics, and pilot templates. It is not an
installable assessment application, a medical device, or a validated clinical method.

## Authoritative specification

The single authoritative working specification is [`research/specs/meddatatrace_specification.tex`](research/specs/meddatatrace_specification.tex).
Its supporting notes and the documented build command are in
[`research/specs/README.md`](research/specs/README.md). Protocol, architecture, pilot,
and policy changes belong in that TeX file in place; ordinary revisions do not create
parallel amendment documents.

The synthetic reference implementation exposes four evidence states:

- `UNKNOWN`: evidence is insufficient within the stated boundary.
- `APPLIES`: positive evidence supports the issue for the assessed scope.
- `NOT_APPLICABLE`: negative evidence supports non-applicability for the assessed scope.
- `CONFLICTING`: positive and negative evidence both exist for the assessed scope.

Conformance tests exercise this bookkeeping contract only. Passing them does not validate
real medical evidence, prove source quality, or demonstrate that the approach is useful.
See the specification for the research scope, evidence boundary, and roadmap.

## Repository layout

- `research/specs/`: authoritative TeX specification, bibliography, synthetic semantics,
  deterministic DM-H01 reference generation, tests, and pilot templates.
- `pyproject.toml` and `uv.lock`: non-package development environment and locked Ruff/mypy
  tooling.
- `Makefile`: reproducible setup, checks, formatting, and specification build commands.
- `.github/`: CI, dependency update, contribution, and security configuration.

## Development

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the Python style, typing, testing, data-boundary,
and pull-request contract.

Prerequisites: Python 3.14 and [uv](https://docs.astral.sh/uv/). The checked-in project
requires Python `>=3.14,<3.15`; CI installs the managed Python version and uses uv 0.12.13.

From the repository root, these commands work in PowerShell, Command Prompt, and Unix
shells:

```text
uv sync --locked
uv run --locked python scripts/tasks.py check
uv run --locked python scripts/tasks.py format
```

`scripts/tasks.py` is the portable task entry point. On Unix, the Makefile remains an
optional convenience wrapper (`make setup`, `make check`, `make format`, `make spec`).

The check task runs Ruff lint and formatting checks, strict mypy, synthetic semantics,
reference-admission and DM-H01 generator unittests, plus JSON syntax checks for all six supplied
pilot artifacts. It does not validate a scientific schema.

## Building the specification

`uv run --locked python scripts/tasks.py spec` runs the documented native command and
writes `research/specs/meddatatrace_specification.pdf`. On Unix, `make spec` is an
optional alias. Native prerequisites are `latexmk`,
`biber`, and the TeX packages used by the preamble: `fontenc`, `inputenc`, `lmodern`,
`geometry`, `microtype`, `setspace`, `xcolor`, `graphicx`, `booktabs`, `tabularx`,
`longtable`, `array`, `amsmath`, `amssymb`, `enumitem`, `titlesec`, `fancyhdr`,
`tcolorbox`, `tikz`, `listings`, `caption`, `float`, `needspace`, `biblatex`,
`csquotes`, `hyperref`, and `bookmark`.

On Debian or Ubuntu, the CI-equivalent package set is:

```bash
sudo apt-get install latexmk biber texlive-latex-recommended texlive-latex-extra \
  texlive-bibtex-extra texlive-fonts-recommended texlive-pictures lmodern
```

Do not install operating-system packages automatically as part of local setup. If native
TeX is unavailable, download `MedDataTrace-Specification` from a successful GitHub Actions
`Specification` job instead.

## Public-safe research boundary

Bootstrap history contains code, the supplied specification, empty templates, and
synthetic examples only. Do not commit acquired source material, raw images, populated
reference labels, reviewer identities, or unreviewed results. `.gitignore` is accident
prevention, not access control. Real withheld labels must remain outside this checkout in
separately access-controlled storage; they must be unavailable both to evaluated methods
and to evaluated extraction or assessment tools. Never populate the checked-in withheld
reference or derivation templates themselves.

The DM-H01 P0 contract is frozen for the official public MedMNIST/DermaMNIST membership
basis, and one complete reference derivation is withheld after reproducibility checks.
The six-study micro-pilot remains unactivated until its operating records are frozen.
Expert validation is optional future work. Repository readiness is not P0 scientific
activation. No paid model account is needed for this foundation.

## License and source rights

The supplied `LICENSE` is GNU AGPL-3.0 and applies as provided. Linked and cited sources
retain their source-specific licenses and rights.
