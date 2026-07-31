# Plotter Line Drawing

This context describes the vocabulary for turning solved plotter color plates
into fixed-coverage SVG marks and artwork-only mark-build animations.

## Language

**Alpha plate**:
A two-dimensional coverage target for one ink.
_Avoid_: opacity image, color channel

**Alpha stack**:
An ordered collection of alpha plates paired one-to-one with an ink set.
_Avoid_: source image, animation frames

**Ink set**:
The ordered inks and paper color used to interpret an alpha stack.
_Avoid_: forced color count, swatch list

**Coverage target**:
The local proportion of a cell that fixed-opacity marks should occupy.
_Avoid_: printable opacity

**Coverage mark**:
A short filled line or lozenge whose density and overlap carry image value.
_Avoid_: squiggle, SVG stroke

**Layered SVG**:
An SVG whose ordered groups each represent one ink plate.
_Avoid_: flattened preview

**Master SVG**:
The layered SVG containing every ink plate in compositing order.
_Avoid_: contact sheet, per-plate SVG

**Budget solve**:
A regenerated coverage-mark field designed for a lower path count.
_Avoid_: pruning

**Prune baseline**:
A comparison field made by deleting lower-ranked marks from the baseline field.
_Avoid_: budget solve

**Mark build**:
An artwork-only animation that progressively reveals paths in the master SVG.
_Avoid_: dashboard, replay, data visualization

**Reveal order**:
The light-to-dark order that determines when ink layers become visible.
_Avoid_: stack order

**Stack order**:
The original master-SVG order used to composite visible ink layers.
_Avoid_: reveal order

**Generated manifest**:
A portable JSON record of source fixity, relative artifact names, settings, and
result structure for one generated output directory.
_Avoid_: machine log, absolute-path dump

**Source fixity**:
The SHA-256 evidence that identifies the exact Alpha Stack, metadata, or Master
SVG used for a run.
_Avoid_: source path

## Relationships

- An **Alpha stack** contains exactly one **Alpha plate** per **Ink set** entry.
- Each **Alpha plate** produces zero or more **Coverage marks** in one **Layered SVG** group.
- A **Master SVG** contains all plate groups in **Stack order**.
- A **Mark build** uses **Reveal order** for timing and **Stack order** for compositing.
- A **Budget solve** and a **Prune baseline** are alternative reductions of the same baseline field.
- A **Generated manifest** records **Source fixity** without exposing the
  caller's filesystem layout.

## Example dialogue

> **Developer:** "If the ink set contains twelve colors, should every color appear in the mark build?"
> **Domain expert:** "No. The alpha stack has twelve plate slots, but an alpha plate may solve to negligible coverage and emit no coverage marks."
>
> **Developer:** "Can I reorder the SVG groups to match the light-to-dark reveal?"
> **Domain expert:** "No. Reveal order controls timing; stack order controls alpha blending and must remain unchanged."

## Flagged ambiguities

- “Animation” previously referred to dashboards and monitor replays. In this repository the canonical output is a **Mark build**.
- “Line” previously included scribble strokes. Here a line is a filled **Coverage mark** with no SVG stroke.
- “Twelve colors” means a twelve-entry **Ink set**, not twelve guaranteed visible layers.
- “Source” in a **Generated manifest** identifies portable input evidence, not
  a private machine path.
