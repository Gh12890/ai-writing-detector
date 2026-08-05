"""
Layer 1: deterministic pattern rules.

Each Rule is independent and independently testable. Add new rules by
appending to REGISTRY -- nothing else needs to change. This starts with
8 rules covering the categories we've already validated against real
text in conversation (chatbot artifacts, meta-summary framing, negative
parallelism, parallel bullets, rule-of-three outlines, em-dash density,
filler phrases, hedge stacking). The remaining patterns from the
SKILL.md's 24 can be added the same way later.
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
    # A finder takes the full text and yields (start, end, matched_text)
    finder: Callable[[str], list[tuple[int, int, str]]]

    def apply(self, text: str) -> list[Flag]:
        return [
            Flag(self.rule_id, self.name, matched, start, end, self.explanation)
            for start, end, matched in self.finder(text)
        ]


def _regex_finder(pattern: str, flags: int = re.I) -> Callable[[str], list[tuple[int, int, str]]]:
    compiled = re.compile(pattern, flags)

    def find(text: str) -> list[tuple[int, int, str]]:
        return [(m.start(), m.end(), m.group(0)) for m in compiled.finditer(text)]

    return find


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
    # Three shapes, all seen in real text during this conversation:
    #   "X isn't Y. It's Z."                (Mummy passage, sentence 1)
    #   "It's not X. It's Y."               (Mummy passage, sentence 2 -- comma
    #                                         and period separators both occur)
    #   "It's not just X, it's Y."          (classic negative-parallelism form)
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
    # Numbered item: "1. Some Title Phrase" (1-5 words), followed by a
    # newline. Fixed from the earlier bug: the original only matched
    # exactly 2-word titles and silently missed 3-word ones like
    # "Recognition of betrayal".
    item_pattern = re.compile(r"^\d+\.\s+([A-Z][a-zA-Z]+(?:\s+[a-zA-Z]+){0,4})\s*$", re.M)
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
]
