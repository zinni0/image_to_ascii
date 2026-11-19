"""HTML renderer: full page or embeddable fragment."""

from html import escape
from typing import Literal

from image_to_ascii.colors import validate_css_color
from image_to_ascii.models import CellGrid
from image_to_ascii.renderers.base import Renderer
from image_to_ascii.runs import Run, group_runs

Mode = Literal["page", "fragment"]

PAGE_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ background:{background}; margin:0; padding:{padding}px; }}
  pre {{ font-family:'IBM Plex Mono','Courier New',monospace; font-size:{font_size}px; line-height:1.0;
         white-space:pre; margin:0; }}
</style>
</head>
<body>
{pre}
</body>
</html>"""


def _run_html(run: Run) -> str:
    text = escape(run.text, quote=False)
    if run.color is None:
        return text
    red, green, blue = run.color
    return f'<span style="color:rgb({red}, {green}, {blue})">{text}</span>'


class HtmlRenderer(Renderer):
    extension = "html"

    def __init__(
        self,
        mode: Mode = "page",
        background: str = "#FFFFFF",
        lang: str = "en",
        font_size: int = 8,
        padding: int = 40,
    ) -> None:
        self.mode = mode
        self.background = validate_css_color(background)
        self.lang = lang
        self.font_size = font_size
        self.padding = padding

    def render(self, grid: CellGrid, title: str = "") -> str:
        lines = ("".join(_run_html(run) for run in group_runs(line)) for line in grid)
        pre = f'<pre class="ascii-art">{chr(10).join(lines)}</pre>'
        if self.mode == "fragment":
            return pre
        return PAGE_TEMPLATE.format(
            lang=escape(self.lang),
            title=escape(title),
            background=self.background,
            padding=self.padding,
            font_size=self.font_size,
            pre=pre,
        )
