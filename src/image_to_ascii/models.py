"""Plain data types shared by the converter and the renderers."""

from dataclasses import dataclass

DEFAULT_RAMP = " .:-=+*#%@"
DEFAULT_CHAR_ASPECT = 0.52
MAX_WIDTH = 2000
MAX_CELLS = 2_000_000

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Cell:
    """One output character together with the color of its source pixel."""

    char: str
    color: Color


CellGrid = list[list[Cell]]


@dataclass(frozen=True)
class ConversionOptions:
    """Settings for turning an image into a cell grid.

    ramp is ordered sparse to dense. char_aspect compensates for monospace
    cells being taller than wide. invert maps dark pixels to dense characters.
    """

    width: int = 100
    invert: bool = True
    ramp: str = DEFAULT_RAMP
    char_aspect: float = DEFAULT_CHAR_ASPECT

    def __post_init__(self) -> None:
        if not 1 <= self.width <= MAX_WIDTH:
            raise ValueError(f"width must be between 1 and {MAX_WIDTH}")
        if self.char_aspect <= 0:
            raise ValueError("char_aspect must be positive")
