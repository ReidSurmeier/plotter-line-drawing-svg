# Paper Figures

`plotter_line_drawing_svg.paper_figures` generates color-focused comparison
figures for regenerated budget solves versus naive pruning.

Outputs:

- `F1_deltaE_vs_budget.pdf`
- `F2_per_ink_coverage_error.pdf`
- `F3_gamut_shrink.pdf`
- `F4_deltaE_heatmap.pdf`
- `F5_ink_load_vs_budget.pdf`
- `F6_hue_rotation_error.pdf`

The figures use:

- CIEDE2000 color difference in Lab space.
- Lab `a*b*` convex hulls for gamut comparison.
- Per-ink mark-area load from the emitted SVG paths.
- A critical default budget of `6.25%`.

Example:

```bash
python -m plotter_line_drawing_svg.paper_figures \
  --jax-dir /srv/woodblock-share/plotter-separation/micron-alpha-available-xsd05-close-lithograph-v1 \
  --regen-root /srv/woodblock-share/plotter-separation/micron-coverage-svg-budget-solve-reduce75-v1 \
  --prune-root /srv/woodblock-share/plotter-separation/plotter-line-drawing-svg-prune-reduce75-v1 \
  --out /srv/woodblock-share/plotter-separation/plotter-line-drawing-svg-paper-figures-v1
```
