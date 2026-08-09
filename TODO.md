\# TODO - Layer 1 pattern coverage



\## Status

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



2 additional rules (meta\_summary\_framing, parallel\_bullet\_em\_dash) are

implemented but are NOT part of the original 24. A legal-boilerplate

exclusion filter is also implemented (see below) -- separate from

pattern coverage, it suppresses flags that fall inside statutory

citations, case citations, or standard contract phrases.



\## Implemented (22/24, verified against SKILL.md)

\- \[x] #1  Undue Emphasis on Significance, Legacy, Broader Trends -> significance\_inflation

\- \[x] #2  Undue Emphasis on Notability and Media Coverage -> notability\_emphasis

\- \[x] #3  Superficial Analyses with -ing Endings -> superficial\_ing\_analysis

\- \[x] #4  Promotional and Advertisement-like Language -> promotional\_language

\- \[x] #5  Vague Attributions and Weasel Words -> vague\_attribution

\- \[x] #6  Outline-like "Challenges and Future Prospects" Sections -> outline\_challenges\_section

\- \[x] #7  Overused "AI Vocabulary" Words  -> ai\_vocabulary

\- \[x] #8  Avoidance of is/are (Copula Avoidance) -> copula\_avoidance

\- \[x] #9  Negative Parallelisms          -> negative\_parallelism

\- \[x] #10 Rule of Three Overuse          -> rule\_of\_three\_outline (partial:

&#x20;     only catches numbered-list form, not rule-of-three inside prose)

\- \[x] #12 False Ranges                   -> false\_ranges

\- \[x] #13 Em Dash Overuse                -> em\_dash\_density

\- \[x] #14 Overuse of Boldface            -> boldface\_overuse

\- \[x] #15 Inline-Header Vertical Lists   -> inline\_header\_list

\- \[x] #17 Emojis                         -> emoji

\- \[x] #18 Curly Quotation Marks          -> curly\_quotes (DETECTED but NOT SCORED -- see Status above)

\- \[x] #19 Collaborative Communication Artifacts -> chatbot\_artifact

\- \[x] #20 Knowledge-Cutoff Disclaimers   -> knowledge\_cutoff\_disclaimer

\- \[x] #21 Sycophantic/Servile Tone       -> sycophantic\_tone

\- \[x] #22 Filler Phrases                 -> filler\_phrase

\- \[x] #23 Excessive Hedging              -> hedge\_stacking

\- \[x] #24 Generic Positive Conclusions   -> generic\_positive\_conclusion



\## Not yet built (2/24) -- deliberately, not just unstarted

\- \[ ] #11 Elegant Variation (Synonym Cycling) -- needs coreference /

&#x20;     tracking the same referent across a document, not a regex problem.

&#x20;     Would need real NLP (spaCy entity linking at minimum) to do honestly.

\- \[ ] #16 Title Case in Headings -- heuristic-fragile. A cheap

&#x20;     capitalization-ratio check risks flagging legitimate headings and

&#x20;     proper-noun-heavy sentences as false positives. Needs a better

&#x20;     approach than "count capital letters" before it's worth shipping.



\## Legal boilerplate exclusion filter -- DONE (v1), scope-limited

Implemented in layer1/exclusions.py: statutory citations ("Section X of

the Y Act, YYYY"), case citations (AIR/SCC formats), and a short list of

standard contract phrases (WHEREAS, IN WITNESS WHEREOF, etc.) are

detected and any Layer 1 span-flag overlapping them is suppressed.

Verified with a deliberately constructed overlap test, not just a

"doesn't misfire" check.



Known v1 limitations:

\- No fuzzy matching against a real standard-clause library (the original

&#x20; design called for this; v1 only does exact citation/phrase patterns)

\- Citation regexes are Indian-law-specific (Section/Act/AIR/SCC format)

&#x20; and won't recognize other jurisdictions' citation conventions



FIXED: document-level flags (em\_dash\_density, boldface\_overuse) are now

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

\## ## False-positive rate measurement -- tool built, real comparison done, still small-n

scripts/measure\_fpr.py and scripts/compare\_corpora.py are built and

tested (5 tests total). Point measure\_fpr.py at a folder of .txt files

for a single-corpus report; compare\_corpora.py takes two folders and

reports both side by side plus a per-rule human-vs-AI breakdown.



Real results exist now -- see FINDINGS.md for the full writeup. Summary:

6 human documents (16,533 words) vs. 7 AI documents (7,328 words,

across ChatGPT/Gemini/Claude) measured. AI text scored 2.85x higher

overall. Structural rules (rule\_of\_three\_outline, em\_dash\_density) show

clean, reproducible discrimination -- zero human false positives across

all 3 models. Vocabulary rules (ai\_vocabulary, promotional\_language) are

weaker and human-leaning. Already produced one real, actionable finding

along the way -- curly\_quotes removal above, found directly from this

measurement, not from guessing.



Still needs: 50+ documents per side for anything resembling a real

benchmark (see FINDINGS.md "Limitations" for the full list of what's

still missing -- controlled prompts, varied human registers, blind

review). Current numbers are directional, not final.

\## Also not built, separate from the above

\- Layer 2 (statistical scorer) not built at all -- separate script exists

&#x20; outside this repo, requires GPU, not yet run for real.



\## Formality confound -- partial fix shipped (tier split)

Real problem, real evidence, real fix -- not a guess. analyze\_confound.py

found r=0.722 correlation between flag density and avg sentence length

across the human corpus in FINDINGS.md. Investigating which rules

produced that: 100% of the flags in that correlation came from lexical

(word/phrase-list) rules -- rule\_of\_three\_outline and em\_dash\_density,

the two rules that survived all 3 AI models with zero human false

positives, never fired on a single human document, so they couldn't

have been part of that correlation either way.



Fix shipped: every rule now carries a tier ("structural" or "lexical").

AnalysisResult reports structural\_density\_per\_1000w and

lexical\_density\_per\_1000w separately instead of one blended number.

analyze\_confound.py now computes correlation per tier, not just

overall. app.py's UI shows both densities and both flag lists

separately, with an explicit caption explaining why.



Honest limits of this fix, stated plainly:

\- This does NOT prove structural rules are confound-free. They simply

&#x20; haven't fired often enough on human text yet to test either way --

&#x20; "None" (undefined correlation, no variance) is not the same claim as

&#x20; "zero correlation, proven clean." The code and the UI both say this

&#x20; explicitly rather than let the silence read as validation.

\- Tier assignment (9 structural, 14 lexical) was done by judgment, not

&#x20; measurement -- e.g. superficial\_ing\_analysis is flagged in code

&#x20; comments as a borderline case (fixed verb list, but structural

&#x20; trigger position).

\- Real next step: keep running analyze\_confound.py as corpus/ grows.

&#x20; If structural rules eventually fire enough to get a real correlation

&#x20; number, that's the point this hypothesis actually gets tested rather

&#x20; than assumed.



\## CI added -- tests now run automatically, not just by hand

.github/workflows/tests.yml runs the full pytest suite on every push and

pull request to master, on Python 3.11 and 3.12. Before this, "69 tests

passing" was only verifiable by whoever ran pytest locally and pasted

the output -- now it's checked automatically and visible as a public

badge on README.md. Does not run Layer 2 (layer2\_binoculars.py isn't in

the pytest suite and needs a GPU CI runners don't have) -- CI covers

Layer 1, the exclusion filter, and the measurement/analysis scripts only.



\## Test coverage measured -- found and closed a real gap

Running pytest-cov for the first time found something worth admitting:

scripts/compare\_corpora.py had 0% coverage despite tests/test\_compare\_corpora.py

existing -- that file's own docstring said outright it only tested the

shared compute\_fpr\_stats() dependency, never compare\_corpora.py's own

compare() function. scripts/measure\_fpr.py was similarly thin (52%) for

the same reason -- its main() print function was untested too.



Added tests/test\_compare\_corpora\_cli.py and tests/test\_measure\_fpr\_cli.py

to actually exercise both files' own output functions (using pytest's

capsys to check printed output, not just return values). Coverage moved

from 78% to 93% overall. Now wired into CI (.github/workflows/tests.yml)

so this number gets recomputed on every push, not just measured once

and left to go stale like several other numbers in this project did

before someone checked them again.



Remaining gaps, honestly: layer1/rules.py 96% (lines 69-74 uncovered),

layer1/scorer.py 93% (lines 53, 57-60, 79), scripts/analyze\_confound.py

93% (lines 106-109), scripts/measure\_fpr.py 92% (lines 91-94),

scripts/compare\_corpora.py 87% (lines 55, 57, 64-67). Not yet

investigated line by line -- next person picking this up should check

what's actually on those lines before assuming they're low-risk.





\## LICENSE added -- a gap that was flagged and then dropped, now fixed

Worth admitting: a LICENSE file was identified as missing when the CI

work started, then never actually added -- coverage measurement got

the follow-through instead and this got left as an open thread. Fixed

now: MIT license added, README.md points to it. Without a license file,

GitHub's default terms mean nobody can legally reuse or fork this

repo, which undercut the "here's a working example" portfolio framing

this project has been built around the whole time.





\## Layer 2 integrated into the Streamlit app -- real gap closed, honestly

Two things were true before tonight that shouldn't have been: app.py

only ever used Layer 1 (the "Layer 2 not built in yet" banner had sat

unchanged since the night it was written), and layer2\_binoculars.py --

including the full-document pooling code that LAYER2\_FINDINGS.md

reports real numbers from -- had never actually been committed to this

repo at all. It only ever existed as a standalone downloadable file and

in Colab notebook cells. That's now fixed: layer2\_binoculars.py is a

real file in this repo, both scoring functions (truncated and

full-document pooled) are in it, and app.py has an opt-in checkbox that

runs both and displays them side by side with the honest caveat that

neither is validated and full-document pooling was tested and found to

not help (see LAYER2\_FINDINGS.md).



Deliberately opt-in, not automatic: loading two 1.5B-parameter models on

CPU (no GPU on the machine this runs on) takes real time and downloads

\~3GB on first use. Making that automatic on every "Run analysis" click

would make the whole app unusable.



Tested: the pooling/chunking math (5 tests, tests/test\_layer2\_binoculars.py)

using fully synthetic fake models -- no real weights, no network, so

these run in CI. NOT tested automatically: load\_models() itself, which

needs real network access and would make CI slow/flaky/costly if it

ran on every push (same reasoning as the Layer 2 GPU work throughout

this project). Manually verified once, in this session, that the app

correctly catches a real model-loading failure and shows a clean error

instead of crashing -- confirmed against this sandbox's actual blocked

network, not a mocked failure.



layer2\_binoculars.py's own coverage is 71% (vs. 93% for layer1+scripts)

\-- the uncovered lines are load\_models() and the \_\_main\_\_ CLI block,

both excluded from automated testing for the reason above. Not folded

into the main coverage number reported elsewhere, since mixing

by-design-untestable code into that figure would make an honest 93%

look like a worse 89% for the wrong reason.



Still unverified: whether this actually works end-to-end on a real

Windows machine, with real internet, on real new text. That's the next

step, and it needs a human to actually click the checkbox and watch

what happens -- same as every other piece of Layer 2 work so far.

