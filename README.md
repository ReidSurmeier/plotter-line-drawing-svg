# Plotter Line Drawing SVG

Focused tooling for turning solved plotter color plates into layered SVG mark fields.

This repo is for the markmaking stage only:

```text
alpha plates -> fixed-opacity coverage marks -> layered SVG plates
```

It does not solve pigments, train DiffVG, or run the full Plotter Separation stack.

Extracted from `ReidSurmeier/plotter-separation-rebuild` so this markmaking
method can move independently from the older build.

## What It Does

- Reads `alpha_stack_float32.npz` and `metadata.json`.
- Converts each alpha plate into filled line/lozenge marks.
- Exports one master layered SVG and one SVG per plate.
- Supports constrained stroke-budget solves instead of deleting marks.

## Usage

```bash
plotter-line-svg /path/to/jax-alpha-folder outputs/proof \
  --tile-px auto \
  --mark-opacity 0.55 \
  --max-paths-per-plate 7200
```

Budget solve examples:

```bash
# 75% reduction from the baseline stroke budget
plotter-line-svg /path/to/jax-alpha-folder outputs/reduce75_step1 \
  --budget-solve-scale 0.25

# Another 75% reduction
plotter-line-svg /path/to/jax-alpha-folder outputs/reduce75_step2 \
  --budget-solve-scale 0.0625
```

## Input Contract

The input folder must contain:

- `alpha_stack_float32.npz` with `alpha_stack` shaped `(plates, height, width)`.
- `metadata.json` with `inkset.inks`, where each ink has `id`, `label`, and `rgb`.

Optional files:

- `target_upscaled.png`
- `composite_from_alpha_plates.png`

## Notes

The alpha value is treated as a coverage target, not printable opacity.
Darkness comes from mark density, mark size, and layer overlap.
