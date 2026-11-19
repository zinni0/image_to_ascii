"""Command line interface."""

import argparse
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from image_to_ascii import AsciiConverter, ConversionOptions
from image_to_ascii.models import DEFAULT_BACKGROUND_THRESHOLD, DEFAULT_WIDTH, MAX_WIDTH
from image_to_ascii.renderers import REGISTRY, format_for_path, get_renderer

DARK_BACKGROUND = "#0B0B0C"
LIGHT_BACKGROUND = "#FFFFFF"


def width_arg(value: str) -> int:
    try:
        width = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}") from None
    if not 1 <= width <= MAX_WIDTH:
        raise argparse.ArgumentTypeError(f"must be between 1 and {MAX_WIDTH}")
    return width


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Convert an image to colored ASCII art")
    p.add_argument("input", help="path to image (jpg, png, ...)")
    p.add_argument("-o", "--output", required=True, help="path to output file")
    p.add_argument(
        "--format",
        choices=sorted(REGISTRY),
        default=None,
        help="output format (default: derived from the -o extension)",
    )
    p.add_argument(
        "--width",
        type=width_arg,
        default=DEFAULT_WIDTH,
        help=f"width in chars (default: {DEFAULT_WIDTH})",
    )
    p.add_argument(
        "--background-threshold",
        type=float,
        default=DEFAULT_BACKGROUND_THRESHOLD,
        help="luminance 0..1 beyond which pixels become spaces; 1.0 turns it off "
        f"(default: {DEFAULT_BACKGROUND_THRESHOLD})",
    )
    p.add_argument(
        "--no-autocontrast",
        action="store_true",
        help="disable percentile contrast stretching",
    )
    p.add_argument(
        "--gamma",
        type=float,
        default=1.0,
        help="gamma applied after contrast stretching; >1 brightens (default: 1.0)",
    )
    p.add_argument(
        "--dark",
        action="store_true",
        help="use the dark default background for HTML pages",
    )
    p.add_argument("--background", default=None, help="CSS color for the background")
    p.add_argument(
        "--bright-is-dense",
        action="store_true",
        help="map bright pixels to dense characters (default: dark pixels are dense)",
    )
    p.add_argument(
        "--html-mode",
        choices=["page", "fragment"],
        default="page",
        help="HTML output: full page or embeddable <pre> fragment (default: page)",
    )
    p.add_argument(
        "--lang", default="en", help="lang attribute of HTML pages (default: en)"
    )
    return p


def renderer_options(fmt: str, args: argparse.Namespace) -> dict:
    if fmt == "html":
        background = args.background or (
            DARK_BACKGROUND if args.dark else LIGHT_BACKGROUND
        )
        return {"mode": args.html_mode, "background": background, "lang": args.lang}
    if fmt == "svg":
        return {"background": args.background}
    return {}


def run(args: argparse.Namespace) -> None:
    fmt = args.format or format_for_path(args.output)
    options = ConversionOptions(
        width=args.width,
        invert=not args.bright_is_dense,
        background_threshold=args.background_threshold,
        contrast=not args.no_autocontrast,
        gamma=args.gamma,
    )
    converter = AsciiConverter(options)
    resized = converter.resize(converter.load(args.input))
    grid = converter.to_grid(resized)
    renderer = get_renderer(fmt, **renderer_options(fmt, args))
    content = renderer.render(grid, title=Path(args.input).name)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"finished: {args.output} ({resized.size[0]}x{resized.size[1]} chars)")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        run(args)
    except UnidentifiedImageError:
        _fail(f"not a readable image: {args.input}")
    except Image.DecompressionBombError as error:
        _fail(f"image too large: {error}")
    except ValueError as error:
        _fail(str(error))
    except OSError as error:
        name = error.filename or args.input
        _fail(f"{name}: {error.strerror or error}")


def _fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)
