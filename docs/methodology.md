# Methodology

This repo isolates one stage from Plotter Separation: converting solved alpha
plates into printable line-drawing SVG plates.

## Coverage Mark Field

An alpha plate is not treated as printable opacity. It is treated as a local
coverage target.

For each plate:

1. Divide the alpha image into tiles.
2. Measure local alpha mass in each tile.
3. Convert that mass into one or more fixed-opacity filled marks.
4. Jitter each mark's position, angle, length, and width.
5. Sort marks by local alpha mass and cap each plate's path count.

The marks are filled lozenges, not SVG strokes. That keeps the visual width
explicit and makes the output browser-renderable.

## Budget Solve

The budget solve is different from deleting marks.

Instead of starting with a full SVG and removing paths, it regenerates the mark
field for a target stroke budget. Lower budgets use larger solve tiles and
coverage compensation so the remaining marks carry the broad value structure.

Example budget ladder:

```text
full
25%
6.25%
1.5625%
```

This is useful for testing plotter time and mark density without changing the
upstream alpha plates.
