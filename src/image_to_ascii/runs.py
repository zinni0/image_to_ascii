"""Grouping of cells into runs of equal color."""

from dataclasses import dataclass

from image_to_ascii.models import Cell, Color


@dataclass(frozen=True)
class Run:
    """Consecutive characters sharing one color (None for spaces)."""

    text: str
    color: Color | None


def _visible_color(cell: Cell) -> Color | None:
    return None if cell.char == " " else cell.color


def group_runs(line: list[Cell]) -> list[Run]:
    """Merge a line into runs; spaces carry no color so they merge freely."""
    runs: list[Run] = []
    for cell in line:
        color = _visible_color(cell)
        if runs and runs[-1].color == color:
            runs[-1] = Run(runs[-1].text + cell.char, color)
        else:
            runs.append(Run(cell.char, color))
    return runs
