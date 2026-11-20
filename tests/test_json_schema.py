"""The JSON renderer output must satisfy schema/ascii-art.v1.schema.json."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from image_to_ascii import Cell, get_renderer

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "ascii-art.v1.schema.json"


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def render(grid):
    return json.loads(get_renderer("json").render(grid, title="x"))


def test_output_matches_schema(validator):
    grid = [[Cell("a", (255, 0, 10)), Cell("a", (255, 0, 10)), Cell(" ", None)]]
    document = render(grid)
    validator.validate(document)
    assert document["rows"] == [[["aa", "#ff000a"], [" ", None]]]
    assert (document["width"], document["height"]) == (3, 1)


def test_empty_grid_matches_schema(validator):
    validator.validate(render([]))


def test_schema_rejects_bad_documents(validator):
    good = render([[Cell("a", (1, 2, 3))]])
    for mutate in (
        lambda d: d.update(schemaVersion=2),
        lambda d: d.pop("generator"),
        lambda d: d.update(rows=[[["a", "rgb(1,2,3)"]]]),
        lambda d: d.update(rows=[[["a", "#FF0000"]]]),
        lambda d: d.update(rows=[[["a", None, 2]]]),
    ):
        bad = json.loads(json.dumps(good))
        mutate(bad)
        assert not validator.is_valid(bad)
    assert validator.is_valid({**good, "rows": [[["a", "#010203", 0.5]]]})
