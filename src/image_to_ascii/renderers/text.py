"""Plain text renderer."""

from image_to_ascii.models import CellGrid
from image_to_ascii.renderers.base import Renderer


class TextRenderer(Renderer):
    extension = "txt"

    def render(self, grid: CellGrid, title: str = "") -> str:
        return "\n".join("".join(cell.char for cell in line) for line in grid)
