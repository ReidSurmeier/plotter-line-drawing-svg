from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

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
    coverage_manifest_path = svg_dir / "coverage_svg_metadata.json"
    coverage_manifest_text = coverage_manifest_path.read_text(encoding="utf-8")
    coverage_manifest = json.loads(coverage_manifest_text)
    assert str(tmp_path) not in coverage_manifest_text
    assert coverage_manifest["source"] == "jax-alpha"
    assert coverage_manifest["source_files"] == {
        "alpha_stack_float32.npz": hashlib.sha256(
            (alpha_dir / "alpha_stack_float32.npz").read_bytes()
        ).hexdigest(),
        "metadata.json": hashlib.sha256(
            (alpha_dir / "metadata.json").read_bytes()
        ).hexdigest(),
    }
    assert coverage_manifest["artifacts"]["master_svg"] == "master_coverage_svg.svg"
    assert coverage_manifest["artifacts"]["plate_svgs"] == [
        "plate_svgs/01_rose.svg",
        "plate_svgs/02_blue.svg",
    ]

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
    manifest_path = animation_dir / "animation_manifest.json"
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert mp4.stat().st_size > 0
    assert str(tmp_path) not in manifest_text
    assert manifest["source_svg"] == "master_coverage_svg.svg"
    assert manifest["source_svg_sha256"] == hashlib.sha256(
        master_svg.read_bytes()
    ).hexdigest()
    assert manifest["output_mp4"] == "smoke.mp4"
    assert manifest["frame_count"] == 4
    assert manifest["fps"] == 2
