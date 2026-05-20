from __future__ import annotations

import numpy as np

from plotter_line_drawing_svg.paper_figures import polygon_area_from_path, target_coverage_load


def test_polygon_area_from_path():
    assert polygon_area_from_path("M 0,0 L 10,0 L 10,5 L 0,5 Z") == 50


def test_target_coverage_load_uses_fixed_opacity_target():
    alpha = np.asarray([[[0.0, 0.55], [1.0, 0.275]]], dtype=np.float32)
    load = target_coverage_load(alpha, mark_opacity=0.55)
    assert np.allclose(load, np.asarray([[0.0, 0.96, 0.96, 0.5]]).mean(axis=1))
