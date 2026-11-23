import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _project() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as f:
        return tomllib.load(f)["project"]


def test_license_declared_and_file_exists():
    project = _project()
    assert project["license"] == "MIT"
    assert project["license-files"] == ["LICENSE"]
    assert (ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")


def test_description_is_not_placeholder():
    description = _project()["description"]
    assert description
    assert "Add your description here" not in description


def test_ci_workflow_runs_lint_format_and_tests():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    for command in (
        "uv sync",
        "uv run ruff check",
        "uv run ruff format --check",
        "uv run pytest -q",
    ):
        assert command in ci
    assert re.search(r"^  push:\n    branches: \[main, develop\]$", ci, re.MULTILINE)
    assert re.search(r"^  pull_request:", ci, re.MULTILINE)
