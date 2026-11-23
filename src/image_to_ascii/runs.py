"""Grouping of cells into runs of equal color."""

from dataclasses import dataclass

from image_to_ascii.models import Cell, Color


@dataclass(frozen=True)
class Run:
    """Consecutive characters sharing one color (None for spaces)."""

    text: str
    color: Color | None
    alpha: float = 1.0


def _visible_color(cell: Cell) -> Color | None:
    return None if cell.char == " " else cell.color


def group_runs(line: list[Cell], *, with_alpha: bool = False) -> list[Run]:
    """Merge a line into runs; spaces carry no color so they merge freely.

    With with_alpha, cells of different alpha are kept in separate runs.
    """
    runs: list[Run] = []
    for cell in line:
        color = _visible_color(cell)
        alpha = cell.alpha if with_alpha and color is not None else 1.0
        if runs and runs[-1].color == color and runs[-1].alpha == alpha:
            runs[-1] = Run(runs[-1].text + cell.char, color, alpha)
        else:
            runs.append(Run(cell.char, color, alpha))
    return runs
