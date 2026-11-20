"""JSON renderer: rows of [text, "#rrggbb" | null] runs, see schema/."""

import json
from importlib.metadata import PackageNotFoundError, version

from image_to_ascii.models import CellGrid
from image_to_ascii.renderers.base import Renderer
from image_to_ascii.runs import Run, group_runs

SCHEMA_VERSION = 1


def _run_json(run: Run) -> list:
    if run.color is None:
        return [run.text, None]
    red, green, blue = run.color
    return [run.text, f"#{red:02x}{green:02x}{blue:02x}"]


def generator_name() -> str:
    try:
        return f"image-to-ascii {version('image-to-ascii')}"
    except PackageNotFoundError:
        return "image-to-ascii unknown"


class JsonRenderer(Renderer):
    extension = "json"

    def render(self, grid: CellGrid, title: str = "") -> str:
        document = {
            "schemaVersion": SCHEMA_VERSION,
            "width": max((len(line) for line in grid), default=0),
            "height": len(grid),
            "generator": generator_name(),
            "rows": [[_run_json(run) for run in group_runs(line)] for line in grid],
        }
        return json.dumps(document, ensure_ascii=False, separators=(",", ":"))
