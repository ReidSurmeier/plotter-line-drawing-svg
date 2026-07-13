from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pytest


@pytest.mark.skipif(
    shutil.which("rsvg-convert") is None or shutil.which("ffmpeg") is None,
    reason="the end-to-end animation smoke test requires rsvg-convert and ffmpeg",
)
def test_user_can_generate_a_layered_svg_and_mp4(tmp_path: Path) -> None:
    alpha_dir = tmp_path / "jax-alpha"
    svg_dir = tmp_path / "coverage-svg"
    animation_dir = tmp_path / "animation"
    alpha_dir.mkdir()

    alpha = np.zeros((2, 16, 20), dtype=np.float32)
    alpha[0, 2:14, 2:10] = 0.75
    alpha[1, 4:12, 8:18] = 0.6
    np.savez_compressed(alpha_dir / "alpha_stack_float32.npz", alpha_stack=alpha)
    (alpha_dir / "metadata.json").write_text(
        json.dumps(
            {
                "inkset": {
                    "paper_rgb": [255, 255, 255],
                    "inks": [
                        {"id": "rose", "label": "Rose", "rgb": [205, 73, 134]},
                        {"id": "blue", "label": "Blue", "rgb": [30, 91, 176]},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "plotter_line_drawing_svg.cli",
            str(alpha_dir),
            str(svg_dir),
            "--tile-px",
            "4",
            "--max-paths-per-plate",
            "100",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    master_svg = svg_dir / "master_coverage_svg.svg"
    assert master_svg.exists()
    assert 'data-mark-family="coverage_line_fill"' in master_svg.read_text(encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "plotter_line_drawing_svg.svg_animation",
            str(master_svg),
            str(animation_dir),
            "--output-name",
            "smoke.mp4",
            "--fps",
            "2",
            "--frames-per-layer",
            "1",
            "--start-hold-frames",
            "1",
            "--end-hold-frames",
            "1",
            "--width-px",
            "160",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    mp4 = animation_dir / "smoke.mp4"
    manifest = json.loads((animation_dir / "animation_manifest.json").read_text(encoding="utf-8"))
    assert mp4.stat().st_size > 0
    assert manifest["frame_count"] == 4
    assert manifest["fps"] == 2
