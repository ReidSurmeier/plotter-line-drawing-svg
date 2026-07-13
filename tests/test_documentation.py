from __future__ import annotations

from pathlib import Path
import re


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
