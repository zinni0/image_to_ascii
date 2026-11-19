"""Image to cell grid conversion."""

from PIL import Image

from image_to_ascii.models import MAX_CELLS, Cell, CellGrid, ConversionOptions


def brightness(red: int, green: int, blue: int) -> float:
    """Return the luminance in 0..1 (Rec. 601 weights)."""
    return (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0


class AsciiConverter:
    """Turns an image into a CellGrid according to ConversionOptions."""

    def __init__(self, options: ConversionOptions | None = None) -> None:
        self.options = options or ConversionOptions()

    def load(self, path: str) -> Image.Image:
        with Image.open(path) as image:
            return image.convert("RGB")

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
        pixels = image.load()
        width, height = image.size
        return [[self._cell(pixels[x, y]) for x in range(width)] for y in range(height)]

    def convert(self, path: str) -> CellGrid:
        """Load, resize and map the image at path in one step."""
        return self.to_grid(self.resize(self.load(path)))

    def _cell(self, color: tuple[int, int, int]) -> Cell:
        value = brightness(*color)
        if self.options.invert:
            value = 1.0 - value
        last = len(self.options.ramp) - 1
        index = min(last, max(0, round(value * last)))
        return Cell(self.options.ramp[index], color)
