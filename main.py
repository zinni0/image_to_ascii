import argparse
import sys

from PIL import Image

RAMP = " .:-=+*#%@"
CHAR_ASPECT = 0.52


def load_image(path: str) -> Image.Image:
    image = Image.open(path)
    return image.convert("RGB")


def resize(image: Image.Image, width_out: int) -> Image.Image:
    width, height = image.size

    height_out = max(1, round((width / height) * width_out * CHAR_ASPECT))
    return image.resize((width_out, height_out), Image.LANCZOS)


def get_brightness(red: int, green: int, blue: int) -> float:
    return (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0


def image_to_lines(image: Image.Image, invert: bool):
    px = image.load()
    width, height = image.size
    lines = []
    n = len(RAMP) - 1

    for y in range(height):
        line = []
        for x in range(width):
            red, green, blue = px[x, y]
            brightness = get_brightness(red, green, blue)
            if invert:
                brightness = 1.0 - brightness
            idx = min(n, max(0, round(brightness * n)))
            line.append((RAMP[idx], (red, green, blue)))
        lines.append(line)

    return lines


def to_text(cells) -> str:
    return "\n".join("".join(ch for ch, _ in line) for line in cells)


def _segment_html(ch: str, color) -> str:
    if not ch:
        return ""
    if color is None:
        return ch
    red, green, blue = color
    return f'<span style="color:rgb({red}, {green}, {blue})">{ch}</span>'


def to_html(cells, background: str, titel: str) -> str:
    tile = []

    for line in cells:
        buf_ch = ""
        buf_color = None
        line_html = []

        for ch, color in line:
            f = None if ch == " " else color

            if f != buf_color:
                line_html.append(_segment_html(ch, color))

                buf_color = f
                buf_ch = ch
            else:
                buf_ch += ch

        line_html.append(_segment_html(buf_ch, buf_color))
        tile.append("".join(line_html))

    body = "\n".join(tile)
    return f"""<!doctype html>
                <html lang="de">
                <head>
                    <meta charset="utf-8">
                    <title>{titel}</title>
                    <style>
  body {{ background:{background}; margin:0; padding:40px; }}
  pre {{ font-family:'IBM Plex Mono','Courier New',monospace; font-size:8px; line-height:1.0;
         white-space:pre; margin:0; }}
</style>
</head>
<body>
<pre>{body}</pre>
</body>
</html>"""


def main():
    p = argparse.ArgumentParser(description="Image to colored Ascii-Art")

    p.add_argument("input", help="path to image (jpg, png, ...)")
    p.add_argument("-o", "--output", required=True, help="path to output file")
    p.add_argument(
        "--format",
        choices=["html", "txt"],
        default=None,
        help="output format. default: using file extension from -o",
    )
    p.add_argument(
        "--width", type=int, default=100, help="width in chars (default: 100)"
    )
    p.add_argument(
        "--dark",
        action="store_true",
        help="for dark backgrounds: brighter spots -> more chars",
    )
    p.add_argument("--background", default=None, help="CSS-Color for HTML-Background")

    args = p.parse_args()

    fmt = args.format or ("html" if args.output.lower().endswith(".html") else "txt")
    bg = args.background or ("#0B0B0C" if args.dark else "#FFFFFF")

    try:
        image = load_image(args.input)
    except FileNotFoundError:
        print(f"file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    resized = resize(image, args.width)
    cells = image_to_lines(resized, invert=not args.dark)

    if fmt == "html":
        out = to_html(cells, bg, titel=args.input)
    else:
        out = to_text(cells)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"finished: {args.output} ({resized.size[0]}x{resized.size[1]} chars)")


if __name__ == "__main__":
    main()
