# Contributing

Contributions are welcome when they preserve the repository's focused role:
turning solved alpha plates into filled coverage-mark SVGs, reduced path-budget
variants, paper figures, and artwork-only mark-build animations.

Read [the domain glossary](CONTEXT.md) and
[the animation workflow](docs/animation-workflow.md) before changing public
behavior. Plate solving, pigment selection, DiffVG training, dashboards, and
source upscaling belong upstream unless the repository boundary is explicitly
reconsidered.

## Set up a development environment

On Ubuntu or WSL2, install the system renderers:

```bash
sudo apt update
sudo apt install -y python3 python3-venv ffmpeg librsvg2-bin
```

Then install the package and all test dependencies:

```bash
git clone https://github.com/ReidSurmeier/plotter-line-drawing-svg.git
cd plotter-line-drawing-svg
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,paper]"
```

## Make a change

1. Create a focused branch from `main`.
2. Add one behavior-level test, make it pass, then continue one behavior at a time.
3. Keep generated runs under `runs/` or `outputs/`; do not commit them by default.
4. Update the user guide when a command, dependency, input contract, or output changes.
5. Run the checks below before opening a pull request.

```bash
ruff check .
python -m pytest -q
```

Tests should exercise public functions or console commands. Avoid tests coupled
to private helper names when the same behavior can be observed through the
package interface.

## Documentation style

Write for a reader following the workflow for the first time:

- put prerequisites before commands that need them;
- name the directory in which a command runs;
- distinguish required tools from optional analysis or publishing tools;
- use the canonical terms in `CONTEXT.md`;
- use relative Markdown links for files in this repository;
- use `> [!NOTE]`, `> [!IMPORTANT]`, or `> [!WARNING]` callouts when emphasis is necessary.

The Markdown should render clearly in both GitHub and Obsidian. Do not use
Obsidian-only wikilinks in public repository documentation because GitHub cannot
resolve them.

## Report a bug

Use the bug-report issue form. Include:

- operating system and Python version;
- the exact command and complete error output;
- whether `rsvg-convert`, FFmpeg, and optional JAX GPU checks pass;
- the alpha-stack shape and ink count;
- `coverage_svg_metadata.json` or `animation_manifest.json` when available;
- a small non-sensitive reproduction input if licensing permits it.

Do not attach a confidential source image to a public issue. Report security
problems through the process in [SECURITY.md](SECURITY.md).

## Open a pull request

Explain the user-visible behavior, the test that proves it, and any generated
artifact you inspected. Keep unrelated cleanup in a separate pull request.

By contributing, you agree that your contributions are licensed under the
repository's [MIT License](LICENSE) and that participation follows the
[Code of Conduct](CODE_OF_CONDUCT.md).
