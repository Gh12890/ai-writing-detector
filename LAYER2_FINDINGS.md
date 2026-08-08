\# Findings: Layer 2 (Binoculars) - first real run



The first time layer2\_binoculars.py's method has actually been

executed against real data, after weeks of sitting as a designed-but-

unrun script. Run on Google Colab's free T4 GPU tier, not this repo's

own environment (still no GPU/network access here). Small-sample,

first-pass results -- read alongside the same "Limitations" discipline

as FINDINGS.md, not as a validated result.



\## Setup



\- Model pair: Qwen/Qwen2.5-1.5B (observer) / Qwen/Qwen2.5-1.5B-Instruct

&#x20; (performer) -- NOT the paper's original Falcon-7B pair. Smaller,

&#x20; free-tier-runnable, unvalidated at this scale.

\- Method: unmodified binoculars\_score() from layer2\_binoculars.py --

&#x20; ratio of perplexity to cross-perplexity between the two models.

\- Truncation caveat, real and unresolved: the tokenizer call uses

&#x20; max\_length=512, so any document over \~380-400 words only has its

&#x20; opening portion scored. Several corpus/ files (3,000-7,000 words)

&#x20; were effectively scored on their introduction alone, not the full text.

\- Corpus: the same 6 human / 7 AI documents from FINDINGS.md.



\## Headline result, as first reported



|              | Mean distance from 1.0 |

|--------------|--------------------------|

| Human (n=6)  | 0.2148                   |

| AI (n=7)     | 0.1161                   |



Direction correct -- AI text scored closer to 1.0 (more "machine-like"

per the paper's convention) than human text, on average.



\## Why that headline number is misleading on its own



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



\## The more interesting, more concerning finding



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

ai\_vocabulary and promotional\_language. Seeing it show up

independently in a completely different detection method (statistical,

not pattern-matching) makes the "this might be a formality detector, not

an AI detector" concern more serious, not less.



\## Limitations, stated plainly



\- n=6 human, n=7 AI. Same small-sample caveat as FINDINGS.md, and

&#x20; more acute here since the gap itself is this fragile to single points.

\- Wrong model scale. Qwen2.5-1.5B, not the paper's Falcon-7B --

&#x20; unknown how much of the weak separation is scale-related.

\- Truncation. Longer documents scored on \~400 words, not their

&#x20; full length.

\- No calibrated threshold. There is no principled cutoff for

&#x20; "this score means AI" on this model pair -- every number here is

&#x20; relative (human mean vs. AI mean), not an absolute verdict.

\- Formality confound, unresolved. See above -- this run cannot

&#x20; distinguish "detects AI" from "detects formal register" any better

&#x20; than Layer 1 could on its own.



\## What would actually resolve the open questions



\- Re-run with human samples that vary in length independent of

&#x20; register (a short formal document, a long informal one) to separate

&#x20; length effects from formality effects

\- Re-run at the paper's original Falcon-7B scale, or with a larger

&#x20; Qwen pair, to check whether separation improves with model size

\- A held-out corpus specifically designed to vary formality

&#x20; independent of authorship -- e.g. formal human writing vs. informal

&#x20; human writing vs. formal AI writing vs. informal AI writing -- to

&#x20; directly test the confound instead of inferring it after the fact

\- Full-document scoring (chunking + averaging across windows) instead

&#x20; of 512-token truncation, for the longer documents



\## Update: full-document pooling tested as a truncation fix -- made it worse



The 512-token truncation flagged above as a limitation was tested directly:

chunk each document into consecutive 512-token windows, score each with the

same binoculars\_score(), and pool cross-entropy sums across all chunks

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

