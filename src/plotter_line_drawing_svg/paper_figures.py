from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from plotter_line_drawing_svg.markmaking import InkSet, load_alpha_stack, load_inkset


METHOD_COLORS = {"regen": "#1870b8", "prune": "#c94232"}
RUNG_ORDER = ["full", "25%", "6.25%", "1.5625%"]
FIGURE_NAMES = [
    "deltaE_vs_budget",
    "per_ink_coverage_error",
    "gamut_shrink",
    "deltaE_heatmap",
    "ink_load_vs_budget",
    "hue_rotation_error",
    "lab_3d_color_solid",
    "cie1976_uv_chromaticity",
    "dot_gain_coverage_curve",
    "hue_angle_error_rose",
]


@dataclass(frozen=True)
class ProofRecord:
    method: str
    rung: str
    proof_dir: Path
    rendered_path: Path
    target_path: Path
    metadata: dict[str, Any]
    paths_per_plate: tuple[int, ...]
    total_paths: int
    budget_scale: float


def main() -> int:
    parser = argparse.ArgumentParser(description="Build paper figures for regen vs prune markmaking.")
    parser.add_argument("--jax-dir", type=Path, required=True)
    parser.add_argument("--regen-root", type=Path, required=True)
    parser.add_argument("--prune-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-side", type=int, default=900)
    parser.add_argument("--critical-scale", type=float, default=0.0625)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    alpha_stack = load_alpha_stack(args.jax_dir)
    inkset = load_inkset(args.jax_dir)
    records = collect_records({"regen": args.regen_root, "prune": args.prune_root})
    if not records:
        raise ValueError("no proof records found")

    figure_delta_e_vs_budget(records, args.out / "F1_deltaE_vs_budget.pdf", max_side=args.max_side)
    figure_per_ink_coverage_error(
        records,
        alpha_stack,
        inkset,
        args.out / "F2_per_ink_coverage_error.pdf",
    )
    figure_gamut_shrink(records, args.out / "F3_gamut_shrink.pdf", max_side=args.max_side)
    figure_delta_e_heatmap(
        records,
        args.out / "F4_deltaE_heatmap.pdf",
        critical_scale=args.critical_scale,
        max_side=args.max_side,
    )
    figure_ink_load_vs_budget(records, inkset, args.out / "F5_ink_load_vs_budget.pdf")
    figure_hue_rotation_error(
        records,
        args.out / "F6_hue_rotation_error.pdf",
        critical_scale=args.critical_scale,
        max_side=args.max_side,
    )
    figure_lab_3d_color_solid(
        records,
        args.out / "F7_lab_3d_color_solid.pdf",
        critical_scale=args.critical_scale,
        max_side=args.max_side,
    )
    figure_cie1976_uv_chromaticity(
        records,
        args.out / "F8_cie1976_uv_chromaticity.pdf",
        critical_scale=args.critical_scale,
        max_side=args.max_side,
    )
    figure_dot_gain_coverage_curve(records, inkset, args.out / "F9_dot_gain_coverage_curve.pdf")
    figure_hue_angle_error_rose(
        records,
        args.out / "F10_hue_angle_error_rose.pdf",
        critical_scale=args.critical_scale,
        max_side=args.max_side,
    )

    summary = {
        "records": [
            {
                "method": record.method,
                "rung": record.rung,
                "total_paths": record.total_paths,
                "budget_scale": record.budget_scale,
                "proof_dir": str(record.proof_dir),
            }
            for record in records
        ],
        "figures": [f"F{i}_{name}.pdf" for i, name in enumerate(FIGURE_NAMES, start=1)],
    }
    (args.out / "paper_figure_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def collect_records(roots: dict[str, Path]) -> list[ProofRecord]:
    records: list[ProofRecord] = []
    for method, root in roots.items():
        for proof_dir in sorted(root.iterdir()):
            if not proof_dir.is_dir():
                continue
            metadata_path = proof_dir / "coverage_svg_metadata.json"
            rendered = proof_dir / "actual_svg_crop.png"
            target = proof_dir / "target_upscaled.png"
            if not (metadata_path.exists() and rendered.exists() and target.exists()):
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            counts = _paths_per_plate(metadata)
            records.append(
                ProofRecord(
                    method=method,
                    rung=_rung_label(proof_dir.name, metadata),
                    proof_dir=proof_dir,
                    rendered_path=rendered,
                    target_path=target,
                    metadata=metadata,
                    paths_per_plate=tuple(counts),
                    total_paths=int(sum(counts)),
                    budget_scale=_budget_scale(proof_dir.name, metadata),
                )
            )
    return sorted(records, key=lambda record: (record.method, -record.total_paths))


def figure_delta_e_vs_budget(records: list[ProofRecord], out: Path, *, max_side: int) -> None:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for method in ("regen", "prune"):
        method_records = sorted(_method_records(records, method), key=lambda item: item.total_paths)
        xs: list[int] = []
        medians: list[float] = []
        p25: list[float] = []
        p75: list[float] = []
        for record in method_records:
            delta = delta_e_for_record(record, max_side=max_side)
            xs.append(record.total_paths)
            medians.append(float(np.median(delta)))
            p25.append(float(np.percentile(delta, 25)))
            p75.append(float(np.percentile(delta, 75)))
        color = METHOD_COLORS[method]
        ax.plot(xs, medians, color=color, lw=2.4, label=method)
        ax.plot(xs, medians, color=color, lw=0.8, alpha=0.35)
        ax.fill_between(xs, p25, p75, color=color, alpha=0.16, linewidth=0)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xlabel("path count")
    ax.set_ylabel("median ΔE2000")
    ax.legend(frameon=False)
    ax.grid(True, which="both", alpha=0.22)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_per_ink_coverage_error(
    records: list[ProofRecord],
    alpha_stack: NDArray[np.float32],
    inkset: InkSet,
    out: Path,
) -> None:
    plt = _plt()
    target_load = target_coverage_load(alpha_stack, mark_opacity=0.55)
    ink_count = len(inkset.inks)
    cols = 3
    rows = int(math.ceil(ink_count / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(11, rows * 2.35), squeeze=False)
    ordered = sorted(records, key=lambda record: (-record.budget_scale, record.method))
    rungs = [rung for rung in RUNG_ORDER if any(record.rung == rung for record in ordered)]
    x = np.arange(len(rungs))
    width = 0.36
    for ink_index, ink in enumerate(inkset.inks):
        ax = axes[ink_index // cols][ink_index % cols]
        color = _rgb01_tuple(ink.rgb)
        for method, offset in (("regen", -width / 2), ("prune", width / 2)):
            values = []
            for rung in rungs:
                record = _record_for(records, method, rung)
                load = path_area_load(record)[ink_index] if record else 0.0
                values.append(abs(load - target_load[ink_index]))
            ax.bar(x + offset, values, width=width, color=color, edgecolor=METHOD_COLORS[method], linewidth=1.3)
        ax.set_title(ink.label, fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(rungs, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel("|coverage error|", fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="y", alpha=0.2)
    for idx in range(ink_count, rows * cols):
        axes[idx // cols][idx % cols].axis("off")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_gamut_shrink(records: list[ProofRecord], out: Path, *, max_side: int) -> None:
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8), sharex=True, sharey=True)
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        method_records = sorted(_method_records(records, method), key=lambda item: -item.budget_scale)
        target_rgb = load_rgb01(method_records[0].target_path, max_side=max_side)
        target_ab = lab_ab_sample(target_rgb)
        _plot_hull(ax, target_ab, color="#111111", lw=1.5, alpha=0.55, label="target")
        cmap = plt.get_cmap("viridis")
        for idx, record in enumerate(method_records):
            rgb = load_rgb01(record.rendered_path, max_side=max_side)
            ab = lab_ab_sample(rgb)
            _plot_hull(
                ax,
                ab,
                color=cmap(idx / max(len(method_records) - 1, 1)),
                lw=1.4,
                alpha=0.85,
                label=record.rung,
            )
        ax.set_title(method)
        ax.set_xlabel("Lab a*")
        ax.grid(True, alpha=0.2)
    axes[0].set_ylabel("Lab b*")
    axes[1].legend(frameon=False, fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_delta_e_heatmap(
    records: list[ProofRecord],
    out: Path,
    *,
    critical_scale: float,
    max_side: int,
) -> None:
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.8), sharex=True, sharey=True)
    images = []
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        record = closest_scale_record(records, method, critical_scale)
        target = load_rgb01(record.target_path, max_side=max_side)
        rendered = load_rgb01(record.rendered_path, max_side=max_side)
        delta = delta_e(target, rendered)
        underlay = np.clip(target * 0.25 + 0.75, 0.0, 1.0)
        ax.imshow(underlay)
        image = ax.imshow(np.clip(delta, 0, 15), cmap="magma", vmin=0, vmax=15, alpha=0.82)
        ax.set_title(f"{method} {record.rung}")
        ax.axis("off")
        images.append(image)
    fig.colorbar(images[-1], ax=axes, fraction=0.03, pad=0.02, label="ΔE2000")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_ink_load_vs_budget(records: list[ProofRecord], inkset: InkSet, out: Path) -> None:
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharey=True)
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        method_records = sorted(_method_records(records, method), key=lambda item: -item.budget_scale)
        labels = [record.rung for record in method_records]
        bottoms = np.zeros(len(method_records), dtype=np.float64)
        for ink_index, ink in enumerate(inkset.inks):
            values = np.asarray([record.paths_per_plate[ink_index] for record in method_records], dtype=np.float64)
            ax.bar(labels, values, bottom=bottoms, color=_rgb01_tuple(ink.rgb), width=0.72)
            bottoms += values
        ax.set_title(method)
        ax.set_xlabel("budget rung")
        ax.tick_params(axis="x", rotation=35)
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("total mark count")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_hue_rotation_error(
    records: list[ProofRecord],
    out: Path,
    *,
    critical_scale: float,
    max_side: int,
) -> None:
    plt = _plt()
    from matplotlib.colors import rgb_to_hsv

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), subplot_kw={"projection": "polar"})
    bins = np.linspace(-np.pi, np.pi, 49)
    width = bins[1] - bins[0]
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        record = closest_scale_record(records, method, critical_scale)
        target = load_rgb01(record.target_path, max_side=max_side)
        rendered = load_rgb01(record.rendered_path, max_side=max_side)
        delta = delta_e(target, rendered)
        target_h = rgb_to_hsv(target)[..., 0]
        rendered_h = rgb_to_hsv(rendered)[..., 0]
        rotation = ((target_h - rendered_h + 0.5) % 1.0 - 0.5) * 2.0 * np.pi
        rotation = rotation[delta > 5.0]
        hist, edges = np.histogram(rotation, bins=bins)
        ax.bar(edges[:-1], hist, width=width, align="edge", color=METHOD_COLORS[method], alpha=0.72)
        ax.set_title(f"{method} {record.rung}")
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_lab_3d_color_solid(
    records: list[ProofRecord],
    out: Path,
    *,
    critical_scale: float,
    max_side: int,
) -> None:
    plt = _plt()
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    regen = closest_scale_record(records, "regen", critical_scale)
    prune = closest_scale_record(records, "prune", critical_scale)
    target_lab = lab_sample(load_rgb01(regen.target_path, max_side=max_side), max_samples=3500)
    regen_lab = lab_sample(load_rgb01(regen.rendered_path, max_side=max_side), max_samples=3500)
    prune_lab = lab_sample(load_rgb01(prune.rendered_path, max_side=max_side), max_samples=3500)

    fig = plt.figure(figsize=(8.5, 6.4))
    ax = fig.add_subplot(111, projection="3d")
    for label, lab, color, alpha in (
        ("target", target_lab, "#111111", 0.10),
        ("regen", regen_lab, METHOD_COLORS["regen"], 0.22),
        ("prune", prune_lab, METHOD_COLORS["prune"], 0.20),
    ):
        plot_points = lab_plot_points(lab)
        faces = convex_hull_faces_3d(plot_points)
        if faces:
            collection = Poly3DCollection(faces, facecolor=color, edgecolor=color, linewidth=0.22, alpha=alpha)
            ax.add_collection3d(collection)
        stride = max(1, len(plot_points) // 850)
        ax.scatter(
            plot_points[::stride, 0],
            plot_points[::stride, 1],
            plot_points[::stride, 2],
            s=1.2,
            color=color,
            alpha=0.18,
            label=label,
        )
    all_points = lab_plot_points(np.vstack([target_lab, regen_lab, prune_lab]))
    ax.set_xlim(*axis_limits(all_points[:, 0]))
    ax.set_ylim(*axis_limits(all_points[:, 1]))
    ax.set_zlim(*axis_limits(all_points[:, 2]))
    ax.set_box_aspect(
        (
            float(np.ptp(all_points[:, 0])),
            float(np.ptp(all_points[:, 1])),
            float(np.ptp(all_points[:, 2])),
        )
    )
    ax.set_xlabel("Lab a*")
    ax.set_ylabel("Lab b*")
    ax.set_zlabel("Lab L*")
    ax.set_title(f"CIELAB color solid at {regen.rung}")
    ax.view_init(elev=22, azim=-52)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_cie1976_uv_chromaticity(
    records: list[ProofRecord],
    out: Path,
    *,
    critical_scale: float,
    max_side: int,
) -> None:
    plt = _plt()
    regen = closest_scale_record(records, "regen", critical_scale)
    prune = closest_scale_record(records, "prune", critical_scale)
    target_uv = uv_prime_sample(load_rgb01(regen.target_path, max_side=max_side))
    regen_uv = uv_prime_sample(load_rgb01(regen.rendered_path, max_side=max_side))
    prune_uv = uv_prime_sample(load_rgb01(prune.rendered_path, max_side=max_side))

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    _plot_hull(ax, target_uv, color="#111111", lw=1.8, alpha=0.75, label="target")
    _plot_hull(ax, regen_uv, color=METHOD_COLORS["regen"], lw=2.1, alpha=0.88, label=f"regen {regen.rung}")
    _plot_hull(ax, prune_uv, color=METHOD_COLORS["prune"], lw=2.1, alpha=0.88, label=f"prune {prune.rung}")
    ax.scatter(target_uv[:: max(1, len(target_uv) // 1200), 0], target_uv[:: max(1, len(target_uv) // 1200), 1], s=1, color="#111111", alpha=0.05)
    ax.set_xlabel("CIE 1976 u'")
    ax.set_ylabel("CIE 1976 v'")
    ax.set_title("CIE 1976 u'v' chromaticity hull")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.22)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_dot_gain_coverage_curve(records: list[ProofRecord], inkset: InkSet, out: Path) -> None:
    plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), sharex=True, sharey=True)
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        method_records = sorted(_method_records(records, method), key=lambda record: record.budget_scale)
        nominal_by_record = [path_area_load(record) for record in method_records]
        measured_by_record = [measured_plate_coverage_load(record, inkset) for record in method_records]
        for ink_index, ink in enumerate(inkset.inks):
            x = np.asarray([load[ink_index] for load in nominal_by_record], dtype=np.float64)
            y = np.asarray([load[ink_index] for load in measured_by_record], dtype=np.float64)
            ax.plot(x, y, color=_rgb01_tuple(ink.rgb), lw=1.1, alpha=0.78)
            ax.scatter(x, y, color=_rgb01_tuple(ink.rgb), edgecolor="#111111", linewidth=0.25, s=22, alpha=0.92)
        max_axis = max(0.01, *(float(np.max(load)) for load in nominal_by_record + measured_by_record))
        ax.plot([0, max_axis], [0, max_axis], color="#111111", lw=0.9, alpha=0.42, linestyle="--")
        ax.set_title(method)
        ax.set_xlabel("nominal lozenge coverage")
        ax.grid(True, alpha=0.22)
    axes[0].set_ylabel("measured rendered coverage")
    fig.suptitle("Dot gain / coverage curve by ink", y=0.99)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def figure_hue_angle_error_rose(
    records: list[ProofRecord],
    out: Path,
    *,
    critical_scale: float,
    max_side: int,
) -> None:
    plt = _plt()
    from skimage.color import rgb2lab

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), subplot_kw={"projection": "polar"})
    bins = np.linspace(-np.pi, np.pi, 49)
    width = bins[1] - bins[0]
    for ax, method in zip(axes, ("regen", "prune"), strict=True):
        record = closest_scale_record(records, method, critical_scale)
        target = load_rgb01(record.target_path, max_side=max_side)
        rendered = load_rgb01(record.rendered_path, max_side=max_side)
        target_lab = rgb2lab(target)
        rendered_lab = rgb2lab(rendered)
        target_angle = np.arctan2(target_lab[..., 2], target_lab[..., 1])
        rendered_angle = np.arctan2(rendered_lab[..., 2], rendered_lab[..., 1])
        target_chroma = np.hypot(target_lab[..., 1], target_lab[..., 2])
        delta = delta_e(target, rendered)
        rotation = ((target_angle - rendered_angle + np.pi) % (2.0 * np.pi)) - np.pi
        rotation = rotation[(delta > 5.0) & (target_chroma > 5.0)]
        hist, edges = np.histogram(rotation, bins=bins)
        ax.bar(edges[:-1], hist, width=width, align="edge", color=METHOD_COLORS[method], alpha=0.72)
        ax.set_title(f"{method} {record.rung}")
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
    fig.suptitle("Lab hue-angle error rose")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def delta_e_for_record(record: ProofRecord, *, max_side: int) -> NDArray[np.float32]:
    return delta_e(load_rgb01(record.target_path, max_side=max_side), load_rgb01(record.rendered_path, max_side=max_side))


def delta_e(target: NDArray[np.float32], rendered: NDArray[np.float32]) -> NDArray[np.float32]:
    from skimage.color import deltaE_ciede2000, rgb2lab

    if target.shape != rendered.shape:
        rendered_img = Image.fromarray((rendered * 255 + 0.5).astype(np.uint8), "RGB")
        rendered_img = rendered_img.resize((target.shape[1], target.shape[0]), Image.Resampling.LANCZOS)
        rendered = np.asarray(rendered_img, dtype=np.float32) / 255.0
    return deltaE_ciede2000(rgb2lab(target), rgb2lab(rendered)).astype(np.float32)


def lab_ab_sample(rgb: NDArray[np.float32], *, max_samples: int = 9000) -> NDArray[np.float32]:
    from skimage.color import rgb2lab

    lab = rgb2lab(rgb).reshape(-1, 3)
    if lab.shape[0] > max_samples:
        step = int(math.ceil(lab.shape[0] / max_samples))
        lab = lab[::step]
    return lab[:, 1:3].astype(np.float32)


def lab_sample(rgb: NDArray[np.float32], *, max_samples: int = 9000) -> NDArray[np.float32]:
    from skimage.color import rgb2lab

    lab = rgb2lab(rgb).reshape(-1, 3)
    if lab.shape[0] > max_samples:
        step = int(math.ceil(lab.shape[0] / max_samples))
        lab = lab[::step]
    return lab.astype(np.float32)


def lab_plot_points(lab: NDArray[np.float32]) -> NDArray[np.float32]:
    """Return Lab samples in plotting order: x=a*, y=b*, z=L*."""
    return lab[:, [1, 2, 0]].astype(np.float32)


def axis_limits(values: NDArray[np.float32], *, pad_fraction: float = 0.08) -> tuple[float, float]:
    low = float(np.min(values))
    high = float(np.max(values))
    pad = max((high - low) * pad_fraction, 1.0)
    return low - pad, high + pad


def uv_prime_sample(rgb: NDArray[np.float32], *, max_samples: int = 9000) -> NDArray[np.float32]:
    from skimage.color import rgb2xyz

    xyz = rgb2xyz(rgb).reshape(-1, 3)
    if xyz.shape[0] > max_samples:
        step = int(math.ceil(xyz.shape[0] / max_samples))
        xyz = xyz[::step]
    x = xyz[:, 0]
    y = xyz[:, 1]
    z = xyz[:, 2]
    denom = x + 15.0 * y + 3.0 * z
    valid = denom > 1e-8
    u = np.zeros_like(x)
    v = np.zeros_like(y)
    u[valid] = 4.0 * x[valid] / denom[valid]
    v[valid] = 9.0 * y[valid] / denom[valid]
    return np.column_stack([u, v]).astype(np.float32)


def convex_hull_faces_3d(points: NDArray[np.float32]) -> list[NDArray[np.float32]]:
    from scipy.spatial import ConvexHull, QhullError

    if points.shape[0] < 4:
        return []
    try:
        hull = ConvexHull(points)
    except QhullError:
        return []
    return [points[simplex] for simplex in hull.simplices]


def target_coverage_load(alpha_stack: NDArray[np.float32], *, mark_opacity: float) -> NDArray[np.float64]:
    coverage = np.clip(alpha_stack / max(mark_opacity, 1e-6), 0.0, 0.96)
    return coverage.reshape(coverage.shape[0], -1).mean(axis=1).astype(np.float64)


def path_area_load(record: ProofRecord) -> NDArray[np.float64]:
    svg = (record.proof_dir / "master_coverage_svg.svg").read_text(encoding="utf-8")
    source_match = re.search(r'data-source-px="(\d+)\s+(\d+)"', svg)
    if not source_match:
        raise ValueError(f"missing data-source-px in {record.proof_dir}")
    width = int(source_match.group(1))
    height = int(source_match.group(2))
    loads = np.zeros(len(record.paths_per_plate), dtype=np.float64)
    group_pattern = re.compile(r"<g\b[^>]*>(.*?)</g>", re.DOTALL)
    path_pattern = re.compile(r'<path[^>]* d="([^"]+)"[^>]*fill-opacity="([0-9.]+)"', re.DOTALL)
    for plate, group_match in enumerate(group_pattern.finditer(svg)):
        if plate >= loads.size:
            break
        for d, opacity in path_pattern.findall(group_match.group(1)):
            loads[plate] += polygon_area_from_path(d) * float(opacity)
    return loads / float(width * height)


def polygon_area_from_path(d: str) -> float:
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", d)]
    points = list(zip(numbers[0::2], numbers[1::2], strict=False))
    if len(points) < 3:
        return 0.0
    area = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1], strict=True):
        area += x0 * y1 - x1 * y0
    return abs(area) * 0.5


def measured_plate_coverage_load(record: ProofRecord, inkset: InkSet) -> NDArray[np.float64]:
    rsvg = shutil.which("rsvg-convert")
    if rsvg is None:
        return path_area_load(record)
    plate_dir = record.proof_dir / "plate_svgs"
    plate_paths = sorted(plate_dir.glob("*.svg"))
    if not plate_paths:
        return path_area_load(record)
    loads = np.zeros(len(inkset.inks), dtype=np.float64)
    with tempfile.TemporaryDirectory(prefix="plotter-line-plate-raster-") as tmp_name:
        tmp = Path(tmp_name)
        for index, ink in enumerate(inkset.inks):
            if index >= len(plate_paths):
                continue
            svg_path = plate_paths[index]
            png_path = tmp / f"plate_{index:02d}.png"
            subprocess.run([rsvg, "-w", "900", str(svg_path), "-o", str(png_path)], check=True, stdout=subprocess.DEVNULL)
            rgb = crop_artwork_from_rendered_svg(png_path, svg_path)
            loads[index] = infer_plate_alpha(rgb, ink.rgb, inkset.paper_rgb).mean()
    return loads


def crop_artwork_from_rendered_svg(png_path: Path, svg_path: Path) -> NDArray[np.float32]:
    svg = svg_path.read_text(encoding="utf-8")
    view_match = re.search(r'viewBox="0 0 ([0-9.]+) ([0-9.]+)"', svg)
    rect_match = re.search(
        r'id="artwork_bounds" x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" height="([0-9.]+)"',
        svg,
    )
    image = Image.open(png_path).convert("RGB")
    if not (view_match and rect_match):
        return np.asarray(image, dtype=np.float32) / 255.0
    page_w = float(view_match.group(1))
    page_h = float(view_match.group(2))
    rect_x, rect_y, rect_w, rect_h = [float(rect_match.group(i)) for i in range(1, 5)]
    px_w, px_h = image.size
    crop_box = (
        int(round(rect_x / page_w * px_w)),
        int(round(rect_y / page_h * px_h)),
        int(round((rect_x + rect_w) / page_w * px_w)),
        int(round((rect_y + rect_h) / page_h * px_h)),
    )
    return np.asarray(image.crop(crop_box), dtype=np.float32) / 255.0


def infer_plate_alpha(
    rgb: NDArray[np.float32],
    ink_rgb: tuple[int, int, int],
    paper_rgb: tuple[int, int, int],
) -> NDArray[np.float32]:
    paper = np.asarray(paper_rgb, dtype=np.float32) / 255.0
    ink = np.asarray(ink_rgb, dtype=np.float32) / 255.0
    direction = paper - ink
    denom = float(np.dot(direction, direction))
    if denom <= 1e-8:
        return np.zeros(rgb.shape[:2], dtype=np.float32)
    alpha = np.tensordot(paper - rgb, direction, axes=([-1], [0])) / denom
    return np.clip(alpha, 0.0, 1.0).astype(np.float32)


def closest_scale_record(records: list[ProofRecord], method: str, target_scale: float) -> ProofRecord:
    method_records = _method_records(records, method)
    if not method_records:
        raise ValueError(f"no records for {method}")
    return min(method_records, key=lambda record: abs(math.log(max(record.budget_scale, 1e-9) / target_scale)))


def load_rgb01(path: Path, *, max_side: int) -> NDArray[np.float32]:
    image = Image.open(path).convert("RGB")
    if max_side > 0:
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return np.asarray(image, dtype=np.float32) / 255.0


def _plot_hull(ax: Any, points: NDArray[np.float32], *, color: Any, lw: float, alpha: float, label: str) -> None:
    from scipy.spatial import ConvexHull, QhullError

    if points.shape[0] < 3:
        ax.scatter(points[:, 0], points[:, 1], s=2, color=color, alpha=alpha, label=label)
        return
    try:
        hull = ConvexHull(points)
    except QhullError:
        ax.scatter(points[:, 0], points[:, 1], s=2, color=color, alpha=alpha, label=label)
        return
    vertices = np.append(hull.vertices, hull.vertices[0])
    ax.plot(points[vertices, 0], points[vertices, 1], color=color, lw=lw, alpha=alpha, label=label)


def _paths_per_plate(metadata: dict[str, Any]) -> list[int]:
    paths = metadata["paths"]
    if "paths_per_plate_after_retention" in paths:
        return [int(v) for v in paths["paths_per_plate_after_retention"]]
    return [int(v) for v in paths["paths_per_plate"]]


def _budget_scale(name: str, metadata: dict[str, Any]) -> float:
    paths = metadata["paths"]
    baseline = paths.get("baseline_paths_per_plate") or paths.get("paths_per_plate_before_retention")
    counts = paths.get("paths_per_plate") or paths.get("paths_per_plate_after_retention")
    if baseline and counts:
        return float(sum(counts) / max(sum(baseline), 1))
    if "full" in name:
        return 1.0
    return 1.0


def _rung_label(name: str, metadata: dict[str, Any]) -> str:
    scale = _budget_scale(name, metadata)
    if scale > 0.85:
        return "full"
    if abs(scale - 0.25) < 0.05:
        return "25%"
    if abs(scale - 0.0625) < 0.018:
        return "6.25%"
    if abs(scale - 0.015625) < 0.008:
        return "1.5625%"
    return f"{scale * 100:.2f}%"


def _method_records(records: list[ProofRecord], method: str) -> list[ProofRecord]:
    return [record for record in records if record.method == method]


def _record_for(records: list[ProofRecord], method: str, rung: str) -> ProofRecord | None:
    candidates = [record for record in records if record.method == method and record.rung == rung]
    return candidates[0] if candidates else None


def _rgb01_tuple(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def _plt() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


if __name__ == "__main__":
    raise SystemExit(main())
