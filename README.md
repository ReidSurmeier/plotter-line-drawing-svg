# Plotter Line Drawing SVG

Status: maintained reference implementation.

Turn solved color-separation plates into layered SVG fields of filled plotter
marks, then reveal those marks as an artwork-only MP4.

Deployment ownership: none. This repository provides local command-line tools
and published media evidence; it does not own GitHub Pages, a Droplet service,
or a Pugnet runtime.

The repository owns the last two stages of this pipeline:

```text
source image
    -> solved alpha plates                 upstream plate solver
    -> fixed-opacity filled coverage marks this repository
    -> layered SVG                         this repository
    -> light-to-dark mark-build MP4        this repository
```

> [!IMPORTANT]
> This is not a one-command image-to-video model. The SVG tools require solved
> alpha plates. If you are starting with a JPG or PNG, follow the
> [complete animation workflow](docs/animation-workflow.md), which includes the
> optional JAX plate-solving stage.

## What the marks are

Each alpha plate is interpreted as a local coverage target. The renderer emits
short, filled line or lozenge paths with fixed opacity. Darkness comes from mark
density, mark size, and overprinting—not translucent scribble strokes.

The result includes:

- one master layered SVG;
- one SVG for each ink plate;
- raster previews and a contact sheet;
- a direct MP4 reveal with no dashboard, labels, metrics, or data visualization.

See [Methodology](docs/methodology.md) for the mark-generation model and
[Provenance](docs/provenance.md) for the relationship to Plotter Separation.

## Quick start from solved plates

Python 3.11 or newer, `rsvg-convert`, and `ffmpeg` are required. On Ubuntu or
WSL2:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv ffmpeg librsvg2-bin

git clone https://github.com/ReidSurmeier/plotter-line-drawing-svg.git
cd plotter-line-drawing-svg
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Convert an existing alpha stack to SVG:

```bash
plotter-line-svg /path/to/jax-alpha-folder outputs/example/coverage-svg \
  --tile-px auto \
  --mark-opacity 0.55 \
  --max-bands-per-cell 3 \
  --min-alpha 0.025 \
  --max-paths-per-plate 7200
```

Animate the master SVG:

```bash
plotter-line-svg-animate \
  outputs/example/coverage-svg/master_coverage_svg.svg \
  outputs/example/animation \
  --output-name mark_build.mp4
```

The input folder must contain `alpha_stack_float32.npz` and `metadata.json`.
See the [complete animation workflow](docs/animation-workflow.md) for every
dependency, raw-image plate solving, GPU checks, output files, parameter tuning,
and troubleshooting.

## Documentation

- [PROJECT.md](PROJECT.md) — project status and custody
- [Complete animation workflow](docs/animation-workflow.md)
- [Methodology](docs/methodology.md)
- [Paper figures](docs/paper-figures.md)
- [Provenance and scope](docs/provenance.md)
- [Contributing](CONTRIBUTING.md)
- [Support](SUPPORT.md)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Development

```bash
source .venv/bin/activate
python -m pip install -e ".[dev,paper]"
python -m pytest -q
ruff check .
```

The project is licensed under the [MIT License](LICENSE).
