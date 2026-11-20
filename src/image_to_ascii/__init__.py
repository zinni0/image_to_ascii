"""Convert images to ASCII art as text, HTML, SVG or JSON."""

from image_to_ascii.converter import AsciiConverter
from image_to_ascii.models import Cell, CellGrid, ConversionOptions
from image_to_ascii.renderers import REGISTRY, Renderer, get_renderer


def convert(path: str, options: ConversionOptions | None = None) -> CellGrid:
    """Convert the image at path into a cell grid."""
    return AsciiConverter(options).convert(path)


__all__ = [
    "REGISTRY",
    "AsciiConverter",
    "Cell",
    "CellGrid",
    "ConversionOptions",
    "Renderer",
    "convert",
    "get_renderer",
]
