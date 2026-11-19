import pytest
from PIL import Image

from image_to_ascii import AsciiConverter, Cell, ConversionOptions
from image_to_ascii.converter import brightness
from image_to_ascii.models import DEFAULT_RAMP
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
    legacy = {"background_threshold": 1.0, "contrast": False}
    inv = AsciiConverter(ConversionOptions(invert=True, **legacy)).to_grid(img)
    assert [c.char for c in inv[0]] == ["@", " "]
    plain = AsciiConverter(ConversionOptions(invert=False, **legacy)).to_grid(img)
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


def _row(colors, **options):
    img = Image.new("RGBA", (len(colors), 1))
    for x, color in enumerate(colors):
        img.putpixel((x, 0), color)
    return AsciiConverter(ConversionOptions(**options)).to_grid(img)[0]


def test_transparent_pixel_becomes_space():
    row = _row([(0, 0, 0, 0), (0, 0, 0, 255)])
    assert row[0] == Cell(" ", None)
    assert row[1].char == "@"


def test_near_white_becomes_space_and_threshold_one_disables():
    near_white = (250, 250, 250, 255)
    assert _row([near_white])[0] == Cell(" ", None)
    kept = _row([near_white], background_threshold=1.0, contrast=False)[0]
    assert kept.color == (250, 250, 250)


def test_background_flips_with_invert():
    row = _row([(0, 0, 0, 255), (255, 255, 255, 255)], invert=False)
    assert row[0] == Cell(" ", None)
    assert row[1].char == "@"


def test_autocontrast_spreads_narrow_gradient():
    colors = [(v, v, v, 255) for v in range(100, 140)]
    plain = {c.char for c in _row(colors, contrast=False)}
    stretched = {c.char for c in _row(colors)}
    assert len(stretched) > len(plain)


def test_gamma_brightens_midtones():
    gray = [(128, 128, 128, 255)]
    flat = _row(gray, contrast=False)[0].char
    bright = _row(gray, contrast=False, gamma=2.0)[0].char
    assert DEFAULT_RAMP.index(bright) < DEFAULT_RAMP.index(flat)


@pytest.mark.parametrize(
    "options",
    [
        {"background_threshold": 1.5},
        {"background_threshold": -0.1},
        {"gamma": 0},
        {"gamma": float("nan")},
        {"gamma": float("inf")},
    ],
)
def test_invalid_options_raise(options):
    with pytest.raises(ValueError):
        ConversionOptions(**options)
