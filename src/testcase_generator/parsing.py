from __future__ import annotations

import json
import re

from .models import KINDS, PRIORITIES, GapAnalysis, Step, TestCase


class ModelOutputError(ValueError):
    """The model's reply was not usable. The message says exactly why."""


def extract_json(raw: str) -> dict:
    """Models sometimes wrap JSON in prose or code fences. Pull the object out."""
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise ModelOutputError("The reply contains no JSON object.")
        text = text[start : end + 1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ModelOutputError(f"The reply is not valid JSON: {exc.msg} at position {exc.pos}.") from exc
    if not isinstance(data, dict):
        raise ModelOutputError("The reply JSON must be an object.")
    return data


def parse_gaps(raw: str) -> GapAnalysis:
    data = extract_json(raw)
    gaps, assumptions = data.get("gaps", []), data.get("assumptions", [])
    if not all(isinstance(x, str) for x in gaps + assumptions):
        raise ModelOutputError("Gaps and assumptions must be lists of text.")
    return GapAnalysis(gaps=gaps, assumptions=assumptions)


def parse_cases(raw: str) -> list[TestCase]:
    data = extract_json(raw)
    items = data.get("test_cases")
    if not isinstance(items, list) or not items:
        raise ModelOutputError("The reply has no test_cases list.")
    cases, seen = [], set()
    for n, item in enumerate(items, start=1):
        where = f"test case {n}"
        for key in ("id", "summary", "kind", "priority", "steps"):
            if key not in item:
                raise ModelOutputError(f"{where}: missing '{key}'.")
        if item["id"] in seen:
            raise ModelOutputError(f"{where}: duplicate id {item['id']}.")
        seen.add(item["id"])
        if item["priority"] not in PRIORITIES:
            raise ModelOutputError(f"{where}: priority must be one of {PRIORITIES}, got {item['priority']!r}.")
        if item["kind"] not in KINDS:
            raise ModelOutputError(f"{where}: kind must be one of {KINDS}, got {item['kind']!r}.")
        if not item["steps"]:
            raise ModelOutputError(f"{where}: needs at least one step.")
        steps = []
        for s in item["steps"]:
            if not s.get("action") or not s.get("expected"):
                raise ModelOutputError(f"{where}: every step needs an action and an expected result.")
            steps.append(Step(action=s["action"], expected=s["expected"]))
        cases.append(TestCase(
            id=item["id"], summary=item["summary"], kind=item["kind"], priority=item["priority"],
            preconditions=list(item.get("preconditions", [])), steps=steps, covers=item.get("covers", ""),
        ))
    return cases
