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
