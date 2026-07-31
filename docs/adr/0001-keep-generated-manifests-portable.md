# ADR 0001: Keep generated manifests portable

- Status: Accepted
- Date: 2026-07-31

## Context

The SVG, animation, and paper-figure commands write JSON beside shareable
Derived output. Those manifests previously serialized the caller's Alpha
Stack, Master SVG, proof directories, output directory, and artifact paths
verbatim. Absolute paths disclose machine layout and stop describing the
output correctly after it is copied.

Removing all input identity would also be harmful: a filename alone cannot
prove which Alpha Stack or Master SVG produced a result.

## Decision

Generated Manifests record:

- portable source and artifact names;
- SHA-256 Source Fixity for required Alpha Stack inputs and the Master SVG;
- existing settings, dimensions, path metrics, and layer order; and
- no caller-specific absolute paths.

Internal command execution may continue using absolute `Path` objects. Only the
shareable manifest schema is constrained.

## Consequences

An output directory can move without making its links or provenance record
false. Reviewers can match the exact input bytes without learning a private
filesystem path. Existing generated manifests are historical artifacts and are
not rewritten automatically; a new non-overwriting canary validates the schema.
