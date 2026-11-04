from __future__ import annotations

from typing import Callable

from . import prompts
from .models import GapAnalysis, TestCase
from .parsing import ModelOutputError, parse_cases, parse_gaps
from .providers import Provider


def analyse_gaps(provider: Provider, requirement: str) -> GapAnalysis:
    return parse_gaps(provider.complete(prompts.GAP_SYSTEM, prompts.gap_prompt(requirement)))


def generate_cases(provider: Provider, requirement: str, assumptions: list[str], retries: int = 1) -> list[TestCase]:
    """Ask for test cases. If the reply is unusable, tell the model what was wrong and try again."""
    user = prompts.cases_prompt(requirement, assumptions)
    last: ModelOutputError | None = None
    for _ in range(retries + 1):
        raw = provider.complete(prompts.CASES_SYSTEM, user)
        try:
            return parse_cases(raw)
        except ModelOutputError as err:
            last = err
            user = f"{prompts.cases_prompt(requirement, assumptions)}\n\nYour previous reply was rejected: {err} Reply again with valid JSON only."
    raise last  # type: ignore[misc]


def run(
    provider: Provider,
    requirement: str,
    approve: Callable[[GapAnalysis], list[str]],
) -> tuple[GapAnalysis, list[TestCase]]:
    """Gap analysis, then a human approval step, then test cases.

    `approve` receives the gaps and returns the assumptions the person confirmed.
    Nothing is generated until a person has answered.
    """
    gaps = analyse_gaps(provider, requirement)
    confirmed = approve(gaps)
    return gaps, generate_cases(provider, requirement, confirmed)
