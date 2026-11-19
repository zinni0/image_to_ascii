"""Byte-for-byte comparison against references generated from blue_flower.png.

Do not update tests/golden/* without explicit approval.
"""

from pathlib import Path

import pytest

from image_to_ascii import AsciiConverter, ConversionOptions, get_renderer

ROOT = Path(__file__).parent.parent
GOLDEN = Path(__file__).parent / "golden"
INPUT = "blue_flower.png"
TITLE = Path(INPUT).name


OPTIONS = ConversionOptions(width=80)


@pytest.fixture(scope="module")
def grid():
    return AsciiConverter(OPTIONS).convert(str(ROOT / INPUT))


@pytest.mark.parametrize(
    ("fmt", "options", "name"),
    [
        ("txt", {}, "blue_flower_w80.txt"),
        ("svg", {}, "blue_flower_w80.svg"),
        ("html", {"mode": "fragment"}, "blue_flower_w80_fragment.html"),
    ],
)
def test_golden(grid, fmt, options, name):
    rendered = get_renderer(fmt, **options).render(grid, title=TITLE)
    expected = (GOLDEN / name).read_bytes()
    assert rendered.encode("utf-8") == expected


def test_transparent_flower_has_clean_border(grid):
    border = grid[0] + grid[-1] + [row[i] for row in grid for i in (0, -1)]
    assert {cell.char for cell in border} == {" "}
