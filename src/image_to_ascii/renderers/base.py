"""Renderer interface."""

from abc import ABC, abstractmethod

from image_to_ascii.models import CellGrid


class Renderer(ABC):
    """Turns a CellGrid into the text of one output format."""

    extension: str

    @abstractmethod
    def render(self, grid: CellGrid, title: str) -> str: ...
