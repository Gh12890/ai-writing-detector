# TODO - Layer 1 pattern coverage

## Status
22 of the SKILL.md's 24 official patterns have working detection logic.
21 of those are actively SCORED. Pattern #18 (Curly Quotation Marks) was
implemented, tested, then deliberately REMOVED from scoring based on
real evidence: measuring it against an actual 4496-word human-written
document (Word-authored, confirmed) showed it producing 42 of 48 total
flags (87.5%) -- entirely because Microsoft Word autocorrects straight
quotes to curly ones by default, not because of anything resembling
AI-written text. The detection function is kept in rules.py (unregistered)
in case it's useful differently later, but it no longer counts toward
any score. This is the first pattern removed on real measured evidence
rather than kept or dropped by design intuition -- see git history for
the actual finding.

2 additional rules (meta_summary_framing, parallel_bullet_em_dash) are
implemented but are NOT part of the original 24. A legal-boilerplate
exclusion filter is also implemented (see below) -- separate from
pattern coverage, it suppresses flags that fall inside statutory
citations, case citations, or standard contract phrases.

## Implemented (22/24, verified against SKILL.md)
- [x] #1  Undue Emphasis on Significance, Legacy, Broader Trends -> significance_inflation
- [x] #2  Undue Emphasis on Notability and Media Coverage -> notability_emphasis
- [x] #3  Superficial Analyses with -ing Endings -> superficial_ing_analysis
- [x] #4  Promotional and Advertisement-like Language -> promotional_language
- [x] #5  Vague Attributions and Weasel Words -> vague_attribution
- [x] #6  Outline-like "Challenges and Future Prospects" Sections -> outline_challenges_section
- [x] #7  Overused "AI Vocabulary" Words  -> ai_vocabulary
- [x] #8  Avoidance of is/are (Copula Avoidance) -> copula_avoidance
- [x] #9  Negative Parallelisms          -> negative_parallelism
- [x] #10 Rule of Three Overuse          -> rule_of_three_outline (partial:
      only catches numbered-list form, not rule-of-three inside prose)
- [x] #12 False Ranges                   -> false_ranges
- [x] #13 Em Dash Overuse                -> em_dash_density
- [x] #14 Overuse of Boldface            -> boldface_overuse
- [x] #15 Inline-Header Vertical Lists   -> inline_header_list
- [x] #17 Emojis                         -> emoji
- [x] #18 Curly Quotation Marks          -> curly_quotes (DETECTED but NOT SCORED -- see Status above)
- [x] #19 Collaborative Communication Artifacts -> chatbot_artifact
- [x] #20 Knowledge-Cutoff Disclaimers   -> knowledge_cutoff_disclaimer
- [x] #21 Sycophantic/Servile Tone       -> sycophantic_tone
- [x] #22 Filler Phrases                 -> filler_phrase
- [x] #23 Excessive Hedging              -> hedge_stacking
- [x] #24 Generic Positive Conclusions   -> generic_positive_conclusion

## Not yet built (2/24) -- deliberately, not just unstarted
- [ ] #11 Elegant Variation (Synonym Cycling) -- needs coreference /
      tracking the same referent across a document, not a regex problem.
      Would need real NLP (spaCy entity linking at minimum) to do honestly.
- [ ] #16 Title Case in Headings -- heuristic-fragile. A cheap
      capitalization-ratio check risks flagging legitimate headings and
      proper-noun-heavy sentences as false positives. Needs a better
      approach than "count capital letters" before it's worth shipping.

## Legal boilerplate exclusion filter -- DONE (v1), scope-limited
Implemented in layer1/exclusions.py: statutory citations ("Section X of
the Y Act, YYYY"), case citations (AIR/SCC formats), and a short list of
standard contract phrases (WHEREAS, IN WITNESS WHEREOF, etc.) are
detected and any Layer 1 span-flag overlapping them is suppressed.
Verified with a deliberately constructed overlap test, not just a
"doesn't misfire" check.

Known v1 limitations:
- No fuzzy matching against a real standard-clause library (the original
  design called for this; v1 only does exact citation/phrase patterns)
- Citation regexes are Indian-law-specific (Section/Act/AIR/SCC format)
  and won't recognize other jurisdictions' citation conventions

FIXED: document-level flags (em_dash_density, boldface_overuse) are now
exclusion-aware. Excluded-span characters get masked out before either
rate is computed, so a document that's mostly legal citations can't trip
a document-level flag purely from characters sitting inside boilerplate
that's already excluded at the span level. Verified with real numbers,
not just asserted: a test case with em dashes deliberately placed inside
a citation span went from a 125.0/1000w raw rate (would massively
exceed the 3.0 threshold) to 0.0 after masking, while a contrast case
with em dashes outside any citation still triggers normally. This also
required widening the statute-citation regex to allow em dashes/hyphens
in act titles, since long act titles legitimately sometimes have a
dash-separated subtitle -- a real improvement, not just a test fixture.

## False-positive rate measurement -- tool built, real comparison done, still small-n
scripts/measure_fpr.py and scripts/compare_corpora.py are built and
tested (5 tests total). Point measure_fpr.py at a folder of .txt files
for a single-corpus report; compare_corpora.py takes two folders and
reports both side by side plus a per-rule human-vs-AI breakdown.

Real results exist now -- see FINDINGS.md for the full writeup. Summary:
6 human documents (16,533 words) vs. 7 AI documents (7,328 words,
across ChatGPT/Gemini/Claude) measured. AI text scored 2.85x higher
overall. Structural rules (rule_of_three_outline, em_dash_density) show
clean, reproducible discrimination -- zero human false positives across
all 3 models. Vocabulary rules (ai_vocabulary, promotional_language) are
weaker and human-leaning. Already produced one real, actionable finding
along the way -- curly_quotes removal above, found directly from this
measurement, not from guessing.

Still needs: 50+ documents per side for anything resembling a real
benchmark (see FINDINGS.md "Limitations" for the full list of what's
still missing -- controlled prompts, varied human registers, blind
review). Current numbers are directional, not final.

## Also not built, separate from the above
- Layer 2 (statistical scorer) not built at all -- separate script exists
  outside this repo, requires GPU, not yet run for real.

## Formality confound -- partial fix shipped (tier split)
Real problem, real evidence, real fix -- not a guess. analyze_confound.py
found r=0.722 correlation between flag density and avg sentence length
across the human corpus in FINDINGS.md. Investigating which rules
produced that: 100% of the flags in that correlation came from lexical
(word/phrase-list) rules -- rule_of_three_outline and em_dash_density,
the two rules that survived all 3 AI models with zero human false
positives, never fired on a single human document, so they couldn't
have been part of that correlation either way.

Fix shipped: every rule now carries a tier ("structural" or "lexical").
AnalysisResult reports structural_density_per_1000w and
lexical_density_per_1000w separately instead of one blended number.
analyze_confound.py now computes correlation per tier, not just
overall. app.py's UI shows both densities and both flag lists
separately, with an explicit caption explaining why.

Honest limits of this fix, stated plainly:
- This does NOT prove structural rules are confound-free. They simply
  haven't fired often enough on human text yet to test either way --
  "None" (undefined correlation, no variance) is not the same claim as
  "zero correlation, proven clean." The code and the UI both say this
  explicitly rather than let the silence read as validation.
- Tier assignment (9 structural, 14 lexical) was done by judgment, not
  measurement -- e.g. superficial_ing_analysis is flagged in code
  comments as a borderline case (fixed verb list, but structural
  trigger position).
- Real next step: keep running analyze_confound.py as corpus/ grows.
  If structural rules eventually fire enough to get a real correlation
  number, that's the point this hypothesis actually gets tested rather
  than assumed.

## CI added -- tests now run automatically, not just by hand
.github/workflows/tests.yml runs the full pytest suite on every push and
pull request to master, on Python 3.11 and 3.12. Before this, "69 tests
passing" was only verifiable by whoever ran pytest locally and pasted
the output -- now it's checked automatically and visible as a public
badge on README.md. Does not run Layer 2 (layer2_binoculars.py isn't in
the pytest suite and needs a GPU CI runners don't have) -- CI covers
Layer 1, the exclusion filter, and the measurement/analysis scripts only.

## Test coverage measured -- found and closed a real gap
Running pytest-cov for the first time found something worth admitting:
scripts/compare_corpora.py had 0% coverage despite tests/test_compare_corpora.py
existing -- that file's own docstring said outright it only tested the
shared compute_fpr_stats() dependency, never compare_corpora.py's own
compare() function. scripts/measure_fpr.py was similarly thin (52%) for
the same reason -- its main() print function was untested too.

Added tests/test_compare_corpora_cli.py and tests/test_measure_fpr_cli.py
to actually exercise both files' own output functions (using pytest's
capsys to check printed output, not just return values). Coverage moved
from 78% to 93% overall. Now wired into CI (.github/workflows/tests.yml)
so this number gets recomputed on every push, not just measured once
and left to go stale like several other numbers in this project did
before someone checked them again.

Remaining gaps, honestly: layer1/rules.py 96% (lines 69-74 uncovered),
layer1/scorer.py 93% (lines 53, 57-60, 79), scripts/analyze_confound.py
93% (lines 106-109), scripts/measure_fpr.py 92% (lines 91-94),
scripts/compare_corpora.py 87% (lines 55, 57, 64-67). Not yet
investigated line by line -- next person picking this up should check
what's actually on those lines before assuming they're low-risk.

## LICENSE added -- a gap that was flagged and then dropped, now fixed
Worth admitting: a LICENSE file was identified as missing when the CI
work started, then never actually added -- coverage measurement got
the follow-through instead and this got left as an open thread. Fixed
now: MIT license added, README.md points to it. Without a license file,
GitHub's default terms mean nobody can legally reuse or fork this
repo, which undercut the "here's a working example" portfolio framing
this project has been built around the whole time.

## Layer 2 integrated into the Streamlit app -- real gap closed, honestly
Two things were true before tonight that shouldn't have been: app.py
only ever used Layer 1 (the "Layer 2 not built in yet" banner had sat
unchanged since the night it was written), and layer2_binoculars.py --
including the full-document pooling code that LAYER2_FINDINGS.md
reports real numbers from -- had never actually been committed to this
repo at all. It only ever existed as a standalone downloadable file and
in Colab notebook cells. That's now fixed: layer2_binoculars.py is a
real file in this repo, both scoring functions (truncated and
full-document pooled) are in it, and app.py has an opt-in checkbox that
runs both and displays them side by side with the honest caveat that
neither is validated and full-document pooling was tested and found to
not help (see LAYER2_FINDINGS.md).

Deliberately opt-in, not automatic: loading two 1.5B-parameter models on
CPU (no GPU on the machine this runs on) takes real time and downloads
~3GB on first use. Making that automatic on every "Run analysis" click
would make the whole app unusable.

Tested: the pooling/chunking math (5 tests, tests/test_layer2_binoculars.py)
using fully synthetic fake models -- no real weights, no network, so
these run in CI. NOT tested automatically: load_models() itself, which
needs real network access and would make CI slow/flaky/costly if it
ran on every push (same reasoning as the Layer 2 GPU work throughout
this project). Manually verified once, in this session, that the app
correctly catches a real model-loading failure and shows a clean error
instead of crashing -- confirmed against this sandbox's actual blocked
network, not a mocked failure.

layer2_binoculars.py's own coverage is 71% (vs. 93% for layer1+scripts)
-- the uncovered lines are load_models() and the __main__ CLI block,
both excluded from automated testing for the reason above. Not folded
into the main coverage number reported elsewhere, since mixing
by-design-untestable code into that figure would make an honest 93%
look like a worse 89% for the wrong reason.

Still unverified: whether this actually works end-to-end on a real
Windows machine, with real internet, on real new text. That's the next
step, and it needs a human to actually click the checkbox and watch
what happens -- same as every other piece of Layer 2 work so far.

## Real live miss found and fixed: essay explicitly prompted to sound AI
Tested in the actual Streamlit app (not a synthetic example): a ChatGPT
essay, explicitly asked to "sound more AI generated," scored as MORE
human-like than either reference corpus's average, on both Layer 1 (2
flags total) and Layer 2 (distance 0.3085 from 1.0, vs. corpus means of
0.1193/0.1366). See FINDINGS.md for the full writeup.

Three fixes shipped: chatbot_artifact now catches "Sure, here's"/"Sure
-- here's"; new repeated_transitions rule (3+ uses of the same
discourse marker); new prose_tricolon rule (rule-of-three lists
embedded in prose, not just numbered lists -- closes the specific gap
rule_of_three_outline has had documented as unfixed since it was
first built). Real result on the same essay: 2 flags become 7.

Now 25 active scored rules (was 23): 21 from the SKILL.md's 24-pattern
taxonomy + 4 original additions (meta_summary_framing,
parallel_bullet_em_dash, repeated_transitions, prose_tricolon).

prose_tricolon has a real, documented, accepted false-positive risk:
it will also fire on legitimate human sentences shaped like "described
as X, Y, and Z" that aren't AI-generated (e.g. "The store was described
as small, clean, and well-organized") -- narrowing the pattern further
would likely also cut real catches, so this is a deliberate tradeoff,
not an oversight. Corpus measurement will show whether it's a practical
problem as more human samples get tested.

Not yet done: re-running compare_corpora.py and analyze_confound.py
against the full corpus with these three new rules active. Every
number in FINDINGS.md above the essay section was measured before this
fix existed -- the real aggregate impact on the 2.85x gap is currently
unknown, only inferred from this one document.

## Real regression found and fixed: repeated_transitions inverted the human/AI comparison
Re-running compare_corpora.py after the previous fix (exactly the
follow-through the previous entry said was needed) found repeated_transitions
firing 31 times on human text and 0 times on AI text -- inverting the
whole comparison from AI 2.85x human to AI 0.93x human. Root cause: fixed
"3+ uses" threshold with no document-length scaling, unlike em_dash_density
and boldface_overuse which were already built as rate checks for exactly
this reason. Fixed: threshold now scales as max(3, word_count/500).
Verified against the real essay (still fires) and a synthetic long
document with the same natural repetition rate (no longer fires).
New regression test locks this in. 89 tests passing.

Still needs: re-running compare_corpora.py and analyze_confound.py
again against this fix to get the real, current aggregate numbers --
same "not yet done" item as before, now against corrected code instead
of the buggy version.

## repeated_transitions fix, take two -- the first fix was insufficient
Re-running compare_corpora.py against the length-scaled fix showed real
but incomplete improvement (31 -> 22 human false positives, ratio only
recovered to 1.16x vs the original 2.85x). Root cause of the shortfall:
the length scaling worked out to a constant 2.0/1000w target rate,
against a confirmed real case running at 10.3/1000w -- correct
direction, wrong magnitude. Replaced with an explicit rate threshold
(7.0/1000w, min count 3), with a new regression test specifically
covering the scenario that exposed the first fix's gap (14 uses across
~6000 words). 90 tests passing.

7.0/1000w is a reasoned choice, not yet independently validated against
the real corpus. Still needs: re-run compare_corpora.py and
analyze_confound.py one more time against this second fix -- same
open item as before, now for the third time on this specific rule.

## repeated_transitions regression: fully resolved, confirmed by re-running the real comparison
Third measurement against this specific rule confirms the second fix
(7.0/1000w) is correct: 0 hits on human, 0 hits on AI, total corpus
numbers now numerically identical to the pre-regression baseline
(15 human / 19 AI / 2.85x, matching to the decimal). Structural
correlation back to None (no variance).

Honest caveat, not yet resolved: repeated_transitions and prose_tricolon
have each fired on exactly one document across this whole project --
the adversarial essay they were built for. Zero hits on the real
ai_corpus/ (7 documents). Safe (no false positives) but unproven at
scale. Whether the current AI corpus just doesn't exhibit this pattern,
or whether 7.0/1000w is calibrated too conservatively to catch a
subtler real version of it, is unknown -- would need more AI samples,
deliberately varied in prompting style, to find out.

## Pattern found: formal/academic-register AI text underdetected (2026-08-13)
Three separate real ChatGPT-generated texts tested live tonight (a
biographical essay on Atatürk, a history of the ASDC autonomy movement,
a history of Assam) each landed at or near zero total flags. Hand-traced
every rule against all three -- confirmed this is not a bug in the usual
sense: these texts genuinely contain almost none of the surface habits
(bullets, bold, em dashes, promotional adjectives, AI-vocabulary words)
most rules are built to catch. Each rule correctly returned zero on the
patterns it's designed to find; the patterns just weren't present.

The real finding is one level up: this rule set may systematically
underdetect a specific AI writing style -- careful, restrained, formal/
academic prose with low stylistic flourish -- even while working well
on chattier, more typical AI output (as documented throughout
FINDINGS.md). This wasn't visible until real formal-register AI text
got tested directly tonight.

Two narrow near-misses found, attempted, and reverted in this pass:
- significance_inflation was broadened to catch "played an important
  role in spreading/transforming/establishing/promoting" (not just
  "pivotal/crucial/significant... in shaping") and "marked an important
  turning point" (not just "significant/pivotal/watershed moment").
  REVERTED: compare_corpora.py showed this broadening firing on real
  human text (sample02: "played a crucial role in promoting") -- a
  genuine false positive introduced by the change, not a pre-existing one.
- meta_summary_framing was broadened to catch "In short" as a heading.
  Also caught up in the same revert for consistency, though the false
  positive evidence specifically implicated significance_inflation, not
  this rule.
- negative_parallelism's earlier "not merely/just/only X, but Y"
  broadening (added during the ASDC investigation, prior session) was
  ALSO reverted in this same pass -- the corpus check that should have
  followed that change immediately never happened until now, and when
  it finally did, it showed 3 human false positives (sample02, sample03)
  on completely ordinary formal-register human rhetoric. This rule had
  been sitting in scored, deployed code for hours before being caught.

Both rules are back to their original, narrower, previously-validated
forms. The gaps that motivated broadening them are real and still
unaddressed -- documented here rather than patched again without a
demonstrated safe fix.

Not resolved by any patch attempted so far: the underlying pattern.
Every attempt to widen a phrase-matching rule to catch more
formal-register AI writing has collided with real human academic
writing sharing the same rhetorical toolkit (parallelism, "played a
role in," summary phrases). Patching one phrase at a time has real,
demonstrated diminishing returns -- twice now. Real next step,
proposed but not yet done: test whether Layer 2 (Binoculars) catches
what Layer 1 misses on this same register, since Layer 2 measures
statistical predictability rather than surface phrasing and has
already been documented (see LAYER2_FINDINGS.md) to be the stronger
signal on at least one other document where Layer 1 was weak.