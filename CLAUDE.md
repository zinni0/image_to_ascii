# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A generator for static ASCII-art assets for websites. It converts an image into colored ASCII art, written as SVG, an HTML page or embeddable HTML fragment, or plain text. Python >=3.12, managed with `uv`; the only runtime dependency is Pillow.

## Commands

```bash
uv sync                                                  # install deps (incl. dev group: pytest, ruff, pre-commit)
uv run image-to-ascii flowers.jpg -o output/out.svg --width 150 # run the converter (also: python -m image_to_ascii)
uv run pytest                                            # run the tests
uv run ruff check --fix && uv run ruff format            # lint + format (same as the pre-commit hooks)
uv run pre-commit install                                # enable the hooks locally
```

## Layout and architecture

```
src/image_to_ascii/
  colors.py     validate_css_color(): whitelist check for background values (HTML and SVG)
  __init__.py   public API: convert(), AsciiConverter, ConversionOptions, Cell, CellGrid, get_renderer
  models.py     frozen dataclasses Cell(char, color), ConversionOptions; CellGrid = list of rows of Cells
  converter.py  AsciiConverter: load -> resize -> to_grid (luminance, Rec. 601, mapped onto the ramp)
  runs.py       group_runs(line): merges a row into color runs (spaces carry no color)
  renderers/    base.Renderer ABC, text/html/svg renderers, REGISTRY + get_renderer + format_for_path
  cli.py        argparse -> ConversionOptions -> Renderer -> file; main()
  __main__.py   python -m image_to_ascii
tests/          pytest: converter, runs, renderers, CLI, golden files (tests/golden/)
```

- Pipeline: `AsciiConverter` -> `CellGrid` -> `Renderer.render(grid, title)`. Height is `height/width * columns * char_aspect` to make up for tall monospace cells. `--width` must be 1..2000 and the grid is capped at `MAX_CELLS`; violations raise `ValueError`, which the CLI reports on stderr with exit 1 (as it does for unreadable images and missing files). The CLI creates the output directory if needed.
- Brightness is inverted by default (dark pixels get dense characters); `--bright-is-dense` turns the inversion off. `--dark` only selects the dark default HTML background.
- Output format comes from the `-o` extension (`.svg`, `.html`, else text) unless `--format` is given.
- HTML has `--html-mode page|fragment`; fragment is just `<pre class="ascii-art">`. SVG uses one `<text>` per row, one `<tspan>` per color run, a `viewBox` for responsive scaling, and a transparent background unless `--background` is set. All user text is escaped.
- To add a renderer: subclass `Renderer` (set `extension`, implement `render`), reuse `group_runs`, register it in `renderers/__init__.py` `REGISTRY`, add CLI options in `cli.renderer_options`, and add tests.

## Conventions

- Code, identifiers, help strings, comments and commit messages are in English.
- Rule of Three for abstraction; small single-purpose functions.
- Modules talk to each other only through public interfaces (package `__init__` / `Renderer`), not internals.
- `flowers.jpg` is the golden-test input; golden references in `tests/golden/` must not be updated without approval. Manual outputs go to `output/` (gitignored); tests write to a temp directory.
