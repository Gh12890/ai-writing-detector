"""
Legal boilerplate exclusion filter.

Legal writing is formulaic on purpose -- statutory citations, case
citations, and standard contract phrases are supposed to sound stiff and
repetitive. Layer 1's pattern rules don't know that, and would flag
normal legal writing as AI-written for the wrong reason.

This module finds spans of text that ARE formulaic by design, so the
scorer can exclude them before counting flags.
"""

import re

_STATUTE_CITATION = re.compile(
    r"\bSection\s+\d+[A-Za-z]?(\(\d+\))?\s+of\s+the\s+[A-Z][\w\s\u2014-]+?\s+Act,?\s+\d{4}\b"
)
_CASE_CITATION = re.compile(
    r"\bAIR\s+\d{4}\s+[A-Z]{2,4}\s+\d+\b"
    r"|\(\d{4}\)\s+\d+\s+SCC\s+\d+\b"
    r"|\b\d{4}\s+SCC\s+OnLine\s+[A-Z]{2,4}\s+\d+\b"
)

_STANDARD_PHRASES = re.compile(
    r"\b(WHEREAS|NOW THEREFORE|IN WITNESS WHEREOF|"
    r"party of the (first|second) part|"
    r"THIS AGREEMENT is made and entered into|"
    r"without prejudice to)\b",
    re.I,
)


def find_excluded_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for pattern in (_STATUTE_CITATION, _CASE_CITATION, _STANDARD_PHRASES):
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    return sorted(spans)


def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def is_excluded(flag_start: int, flag_end: int, excluded_spans: list[tuple[int, int]]) -> bool:
    return any(_overlaps(flag_start, flag_end, es, ee) for es, ee in excluded_spans)