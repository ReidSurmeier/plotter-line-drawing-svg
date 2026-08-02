from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_leads_to_a_complete_animation_workflow() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    workflow_path = ROOT / "docs" / "animation-workflow.md"

    assert "docs/animation-workflow.md" in readme
    assert workflow_path.exists()

    workflow = workflow_path.read_text(encoding="utf-8")
    for required_term in (
        "alpha_stack_float32.npz",
        "metadata.json",
        "plotter-line-svg",
        "plotter-line-svg-animate",
        "rsvg-convert",
        "ffmpeg",
        "source_files",
        "source_svg_sha256",
        "does not include caller-specific absolute paths",
    ):
        assert required_term in workflow


def test_community_files_and_local_markdown_links_are_complete() -> None:
    required_files = (
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CITATION.cff",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/pull_request_template.md",
        ".github/workflows/ci.yml",
    )
    for relative_path in required_files:
        assert (ROOT / relative_path).exists(), relative_path

    markdown_link = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
    for document in ROOT.glob("*.md"):
        text = document.read_text(encoding="utf-8")
        for target in markdown_link.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_text = target.split("#", 1)[0]
            assert (document.parent / path_text).resolve().exists(), (
                f"{document.relative_to(ROOT)} links to missing {target}"
            )

    for document in (ROOT / "docs").rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        for target in markdown_link.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_text = target.split("#", 1)[0]
            assert (document.parent / path_text).resolve().exists(), (
                f"{document.relative_to(ROOT)} links to missing {target}"
            )


def test_project_resume_packet_matches_the_repository_boundary() -> None:
    required_files = (
        "README.md",
        "PROJECT.md",
        "AGENTS.md",
        "CONTEXT.md",
        "context.toml",
        "docs/adr/0001-keep-generated-manifests-portable.md",
        "docs/ignored-run-custody.md",
        "docs/agents/domain.md",
        "docs/agents/issue-tracker.md",
        "docs/agents/triage-labels.md",
    )
    assert [
        relative_path
        for relative_path in required_files
        if not (ROOT / relative_path).is_file()
    ] == []

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "[PROJECT.md](PROJECT.md)" in readme
    assert "Deployment ownership: none" in readme

    project = (ROOT / "PROJECT.md").read_text(encoding="utf-8")
    for fact in (
        "2e0b3a8e1370a839c55ad70b39b12b14c5b491ed",
        "17 tests",
        "six H.264",
        "GitHub Pages is absent",
        "plotter-separation-rebuild",
        "two byte-identical",
        "21 tests",
        "94e9c8338224b4c299007bb2bc0bdc468eb3ee6040744044478fb9ff799e6af3",
        "5666eee5f8dcf5113ca52f577534ba6daf3971c8fbe71ef9b0bd329da5aeb603",
        "Issue 4 is closed",
    ):
        assert fact in project

    private_home = "/" + "home/reidsurmeier"
    for relative_path in (
        "README.md",
        "PROJECT.md",
        "AGENTS.md",
        "CONTEXT.md",
        "context.toml",
    ):
        assert private_home not in (ROOT / relative_path).read_text(
            encoding="utf-8"
        )


def test_published_export_lineage_is_recorded_without_claiming_rights() -> None:
    provenance = " ".join(
        (ROOT / "docs" / "provenance.md").read_text(encoding="utf-8").split()
    )

    assert "ReidSurmeier/plotter-image-animations" in provenance
    assert (
        "a7bd0d91aface1ccf123401b1f10a253e24e26fa2b0d34811036c78268ba0676"
        in provenance
    )
    assert (
        "d0bb5232b30e8e1ecc57ff5229b1e5fd7a5746ce99d8d61da2fee447c4df040f"
        in provenance
    )
    assert "does not establish publication rights" in provenance
    assert "2026-08-02" in provenance
    assert "authorized to publish the current portrait and bathroom exports" in provenance


def test_ignored_run_custody_is_fixity_addressed_without_publishing_it() -> None:
    custody = (ROOT / "docs" / "ignored-run-custody.md").read_text(
        encoding="utf-8"
    )

    for fact in (
        "290",
        "244,531,468",
        "5d8e06d5681289ee5ca362d34717598905edc1131d83a4705eaacdf3d308d21e",
        "3f6cd69eec452e876b6f4cf2c324c733cdbe7269a7a41917c8d463fa614680e9",
        "94e9c8338224b4c299007bb2bc0bdc468eb3ee6040744044478fb9ff799e6af3",
        "5666eee5f8dcf5113ca52f577534ba6daf3971c8fbe71ef9b0bd329da5aeb603",
        "publication rights remain unresolved",
        "move with the repository",
    ):
        assert fact in custody

    assert "/home/reidsurmeier" not in custody


def test_paper_figure_manifest_contract_is_documented() -> None:
    paper_figures = (ROOT / "docs" / "paper-figures.md").read_text(
        encoding="utf-8"
    )

    assert "paper_figure_manifest.json" in paper_figures
    assert "coverage_manifest_sha256" in paper_figures
    assert "does not record caller-specific absolute paths" in paper_figures
