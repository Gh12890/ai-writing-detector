"""
Lightweight formality proxies -- no NLP model, just two well-established
markers used in readability/register research: sentence length and
contraction rate. Neither is a perfect formality measure, but both are
cheap, transparent, and defensible as a first-pass proxy, which is all
this needs to be to test a hypothesis, not to publish a linguistics paper.
"""

import re


def avg_sentence_length(text: str) -> float:
    sentences = re.split(r"[.!?]+(?:\s+|$)", text.strip())
    sentences = [s for s in sentences if s.strip()]
    if not sentences:
        return 0.0
    word_counts = [len(s.split()) for s in sentences]
    return round(sum(word_counts) / len(word_counts), 2)


def contraction_rate_per_1000w(text: str) -> float:
    word_count = len(text.split())
    if word_count == 0:
        return 0.0
    contractions = re.findall(r"\b\w+'(?:t|re|ll|ve|d|m|s)\b", text, re.I)
    return round(len(contractions) / word_count * 1000, 2)