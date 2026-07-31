from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from plotter_line_drawing_svg.paper_figures import (
    ProofRecord,
    infer_plate_alpha,
    lab_plot_points,
    paper_figure_manifest,
    polygon_area_from_path,
    target_coverage_load,
    uv_prime_sample,
)


def test_polygon_area_from_path():
    assert polygon_area_from_path("M 0,0 L 10,0 L 10,5 L 0,5 Z") == 50


def test_target_coverage_load_uses_fixed_opacity_target():
    alpha = np.asarray([[[0.0, 0.55], [1.0, 0.275]]], dtype=np.float32)
    load = target_coverage_load(alpha, mark_opacity=0.55)
    assert np.allclose(load, np.asarray([[0.0, 0.96, 0.96, 0.5]]).mean(axis=1))


def test_infer_plate_alpha_from_white_paper_overprint():
    rgb = np.asarray([[[1.0, 1.0, 1.0], [0.5, 0.5, 0.5], [0.0, 0.0, 0.0]]], dtype=np.float32)
    alpha = infer_plate_alpha(rgb, ink_rgb=(0, 0, 0), paper_rgb=(255, 255, 255))
    assert np.allclose(alpha, [[0.0, 0.5, 1.0]])


def test_uv_prime_sample_shape():
    rgb = np.ones((2, 2, 3), dtype=np.float32)
    uv = uv_prime_sample(rgb)
    assert uv.shape == (4, 2)
    assert np.all(np.isfinite(uv))


def test_lab_plot_points_reorders_lab_for_3d_axes():
    lab = np.asarray([[50.0, -10.0, 20.0]], dtype=np.float32)
    plotted = lab_plot_points(lab)
    assert np.allclose(plotted, [[-10.0, 20.0, 50.0]])


def test_paper_figure_manifest_uses_portable_proof_fixity(
    tmp_path: Path,
) -> None:
    proof_dir = tmp_path / "private-machine-layout" / "regen-full"
    proof_dir.mkdir(parents=True)
    coverage_manifest = proof_dir / "coverage_svg_metadata.json"
    coverage_manifest.write_text('{"paths": {"paths_per_plate": [3, 4]}}', encoding="utf-8")
    record = ProofRecord(
        method="regen",
        rung="full",
        proof_dir=proof_dir,
        rendered_path=proof_dir / "actual_svg_crop.png",
        target_path=proof_dir / "target_upscaled.png",
        metadata={"paths": {"paths_per_plate": [3, 4]}},
        paths_per_plate=(3, 4),
        total_paths=7,
        budget_scale=1.0,
    )

    manifest = paper_figure_manifest([record])
    manifest_text = json.dumps(manifest)

    assert str(tmp_path) not in manifest_text
    assert manifest["records"][0]["proof"] == "regen-full"
    assert manifest["records"][0]["coverage_manifest_sha256"] == hashlib.sha256(
        coverage_manifest.read_bytes()
    ).hexdigest()
