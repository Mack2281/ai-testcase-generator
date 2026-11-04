from __future__ import annotations

import json
import os
from typing import Protocol


class Provider(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return the model's raw text reply."""


class AnthropicProvider:
    """Calls the Anthropic API. Needs `pip install anthropic` and ANTHROPIC_API_KEY."""

    def __init__(self, model: str | None = None):
        import anthropic  # imported lazily so the tool works offline without it

        self.client = anthropic.Anthropic()
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

    def complete(self, system: str, user: str) -> str:
        reply = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(block.text for block in reply.content if block.type == "text")


class OfflineProvider:
    """A canned stand-in so the whole pipeline can be run and demonstrated without a model."""

    def complete(self, system: str, user: str) -> str:
        if "missing, " in system:
            return json.dumps({
                "gaps": ["What happens after five failed sign-in attempts?",
                         "Is the username case sensitive?"],
                "assumptions": ["Passwords are at least 8 characters"],
            })
        return json.dumps({"test_cases": [
            {"id": "TC-001", "summary": "Sign in with valid credentials", "kind": "positive",
             "priority": "High", "preconditions": ["A registered user exists"],
             "steps": [{"action": "Enter a valid username and password and submit",
                        "expected": "The user lands on the dashboard"}],
             "covers": "A registered user can sign in"},
            {"id": "TC-002", "summary": "Sign in with a wrong password", "kind": "negative",
             "priority": "High", "preconditions": ["A registered user exists"],
             "steps": [{"action": "Enter a valid username and a wrong password and submit",
                        "expected": "An error message is shown and the user stays on the sign-in page"}],
             "covers": "An error is shown for bad credentials"},
            {"id": "TC-003", "summary": "Password at the minimum length", "kind": "boundary",
             "priority": "Medium", "preconditions": [],
             "steps": [{"action": "Create an account with an 8-character password",
                        "expected": "The account is created"}],
             "covers": "Passwords are at least 8 characters"},
        ]})
