import json

import pytest

from testcase_generator.parsing import ModelOutputError, extract_json, parse_cases, parse_gaps

GOOD = {"test_cases": [{"id": "TC-1", "summary": "s", "kind": "positive", "priority": "High",
                         "preconditions": [], "steps": [{"action": "a", "expected": "e"}], "covers": "line"}]}


def test_extracts_json_from_code_fence():
    assert extract_json("Here you go:\n```json\n{\"a\": 1}\n```") == {"a": 1}


def test_extracts_json_surrounded_by_prose():
    assert extract_json("Sure! {\"a\": 1} Hope that helps.") == {"a": 1}


def test_rejects_reply_without_json():
    with pytest.raises(ModelOutputError, match="no JSON"):
        extract_json("I cannot help with that.")


def test_rejects_invalid_json_with_position():
    with pytest.raises(ModelOutputError, match="not valid JSON"):
        extract_json("{\"a\": }")


def test_parses_gaps():
    g = parse_gaps(json.dumps({"gaps": ["q?"], "assumptions": ["a"]}))
    assert g.gaps == ["q?"] and g.assumptions == ["a"]


def test_parses_valid_cases():
    cases = parse_cases(json.dumps(GOOD))
    assert cases[0].id == "TC-1" and cases[0].steps[0].expected == "e"


@pytest.mark.parametrize("mutate, message", [
    (lambda d: d["test_cases"][0].update(priority="Urgent"), "priority"),
    (lambda d: d["test_cases"][0].update(kind="happy"), "kind"),
    (lambda d: d["test_cases"][0].update(steps=[]), "at least one step"),
    (lambda d: d["test_cases"][0]["steps"][0].update(expected=""), "action and an expected"),
    (lambda d: d["test_cases"][0].pop("summary"), "missing 'summary'"),
    (lambda d: d["test_cases"].append(dict(d["test_cases"][0])), "duplicate id"),
])
def test_rejects_bad_cases(mutate, message):
    data = json.loads(json.dumps(GOOD))
    mutate(data)
    with pytest.raises(ModelOutputError, match=message):
        parse_cases(json.dumps(data))


def test_rejects_empty_list():
    with pytest.raises(ModelOutputError, match="no test_cases"):
        parse_cases(json.dumps({"test_cases": []}))
