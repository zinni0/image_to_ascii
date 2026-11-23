# image-to-ascii

Converts an image into colored ASCII art as SVG, HTML, JSON or plain text.

```bash
uv run image-to-ascii blue_flower.png -o output/out.json --width 150
```

The format follows the `-o` extension (`.svg`, `.html`, `.json`, else text) unless `--format` is given.

## JSON format

`--format json` writes a document that validates against [`schema/ascii-art.v1.schema.json`](schema/ascii-art.v1.schema.json):

```json
{"schemaVersion":1,"width":3,"height":1,"generator":"image-to-ascii 0.2.0","rows":[[["aa","#ff000a"],[" ",null]]]}
```

Each row is a list of runs `[text, "#rrggbb" | null, alpha?]`. `null` means uncolored (spaces). `alpha` (0..1) is optional and not emitted yet.

Versioning (SemVer): a breaking change to the format bumps the major version (`schemaVersion` and a new `ascii-art.vN.schema.json`). Additive changes such as optional fields are minor. Releases are tagged `vX.Y.Z`; the release workflow attaches the schema file to the release, and the schema's `$id` is that asset's download URL (`https://github.com/zinni0/image_to_ascii/releases/latest/download/ascii-art.v1.schema.json`).

## License

MIT, see [LICENSE](LICENSE).
