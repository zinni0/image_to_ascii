"""SVG renderer: one <text> per line, one <tspan> per color run."""

from xml.sax.saxutils import escape, quoteattr

from image_to_ascii.colors import validate_css_color
from image_to_ascii.models import CellGrid
from image_to_ascii.renderers.base import Renderer
from image_to_ascii.runs import Run, group_runs


def _tspan(run: Run) -> str:
    text = escape(run.text)
    if run.color is None:
        return f"<tspan>{text}</tspan>"
    red, green, blue = run.color
    return f'<tspan fill="rgb({red},{green},{blue})">{text}</tspan>'


class SvgRenderer(Renderer):
    extension = "svg"

    def __init__(
        self,
        background: str | None = None,
        font_size: float = 10.0,
        char_width: float = 6.0,
        line_height: float = 11.5,
    ) -> None:
        self.background = validate_css_color(background) if background else None
        self.font_size = font_size
        self.char_width = char_width
        self.line_height = line_height

    def render(self, grid: CellGrid, title: str = "") -> str:
        columns = max((len(line) for line in grid), default=0)
        width = columns * self.char_width
        height = len(grid) * self.line_height
        header = (
            '<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" '
            f'viewBox="0 0 {width:g} {height:g}" font-family="monospace" '
            f'font-size="{self.font_size:g}">'
        )
        parts = [header, f"<title>{escape(title)}</title>"]
        if self.background:
            parts.append(
                f'<rect width="100%" height="100%" fill={quoteattr(self.background)}/>'
            )
        parts.extend(self._line(i, line) for i, line in enumerate(grid))
        parts.append("</svg>")
        return "\n".join(parts)

    def _line(self, index: int, line) -> str:
        y = (index + 1) * self.line_height - (self.line_height - self.font_size) / 2
        spans = "".join(_tspan(run) for run in group_runs(line))
        return (
            f'<text x="0" y="{y:g}" textLength="{len(line) * self.char_width:g}" '
            f'lengthAdjust="spacing">{spans}</text>'
        )
