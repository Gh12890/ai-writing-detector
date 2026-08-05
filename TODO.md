# TODO - Layer 1 pattern coverage

## Status
6 of the SKILL.md's 24 official patterns are implemented and tested.
2 additional rules (meta_summary_framing, parallel_bullet_em_dash) are
implemented but are NOT part of the original 24 -- they were added because
they fired on the Mummy passage during testing, not because they're in the
source taxonomy. Keep that distinction visible; don't let the rule count
imply more taxonomy coverage than actually exists.

## Implemented (6/24, verified against SKILL.md)
- [x] #9  Negative Parallelisms          -> negative_parallelism
- [x] #10 Rule of Three Overuse          -> rule_of_three_outline (partial:
      only catches numbered-list form, not rule-of-three inside prose)
- [x] #13 Em Dash Overuse                -> em_dash_density
- [x] #19 Collaborative Communication Artifacts -> chatbot_artifact
- [x] #22 Filler Phrases                 -> filler_phrase
- [x] #23 Excessive Hedging              -> hedge_stacking

## Not yet built (18/24)
- [ ] #1  Undue Emphasis on Significance, Legacy, and Broader Trends
- [ ] #2  Undue Emphasis on Notability and Media Coverage
- [ ] #3  Superficial Analyses with -ing Endings
- [ ] #4  Promotional and Advertisement-like Language
- [ ] #5  Vague Attributions and Weasel Words
- [ ] #6  Outline-like "Challenges and Future Prospects" Sections
- [ ] #7  Overused "AI Vocabulary" Words
- [ ] #8  Avoidance of is/are (Copula Avoidance)
- [ ] #11 Elegant Variation (Synonym Cycling)
- [ ] #12 False Ranges
- [ ] #14 Overuse of Boldface
- [ ] #15 Inline-Header Vertical Lists
- [ ] #16 Title Case in Headings
- [ ] #17 Emojis
- [ ] #18 Curly Quotation Marks
- [ ] #20 Knowledge-Cutoff Disclaimers
- [ ] #21 Sycophantic/Servile Tone
- [ ] #24 Generic Positive Conclusions

## Also not built, separate from the above
- No exclusion filter for legal/formulaic boilerplate (design discussed,
  not implemented -- currently just verified the 8 existing rules don't
  misfire on one sample legal paragraph, which is not the same thing)
- No real false-positive rate. Two control texts is not a measured FPR.
- Layer 2 (statistical scorer) not built at all -- separate script exists
  outside this repo, requires GPU, not yet run for real.
