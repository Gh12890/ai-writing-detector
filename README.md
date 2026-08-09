# Draft Audit

[![Tests](https://github.com/Gh12890/ai-writing-detector/actions/workflows/tests.yml/badge.svg)](https://github.com/Gh12890/ai-writing-detector/actions/workflows/tests.yml)

A pattern-based AI-writing detector,, built as a working exploration of
what a transparent, evidence-driven text auditor looks like -- one that
shows its reasoning, admits what it doesn't know, and gets corrected
when real evidence contradicts a design assumption, instead of quietly
drifting out of date.

See FINDINGS.md for real measured results (human vs. AI text,
across 3 models) and TODO.md for exactly what's built, what's
deliberately not, and why.

## Quick start
pip install -r requirements.txt
python -m pytest tests/ -v # 51 tests
streamlit run app.py
## What's actually in here
layer1/
rules.py 23 active regex-based rules (21 from the SKILL.md's
24-pattern taxonomy + 2 original additions), plus 1
more (curly_quotes) implemented but deliberately
excluded from scoring -- see TODO.md for why
scorer.py PatternScorer: runs every rule, quote normalization,
density metrics
exclusions.py Legal-boilerplate filter: suppresses flags that fall
inside statutory citations, case citations, or
standard contract phrases

app.py Streamlit UI -- paste text, see it annotated with
red (flagged) and gray (excluded, legal boilerplate)
highlights, plus per-flag explanations

scripts/
measure_fpr.py Reports flags/1000w and a per-rule breakdown
against a folder of known-human text
compare_corpora.py Side-by-side human-vs-AI comparison, with a
per-rule "which side is this actually catching"
verdict

tests/ 51 tests across 5 files -- every rule, the exclusion
filter, both measurement scripts, and the Streamlit
app itself (via Streamlit's own AppTest harness)

FINDINGS.md Real measured results, not aspirational ones: AI
text scored 2.85x higher than human text across a
6-human / 7-AI-document comparison spanning three
models (ChatGPT, Gemini, Claude)

TODO.md Exact pattern coverage, what's deliberately not
built and why, known limitations of what is

layer2_binoculars.py Statistical scorer (Binoculars method) -- NOT
wired into this repo's pipeline. Needs a GPU and
network access to run; exists as a standalone
script, not yet integrated.
## Design principles this project tries to hold to

- Every rule is a readable regex, not a black box -- open rules.py
  and you can see exactly why anything got flagged.
- Nothing gets scored without a positive test proving it fires, and a
  negative test proving it doesn't misfire on a control text.
- Real bugs found during actual use get a regression test locking in
  the fix, not just a silent patch (see test_real_pasted_text_regression,
  test_rule_of_three_outline_regression).
- Claims get corrected when evidence contradicts them, not left to go
  stale. curly_quotes was implemented, tested, then removed from
  scoring after measurement showed it was detecting "typed in Microsoft
  Word," not AI-written text -- see the git history around that change.
- Legal boilerplate is deliberately excluded from scoring, because
  formulaic writing isn't the same thing as AI-written text.

## License

MIT -- see LICENSE. Use it, fork it, adapt it. If you build on the
detection rules or the exclusion filter for something with real stakes
attached to its output, please read TODO.md and FINDINGS.md first --
this project's own measurements are the reason not to trust it blindly.

## What this is not

## What this is not

Not a finished product. Not a validated benchmark -- see FINDINGS.md's
"Limitations" section before citing any number in this repo as
authoritative. Not a replacement for Turnitin, GPTZero, or similar
tools, and not able to produce a single "% AI" confidence score --
that would require Layer 2 (Binoculars), which exists as a script but
isn't wired into the running pipeline.