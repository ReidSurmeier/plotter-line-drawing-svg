from __future__ import annotations

import json

import numpy as np

from plotter_line_drawing_svg.markmaking import (
    CoverageConfig,
    alpha_masks_to_budget_solved_paths,
    alpha_masks_to_coverage_paths,
    coverage_svg_document,
    load_alpha_stack,
    load_inkset,
    retain_paths_per_plate,
)


def test_load_alpha_stack_and_inkset(tmp_path):
    alpha = np.ones((2, 12, 16), dtype=np.float32) * 0.5
    np.savez(tmp_path / "alpha_stack_float32.npz", alpha_stack=alpha)
    (tmp_path / "metadata.json").write_text(
        json.dumps(
            {
                "inkset": {
                    "paper_rgb": [255, 255, 255],
                    "inks": [
                        {"id": "red", "label": "Red", "rgb": [255, 0, 0]},
                        {"id": "blue", "label": "Blue", "rgb": [0, 0, 255]},
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    loaded = load_alpha_stack(tmp_path)
    inkset = load_inkset(tmp_path)

    assert loaded.shape == (2, 12, 16)
    assert len(inkset.inks) == 2
    assert inkset.inks[0].rgb == (255, 0, 0)


def test_budget_solve_hits_lower_path_budget():
    alpha = np.zeros((2, 40, 40), dtype=np.float32)
    alpha[0, 4:34, 4:34] = 0.8
    alpha[1, 10:38, 2:30] = 0.6
    config = CoverageConfig(tile_px=4, max_paths_per_plate=200, mark_opacity=0.55)

    baseline_paths, baseline_metrics = alpha_masks_to_coverage_paths(alpha, config=config)
    budget_paths, budget_metrics = alpha_masks_to_budget_solved_paths(
        alpha,
        baseline_counts=baseline_metrics["paths_per_plate"],
        config=config,
        scale=0.25,
    )

    assert baseline_paths
    assert budget_paths
    assert budget_metrics["mode"] == "alpha_budget_solve"
    assert sum(budget_metrics["paths_per_plate"]) < sum(baseline_metrics["paths_per_plate"])


def test_retain_paths_prunes_each_plate():
    alpha = np.ones((2, 24, 24), dtype=np.float32) * 0.8
    config = CoverageConfig(tile_px=4, max_paths_per_plate=200, mark_opacity=0.55)
    paths, metrics = alpha_masks_to_coverage_paths(alpha, config=config)

    retained, retained_metrics = retain_paths_per_plate(paths, 0.25)

    assert retained
    assert retained_metrics["mode"] == "ranked_prune"
    assert retained_metrics["paths_per_plate"][0] < metrics["paths_per_plate"][0]
    assert retained_metrics["paths_per_plate"][1] < metrics["paths_per_plate"][1]


def test_svg_document_keeps_plate_layers():
    alpha = np.ones((1, 16, 16), dtype=np.float32) * 0.8
    config = CoverageConfig(tile_px=8, max_paths_per_plate=10)
    paths, _metrics = alpha_masks_to_coverage_paths(alpha, config=config)
    inkset = load_inkset_from_dict({"inkset": {"inks": [{"id": "black", "label": "Black", "rgb": [0, 0, 0]}]}})

    svg = coverage_svg_document(
        paths,
        inkset,
        width_px=16,
        height_px=16,
        rect_mm=(0, 0, 100, 100),
        include_plate=None,
        title="Test",
    )

    assert 'inkscape:label="01 Black"' in svg
    assert 'data-mark-family="coverage_line_fill"' in svg
    assert "<path" in svg


def load_inkset_from_dict(metadata: dict):
    tmp = __import__("tempfile").TemporaryDirectory()
    from pathlib import Path

    path = Path(tmp.name)
    (path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return load_inkset(path)
