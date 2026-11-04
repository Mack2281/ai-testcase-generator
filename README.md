# Test case generator

[![Tests](https://github.com/Mack2281/ai-testcase-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/Mack2281/ai-testcase-generator/actions/workflows/tests.yml)

A small command-line tool that turns a written requirement into structured test cases using a language model, with a person approving the key step. It is a compact, public version of the ideas behind the AI tester I built at work.

```
requirement  ->  find gaps  ->  a person confirms assumptions  ->  test cases  ->  CSV
```

## Why it is built this way

- **A person approves before cases are written.** The tool lists what the requirement leaves open and proposes assumptions. Nothing is generated until you confirm them (a test checks this order).
- **The model's reply is never trusted.** Output is parsed and validated: valid JSON, allowed priorities and types, no duplicate IDs, every step has an expected result. A bad reply is sent back once with the exact error, then the run fails with a clear message.
- **Every case traces to the requirement.** Each test case quotes the line it covers.
- **Provider is swappable.** A small interface keeps the model behind one method. There is a real provider for Anthropic and an offline one for demos and tests.
- **Plain output.** One CSV row per step, ready for most test management tools.

## Try it without an API key

```bash
pip install -e ".[dev]"
testcase-generator examples/sign_in_requirement.txt --provider offline --yes
pytest
```

The offline provider returns canned answers so you can see the whole flow and the CSV.

## Use a real model

```bash
pip install -e ".[anthropic]"
export ANTHROPIC_API_KEY=...        # optional: ANTHROPIC_MODEL to pick a model
testcase-generator examples/sign_in_requirement.txt
```

## What is tested

The tests use a fake model that replays prepared replies, so they run anywhere without network access. They cover JSON extraction from messy replies, every validation rule, the retry with the error fed back, the approval order, assumptions reaching the prompt, and the CSV layout.

Honest note: the real-model path (`AnthropicProvider`) is a thin wrapper and is not covered by automated tests, because that would need a paid API key and gives non-repeatable answers.

Author: Mayank Agrawal, Senior QA Engineer.
