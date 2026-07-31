# Plotter Line Drawing SVG agent guide

Read `CONTEXT.md` before changing domain language. Preserve the repository
boundary: alpha-plate solving belongs upstream; this package owns coverage-mark
SVG generation, budget reduction, paper figures, and mark-build animation.
Read `PROJECT.md` before changing custody, publication, or deployment claims.

## Boundaries

- Treat Alpha Stacks as source inputs and generated SVG, PNG, JSON, and MP4
  files as Derived output with separate custody.
- Do not overwrite the ignored reference run or the six checked-in public MP4s
  during tests.
- Keep Generated Manifests portable: use artifact names and fixity, not caller
  absolute paths.
- Do not claim source-image publication rights from repository visibility.
- Keep credentials, private paths, and raw secret-scan findings out of
  committed files and shareable manifests.
- Tests must use temporary fixtures and must not publish media, register
  services, or mutate external systems.

## Commands

```bash
python -m pip install -e ".[dev,paper]"
python -m pytest -q
ruff check .
python -m compileall -q src tests
gitleaks git --no-banner --redact
```

The end-to-end test requires `rsvg-convert` and `ffmpeg`; a skip is not a
complete local acceptance result when both tools can be installed.

## Agent skills

### Issue tracker

Issues and PRDs live in this repository's GitHub Issues. See
`docs/agents/issue-tracker.md`.

### Triage labels

Use the five standard triage labels documented in
`docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository with `CONTEXT.md` at the root. See
`docs/agents/domain.md`.
