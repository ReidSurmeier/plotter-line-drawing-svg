# Project packet

## Classification

`plotter-line-drawing-svg` is a maintained reference implementation for the
last two stages of a plotter markmaking workflow: solved Alpha Plates become
Coverage Marks in a Layered SVG, then a Master SVG becomes a Mark Build MP4.

Verified on 2026-07-31 against the original `main` commit
`2e0b3a8e1370a839c55ad70b39b12b14c5b491ed`.

## Source and upstream boundary

This package owns:

- fixed-opacity Coverage Mark generation;
- baseline, Prune Baseline, and Budget Solve paths;
- Master and per-plate SVG output;
- raster proofs, contact sheets, and paper figures; and
- artwork-only Mark Build rendering with `rsvg-convert` and FFmpeg.

Raw-image plate solving remains in
[`ReidSurmeier/plotter-separation-rebuild`](https://github.com/ReidSurmeier/plotter-separation-rebuild).
The read-only `upstream` remote records that lineage; writable `origin` is this
repository's canonical GitHub identity.

## Verified implementation

A clean Python 3.12 environment installed `.[dev,paper]`. The original
checkpoint passed 17 tests. The suite includes a real temporary-directory
Alpha Stack → Layered SVG → H.264 MP4 acceptance path when `rsvg-convert` and
FFmpeg are installed.

The 2026-07-31 tracer adds Source Fixity and portable artifact names to all
three Generated Manifests. It also restores compatibility with the currently
resolved Ruff rule set without changing Coverage Mark geometry, Reveal Order,
Stack Order, or encoding settings.

The completed tree passes 21 tests, Ruff, Python compilation, and dependency
consistency checks. A non-overwriting canary using the preserved 12-plate run
produced an exact historical Master SVG match at
`94e9c8338224b4c299007bb2bc0bdc468eb3ee6040744044478fb9ff799e6af3`
and an exact historical 208-frame MP4 match at
`5666eee5f8dcf5113ca52f577534ba6daf3971c8fbe71ef9b0bd329da5aeb603`.
Only the Generated Manifest schema changed. Issue 4 is closed against that
evidence.

## Published and local media custody

`public_assets/` contains six H.264, 1920x1080 public MP4 exports. Their
durations are 25.0 or 25.2 seconds and their frame rates are 25 or 30 fps.
They remain byte-preserved.

The repositories share two byte-identical exports with
`ReidSurmeier/plotter-image-animations`:

- the bathroom SVG reveal:
  `a7bd0d91aface1ccf123401b1f10a253e24e26fa2b0d34811036c78268ba0676`;
  and
- the full-contact portrait build:
  `d0bb5232b30e8e1ecc57ff5229b1e5fd7a5746ce99d8d61da2fee447c4df040f`.

That establishes export lineage, not the exact generating Alpha Stack or
source-image rights. [Issue 2](https://github.com/ReidSurmeier/plotter-line-drawing-svg/issues/2)
owns the human provenance and publication-rights review.

On 2026-08-02, the repository owner confirmed that they own or are authorized
to publish the portrait, bathroom, and fashion imagery represented by the
three-file `plotter-image-animations` snapshot. The six exports here depict the
same portrait and bathroom subjects, so continued distribution of these six
unchanged exports is authorized. This human authorization does not identify
the exact generating Alpha Stacks or source files; issue 2 remains open for
that provenance evidence.

The clean home checkout also contains an ignored 234 MB
`runs/tumblr-790aa7518ed1` reference run. It is local custody, not tracked
source. [Issue 3](https://github.com/ReidSurmeier/plotter-line-drawing-svg/issues/3)
is now backed by the additive fixity and move map in
`docs/ignored-run-custody.md`. The run must move with the repository without
being published or rewritten.

## Runtime and deployment ownership

There is no persistent runtime. GitHub Pages is absent, the GitHub deployments
list is empty, and a fresh 44-component Droplet snapshot contains no matching
Runtime Component. Pugnet and Tailscale Serve are optional sharing mechanisms,
not owned deployments.

Orca is configured to create worktrees from `origin/main`. Its cached Project
identity incorrectly selects the lineage `upstream` remote; Workspace
Operations issue 37 retains that tooling defect. No Orca internal state was
edited.

## Validation

```bash
python -m pip install -e ".[dev,paper]"
python -m pytest -q
ruff check .
python -m compileall -q src tests
```

Run with both system renderers present so the end-to-end acceptance test does
not skip. Use a temporary output directory for any real visual canary.

## Next actions

1. Continue exact source-image and Alpha Stack provenance recovery in issue 2;
   publication authorization for the current unchanged exports is recorded.
2. Preserve the issue 3 fixity record whenever the ignored run is relocated.
3. Preserve the closed portable-manifest canary evidence in
   [issue 4](https://github.com/ReidSurmeier/plotter-line-drawing-svg/issues/4)
   when the manifest schema changes again.
