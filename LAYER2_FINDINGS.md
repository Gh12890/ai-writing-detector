
# Findings: Layer 2 (Binoculars) - first real run

The first time layer2_binoculars.py's method has actually been
executed against real data, after weeks of sitting as a designed-but-
unrun script. Run on Google Colab's free T4 GPU tier, not this repo's
own environment (still no GPU/network access here). Small-sample,
first-pass results -- read alongside the same "Limitations" discipline
as FINDINGS.md, not as a validated result.

## Setup

- Model pair: Qwen/Qwen2.5-1.5B (observer) / Qwen/Qwen2.5-1.5B-Instruct
  (performer) -- NOT the paper's original Falcon-7B pair. Smaller,
  free-tier-runnable, unvalidated at this scale.
- Method: unmodified binoculars_score() from layer2_binoculars.py --
  ratio of perplexity to cross-perplexity between the two models.
- Truncation caveat, real and unresolved: the tokenizer call uses
  max_length=512, so any document over ~380-400 words only has its
  opening portion scored. Several corpus/ files (3,000-7,000 words)
  were effectively scored on their introduction alone, not the full text.
- Corpus: the same 6 human / 7 AI documents from FINDINGS.md.

## Headline result, as first reported

|              | Mean distance from 1.0 |
|--------------|--------------------------|
| Human (n=6)  | 0.2148                   |
| AI (n=7)     | 0.1161                   |

Direction correct -- AI text scored closer to 1.0 (more "machine-like"
per the paper's convention) than human text, on average.

## Why that headline number is misleading on its own

One document accounts for most of the gap. corpus/sample05.txt
(WhatsApp export, 544 words, the shortest document in the set) scored a
distance of 0.6016 -- nearly 3x the next-highest score across all 13
documents. Removing it:

|              | Mean distance from 1.0 (sample05 excluded) |
|--------------|-----------------------------------------------|
| Human (n=5)  | 0.1375                                         |
| AI (n=7)     | 0.1161                                         |

The gap drops from 0.0987 to 0.0214 -- about 80% of the apparent
signal disappears when one outlier is removed. The direction still
holds, but "AI text is noticeably more machine-like on average" and "AI
text is very slightly more machine-like on average, driven mostly by
one atypical human document" are different claims, and the second one
is the honest one.

Plausible explanation for the outlier, unconfirmed: the two shortest
documents in the whole corpus (sample05, 544 words; sample06, 365
words, both WhatsApp exports) have the two highest human distances
(0.6016 and 0.2578). Perplexity-based scoring is known to get noisier on
short text -- fewer tokens, less stable an average. This could be a real
effect (informal writing genuinely looks most human) or a length
artifact. Two data points can't distinguish between those.

## The more interesting, more concerning finding

Within the human corpus, Layer 1's flag count and Layer 2's
machine-likeness are suspiciously well correlated:

| Document | Layer 1 flags        | Binoculars distance from 1.0 |
|----------|-----------------------|-------------------------------|
| sample03 | 7 (most flagged)      | 0.0352 (most machine-like)    |
| sample02 | 6                     | 0.0508                        |
| sample01 | 1                     | 0.1484                        |
| sample04 | 1                     | 0.1953                        |
| sample06 | 0                     | 0.2578                        |
| sample05 | 0 (least flagged)     | 0.6016 (most human-like)      |

Near-perfect rank agreement, on confirmed human text. Two
independently-built detectors agreeing on document ranking sounds like
validation, but since every document here is genuinely human, it more
likely means both methods are tracking the same underlying variable --
formal register -- rather than independently detecting authorship.
This is the same confound already flagged in FINDINGS.md regarding
ai_vocabulary and promotional_language. Seeing it show up
independently in a completely different detection method (statistical,
not pattern-matching) makes the "this might be a formality detector, not
an AI detector" concern more serious, not less.

## Limitations, stated plainly

- n=6 human, n=7 AI. Same small-sample caveat as FINDINGS.md, and
  more acute here since the gap itself is this fragile to single points.
- Wrong model scale. Qwen2.5-1.5B, not the paper's Falcon-7B --
  unknown how much of the weak separation is scale-related.
- Truncation. Longer documents scored on ~400 words, not their
  full length.
- No calibrated threshold. There is no principled cutoff for
  "this score means AI" on this model pair -- every number here is
  relative (human mean vs. AI mean), not an absolute verdict.
- Formality confound, unresolved. See above -- this run cannot
  distinguish "detects AI" from "detects formal register" any better
  than Layer 1 could on its own.

## What would actually resolve the open questions

- Re-run with human samples that vary in length independent of
  register (a short formal document, a long informal one) to separate
  length effects from formality effects
- Re-run at the paper's original Falcon-7B scale, or with a larger
  Qwen pair, to check whether separation improves with model size
- A held-out corpus specifically designed to vary formality
  independent of authorship -- e.g. formal human writing vs. informal
  human writing vs. formal AI writing vs. informal AI writing -- to
  directly test the confound instead of inferring it after the fact
- Full-document scoring (chunking + averaging across windows) instead
  of 512-token truncation, for the longer documents

## Update: full-document pooling tested as a truncation fix -- made it worse

The 512-token truncation flagged above as a limitation was tested directly:
chunk each document into consecutive 512-token windows, score each with the
same binoculars_score(), and pool cross-entropy sums across all chunks
before computing a single ratio (not an average of per-chunk ratios --
pooling at the cross-entropy level before the final division, which is the
mathematically correct way to combine chunks of different sizes).

This did not fix the truncation limitation. It made the human/AI
separation worse, not better, once read past the headline number.

|                | Mean distance from 1.0, truncated (512 tok) | Mean distance from 1.0, full-document pooled |
|----------------|-----------------------------------------------|-------------------------------------------------|
| Human (n=6)    | 0.2148                                         | 0.1965                                           |
| AI (n=7)       | 0.1161                                         | 0.1366                                           |
| Gap            | 0.0987                                         | 0.0599 (39% smaller)                             |

And with the sample05 outlier excluded (same outlier flagged earlier in
this document), the direction actually flips:

|                | Human mean (n=5, sample05 excluded) | AI mean (n=7)                                  |
|----------------|----------------------------------------|--------------------------------------------------|
| Truncated      | 0.1375                                  | 0.1161 (AI closer to 1.0 -- correct direction)    |
| Full-document  | 0.1193                                  | 0.1366 (human closer to 1.0 -- wrong direction)   |

This wasn't one noisy pair -- it was a consistent, systematic shift.
Comparing truncated vs. full-document distance per document: 6 of 7 AI
documents moved further from 1.0 (more human-looking) under full-document
pooling. Only 1 AI document (sample13) moved closer. Meanwhile 2 of 6 human
documents (sample01, sample04) moved closer to 1.0 (more machine-looking).
That's a real, repeatable pattern in this run, not scatter.

Working hypothesis for why, not confirmed: truncation kept only each
document's opening section -- plausibly the most deliberately-composed part
of any piece of writing, human or AI. Pooling in the middle and later
sections may add noisier, less distinctive material that dilutes whatever
signal the opening carried, for both classes of text. Untested against
this data specifically.

sample05 remains unexplained and is now the single most consequential
data point in this entire Layer 2 analysis -- it drove the outlier
finding in the original truncated run AND remains the dominant outlier
in the full-document run (distance 0.5830, nearly 3x the next-highest
score in either corpus, either method). It has not been directly
inspected for content -- only its aggregate stats (544 words, shortest
document in the human corpus, WhatsApp export) have been reasoned about.
Actually reading it and checking for anything unusual (heavy quotation,
unusual formatting, code-switching, non-standard characters) is the
single highest-value remaining step in this whole Layer 2 investigation,
and it's a five-minute task, not a re-run.

Conclusion: full-document pooling is not currently a net improvement
and should not be treated as "the fix" for the truncation limitation.
The original 512-token approach and this pooled approach are both weak,
in different and not-yet-fully-understood ways. Neither is validated
enough to trust over the other without more data and, specifically,
without resolving what's actually happening in sample05.

## sample05 outlier -- investigated, plausibly explained

Actually read, not just reasoned about from aggregate stats: sample05 is
a single-voice, emotionally specific personal narrative -- one person's
private disclosure of significant personal hardship, not a back-and-forth
conversation. No further content details are recorded here; this document
contains private personal material and stays excluded from git via
.gitignore, same as the rest of corpus/.

This plausibly explains the extreme score. Perplexity measures how
predictable text is to a model trained on generic text. Deeply specific,
personal emotional disclosure is about as far from "generic, predictable"
language as text gets -- there's little in generic training data that
resembles an unrepeatable, individual account like this one. That
unpredictability is exactly what a high Binoculars distance-from-1.0
score reflects, and it would be concentrated further by the document
being short (544 words, the shortest in the corpus) and single-voice (no
conversational turn-taking to dilute it).

Reframe: this isn't an unexplained anomaly or evidence the method is
broken -- it's a plausible instance of the method correctly registering
genuinely unpredictable, specific human writing as strongly human. It's
an extreme data point, not necessarily a flawed one.

Not confirmed beyond this single case. Would need more emotionally
specific, single-voice personal-narrative samples in the corpus to know
whether this is a general pattern (this whole category of writing scores
as an outlier) or something particular to this one document. Given the
privacy of this material, deliberately expanding that specific category
in the corpus is not a direction this project intends to pursue.

## A second real essay, the reverse pattern: Layer 2 carries the signal this time, not Layer 1

A second ChatGPT-generated essay (Donald Trump's impact on U.S.
politics, ~545 tokens) tested the same way as the India-US-Iran essay.
Results:

|                                    | Layer 1                                    | Layer 2 (full-document) |
|------------------------------------|---------------------------------------------|----------------------------|
| This essay                        | 2 flags (0 structural, 2 lexical: vague_attribution, meta_summary_framing) | distance 0.1174 |
| India-US-Iran essay (after fixes) | 7 flags (5 structural, 2 lexical)          | distance 0.2670 |
| Human corpus mean                 | --                                          | 0.1193 (sample05 excluded) |
| AI corpus mean                    | --                                          | 0.1366 |

**This essay's Layer 2 score (0.1174) is lower than both the human
mean (0.1193) AND the AI mean (0.1366)** -- reading as more
machine-like than the average confirmed-AI document in the whole
corpus. Layer 1, on the same essay, is comparatively weak: two genuine
lexical catches, nothing structural. repeated_transitions and
prose_tricolon correctly stayed silent -- "therefore" only appears
twice (below the minimum count of 3 regardless of rate), and nothing
matches prose_tricolon's five anchored framing verbs. Not a bug on
either rule; the essay genuinely doesn't contain those specific forms.

**This is the reverse of what happened on the India-US-Iran essay**,
where Layer 1 carried the signal (7 flags, largely structural) and
Layer 2 stayed flat and human-reading (0.2670, above both corpus
means). Here, Layer 2 carries the signal and Layer 1 is comparatively
quiet. Across the two real AI essays tested so far, each layer has
been the stronger signal exactly once. Neither layer is consistently
better -- which is the actual argument for showing both scores rather
than either alone, now demonstrated on two independent real documents
instead of asserted as a design principle.

**A real Layer 1 gap surfaced by this essay, not yet built:** the
essay's introduction and conclusion each list the same ~5 items
("political communication, political policies, political parties,
elections, and American society in general" / "political
communication, the Republican Party, political polarization,
elections, and public attitudes toward government and democracy") --
a near-verbatim restated enumeration, a recognizable formulaic-essay
habit distinct from anything currently built. Not rule_of_three_outline
(not a numbered list), not prose_tricolon (five items, not three, no
anchoring framing verb, and the pattern is the repetition between
intro and conclusion, not the list itself). Logged here as a candidate
for future work, not built tonight -- this project's rate on new rules
tonight was one real two-iteration regression per rule added, and
that's reason enough to not add a fourth without deliberate, separate
testing.

## Full corpus scoring session: human/AI distance overlap (2026-08-14)

First time all 11 corpus documents (6 human, 5 AI train/dev -- sample07/12
held-out excluded, per SPLIT.md) were scored through Layer 2 in a single
session and compared as complete groups, rather than one-off individual
documents. Truncated score (first ~512 tokens) used throughout, per this
project's existing preference for that method over full-document pooling
(see "Full-document pooling" section above).

### Raw results

| Document | Score | Distance from 1.0 |
|---|---|---|
| sample02 (human) | 0.9492 | 0.0508 |
| sample03 (human) | 0.9648 | 0.0352 |
| sample04 (human) | 1.1953 | 0.1953 |
| sample05 (human) | 1.6016 | 0.6016 |
| sample14 (human) | 1.1875 | 0.1875 |
| sample15 (human) | 0.9102 | 0.0898 |
| sample08 (AI) | 1.0781 | 0.0781 |
| sample09 (AI) | 1.1328 | 0.1328 |
| sample10 (AI) | 1.2031 | 0.2031 |
| sample11 (AI) | 1.1484 | 0.1484 |
| sample13 (AI) | 0.9375 | 0.0625 |

### The finding

Human mean distance across all 6: 0.1934. But sample05 (informal
WhatsApp-style text) is a severe outlier at 0.6016 -- roughly 3-5x every
other document's distance, human or AI. Excluding it, human mean drops
to 0.1117.

AI mean distance across the 5 train/dev documents: 0.1250.

**Human mean (excl. outlier) and AI mean are close: 0.1117 vs 0.1250.**
More importantly, the actual ranges overlap almost completely:

- Human (excl. sample05): 0.0352 - 0.1953
- AI: 0.0625 - 0.2031

The only non-overlapping slivers are below 0.0352 (below both groups'
observed minimums) and above 0.2031 (above both groups' observed
maximums) -- meaning most of the plausible range a real document could
land in gives no reliable separation by this metric alone, at this
corpus size.

### What this means, and doesn't mean

This does NOT mean Binoculars/the truncated score is broken or useless
-- the Binoculars paper's own validation was done on far larger, more
controlled corpora than this project's 11 documents. What it does mean:
**this project's own corpus is too small, and too varied in register,
to support confident directional claims from this score alone.**
Sample05 alone illustrates why -- a single informal, conversational
human document sits so far outside this small corpus's typical range
that it alone shifts the human mean above the AI mean, inverting the
expected direction if it isn't excluded.

### Consequence: UI language changed

The Colab notebook's plain-language Layer 2 summary (added 2026-08-13)
originally used three confident-sounding zones ("strongly" / "somewhat"
/ "not particularly" AI-like) anchored to placeholder thresholds that
were never checked against real data. Once this full-corpus session
ran, those placeholder thresholds were revealed to sit inside the
overlap band entirely -- meaning the confident wording was not
supportable.

Replaced with a hedged two-lean version (see colab_demo.ipynb):
"closer to this project's typical AI-document scores" / "closer to
...human-document scores" / "sits in the range where human and AI
documents overlap -- no reliable lean either way", using the real
measured means above as anchors (midpoint 0.1183, ±0.02 buffer band
for "unclear"), with a persistent caveat about the overlap shown on
every result, not just when the two scoring methods disagree.

### Not yet done

- This measurement used only the current train/dev corpus (11
  documents). Should be re-run as the corpus grows -- the overlap
  finding may narrow or persist at higher n, and won't be known until
  measured again.
- sample05's exclusion from the human anchor calculation is a judgment
  call, not independently validated -- it is still scored and
  displayed normally when analyzed individually; it is only excluded
  from setting the comparison anchors, to avoid one outlier defining
  the boundary for every other document.
- No held-out documents (sample07, sample12, sample09, sample13 in
  their Layer-3 held-out role) were used to set these anchors --
  consistent with existing project discipline, though note sample09
  and sample13 ARE part of the AI train/dev group used here for Layer
  2 scoring specifically, a different use than their Layer-3 held-out
  designation.