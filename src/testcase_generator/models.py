from __future__ import annotations

from dataclasses import dataclass, field

PRIORITIES = ("High", "Medium", "Low")
KINDS = ("positive", "negative", "boundary")


@dataclass
class Step:
    action: str
    expected: str


@dataclass
class TestCase:
    id: str
    summary: str
    kind: str
    priority: str
    preconditions: list[str] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    covers: str = ""  # the line of the requirement this case traces back to


@dataclass
class GapAnalysis:
    gaps: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
