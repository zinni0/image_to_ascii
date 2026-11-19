import pytest
from PIL import Image

from image_to_ascii.cli import main


@pytest.fixture
def image(tmp_path):
    path = tmp_path / "in.png"
    Image.new("RGB", (20, 20), (10, 20, 30)).save(path)
    return str(path)


@pytest.mark.parametrize(
    ("name", "marker"),
    [("o.svg", "<svg"), ("o.html", "<!doctype html>"), ("o.txt", "%")],
)
def test_format_from_extension(tmp_path, image, name, marker):
    out = tmp_path / name
    main([image, "-o", str(out), "--width", "8"])
    assert marker in out.read_text(encoding="utf-8")


def test_fragment_and_bright_is_dense(tmp_path, image):
    out = tmp_path / "o.html"
    main(
        [
            image,
            "-o",
            str(out),
            "--width",
            "8",
            "--html-mode",
            "fragment",
            "--bright-is-dense",
        ]
    )
    text = out.read_text(encoding="utf-8")
    assert text.startswith("<pre") and "@" not in text


def test_missing_file(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main([str(tmp_path / "nope.png"), "-o", str(tmp_path / "o.txt")])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "nope.png" in err and "No such file" in err


def test_output_parent_is_file(tmp_path, image, capsys):
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(blocker / "o.txt"), "--width", "8"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert err.startswith("error:") and "in.png" not in err


def test_output_is_directory(tmp_path, image, capsys):
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(tmp_path), "--width", "8"])
    assert exc.value.code == 1
    assert str(tmp_path) in capsys.readouterr().err


@pytest.mark.parametrize("width", ["0", "99999", "abc"])
def test_invalid_width_is_argparse_error(tmp_path, image, width):
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(tmp_path / "o.txt"), "--width", width])
    assert exc.value.code == 2


def test_creates_output_directory(tmp_path, image):
    out = tmp_path / "nested" / "o.txt"
    main([image, "-o", str(out), "--width", "8"])
    assert out.exists()


def test_not_an_image(tmp_path, capsys):
    bad = tmp_path / "bad.png"
    bad.write_text("nope")
    with pytest.raises(SystemExit) as exc:
        main([str(bad), "-o", str(tmp_path / "o.txt")])
    assert exc.value.code == 1
    assert "error:" in capsys.readouterr().err


def test_too_many_cells(tmp_path, capsys):
    path = tmp_path / "thin.png"
    Image.new("RGB", (1, 4000)).save(path)
    with pytest.raises(SystemExit) as exc:
        main([str(path), "-o", str(tmp_path / "o.txt"), "--width", "2000"])
    assert exc.value.code == 1
    assert "cells" in capsys.readouterr().err


def test_bad_background(tmp_path, image, capsys):
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(tmp_path / "o.html"), "--background", "red;}"])
    assert exc.value.code == 1
    assert "invalid CSS color" in capsys.readouterr().err


def test_background_threshold_and_autocontrast_flags(tmp_path):
    src = tmp_path / "g.png"
    Image.new("RGB", (10, 10), (200, 200, 200)).save(src)
    out = tmp_path / "o.txt"
    base = [str(src), "-o", str(out), "--width", "4"]
    main(base)
    assert out.read_text(encoding="utf-8").strip() != ""
    main([*base, "--background-threshold", "0.5"])
    assert out.read_text(encoding="utf-8").strip() == ""
    main([*base, "--no-autocontrast", "--gamma", "1.5"])
    assert out.read_text(encoding="utf-8").strip() != ""


@pytest.mark.parametrize("flag", ["--background-threshold", "--gamma"])
def test_invalid_numeric_option_reports_error(tmp_path, image, capsys, flag):
    value = "2" if flag == "--background-threshold" else "0"
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(tmp_path / "o.txt"), flag, value])
    assert exc.value.code == 1
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("value", ["nan", "inf"])
def test_non_finite_gamma_reports_error(tmp_path, image, capsys, value):
    with pytest.raises(SystemExit) as exc:
        main([image, "-o", str(tmp_path / "o.txt"), "--gamma", value])
    assert exc.value.code == 1
    assert "gamma must be a finite number" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("name", "tag"),
    [("o.svg", "<title>in.png</title>"), ("o.html", "<title>in.png</title>")],
)
def test_title_is_file_name_only(tmp_path, image, name, tag):
    out = tmp_path / name
    main([image, "-o", str(out), "--width", "8"])
    text = out.read_text(encoding="utf-8")
    assert tag in text
    assert str(tmp_path) not in text
