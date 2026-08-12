# Draft Audit

[![Tests](https://github.com/Gh12890/ai-writing-detector/actions/workflows/tests.yml/badge.svg)](https://github.com/Gh12890/ai-writing-detector/actions/workflows/tests.yml)

A three-layer AI-writing detector built as a working exploration of what
transparent, evidence-driven text auditing looks like: every claim is
backed by a measurement you can re-run, every rule is a readable check
you can inspect, and every finding that turned out wrong -- or
inconsistent -- got corrected and documented in public, not smoothed
over. See FINDINGS.md, LAYER2_FINDINGS.md, HUMANIZER_FINDINGS.md, and
LAYER3_FINDINGS.md for the real results this README summarizes, and
TODO.md for exactly what's built, what's deliberately not, and why.

**Live demo (Layer 1 only):** [your Streamlit Cloud URL]
Layer 2 and Layer 3 need real compute -- see `colab_demo.ipynb`, which
runs all three layers together, free, on your own Google account.

## What this actually is

**Layer 1 -- pattern rules.** 25 active, readable regex-based rules (21
from a published 24-pattern AI-writing taxonomy, plus 4 original
additions built after a live adversarial test found real gaps) split
into structural and lexical tiers, because measurement showed they
behave differently: structural rules (em-dash density, rule-of-three
outlines) showed zero false positives across the human corpus tested;
lexical rules correlated with formal writing register (r=0.722 with
sentence length) independent of AI-ness. Both tiers are reported
separately in the UI. Runs instantly, offline, no GPU needed --
the only layer live in the deployed app, deliberately.

**Layer 2 -- statistical scorer (Binoculars method).** Two scoring
modes were built and tested against each other; full-document pooling
was found to *reduce* human/AI separation rather than improve it -- see
LAYER2_FINDINGS.md. Needs a GPU and ~3GB of model weights, so it's not
in the live web app -- run it via `colab_demo.ipynb` instead.

**Layer 3 -- adversarial robustness testing.** Not a humanizing feature
-- a transparency tool. Answers one question: if a document is flagged,
how much does that verdict survive a paraphrase attack? Two attackers
have been tested and documented separately, deliberately not blended
into one number:

- A local, free model (Qwen2.5-1.5B-Instruct) -- weaker, but costs
  nothing and needs no API key. Inconsistent results: worked on 2 of 3
  train/dev documents, then backfired on both held-out documents --
  direction reversed between the two sets.
- The Claude API -- stronger instruction-following (no chunking
  workaround needed, unlike the local model, which reliably compressed
  whole documents into summaries). More consistent finding: across
  5 documents (3 train/dev, 2 held-out, evaluated separately to avoid
  reusing spent held-out data), the attack never once reduced
  detectability, and backfired on 3 of 5 -- a real, if still small-sample,
  signal that a more fluent paraphraser may introduce its own
  detectable patterns rather than evading detection. Costs money per
  call and requires an Anthropic API key -- the one part of this
  project that isn't free to reproduce.

A separate, manually-run test against a real commercial paraphraser
(Quillbot) is documented in HUMANIZER_FINDINGS.md -- a different attack
strength again, explicitly not treated as equivalent to either of the
above.

## Quick start

**Layer 1 only, locally or deployed:**
​```
pip install -r requirements.txt
python -m pytest tests/ -v   # 95 tests, 96% coverage
streamlit run app.py
​```

**All three layers, free, on your own GPU:**
Open `colab_demo.ipynb` in Google Colab (or use the link in the deployed
app), run the cells in order. Clones this repo directly -- no manual
file uploads needed.
## Real measured results, not aspirational ones

- AI text scored 2.85x higher than human text on Layer 1, across the
  original corpus comparison -- see FINDINGS.md, including a later
  addendum documenting how the corpus and numbers evolved as more
  documents were added.
- One rule (`curly_quotes`) was built, tested, then removed from
  scoring after measurement showed it was detecting "typed in Microsoft
  Word," not AI-written text.
- A formality confound (r=0.722) was found, isolated to lexical rules
  specifically, and fixed by reporting structural and lexical density
  separately.
- Layer 3's two attackers produced genuinely different, sometimes
  contradictory results on the same documents -- reported as-is, with
  the disagreement itself treated as a finding worth stating plainly,
  not a problem to hide.

## What this is not

Not a finished product. Not a validated benchmark -- every findings
document says so explicitly, and none of the numbers here should be
cited as authoritative without reading that document's limitations
section first. Not a replacement for Turnitin, GPTZero, or similar
tools, and deliberately does not produce a single "% AI" confidence
score.

Layer 3 is explicitly not a tool to help evade detection -- it exists
to report how confident you should be in a detection verdict, not to
help anyone get past one.

## License

MIT -- see LICENSE. If you build on the detection rules or the
adversarial-testing approach for something with real stakes attached,
read TODO.md and the findings docs first.