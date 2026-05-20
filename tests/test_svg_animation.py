from __future__ import annotations

import numpy as np

from plotter_line_drawing_svg.svg_animation import (
    artwork_rect,
    compose_frame_svg,
    parse_layered_svg,
    relative_luminance,
    smoothstep,
)


def test_parse_layered_svg_extracts_layer_metadata():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
<rect id="artwork_bounds" x="1" y="2" width="3" height="4"/>
<g inkscape:label="01 Yellow" data-ink-color="#ffff00"><path d="M 0,0 L 1,0 L 1,1 Z" fill="#ffff00"/></g>
<g inkscape:label="02 Black" data-ink-color="#000000"><path d="M 0,0 L 2,0 L 2,2 Z" fill="#000000"/></g>
</svg>"""
    parsed = parse_layered_svg(svg)

    assert parsed.artwork_rect == (1.0, 2.0, 3.0, 4.0)
    assert len(parsed.layers) == 2
    assert parsed.layers[0].label == "01 Yellow"
    assert parsed.layers[0].color == "#ffff00"
    assert len(parsed.layers[0].paths) == 1


def test_light_color_has_higher_luminance_than_dark_color():
    assert relative_luminance((1.0, 1.0, 0.0)) > relative_luminance((0.0, 0.0, 0.0))


def test_smoothstep_endpoints():
    assert np.isclose(smoothstep(0.0), 0.0)
    assert np.isclose(smoothstep(1.0), 1.0)
    assert 0.0 < smoothstep(0.5) < 1.0


def test_artwork_rect_missing_returns_none():
    assert artwork_rect("<svg></svg>") is None


def test_compose_frame_preserves_original_svg_stack_order():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">
<g inkscape:label="01 Dark" data-ink-color="#000000"><path id="dark" d="M 0,0 L 1,0 L 1,1 Z" fill="#000000"/></g>
<g inkscape:label="02 Light" data-ink-color="#ffffff"><path id="light" d="M 0,0 L 2,0 L 2,2 Z" fill="#ffffff"/></g>
</svg>"""
    parsed = parse_layered_svg(svg)
    light_first = tuple(sorted(parsed.layers, key=lambda layer: layer.luminance, reverse=True))

    frame_svg = compose_frame_svg(
        parsed,
        ordered_layers=light_first,
        layer_progress={parsed.layers[0].index: 1.0, parsed.layers[1].index: 1.0},
    )

    assert frame_svg.index('id="dark"') < frame_svg.index('id="light"')
