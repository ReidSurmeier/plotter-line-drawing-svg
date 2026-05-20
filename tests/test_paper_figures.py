from __future__ import annotations

import numpy as np

from plotter_line_drawing_svg.paper_figures import (
    infer_plate_alpha,
    lab_plot_points,
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
