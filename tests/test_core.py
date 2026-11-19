import pytest
from PIL import Image

from image_to_ascii import AsciiConverter, Cell, ConversionOptions
from image_to_ascii.converter import brightness
from image_to_ascii.runs import Run, group_runs

RED = (255, 0, 0)
BLUE = (0, 0, 255)


def test_brightness_extremes():
    assert brightness(0, 0, 0) == 0.0
    assert brightness(255, 255, 255) == 1.0


def test_resize_height_uses_char_aspect():
    out = AsciiConverter(ConversionOptions(width=40)).resize(
        Image.new("RGB", (100, 50))
    )
    assert out.size == (40, round(0.5 * 40 * 0.52))


def test_grid_inverted_and_not():
    img = Image.new("RGB", (2, 1))
    img.putpixel((1, 0), (255, 255, 255))
    inv = AsciiConverter(ConversionOptions(invert=True)).to_grid(img)
    assert [c.char for c in inv[0]] == ["@", " "]
    plain = AsciiConverter(ConversionOptions(invert=False)).to_grid(img)
    assert [c.char for c in plain[0]] == [" ", "@"]
    assert inv[0][1].color == (255, 255, 255)


def test_convert_loads_file(tmp_path):
    path = tmp_path / "x.png"
    Image.new("RGB", (10, 10), (0, 0, 0)).save(path)
    grid = AsciiConverter(ConversionOptions(width=4)).convert(str(path))
    assert len(grid[0]) == 4 and grid[0][0].char == "@"


def test_group_runs_merges_colors_and_spaces():
    line = [Cell(c, RED) for c in "abc "] + [
        Cell(" ", BLUE),
        Cell("d", BLUE),
        Cell("e", BLUE),
    ]
    assert group_runs(line) == [Run("abc", RED), Run("  ", None), Run("de", BLUE)]


def test_group_runs_empty():
    assert group_runs([]) == []


def _resize(size, width=40):
    return AsciiConverter(ConversionOptions(width=width)).resize(Image.new("RGB", size))


def test_resize_portrait_is_taller():
    assert _resize((100, 200)).size == (40, 42)


def test_resize_landscape_is_shorter():
    assert _resize((200, 100)).size == (40, 10)


def test_resize_one_pixel_wide_hits_cap():
    with pytest.raises(ValueError, match="cells"):
        _resize((1, 4000), width=2000)


def test_resize_one_pixel_high_is_small():
    assert _resize((4000, 1)).size == (40, 1)


@pytest.mark.parametrize("width", [0, -1, 2001])
def test_invalid_width_rejected(width):
    with pytest.raises(ValueError):
        ConversionOptions(width=width)


def test_invalid_char_aspect_rejected():
    with pytest.raises(ValueError):
        ConversionOptions(char_aspect=0)
