# Contributing to MedDataTrace

MedDataTrace is a public research foundation. Keep changes reproducible, synthetic where
appropriate, and within the boundary described by the authoritative specification.

## Workflow

1. Create a feature branch from `main`.
2. Keep a pull request focused and describe the change and its evidence.
3. Run the exact checks below before requesting review.
4. Review staged paths for secrets, restricted source material, patient data, populated
   held-out answers, and unsupported claims.

```bash
make setup
make check
```

Use `make format` for the repository's Ruff formatting and import-order fixes. When native
TeX prerequisites are installed, run `make spec` and inspect the generated PDF. Without
them, the GitHub Actions `Specification` job is the supported build route.

## Research boundaries

- Reference semantics and tests are synthetic bookkeeping conformance, not medical
  validation or a usefulness claim.
- Preserve the separation between source artifacts, reference semantics, pilot templates,
  and operational actions.
- Keep the pilot unapproved and unpopulated. Do not add acquired sources, raw images,
  populated reference labels, reviewer identities, patient records, or unreviewed results.
- Update the single authoritative specification in
  `research/specs/meddatatrace_specification.tex` in place for actual protocol,
  architecture, pilot, or policy changes. Do not create competing specification files.

See `README.md` for the public-safe content policy and `SECURITY.md` for reporting
security concerns.
