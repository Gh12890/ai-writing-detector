\# Findings: human vs. AI corpus comparison



Real, measured results from scripts/compare\_corpora.py, run against a

manually-assembled corpus. This is small-sample manual testing, not a

rigorous benchmark -- treat every number here as directional, not final,

and see "Limitations" at the bottom before citing any of it.



\## Corpus composition (as of this measurement)



Human corpus (corpus/, gitignored, not in this repo): 6 documents,

16,533 words. Mixed register: two academic papers (M.A. History level),

one longer academic piece, two informal WhatsApp exports.



AI corpus (ai\_corpus/, gitignored, not in this repo): 7 documents,

7,328 words, generated across three different models specifically to

test whether findings held up across generators, not just one:

\- 4 documents: rewrites of one human source document (model unspecified

&#x20; in this log -- treat these 4 as one cluster, not four independent points)

\- 1 document: ChatGPT, topic: Adam and Eve narrative

\- 1 document: Gemini, topic: the sun and solar system

\- 1 document: Claude, topic: India-US relations



\## Headline result



|                | Documents | Words  | Flags | Flags/1000w |

|----------------|-----------|--------|-------|--------------|

| Human          | 6         | 16,533 | 15    | 0.91         |

| AI             | 7         | 7,328  | 19    | 2.59         |



AI-generated text scored 2.85x higher than human-written text on this

corpus. This is the first evidence this project has produced that

Layer 1's pattern rules discriminate between human and AI writing at

all, rather than just measuring formality or writing register.



\## Per-rule breakdown -- the more important result



Not all rules contributed equally, and the split is the real finding:



Structural rules -- strong, reproducible signal:

\- rule\_of\_three\_outline: 6 AI hits, 0 human hits. Caught a real,

&#x20; recognizable AI habit directly -- one AI sample (report-style prompt)

&#x20; structured its answer as a 6-item numbered outline with generic

&#x20; abstract-noun headers ("Purpose of this Report," "Historical

&#x20; Background," etc.), and the rule caught every item. Scope-limited:

&#x20; only fires on report-style prompts with a literal numbered list, not

&#x20; on narrative or essay-style AI writing without that structure.

\- em\_dash\_density: 6 AI hits, 0 human hits, across all three models

&#x20; tested. The single cleanest result in this whole comparison.



Vocabulary rules -- weak, present, human-leaning:

\- ai\_vocabulary: 3 human, 1 AI (the AI hit was "leverage," in a

&#x20; Claude-generated India-US relations essay -- no obvious topical

&#x20; reason for the word to appear, read as a genuine catch, not

&#x20; vocabulary forced by subject matter)

\- promotional\_language: 3 human, 1 AI (same essay, "seamless," same

&#x20; reasoning)

\- Both rules are outnumbered by their own human-side false positives.

&#x20; Working hypothesis, not yet confirmed: current-generation models may

&#x20; have been trained/prompted away from the most obvious AI-vocabulary

&#x20; tells (this is a documented industry-wide phenomenon), which would

&#x20; make these rules measure an older generation of AI writing habits.



Zero AI hits across all three models tested, genuinely promising:

\- copula\_avoidance: 2 human, 0 AI (ChatGPT, Gemini, Claude, all zero)

\- filler\_phrase: 5 human, 0 AI (same, all zero)

\- Read cautiously -- "zero across 3 models, 7 documents" is a real

&#x20; pattern, not proof. It could mean these two AI-writing habits from the

&#x20; SKILL.md source just aren't common in the current generation of

&#x20; models, or it could mean the sample is still too small.



One-off, not enough data to characterize:

\- superficial\_ing\_analysis: 2 human, 4 AI -- AI-leaning, worth

&#x20; watching as the corpus grows

\- generic\_positive\_conclusion: 0 human, 1 AI -- single data point



\## Why curly\_quotes isn't in this table at all



Removed from scoring entirely before this comparison was run -- see

TODO.md and the git history around commit af0e7eb. It produced 87.5% of

flags on one real human document, caused by Microsoft Word's default

quote autocorrect, not by anything resembling AI-written text.



\## Limitations, stated plainly



\- Small n. 6 human documents, 7 AI documents. Not remotely enough

&#x20; for a real statistical claim -- treat every percentage and ratio here

&#x20; as suggestive, not conclusive.

\- AI corpus is unbalanced. 4 of 7 AI documents are rewrites of one

&#x20; source (register/topic effects from that source could be inflating or

&#x20; deflating specific rules in ways that wouldn't hold on more varied text).

\- Prompts weren't controlled. No fixed prompt template was used

&#x20; across models, so differences between AI documents may reflect prompt

&#x20; differences as much as model differences.

\- Human corpus skews academic/formal, with two informal (WhatsApp)

&#x20; samples. Not representative of all human writing registers -- legal

&#x20; writing, casual social media, technical documentation, etc. are all

&#x20; unrepresented.

\- No inter-rater reliability check. Every "genuine catch" vs. "false

&#x20; positive" judgment on individual flagged spans was made by one person

&#x20; (project owner), reading the flag in isolation -- not blind-reviewed.

\- This is Layer 1 only. No statistical layer (Binoculars/Layer 2)

&#x20; contributes to any number here -- these are pattern-match counts only.



\## What would make this a real benchmark instead of a working log



\- 50+ documents per side minimum, ideally 100+

\- AI documents generated from a fixed, varied prompt set across models,

&#x20; not ad hoc topics

\- Human documents spanning multiple registers deliberately, not

&#x20; convenience-sampled from what was on hand

\- Blind review of flagged spans by someone other than the rule's author



\## A real miss, found live and fixed: ChatGPT prompted to sound maximally AI



Tested directly in this project's Streamlit app: a short essay

generated by ChatGPT, with the explicit prompt "make it more AI

generated" -- deliberately the easiest possible case for a detector.



\*\*Before this fix:\*\* Layer 1 found only 2 flags (1 structural

em\_dash\_density, 1 lexical meta\_summary\_framing on "In conclusion").

Layer 2 (Binoculars, full-document pooled) scored it at distance 0.3085

from 1.0 -- further from 1.0, i.e. MORE human-like, than either

corpus's average in this project (human 0.1193, AI 0.1366, both

excluding the sample05 outlier). A document explicitly engineered to

be maximally AI-sounding scored as more human-like than the typical

document in either reference set, on both detection layers.



\*\*Why:\*\* every existing lexical rule was built from AI-chatbot

conversational tells (ai\_vocabulary, sycophantic\_tone, etc.). This

essay wasn't asked to sound like a chatbot -- it was asked to sound

like a textbook. Different register, different tells, and this

project's rules had never been tested against that specific target

before.



\*\*Real tells present in the essay that no rule caught, until now:\*\*

\- ChatGPT's own preamble, left in: "Sure -- here's a deliberately very

&#x20; AI-sounding version..." -- a textbook chatbot opener, just not one

&#x20; that had been added to chatbot\_artifact's pattern list yet.

\- "Therefore" used 3 times across 5 short paragraphs -- a real

&#x20; over-reliance-on-one-connective habit, previously undetected by any rule.

\- "described as one of strategic autonomy, pragmatism, and national

&#x20; interest" -- a rule-of-three tricolon embedded in a sentence, not a

&#x20; numbered list. rule\_of\_three\_outline's "only catches numbered-list

&#x20; form" limitation, noted in TODO.md since the very first version of

&#x20; that rule, turned out to matter in a real document.



\*\*Fixed:\*\* three new/extended rules -- chatbot\_artifact now catches

"Sure, here's" / "Sure -- here's"; a new repeated\_transitions rule

flags any discourse marker used 3+ times; a new prose\_tricolon rule

catches rule-of-three lists embedded in prose, anchored on

abstract-summary framing verbs ("described as," "characterized by")

to limit false positives. Real result on the same essay, same words,

after the fix: 2 flags become 7 (5 structural, 2 lexical) -- see git

history and TODO.md for the actual before/after numbers and the

known, accepted false-positive risk on prose\_tricolon.



\*\*What this means for everything else in this document:\*\* every result

above this section was measured before these three fixes existed. The

2.85x human/AI gap, the per-rule breakdown, all of it -- computed

against a Layer 1 that had this specific blind spot. Re-running the

full corpus comparison with the current rule set would very plausibly

show a wider gap than what's reported above, since at least one

document in ai\_corpus/ may have been under-scored the same way this

essay was. That re-run hasn't happened yet.



\## A real regression, found immediately by re-running the comparison: repeated\_transitions inverted the whole result



Following through on "re-run compare\_corpora.py and analyze\_confound.py

with the new rules" (flagged as not-yet-done above) found a real,

serious bug within one run.



\*\*What happened:\*\* re-running the human-vs-AI comparison with the three

new rules active showed the AI rate DROPPING from 2.85x the human rate

to 0.93x -- meaning human text now scored as slightly MORE machine-like

than AI text. That's not a smaller improvement than hoped; it's an

inversion of the project's headline result.



\*\*Diagnosis, confirmed by the numbers, not guessed:\*\* repeated\_transitions

alone accounted for the entire swing -- 31 human flags, 0 AI flags, on

a rule that was supposed to be roughly symmetric. analyze\_confound.py's

per-document breakdown showed the highest structural density

concentrated in the two longest human documents (sample02, sample03),

even after already dividing by word count -- a strong sign of a

document-length artifact, not a real authorship signal.



\*\*Root cause:\*\* the rule used a fixed "3+ uses anywhere in the

document" threshold with no length adjustment. A long document

naturally uses a connective like "however" a few times across many

pages -- unremarkable. The same 3 uses in a \~300-word essay (the

original motivating case) is genuinely unusual. em\_dash\_density and

boldface\_overuse were already built as rate checks specifically to

avoid this failure mode; repeated\_transitions was added without that

same safeguard.



\*\*Fixed:\*\* the threshold now scales with document length

(max(3, word\_count / 500)), so the original short-essay catch is

preserved exactly while long-form documents need proportionally more

repetition to trigger. Verified against the real essay (still fires,

threshold stays at 3 for \~300 words) and a synthetic long document

using "however" 3 times across \~4,800 words (no longer fires, needed

\~10 uses at that length). Locked in with a permanent regression test.



\*\*The real lesson, worth stating plainly:\*\* this project's own stated

practice -- re-run the comparison after any rule change, don't trust a

single document's result -- is exactly what caught this before it sat

undetected in a "real" finding. If compare\_corpora.py hadn't been

re-run immediately after the previous fix, this inversion would have

gone unnoticed, and the next person reading this repo would have

inherited a broken headline number without knowing it.



\*\*Re-run again after this fix, results pending\*\* -- update this section

once compare\_corpora.py and analyze\_confound.py are re-run against

the fixed rule.





\## The repeated\_transitions fix needed a second iteration -- the first one wasn't enough



Re-running compare\_corpora.py against the "fixed" rule (the length-scaling

change described above) showed real improvement -- human flags from this

rule dropped from 31 to 22 -- but not a real fix. repeated\_transitions

was still the largest single contributor to human flags (22 of 37, 59%),

still driven by sample03, and the aggregate AI/human ratio only

recovered to 1.16x, far short of the 2.85x measured before either bug

existed.



\*\*Why the first fix was insufficient, worked out precisely:\*\* threshold

= word\_count / 500 is mathematically equivalent to a CONSTANT target

rate of exactly 2.0 occurrences per 1000 words, for any document long

enough that the max(3, ...) floor doesn't bind. The one confirmed

genuine case -- the AI essay, 3 uses of "therefore" in 291 words -- has

an actual rate of 10.3 per 1000 words. The first fix set the bar at

roughly a fifth of that. It was scaled in the right direction, just by

far too little.



\*\*Second fix:\*\* replaced the length-scaled count with an explicit rate

threshold (7.0 per 1000 words, plus a minimum absolute count of 3) --

real margin below the confirmed genuine case's 10.3, and well above the

2.0 that just proved too weak on real data. Verified against three

cases: the real essay (still fires, 10.3/1000w), the original synthetic

long document (still doesn't fire), and a new stress test specifically

built to match the scenario that got through the first fix -- 14 uses

of "however" across \~6,000 words, a rate of 2.3/1000w, which the first

fix would have let through and the second correctly doesn't.



\*\*Still not independently validated at this exact number (7.0/1000w)

against the real corpus\*\* -- chosen with a reasoned margin, not

measured. The honest next step is the same one that caught both bugs

so far: re-run compare\_corpora.py and analyze\_confound.py again and

see what the real data says, rather than trust the reasoning alone a

third time.



\## Regression fully resolved -- but with an honest asterisk



Re-running compare\_corpora.py against the second fix (7.0/1000w rate

threshold) confirms it's fully fixed, not just improved: repeated\_transitions

no longer appears in the rule breakdown at all -- zero hits on human,

zero on AI. Total flags, per-corpus, are now numerically identical to

the very first measurement in this document, before any of the three

new rules (chatbot\_artifact's "Sure, here's" addition,

repeated\_transitions, prose\_tricolon) existed: 15 human flags, 19 AI

flags, 2.85x ratio, to the decimal. Structural correlation with

sentence length is back to None (no variance -- nothing fired).



\*\*The honest asterisk:\*\* repeated\_transitions and prose\_tricolon have

now fired on exactly one document in this entire project -- the

adversarial essay they were built to catch. Zero hits on any of the 13

corpus documents (6 human, 7 AI), including the AI side. The 7.0/1000w

threshold that stopped the false positives is also, apparently,

conservative enough that it doesn't fire on any of the real AI samples

either. That's a real, different claim than "these rules work": they're

currently validated against one hand-picked adversarial case, not shown

to generalize to this project's actual AI corpus at all. Whether that's

because the current ai\_corpus/ documents genuinely don't exhibit this

pattern, or because the threshold is calibrated too conservatively to

catch a real but subtler version of it, is an open question -- more AI

samples, deliberately varied in how they're prompted (report-style vs.

essay-style vs. explicitly-asked-to-sound-AI, the way this one was),

would be the way to find out.



\*\*Net honest state of this whole multi-turn detour:\*\* a real bug was

found, diagnosed correctly, and fixed in two iterations, each verified

against real data rather than assumed correct after the first attempt.

The original 2.85x finding survives, unchanged. Two new rules exist,

are tested, and are currently safe (no false positives) but unproven at

scale (one confirmed catch, zero corpus-wide signal either direction).





\---



\## Addendum (2026-08-11): Corpus Expansion and a Confound Worth Watching



The corpus composition changed in two ways since the original analysis above, and

they happened together, not separately -- this addendum's numbers are NOT a clean

before/after comparison against the original 2.85x figure.



\*\*Change 1:\*\* Two files from each class (sample01, sample06 human; sample07, sample12

AI) were moved to a held-out test set (see SPLIT.md) and are excluded from all

corpus-comparison numbers going forward, including below.



\*\*Change 2:\*\* Two new human documents were added to the human corpus:

\- sample14.txt (5,390 words) -- political history, formal/academic register

\- sample15.txt (403 words) -- political history, formal/academic register



Current aggregate (6 human docs incl. sample14/15, 5 AI docs, held-out files excluded

from both sides):



&#x20;   Human: 21,031 words, 14 flags, 0.67 flags/1000w

&#x20;   AI:     4,854 words, 15 flags, 3.09 flags/1000w

&#x20;   AI rate is 4.61x the human rate



This ratio is not directly comparable to the original 2.85x -- both the held-out

removal and the new additions changed the denominator simultaneously.



\*\*The finding that matters:\*\* sample14 and sample15, scored individually, produced

zero flags each across all 25 rules. Together they contribute 5,793 words -- over a

quarter of the human corpus -- with no flags at all, which is the primary driver of

the lower aggregate human rate above.



At n=2, this doesn't distinguish between two different explanations, and no claim

stronger than "zero flags observed" is supported yet:

1\. The rule set is well-calibrated against formal/academic prose specifically, or

2\. Formal/academic writing structurally lacks the surface patterns (filler phrases,

&#x20;  copula avoidance, promotional language, etc.) these rules were built to detect,

&#x20;  independent of whether a document is AI-generated -- meaning this register may be

&#x20;  under-tested rather than validated.



Worth flagging explicitly: this sits in tension with the formality confound already

documented above (r=0.722 between flag density and average sentence length on

confirmed human text). That earlier finding showed lexical-tier rules firing MORE on

longer, more formal human sentences; sample14/15 -- both long and formal -- fired

NONE. Both observations are real; they are not yet reconciled. A larger sample of

formal/academic human writing would be needed to determine which pattern dominates

at scale, or whether both are true under different sub-conditions not yet identified.



No rule thresholds or exclusion filters were modified in response to this data.

