# MedDataTrace - authoritative working specification

The project has one authoritative document:

- `meddatatrace_specification.tex` -> `MedDataTrace_Specification.pdf`

Update this file in place for future protocol, architecture, pilot, or policy changes. Do not create amendment PDFs for ordinary revisions. Use version control or commit history to track changes privately.

The core study is designed to be feasible without recruited domain-expert reviewers. Primary held-out reference labels must be **artifact-grounded**: the complete derivation from the named reported evaluation to the exact artifact/membership basis must be source-supported and reproducible, and the issue-specific result must then be deterministically generated. LLM/heuristic annotations are **silver** training/development data only. A reproducibly justified `UNKNOWN` may be gold. Cases whose *reference itself* cannot be established are `REFERENCE_UNSCORABLE`; cases requiring domain interpretation outside the frozen contract are `EXPERT_REQUIRED`. Neither is used for gold correctness claims.

Supporting files are implementation artifacts rather than separate project specifications:

- `references.bib`: bibliography
- `reference_semantics/`: synthetic conformance code/tests
- `pilot_templates/`: editable JSON templates for artifact-grounded pilot records

Build:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error meddatatrace_specification.tex
```
