GAP_SYSTEM = (
    "You are a senior QA engineer. Read the requirement and list what is missing, "
    "ambiguous or untestable. Reply with JSON only: "
    '{"gaps": [string], "assumptions": [string]}. '
    "Each gap is a question a product owner could answer. Do not invent facts."
)

CASES_SYSTEM = (
    "You are a senior QA engineer writing test cases. Reply with JSON only: "
    '{"test_cases": [{"id": string, "summary": string, "kind": "positive|negative|boundary", '
    '"priority": "High|Medium|Low", "preconditions": [string], '
    '"steps": [{"action": string, "expected": string}], "covers": string}]}. '
    "Cover normal, negative and boundary behaviour. Every case must quote the part of the "
    "requirement it covers in `covers`. Use the confirmed assumptions; do not test behaviour "
    "the requirement does not describe."
)


def gap_prompt(requirement: str) -> str:
    return f"Requirement:\n{requirement.strip()}"


def cases_prompt(requirement: str, assumptions: list[str]) -> str:
    notes = "\n".join(f"- {a}" for a in assumptions) or "- none"
    return f"Requirement:\n{requirement.strip()}\n\nConfirmed assumptions:\n{notes}"
