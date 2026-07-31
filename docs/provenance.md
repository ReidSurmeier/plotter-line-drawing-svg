# Provenance

This repo was extracted from `ReidSurmeier/plotter-separation-rebuild`.

The method comes from the fixed-coverage SVG proof path:

```text
coverage_svg / proof35b fixed coverage marks
```

The useful part was kept:

- alpha plate input contract
- fixed-opacity coverage marks
- deterministic jitter
- layered per-plate SVG export
- constrained budget solve

The old repo's broader experiments are intentionally left out:

- pigment solving
- DiffVG training
- W&B observability
- proof animation
- source image upscaling

This repo should stay small and specific: line-drawing SVG markmaking from
already-solved plates.

## Published export lineage

Two checked-in exports are byte-identical to files later collected in
`ReidSurmeier/plotter-image-animations`:

- the bathroom SVG reveal has SHA-256
  `a7bd0d91aface1ccf123401b1f10a253e24e26fa2b0d34811036c78268ba0676`;
  and
- the full-contact portrait build has SHA-256
  `d0bb5232b30e8e1ecc57ff5229b1e5fd7a5746ce99d8d61da2fee447c4df040f`.

This establishes export custody and code lineage. It does not identify the
exact generating Alpha Stacks or source images, and it does not establish
publication rights. Those questions remain assigned to the repository's
human provenance review.
