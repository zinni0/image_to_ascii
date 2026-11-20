"""Renderer registry."""

from image_to_ascii.renderers.base import Renderer
from image_to_ascii.renderers.html import HtmlRenderer
from image_to_ascii.renderers.json import JsonRenderer
from image_to_ascii.renderers.svg import SvgRenderer
from image_to_ascii.renderers.text import TextRenderer

REGISTRY: dict[str, type[Renderer]] = {
    "txt": TextRenderer,
    "html": HtmlRenderer,
    "svg": SvgRenderer,
    "json": JsonRenderer,
}

DEFAULT_FORMAT = "txt"


def get_renderer(name: str, **options) -> Renderer:
    """Instantiate the renderer registered under name."""
    return REGISTRY[name](**options)


def format_for_path(path: str) -> str:
    """Pick a registered format from the file extension, falling back to text."""
    lowered = path.lower()
    for name, renderer in REGISTRY.items():
        if lowered.endswith(f".{renderer.extension}"):
            return name
    return DEFAULT_FORMAT


__all__ = ["REGISTRY", "Renderer", "format_for_path", "get_renderer"]
