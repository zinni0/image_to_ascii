"""Plain data types shared by the converter and the renderers."""

import math
from dataclasses import dataclass

RAMP_PRESETS = {
    "classic": " .:-=+*#%@",
    "blocks": " ░▒▓█",
    "minimal": " .:#",
}
DEFAULT_RAMP = RAMP_PRESETS["classic"]
DEFAULT_CHAR_ASPECT = 0.52
DEFAULT_WIDTH = 200
DEFAULT_BACKGROUND_THRESHOLD = 0.94
MAX_WIDTH = 2000
MAX_CELLS = 2_000_000

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Cell:
    """One output character together with the color of its source pixel."""

    char: str
    color: Color | None
    alpha: float = 1.0


CellGrid = list[list[Cell]]


@dataclass(frozen=True)
class ConversionOptions:
    """Settings for turning an image into a cell grid.

    ramp is ordered sparse to dense. char_aspect compensates for monospace
    cells being taller than wide. invert maps dark pixels to dense characters.
    background_threshold (0..1) turns near-background pixels into spaces: with
    invert these are bright pixels above the threshold, otherwise dark pixels
    below 1 - threshold; 1.0 disables the detection. contrast enables
    percentile autocontrast over the non-background pixels; gamma > 1 brightens
    midtones.
    """

    width: int = DEFAULT_WIDTH
    invert: bool = True
    ramp: str = DEFAULT_RAMP
    char_aspect: float = DEFAULT_CHAR_ASPECT
    background_threshold: float = DEFAULT_BACKGROUND_THRESHOLD
    contrast: bool = True
    gamma: float = 1.0

    def __post_init__(self) -> None:
        if not 1 <= self.width <= MAX_WIDTH:
            raise ValueError(f"width must be between 1 and {MAX_WIDTH}")
        if not self.ramp:
            raise ValueError("ramp must not be empty")
        if not math.isfinite(self.char_aspect) or self.char_aspect <= 0:
            raise ValueError("char_aspect must be a finite number greater than 0")
        if not 0.0 <= self.background_threshold <= 1.0:
            raise ValueError("background_threshold must be between 0 and 1")
        if not math.isfinite(self.gamma) or self.gamma <= 0:
            raise ValueError("gamma must be a finite number greater than 0")
