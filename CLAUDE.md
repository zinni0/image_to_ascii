# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A generator for static ASCII-art assets for websites. It converts an image into colored ASCII art, written as SVG, an HTML page or embeddable HTML fragment, or plain text. Python >=3.12, managed with `uv`; the only runtime dependency is Pillow.

## Commands

```bash
uv run image-to-ascii blue_flower.png -o output/out.svg --width 150 # run the converter (also: python -m image_to_ascii)
```

## Layout and architecture

- Pipeline: `AsciiConverter` -> `CellGrid` -> `Renderer.render(grid, title)`. Height is `height/width * columns * char_aspect` to make up for tall monospace cells. `--width` must be 1..2000 and the grid is capped at `MAX_CELLS`; violations raise `ValueError`, which the CLI reports on stderr with exit 1 (as it does for unreadable images and missing files). The CLI creates the output directory if needed.
- Default `--width` is 200. Background pixels become uncolored spaces: alpha < 128, or luminance beyond `--background-threshold` (default 0.94, 1.0 = off; with inversion it is luminance > threshold, otherwise luminance < 1 - threshold). Autocontrast stretches the 2nd..98th percentile over non-background pixels (`--no-autocontrast` disables it); `--gamma` (finite, > 0; >1 brightens) is applied after.
- Brightness is inverted by default (dark pixels get dense characters); `--bright-is-dense` turns the inversion off. `--dark` only selects the dark default HTML background.
- Output format comes from the `-o` extension (`.svg`, `.html`, else text) unless `--format` is given.
- HTML has `--html-mode page|fragment`; fragment is just `<pre class="ascii-art">`. SVG uses one `<text>` per row, one `<tspan>` per color run, a `viewBox` for responsive scaling, and a transparent background unless `--background` is set. All user text is escaped. The SVG/HTML title is only the input file name (`Path(input).name`).
- To add a renderer: subclass `Renderer` (set `extension`, implement `render`), reuse `group_runs`, register it in `renderers/__init__.py` `REGISTRY`, add CLI options in `cli.renderer_options`, and add tests.

## Conventions

- Code, identifiers, help strings, comments and commit messages are in English.
- Rule of Three for abstraction; small single-purpose functions.
- Modules talk to each other only through public interfaces (package `__init__` / `Renderer`), not internals.
- Golden references in `tests/golden/` must not be updated without approval. Manual outputs go to `output/` (gitignored); tests write to a temp directory.
- `blue_flower.png` (1600 px wide, transparent background) is the test image for background detection; source: Wikimedia Commons `File:Blue_Flower_Transparent_Background.png`, CC0.
