# Layer 1 — pattern scorer

Deterministic, regex-based detection of AI-writing tells. No model calls,
no network, no GPU. Runs anywhere Python runs.

## Structure

```
layer1/
  rules.py    Rule dataclass + REGISTRY (8 rules to start)
  scorer.py   PatternScorer: runs every rule, computes density metrics
tests/
  test_layer1.py   11 tests: one per rule, one regression test for a real
                    bug found live, one full-document regression test,
                    two false-positive controls (human text, legal text)
```

## Run the tests

```
pip install pytest --break-system-packages
python -m pytest tests/ -v
```

## Use it

```python
from layer1 import PatternScorer

result = PatternScorer().analyze(your_text)
print(result.flag_count, result.density_per_1000w)
for flag in result.flags:
    print(flag.rule_id, flag.match_text, flag.explanation)
```

## Add a new rule

1. Write a `_find_x(text) -> list[tuple[start, end, matched_text]]` function
   in `rules.py`.
2. Wrap it in a `Rule(...)` and append to `REGISTRY`.
3. Write at least one positive test and confirm it doesn't fire on
   `HUMAN_CONTROL_TEXT` or `LEGAL_BOILERPLATE_TEXT` in the test file.

That's the whole extension path — 16 more patterns from the original
SKILL.md are still unported, and each one follows this same pattern.

## Known limitation

This is regex over raw text, not a dependency parse. It will miss
phrasings it wasn't written for — the `rule_of_three_outline` bug fixed
in this version is proof of that failure mode, not an exception to it.
Treat every new rule as "probably has a gap," and let the false-positive
controls in the test file be the thing that catches drift, not
inspection by eye.

## What this is not

This is Layer 1 only — pattern density, nothing statistical. It has no
opinion about whether text is AI-written; it only counts surface tells.
The ensemble verdict needs Layer 2 (Binoculars, see
`layer2_binoculars.py` from earlier in the conversation) before any
human/machine claim is defensible.
