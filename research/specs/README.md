# MedDataTrace - authoritative working specification

The project has one authoritative document:

- `meddatatrace_specification.tex` -> `meddatatrace_specification.pdf`

Update this file in place for future protocol, architecture, pilot, or policy changes. Do not create amendment PDFs for ordinary revisions. Use version control or commit history to track changes privately.

Supporting files are implementation artifacts rather than separate project specifications:

- `references.bib`: bibliography
- `reference_semantics/`: synthetic conformance code/tests
- `pilot_templates/`: editable JSON templates for the pilot

Build:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error meddatatrace_specification.tex
```
