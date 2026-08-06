\# TODO - Layer 1 pattern coverage



\## Status

10 of the SKILL.md's 24 official patterns are implemented and tested.

2 additional rules (meta\_summary\_framing, parallel\_bullet\_em\_dash) are

implemented but are NOT part of the original 24 -- they were added because

they fired on the Mummy passage during testing, not because they're in the

source taxonomy. Keep that distinction visible; don't let the rule count

imply more taxonomy coverage than actually exists.



\## Implemented (10/24, verified against SKILL.md)

\- \[x] #4  Promotional and Advertisement-like Language -> promotional\_language

\- \[x] #7  Overused "AI Vocabulary" Words  -> ai\_vocabulary

\- \[x] #9  Negative Parallelisms          -> negative\_parallelism

\- \[x] #10 Rule of Three Overuse          -> rule\_of\_three\_outline (partial:

&#x20;     only catches numbered-list form, not rule-of-three inside prose)

\- \[x] #12 False Ranges                   -> false\_ranges

\- \[x] #13 Em Dash Overuse                -> em\_dash\_density

\- \[x] #18 Curly Quotation Marks          -> curly\_quotes

\- \[x] #19 Collaborative Communication Artifacts -> chatbot\_artifact

\- \[x] #22 Filler Phrases                 -> filler\_phrase

\- \[x] #23 Excessive Hedging              -> hedge\_stacking



\## Not yet built (14/24)

\- \[ ] #1  Undue Emphasis on Significance, Legacy, and Broader Trends

\- \[ ] #2  Undue Emphasis on Notability and Media Coverage

\- \[ ] #3  Superficial Analyses with -ing Endings

\- \[ ] #5  Vague Attributions and Weasel Words

\- \[ ] #6  Outline-like "Challenges and Future Prospects" Sections

\- \[ ] #8  Avoidance of is/are (Copula Avoidance)

\- \[ ] #11 Elegant Variation (Synonym Cycling)

\- \[ ] #14 Overuse of Boldface

\- \[ ] #15 Inline-Header Vertical Lists

\- \[ ] #16 Title Case in Headings

\- \[ ] #17 Emojis

\- \[ ] #20 Knowledge-Cutoff Disclaimers

\- \[ ] #21 Sycophantic/Servile Tone

\- \[ ] #24 Generic Positive Conclusions



\## Also not built, separate from the above

\- No exclusion filter for legal/formulaic boilerplate (design discussed,

&#x20; not implemented -- currently just verified the rules don't misfire on

&#x20; one sample legal paragraph, which is not the same thing)

\- No real false-positive rate. Two control texts is not a measured FPR.

\- Layer 2 (statistical scorer) not built at all -- separate script exists

&#x20; outside this repo, requires GPU, not yet run for real.

