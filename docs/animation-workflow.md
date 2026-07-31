# Complete animation workflow

This guide covers both supported starting points:

1. You already have solved alpha plates and want a layered SVG and MP4.
2. You have a JPG or PNG and need to solve the alpha plates first.

The commands use Ubuntu or WSL2. macOS equivalents are included below. Run
commands from the repository named in each section; the two repositories have
different responsibilities.

## What each stage does

| Stage | Input | Output | Implementation |
| --- | --- | --- | --- |
| Plate solve | JPG or PNG | `alpha_stack_float32.npz` and `metadata.json` | `plotter-separation-rebuild` |
| Markmaking | solved alpha stack | layered and per-plate SVGs | `plotter-line-drawing-svg` |
| Mark build | master layered SVG | H.264 MP4 | `plotter-line-drawing-svg` |

> [!NOTE]
> The plate solve is upstream because this repository deliberately starts from
> solved plates. JAX is therefore optional when you already have a valid alpha
> stack. DiffVG is not used anywhere in the workflow documented here.

## Dependencies

### Required for SVG and MP4 generation

| Tool | Why it is needed | How to verify |
| --- | --- | --- |
| Git | downloads the repositories | `git --version` |
| Python 3.11+ | runs the two console applications | `python3 --version` |
| NumPy | reads and processes alpha stacks | installed by the package |
| Pillow | writes previews and contact sheets | installed by the package |
| `rsvg-convert` | rasterizes each SVG animation frame | `rsvg-convert --version` |
| FFmpeg | encodes PNG frames as H.264 MP4 | `ffmpeg -version` |

### Optional tools

| Tool | When it is needed |
| --- | --- |
| JAX | solves plates from a source image in the upstream repository |
| NVIDIA driver and CUDA-capable GPU | accelerates the optional JAX solve |
| ImageMagick | resizes unusually large inputs before a solve |
| Real-ESRGAN NCNN Vulkan | optional upstream source upscaling |
| pytest and Ruff | tests and checks contributions |
| GitNexus | maps code paths during repository analysis; not a runtime dependency |
| GitHub CLI (`gh`) | manages repository settings, issues, and releases |
| Tailscale Serve | privately shares a finished MP4; not required to create it |

### Ubuntu or WSL2 system packages

```bash
sudo apt update
sudo apt install -y \
  git \
  python3 \
  python3-venv \
  ffmpeg \
  librsvg2-bin
```

Add ImageMagick only if you want the optional resize command:

```bash
sudo apt install -y imagemagick
```

### macOS system packages

Install [Homebrew](https://brew.sh/) first, then run:

```bash
brew install git python ffmpeg librsvg imagemagick
```

### Windows

WSL2 with Ubuntu is the documented Windows path. Install the current NVIDIA
Windows driver if you want JAX GPU acceleration, then verify that `nvidia-smi`
works inside WSL before installing the Python GPU extra.

## Install the SVG and animation repository

```bash
mkdir -p plotter-work
cd plotter-work
git clone https://github.com/ReidSurmeier/plotter-line-drawing-svg.git
cd plotter-line-drawing-svg

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Confirm both public commands and both system renderers:

```bash
plotter-line-svg --help
plotter-line-svg-animate --help
rsvg-convert --version
ffmpeg -version
```

The optional paper-figure dependencies are separate because they are not needed
for SVG or MP4 creation:

```bash
python -m pip install -e ".[dev,paper]"
```

## Path A: start from solved alpha plates

### 1. Check the input contract

The alpha folder must contain:

```text
jax-alpha/
├── alpha_stack_float32.npz
└── metadata.json
```

`alpha_stack_float32.npz` must contain an `alpha_stack` array shaped
`(plates, height, width)`. `metadata.json` must contain `inkset.inks`, with one
`id`, `label`, and RGB triplet per plate. The plate count and ink count must
match.

The folder may also contain `target_upscaled.png` and
`composite_from_alpha_plates.png`. If present, the SVG command copies them into
its proof output for comparison.

### 2. Generate coverage marks and layered SVGs

From `plotter-line-drawing-svg` with its virtual environment active:

```bash
plotter-line-svg /path/to/jax-alpha outputs/example/coverage-svg \
  --tile-px auto \
  --mark-opacity 0.55 \
  --max-bands-per-cell 3 \
  --min-alpha 0.025 \
  --max-paths-per-plate 7200
```

The most important outputs are:

```text
outputs/example/coverage-svg/
├── master_coverage_svg.svg
├── plate_svgs/
├── actual_svg_crop.png
├── actual_svg_preview.png
├── contact_sheet.png
├── coverage_svg_metadata.json
└── index.html
```

Open `actual_svg_crop.png` before animating. It is the quickest way to catch an
incorrect palette, empty plates, excessive mark density, or an unexpected crop.

### 3. Generate the artwork-only MP4

```bash
plotter-line-svg-animate \
  outputs/example/coverage-svg/master_coverage_svg.svg \
  outputs/example/animation \
  --output-name mark_build.mp4 \
  --fps 18 \
  --frames-per-layer 14 \
  --start-hold-frames 10 \
  --end-hold-frames 30 \
  --width-px 1080
```

The animator reveals lighter ink layers before darker ones. Each frame is still
composited in the master SVG's original layer order because alpha blending is
order-dependent. The output contains the artwork only—no source panel, labels,
metrics, swatches, contact sheet, or dashboard.

The frame count is:

```text
start hold + (number of SVG layers × frames per layer) + end hold
```

Duration is the frame count divided by FPS. Twelve layers with the defaults
produce 208 frames, or about 11.56 seconds at 18 FPS.

The output folder contains the MP4, its manifest, an HTML player, and rendered
PNG frames. Add `--keep-frame-svgs` only when debugging because it preserves an
additional SVG file for every frame.

### 4. Validate the video

```bash
ffprobe -v error \
  -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  outputs/example/animation/mark_build.mp4
```

Expected properties are H.264 video, even pixel dimensions, and `yuv420p`, which
keeps the MP4 compatible with browsers and common video players.

### 5. Verify portable manifests

Both commands write JSON intended to travel with their output directories. A
Generated Manifest does not include caller-specific absolute paths.

`coverage_svg_metadata.json` records the portable Alpha Stack directory name,
the SHA-256 of both required inputs under `source_files`, and artifact paths
relative to the coverage output directory. `animation_manifest.json` records
the Master SVG filename and its SHA-256 under `source_svg_sha256`, plus the
output MP4 filename.

Check that a shareable output does not expose its former filesystem location:

```bash
jq '{source, source_files, artifacts}' \
  outputs/example/coverage-svg/coverage_svg_metadata.json
jq '{source_svg, source_svg_sha256, output_mp4}' \
  outputs/example/animation/animation_manifest.json
```

The hashes identify exact inputs after an output directory moves. They do not
establish source-image authorship or publication rights.

## Path B: start from a JPG or PNG

This path adds the upstream JAX alpha-plate solver. The installation above puts
the SVG repository under `plotter-work`; keep the solver beside it so the
commands remain easy to read:

```text
plotter-work/
├── plotter-separation-rebuild/
├── plotter-line-drawing-svg/
├── inputs/
└── runs/
```

### 1. Clone and install the upstream solver

```bash
cd ..
mkdir -p inputs runs
git clone https://github.com/ReidSurmeier/plotter-separation-rebuild.git
cd plotter-separation-rebuild

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

For a CUDA 12 GPU solve:

```bash
python -m pip install -e ".[gpu]"
```

For a slower CPU solve:

```bash
python -m pip install -e ".[ml]"
```

> [!WARNING]
> Do not install an unqualified `jax` wheel for a GPU proof and assume it found
> CUDA. Always run the backend check below. A working `nvidia-smi` command alone
> does not prove that JAX selected the GPU.

Verify JAX before a long solve:

```bash
python -c "import jax; print(jax.__version__); print(jax.default_backend()); print(jax.devices())"
```

For the GPU path, the backend should be `gpu` and the device list should include
a CUDA device.

### 2. Prepare the source image

Copy a JPG or PNG into `plotter-work/inputs`. Large images increase solve time
and memory use. A practical optional working-size conversion is:

```bash
magick ../inputs/source.jpg -resize '1000x1000>' ../inputs/source_working.png
```

If your ImageMagick installation provides `convert` instead of `magick`:

```bash
convert ../inputs/source.jpg -resize '1000x1000>' ../inputs/source_working.png
```

### 3. Solve a 12-ink alpha stack

From `plotter-separation-rebuild` with its environment active:

```bash
CUDA_VISIBLE_DEVICES=0 XLA_PYTHON_CLIENT_PREALLOCATE=false \
python scripts/generate_micron_alpha_plates.py \
  ../inputs/source_working.png \
  ../runs/example/jax-alpha \
  --target-mode full \
  --upscale none \
  --steps 700 \
  --palette full12 \
  --seed 2001
```

The solve writes the two files required by this repository plus previews,
16-bit and 8-bit masks, a reconstructed composite, metrics, and a contact sheet.
Inspect `runs/example/jax-alpha/contact_sheet.png` before continuing.

> [!IMPORTANT]
> `--palette full12` provides twelve available ink plates. It does not force all
> twelve colors into the picture. A source with a narrow gamut can legitimately
> produce empty or nearly empty plates, which then contribute no visible marks.

### 4. Generate SVG and MP4

Activate the `plotter-line-drawing-svg` environment, then run Path A against the
new alpha folder:

```bash
cd ../plotter-line-drawing-svg
source .venv/bin/activate

plotter-line-svg ../runs/example/jax-alpha ../runs/example/coverage-svg \
  --tile-px auto \
  --mark-opacity 0.55 \
  --max-bands-per-cell 3 \
  --min-alpha 0.025 \
  --max-paths-per-plate 7200

plotter-line-svg-animate \
  ../runs/example/coverage-svg/master_coverage_svg.svg \
  ../runs/example/animation \
  --output-name mark_build.mp4
```

## Tuning the mark field

| Option | Effect |
| --- | --- |
| `--tile-px auto` | scales cell size with image dimensions; start here |
| `--mark-opacity` | fixed opacity assigned to every emitted mark |
| `--max-bands-per-cell` | maximum filled marks generated from one tile |
| `--min-alpha` | ignores low-coverage cells below this threshold |
| `--max-paths-per-plate` | caps each plate after ranking by local alpha mass |
| `--budget-solve-scale` | regenerates a mark field for a fraction of the baseline path budget |
| `--path-retention` | naively keeps a fraction of ranked baseline paths for comparison |

A budget solve is preferable when reducing plot time because it regenerates the
field with larger solve tiles and coverage compensation. `--path-retention` is
an intentionally naive pruning baseline for comparison.

Example at 25 percent of the baseline path budget:

```bash
plotter-line-svg /path/to/jax-alpha outputs/example/reduced \
  --budget-solve-scale 0.25
```

## Troubleshooting

### `rsvg-convert is required to rasterize SVG frames`

Install `librsvg2-bin` on Ubuntu/WSL2 or `librsvg` with Homebrew.

### `ffmpeg is required to encode MP4`

Install FFmpeg, then open a new shell or confirm its installation directory is
on `PATH`.

### JAX reports `cpu` on a GPU machine

Reinstall the upstream repository with its `gpu` extra, then repeat the JAX
backend check. In WSL2, verify the Windows NVIDIA driver and WSL GPU access
before changing Python packages.

### Alpha plate count does not match metadata ink count

Regenerate or repair the input as one unit. Do not delete an alpha plate without
also removing its corresponding `inkset.inks` entry.

### The SVG looks like scribbles

Confirm you ran `plotter-line-svg` from this repository and inspect
`coverage_svg_metadata.json`. Its method should be `coverage_line_fill`. The
native marks are filled lozenges with `stroke="none"`.

### Some of the 12 colors never appear

This is usually correct for a limited-gamut source. Check the per-plate path
counts in `coverage_svg_metadata.json`; unused solved plates can contain zero
paths.

### The animation changes the final color

Use the repository's current animator. Reveal timing is light-to-dark, but final
compositing must preserve the original SVG stack order.

### Generated files are too large for Git

Keep runs under `runs/` or `outputs/`; both are ignored. Commit only intentional
reference assets. Use Git LFS or a release asset when a large binary genuinely
belongs in the public repository.

## Tools used in the validated reference run

The reference workflow was analyzed with GitNexus, orchestrated in Codex, and
executed with JAX on an NVIDIA GPU. ImageMagick prepared the working image,
NumPy and Pillow handled plate and preview data, the repository emitted the
layered SVG, `rsvg-convert` rasterized reveal frames, FFmpeg encoded H.264, and
`ffprobe` verified the finished MP4. pytest checked markmaking and animation
behavior. Tailscale Serve was used only to share the finished file privately.

Only Python, NumPy, Pillow, `rsvg-convert`, and FFmpeg are required when valid
alpha plates already exist.
