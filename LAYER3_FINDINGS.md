\# Layer 3: Adversarial Robustness Testing (Local Paraphrase Attack)



\## What this is, and isn't

Not a user-facing "humanize this text" feature. This tests how much a Layer 1/2

verdict survives a cheap, fully automated paraphrase attack run locally on

Qwen2.5-1.5B-Instruct (the same model already loaded as Layer 2's performer --

no additional model, no additional GPU memory).



This is a WEAKER attack than the manually-run Quillbot test documented in

HUMANIZER\_FINDINGS.md. The two are not comparable and should never be reported

as equivalent evidence. This module answers: "how robust is detection against a

cheap, automatable, self-hosted attack?" -- not "how robust is detection against

the best commercial humanizer available?"



\## Methodology

\- Model: Qwen2.5-1.5B-Instruct, single-shot prompted paraphrase per chunk.

\- Text is split into \~120-word chunks by sentence boundary (not paragraph --

&#x20; see "Chunking, and why it needed fixing" below), each paraphrased

&#x20; independently, then concatenated.

\- Run against train/dev AI corpus only (sample08, sample10, sample11).

&#x20; Held-out files (sample07, sample12) were NOT used -- per SPLIT.md, they

&#x20; remain reserved for a single final evaluation, not method development.

\- Both Layer 1 (flag count, rule IDs) and Layer 2 (Binoculars score) recorded

&#x20; before and after paraphrase for each document.



\## Chunking, and why it needed fixing

First attempt (whole-document, single generation call, max\_new\_tokens=1024):

paraphrase came back at 18% of original length (1222 -> 216 words). Raising

the token budget to 2048 did not fix it (still 25% -- 1222 -> 307 words).

Root cause: at this model size, single-shot "paraphrase this" on a long input

defaults to summarization, not paraphrase, regardless of available token

budget. Splitting by paragraph also failed, because sample08.txt had no

internal paragraph breaks (one 1211-word block).



Fix: split by sentence into \~120-word chunks. This restored length fidelity

(0.93-1.08 ratio across all three test documents) and is the method used for

all results below. This is itself a finding: local sub-2B models are not

reliable paraphrasers on long-form input without chunking, independent of

anything about detection.



\## Results (n=3, train/dev corpus)



| Document | Flags (orig -> para) | Rules lost | Rules kept | Rules newly introduced | Binoculars (orig -> para) | Direction |

|---|---|---|---|---|---|---|

| sample08 | 8 -> 2 | rule\_of\_three\_outline, superficial\_ing\_analysis | em\_dash\_density | copula\_avoidance | 1.0781 -> 1.2266 | attack worked |

| sample10 | 1 -> 0 | em\_dash\_density | none | none | 1.2031 -> 1.2422 | attack worked (weak signal, orig only had 1 flag) |

| sample11 | 2 -> 4 | generic\_positive\_conclusion | superficial\_ing\_analysis | ai\_vocabulary, copula\_avoidance | 1.1484 -> 0.9102 | attack backfired |



Word count ratios (paraphrase/original): 0.93, 0.97, 1.08 -- all three runs are

length-trustworthy, not truncation artifacts.



\## Interpretation

No consistent direction across n=3. Two of three documents showed the

paraphrase attack reducing both Layer 1 flags and Layer 2 AI-likelihood;

one showed the opposite on both layers simultaneously. This is not resolved

by adding more documents casually -- it is consistent with the pattern

already documented in LAYER2\_FINDINGS.md, where two real AI essays each had

Layer 1 and Layer 2 take turns being the stronger signal. The honest reading

is that detection AND evasion both behave inconsistently across documents at

this scale, not that the attack "works" or "doesn't work" in general.



A second, unplanned finding: paraphrasing does not only remove flags, it

introduces new ones. copula\_avoidance and ai\_vocabulary both appeared in

paraphrased text where they were absent in the original, across two of the

three documents. A paraphrase attack is not a clean "quieter" version of the

original text -- it trades one set of surface AI-tells for a different set,

sometimes a larger one (sample11).



\## Explicitly not done here

\- Not run against the held-out test set (sample07, sample12) -- reserved,

&#x20; per SPLIT.md, for a single final evaluation pass, not iterative testing.

\- No rule thresholds or exclusion filters were changed in response to any

&#x20; result in this document.

\- No comparison is drawn against the Quillbot-based HUMANIZER\_FINDINGS.md

&#x20; numbers beyond noting they measure different attack strengths.



\## Attempted: Stronger-Model Comparison (Not Completed)



An attempt was made to repeat this test using a larger model (Qwen2.5-7B-Instruct,

then Qwen2.5-3B-Instruct as a fallback) as a stronger paraphrase attacker, to

compare against the 1.5B results above. Both attempts crashed the free-tier

Colab T4 instance on RAM during model loading, before any paraphrase could be

generated. This is a resource constraint of the free-tier environment, not a

finding about attack strength -- no data was produced and no conclusion should

be drawn from this section beyond "not tested at this model size, on this

infrastructure." Revisiting this would require either a paid compute tier or

8-bit/4-bit quantization, neither pursued here.

