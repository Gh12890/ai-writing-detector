"""
Layer 1: deterministic pattern rules.

Each Rule is independent and independently testable. Add new rules by
appending to REGISTRY -- nothing else needs to change.
"""

import re
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Flag:
    rule_id: str
    rule_name: str
    match_text: str
    start: int
    end: int
    explanation: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    explanation: str
    finder: Callable[[str], list[tuple[int, int, str]]]
    use_original: bool = False

    def apply(self, text: str) -> list[Flag]:
        return [
            Flag(self.rule_id, self.name, matched, start, end, self.explanation)
            for start, end, matched in self.finder(text)
        ]


def _find_chatbot_artifact(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(if you (want|like|'d like),? I can (also )?(give|provide|walk|break|expand|show)"
        r"|let me know if"
        r"|I hope this helps"
        r"|would you like me to)",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_meta_summary(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(so the short answer is|in summary|to summarize|in conclusion)\b:?", re.I
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_negative_parallelism(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"[^.]*\bisn'?t\b[^.]*\.\s*It'?s\b[^.]*\."
        r"|\bIt'?s not\b[^.]*[,.]\s*It'?s\b[^.]*\.",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0).strip()) for m in pattern.finditer(text)]


def _find_parallel_bullets(text: str) -> list[tuple[int, int, str]]:
    bullet_pattern = re.compile(r"^\s*[\*\-]\s+.*\u2014.*$", re.M)
    matches = list(bullet_pattern.finditer(text))
    if len(matches) < 2:
        return []
    return [(m.start(), m.end(), m.group(0)) for m in matches]


def _find_rule_of_three_outline(text: str) -> list[tuple[int, int, str]]:
    item_pattern = re.compile(
        r"^\d+\.\s+\*{0,2}([A-Z][a-zA-Z]+(?:\s+[a-zA-Z]+){0,4})\*{0,2}\s*$", re.M
    )
    matches = list(item_pattern.finditer(text))
    if len(matches) < 3:
        return []
    return [(m.start(), m.end(), m.group(0)) for m in matches]


def _find_filler_phrases(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(in order to|due to the fact that|at this point in time|"
        r"in the event that|has the ability to|it is important to note that)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_hedge_stacking(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(r"\b(could|might|may)\s+(potentially|possibly)\s+(be\s+)?(argued|the case)\b", re.I)
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_promotional_language(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(groundbreaking|revolutionary|game[- ]changing|seamless(ly)?|"
        r"cutting[- ]edge|unparalleled|unprecedented|transformative|"
        r"world[- ]class|state[- ]of[- ]the[- ]art|best[- ]in[- ]class)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_ai_vocabulary(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(delve(s|d)?\s+into|tapestry|testament\s+to|underscor(es|ing|ed)|"
        r"leverage(s|d)?|robust|vibrant\s+landscape|multifaceted|"
        r"ever[- ]evolving|realm\s+of|boasts?)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_false_ranges(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\bfrom\s+[\w\s]{1,30}?\s+to\s+[\w\s]{1,30}?,\s*from\s+[\w\s]{1,30}?\s+to\s+[\w\s]{1,30}?\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_curly_quotes(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(r"[\u2018\u2019\u201c\u201d]")
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_emojis(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_vague_attribution(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(industry (observers|experts|analysts)|some (argue|say|believe)|"
        r"many (believe|argue|say)|experts (say|believe|argue)|"
        r"critics (argue|say)|observers (note|say))\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_sycophantic_tone(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(great question|excellent question|i'?d be happy to|"
        r"certainly!|absolutely!|what a (great|wonderful) (question|idea))\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_knowledge_cutoff_disclaimer(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(as of my (last update|knowledge cutoff|training)|"
        r"i don'?t have access to real-time|"
        r"my (knowledge|training) (cutoff|is limited to)|"
        r"i'?m not able to browse the (internet|web))\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_significance_inflation(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(stands as a testament to|solidif(y|ies|ied) (its|his|her|their) (place|legacy)|"
        r"cements? (its|his|her|their) legacy|will (long )?be remembered as|"
        r"marked a (significant|pivotal|watershed) moment|"
        r"played a (pivotal|crucial|significant) role in shaping)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_superficial_ing_analysis(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r",\s+(underscoring|highlighting|reflecting|emphasizing|showcasing|"
        r"illustrating|demonstrating|signaling|cementing|solidifying|"
        r"reinforcing|revealing|further (solidifying|cementing))\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_generic_positive_conclusion(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(moving forward|in today'?s fast-paced world|"
        r"as we (move|look) (into|toward) the future|"
        r"overall,? this (represents|marks)|this marks an exciting( new)? chapter|"
        r"the future (looks|remains) bright)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]

def _find_notability_emphasis(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"\b(has been (featured|covered) (in|by)|"
        r"garnered (significant|widespread) attention|"
        r"received widespread (coverage|recognition)|"
        r"has been the subject of numerous|widely covered by)\b",
        re.I,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_outline_challenges_section(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(
        r"^#{0,3}\s*(challenges and (future )?(prospects|outlook)|"
        r"looking ahead|future outlook|road ahead)\s*$",
        re.I | re.M,
    )
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_copula_avoidance(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(r"\b(serves as (a|an)|functions as (a|an)|acts as (a|an))\b", re.I)
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]


def _find_inline_header_list(text: str) -> list[tuple[int, int, str]]:
    pattern = re.compile(r"^\s*[\*\-]\s+\*{2}[^*\n]+:\*{2}", re.M)
    return [(m.start(), m.end(), m.group(0)) for m in pattern.finditer(text)]
REGISTRY: list[Rule] = [
    Rule("chatbot_artifact", "Chatbot artifact",
         "Assistant-style sign-off or offer to continue, not how a person talks mid-thought",
         _find_chatbot_artifact),
    Rule("meta_summary_framing", "Meta-summary framing",
         "Announces a summary instead of just giving it",
         _find_meta_summary),
    Rule("negative_parallelism", "Negative parallelism",
         "'It's not X, it's Y' contrast structure",
         _find_negative_parallelism),
    Rule("parallel_bullet_em_dash", "Parallel bullet template",
         "Two or more bullets built on an identical 'X, em dash, clause' shape",
         _find_parallel_bullets),
    Rule("rule_of_three_outline", "Rule-of-three outline",
         "Three or more numbered items, each a short abstract-noun label",
         _find_rule_of_three_outline),
    Rule("filler_phrase", "Filler phrase",
         "Wordy construction with a shorter natural equivalent",
         _find_filler_phrases),
    Rule("hedge_stacking", "Excessive hedging",
         "Stacked qualifiers weakening a claim that could be stated plainly",
         _find_hedge_stacking),
    Rule("promotional_language", "Promotional language",
         "Advertisement-style superlative, rare in ordinary prose",
         _find_promotional_language),
    Rule("ai_vocabulary", "Overused AI vocabulary",
         "Word or phrase disproportionately common in LLM output vs human writing",
         _find_ai_vocabulary),
    Rule("false_ranges", "False range",
         "Two parallel 'from X to Y' ranges stacked for false comprehensiveness",
         _find_false_ranges),
    Rule("curly_quotes", "Curly quotation marks",
         "Typographic quotes/apostrophes, common in AI output and word processors",
         _find_curly_quotes, use_original=True),
    Rule("emoji", "Emoji",
         "Emoji character, rare in formal prose and disproportionately common in chatbot output",
         _find_emojis, use_original=True),
    Rule("vague_attribution", "Vague attribution",
         "Cites an unnamed source ('some argue', 'industry observers') instead of a real one",
         _find_vague_attribution),
    Rule("sycophantic_tone", "Sycophantic tone",
         "Assistant-style flattery or eagerness-to-please phrasing",
         _find_sycophantic_tone),
    Rule("knowledge_cutoff_disclaimer", "Knowledge-cutoff disclaimer",
         "Assistant-style disclaimer about training data or real-time access",
         _find_knowledge_cutoff_disclaimer),
    Rule("significance_inflation", "Significance inflation",
         "Grand, unsupported claim about legacy or historical importance",
         _find_significance_inflation),
    Rule("superficial_ing_analysis", "Superficial -ing analysis",
         "Comma-plus-participle tacked onto a sentence, adding interpretation without new information",
         _find_superficial_ing_analysis),
    Rule("generic_positive_conclusion", "Generic positive conclusion",
         "Stock upbeat closing phrase, rare in writing with a specific point to make",
         _find_generic_positive_conclusion),
    Rule("notability_emphasis", "Notability/media emphasis",
         "Unsupported claim about media coverage or public attention",
         _find_notability_emphasis),
    Rule("outline_challenges_section", "Outline-style section heading",
         "Stock 'Challenges and Future Prospects'-style heading, common in AI-generated overviews",
         _find_outline_challenges_section),
    Rule("copula_avoidance", "Copula avoidance",
         "'Serves as/functions as/acts as a' used in place of the plainer 'is a'",
         _find_copula_avoidance),
    Rule("inline_header_list", "Inline-header vertical list",
         "Bullet opening with a bolded label and colon, common in AI-generated lists",
         _find_inline_header_list),
]