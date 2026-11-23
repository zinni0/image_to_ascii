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
