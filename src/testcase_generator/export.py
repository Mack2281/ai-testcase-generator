from __future__ import annotations

import csv
from pathlib import Path

from .models import TestCase

COLUMNS = ["Test Case ID", "Summary", "Type", "Priority", "Preconditions", "Step", "Expected Result", "Covers"]


def write_csv(cases: list[TestCase], path: str | Path) -> Path:
    """One row per step. Continuation rows only fill the step columns, as most test tools expect."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for c in cases:
            for i, s in enumerate(c.steps):
                if i == 0:
                    w.writerow([c.id, c.summary, c.kind, c.priority, "\n".join(c.preconditions), s.action, s.expected, c.covers])
                else:
                    w.writerow(["", "", "", "", "", s.action, s.expected, ""])
    return path
