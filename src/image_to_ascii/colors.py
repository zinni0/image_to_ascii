"""CSS color validation for values interpolated into HTML and SVG output."""

import re

_CSS_COLOR = re.compile(
    r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})"
    r"|[a-zA-Z]{3,30}"
    r"|rgba?\(\s*[0-9.%]+(?:\s*[,/ ]\s*[0-9.%]+){2,3}\s*\)",
    re.ASCII,
)


def validate_css_color(value: str) -> str:
    """Return value if it is a hex, named or rgb(a) color, else raise ValueError."""
    if not _CSS_COLOR.fullmatch(value):
        raise ValueError(f"invalid CSS color: {value!r}")
    return value
