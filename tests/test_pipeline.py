import csv
import json

from testcase_generator.export import COLUMNS, write_csv
from testcase_generator.pipeline import generate_cases, run
from testcase_generator.providers import OfflineProvider

GOOD_CASES = json.dumps({"test_cases": [{"id": "TC-1", "summary": "s", "kind": "negative", "priority": "Low",
                                         "preconditions": ["p1", "p2"],
                                         "steps": [{"action": "a1", "expected": "e1"}, {"action": "a2", "expected": "e2"}],
                                         "covers": "line"}]})


class Scripted:
    """A fake model that replays prepared replies and records what it was asked."""

    def __init__(self, *replies):
        self.replies, self.asked = list(replies), []

    def complete(self, system, user):
        self.asked.append(user)
        return self.replies.pop(0)


def test_retries_once_with_the_error_in_the_prompt():
    model = Scripted("not json at all", GOOD_CASES)
    cases = generate_cases(model, "req", [])
    assert cases[0].id == "TC-1"
    assert "rejected" in model.asked[1] and "no JSON" in model.asked[1]


def test_gives_up_after_retries():
    model = Scripted("nope", "still nope")
    try:
        generate_cases(model, "req", [], retries=1)
    except ValueError as err:
        assert "no JSON" in str(err)
    else:
        raise AssertionError("expected a failure")


def test_cases_are_not_generated_until_a_person_answers():
    order = []
    model = OfflineProvider()
    original = model.complete
    model.complete = lambda s, u: (order.append("model"), original(s, u))[1]

    def approve(gaps):
        order.append("person")
        return gaps.assumptions + ["Usernames are not case sensitive"]

    run(model, "req", approve)
    assert order == ["model", "person", "model"]


def test_confirmed_assumptions_reach_the_prompt():
    model = Scripted(json.dumps({"gaps": ["q"], "assumptions": ["A1"]}), GOOD_CASES)
    run(model, "req", lambda g: g.assumptions + ["Extra"])
    assert "- A1" in model.asked[1] and "- Extra" in model.asked[1]


def test_csv_has_one_row_per_step_with_continuation_rows(tmp_path):
    model = Scripted(GOOD_CASES)
    cases = generate_cases(model, "req", [])
    path = write_csv(cases, tmp_path / "out.csv")
    rows = list(csv.reader(path.open(encoding="utf-8")))
    assert rows[0] == COLUMNS
    assert rows[1][0] == "TC-1" and rows[1][4] == "p1\np2" and rows[1][5] == "a1"
    assert rows[2][:5] == ["", "", "", "", ""] and rows[2][5] == "a2"


def test_offline_pipeline_end_to_end(tmp_path):
    _, cases = run(OfflineProvider(), "A registered user can sign in", lambda g: g.assumptions)
    assert {c.kind for c in cases} == {"positive", "negative", "boundary"}
    assert write_csv(cases, tmp_path / "x.csv").exists()
