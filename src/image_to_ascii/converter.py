"""Image to cell grid conversion."""

from PIL import Image

from image_to_ascii.models import MAX_CELLS, Cell, CellGrid, Color, ConversionOptions

ALPHA_CUTOFF = 128
LOW_PERCENTILE = 0.02
HIGH_PERCENTILE = 0.98


def brightness(red: int, green: int, blue: int) -> float:
    """Return the luminance in 0..1 (Rec. 601 weights)."""
    return (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0


def _percentile(sorted_values: list[float], fraction: float) -> float:
    return sorted_values[round(fraction * (len(sorted_values) - 1))]


def _stretch_range(values: list[float]) -> tuple[float, float]:
    """Return the 2nd and 98th percentile of values."""
    ordered = sorted(values)
    return _percentile(ordered, LOW_PERCENTILE), _percentile(ordered, HIGH_PERCENTILE)


def stretch_luminance(value: float, low: float, high: float, gamma: float) -> float:
    """Map value from [low, high] onto 0..1, then apply gamma (>1 brightens)."""
    if high > low:
        value = min(1.0, max(0.0, (value - low) / (high - low)))
    return value ** (1.0 / gamma)


class AsciiConverter:
    """Turns an image into a CellGrid according to ConversionOptions."""

    def __init__(self, options: ConversionOptions | None = None) -> None:
        self.options = options or ConversionOptions()

    def load(self, path: str) -> Image.Image:
        with Image.open(path) as image:
            return image.convert("RGBA")

    def resize(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        width_out = self.options.width
        height_out = max(
            1, round((height / width) * width_out * self.options.char_aspect)
        )
        if width_out * height_out > MAX_CELLS:
            raise ValueError(
                f"output would have {width_out * height_out} cells "
                f"(limit {MAX_CELLS}); use a smaller width or a different image"
            )
        return image.resize((width_out, height_out), Image.LANCZOS)

    def to_grid(self, image: Image.Image) -> CellGrid:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        pixels = self._extract_pixels(rgba)
        values = [brightness(*pixel[:3]) for pixel in pixels]
        is_background = self._background_mask(pixels, values)
        values = self._tone(values, is_background)
        cells = self._build_cells(pixels, values, is_background)
        return [cells[y * width : (y + 1) * width] for y in range(height)]

    def convert(self, path: str) -> CellGrid:
        """Load, resize and map the image at path in one step."""
        return self.to_grid(self.resize(self.load(path)))

    @staticmethod
    def _extract_pixels(rgba: Image.Image) -> list[tuple[int, int, int, int]]:
        """Return the RGBA pixels in row-major order."""
        width, height = rgba.size
        access = rgba.load()
        return [access[x, y] for y in range(height) for x in range(width)]

    def _background_mask(
        self, pixels: list[tuple[int, int, int, int]], values: list[float]
    ) -> list[bool]:
        return [
            self._is_background(pixel[3], value)
            for pixel, value in zip(pixels, values, strict=True)
        ]

    def _build_cells(
        self,
        pixels: list[tuple[int, int, int, int]],
        values: list[float],
        is_background: list[bool],
    ) -> list[Cell]:
        return [
            Cell(" ", None) if hidden else self._cell(pixel[:3], value, pixel[3])
            for pixel, value, hidden in zip(pixels, values, is_background, strict=True)
        ]

    def _is_background(self, alpha: int, value: float) -> bool:
        if alpha < ALPHA_CUTOFF:
            return True
        if self.options.invert:
            return value > self.options.background_threshold
        return value < 1.0 - self.options.background_threshold

    def _tone(self, values: list[float], is_background: list[bool]) -> list[float]:
        """Stretch contrast using only the non-background pixels."""
        foreground = [
            v for v, hidden in zip(values, is_background, strict=True) if not hidden
        ]
        if not foreground:
            return values
        low, high = _stretch_range(foreground) if self.options.contrast else (0.0, 1.0)
        return [stretch_luminance(v, low, high, self.options.gamma) for v in values]

    def _cell(self, color: Color, value: float, alpha: int) -> Cell:
        if self.options.invert:
            value = 1.0 - value
        last = len(self.options.ramp) - 1
        index = min(last, max(0, round(value * last)))
        return Cell(self.options.ramp[index], color, round(alpha / 255, 2))
