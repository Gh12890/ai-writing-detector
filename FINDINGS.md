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

