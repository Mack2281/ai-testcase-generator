from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .export import write_csv
from .models import GapAnalysis
from .pipeline import run
from .providers import AnthropicProvider, OfflineProvider


def ask_person(gaps: GapAnalysis) -> list[str]:
    """The approval gate: show the gaps and let a person confirm the assumptions."""
    print("\nQuestions the requirement leaves open:")
    for g in gaps.gaps:
        print(f"  ? {g}")
    print("\nProposed assumptions:")
    for a in gaps.assumptions:
        print(f"  - {a}")
    answer = input("\nPress Enter to accept these, or type extra assumptions separated by ';': ").strip()
    extra = [x.strip() for x in answer.split(";") if x.strip()]
    return gaps.assumptions + extra


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Turn a requirement into reviewed test cases.")
    p.add_argument("requirement", help="path to a text file with the requirement")
    p.add_argument("-o", "--output", default="out/test_cases.csv")
    p.add_argument("--provider", choices=["anthropic", "offline"], default="anthropic")
    p.add_argument("--yes", action="store_true", help="accept the proposed assumptions without asking")
    args = p.parse_args(argv)

    requirement = Path(args.requirement).read_text(encoding="utf-8")
    provider = OfflineProvider() if args.provider == "offline" else AnthropicProvider()
    approve = (lambda g: g.assumptions) if args.yes else ask_person
    _, cases = run(provider, requirement, approve)
    out = write_csv(cases, args.output)
    print(f"\nWrote {len(cases)} test cases to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
