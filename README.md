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
  tests, and pilot templates.
- `pyproject.toml` and `uv.lock`: non-package development environment and locked Ruff
  tooling.
- `Makefile`: reproducible setup, checks, formatting, and specification build commands.
- `.github/`: CI, dependency update, contribution, and security configuration.

## Development

Prerequisites: Python 3.14 and [uv](https://docs.astral.sh/uv/). The checked-in project
requires Python `>=3.14,<3.15`; CI installs the managed Python version and uses uv 0.12.10.

```bash
make setup
make check
make format
```

`make check` runs Ruff, the 24 synthetic unittest methods, and JSON syntax checks for all
five supplied pilot artifacts. It does not validate a scientific schema.

## Building the specification

`make spec` runs the documented native command and writes
`research/specs/meddatatrace_specification.pdf`. Native prerequisites are `latexmk`,
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
and to naive readers. Never populate the checked-in reference-label template itself.

The pilot remains explicitly unapproved and unpopulated. Repository readiness is not P0
scientific activation. No paid model account is needed for this foundation.

## License and source rights

The supplied `LICENSE` is GNU AGPL-3.0 and applies as provided. Linked and cited sources
retain their source-specific licenses and rights.
