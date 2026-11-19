import xml.etree.ElementTree as ET

import pytest

from image_to_ascii import Cell, get_renderer
from image_to_ascii.renderers import format_for_path

RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRID = [
    [Cell("a", RED), Cell("b", RED), Cell(" ", RED), Cell("<", BLUE)],
    [Cell("c", BLUE), Cell(" ", BLUE), Cell(" ", BLUE), Cell("&", BLUE)],
]


def test_text():
    assert get_renderer("txt").render(GRID, "t") == "ab <\nc  &"


def test_html_page_runs_escape_and_options():
    html = get_renderer("html", background="#000", lang="de").render(GRID, "<x>&")
    assert '<span style="color:rgb(255, 0, 0)">ab</span> ' in html
    assert '<span style="color:rgb(0, 0, 255)">&lt;</span>' in html
    assert "<title>&lt;x&gt;&amp;</title>" in html
    assert "background:#000" in html and '<html lang="de">' in html


def test_html_fragment():
    html = get_renderer("html", mode="fragment").render(GRID, "t")
    assert html.startswith('<pre class="ascii-art">') and html.endswith("</pre>")
    assert "<html" not in html


def test_svg_well_formed_and_escaped():
    svg = get_renderer("svg").render(GRID, "<t>&")
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    assert root.get("viewBox") == "0 0 24 23"
    assert root.find(f"{ns}title").text == "<t>&"
    texts = root.findall(f"{ns}text")
    assert len(texts) == 2
    assert "".join(texts[0].itertext()) == "ab <"
    assert texts[0].find(f"{ns}tspan").get("fill") == "rgb(255,0,0)"
    assert root.find(f"{ns}rect") is None


def test_svg_background_rect():
    root = ET.fromstring(get_renderer("svg", background="#0B0B0C").render(GRID, "t"))
    assert root.find("{http://www.w3.org/2000/svg}rect").get("fill") == "#0B0B0C"


def test_format_for_path():
    assert format_for_path("a.SVG") == "svg"
    assert format_for_path("a.html") == "html"
    assert format_for_path("a.txt") == "txt"
    assert format_for_path("a") == "txt"


@pytest.mark.parametrize("fmt", ["html", "svg"])
@pytest.mark.parametrize(
    "bad",
    [
        "#12345",
        "#1234567",
        "red;} body{display:none",
        "</style><script>",
        'red"/><script>',
    ],
)
def test_malicious_background_rejected(fmt, bad):
    with pytest.raises(ValueError):
        get_renderer(fmt, background=bad)


@pytest.mark.parametrize("good", ["#fff", "#0B0B0C", "red", "rgb(1, 2, 3)"])
def test_valid_background_accepted(good):
    assert get_renderer("html", background=good).render([[]])
