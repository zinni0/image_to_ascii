"""Byte-for-byte comparison against references generated from flowers.jpg.

Do not update tests/golden/* without explicit approval.
"""

from pathlib import Path

import pytest

from image_to_ascii import AsciiConverter, ConversionOptions, get_renderer

ROOT = Path(__file__).parent.parent
GOLDEN = Path(__file__).parent / "golden"
TITLE = "flowers.jpg"


@pytest.fixture(scope="module")
def grid():
    return AsciiConverter(ConversionOptions(width=80)).convert(str(ROOT / TITLE))


@pytest.mark.parametrize(
    ("fmt", "options", "name"),
    [
        ("txt", {}, "flowers_w80.txt"),
        ("svg", {}, "flowers_w80.svg"),
        ("html", {"mode": "fragment"}, "flowers_w80_fragment.html"),
    ],
)
def test_golden(grid, fmt, options, name):
    rendered = get_renderer(fmt, **options).render(grid, title=TITLE)
    expected = (GOLDEN / name).read_bytes()
    assert rendered.encode("utf-8") == expected
