"""Layer 1: runs all registered rules over a document and produces a result."""

from dataclasses import dataclass, field

from .rules import REGISTRY, Flag

EM_DASH_RATE_THRESHOLD_PER_1000W = 3.0
BOLDFACE_RATE_THRESHOLD_PER_1000W = 5.0

# Smart-quote variants mapped to their straight-quote equivalents. Every
# rule regex is written against straight quotes; without this, curly
# quotes from Word, browsers, or messaging apps silently break any
# pattern that checks for an apostrophe. Each mapping is one character to
# one character, so span offsets computed after this runs stay valid
# against the normalized text.
_QUOTE_MAP = str.maketrans({
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
})


def normalize_quotes(text: str) -> str:
    return text.translate(_QUOTE_MAP)


@dataclass
class AnalysisResult:
    text: str
    word_count: int
    flags: list[Flag] = field(default_factory=list)
    em_dash_rate_per_1000w: float = 0.0

    @property
    def flag_count(self) -> int:
        return len(self.flags)

    @property
    def density_per_1000w(self) -> float:
        if self.word_count == 0:
            return 0.0
        return round(self.flag_count / self.word_count * 1000, 1)

    def flags_by_rule(self) -> dict[str, list[Flag]]:
        grouped: dict[str, list[Flag]] = {}
        for flag in self.flags:
            grouped.setdefault(flag.rule_id, []).append(flag)
        return grouped


class PatternScorer:
    """Runs every rule in REGISTRY against a document."""

    def __init__(self, rules=None):
        self.rules = rules if rules is not None else REGISTRY

    def analyze(self, text: str) -> AnalysisResult:
        original = text
        normalized = normalize_quotes(text)
        word_count = len(normalized.split())
        flags: list[Flag] = []
        for rule in self.rules:
            source = original if rule.use_original else normalized
            flags.extend(rule.apply(source))

        em_dash_count = normalized.count("\u2014")
        em_dash_rate = round(em_dash_count / word_count * 1000, 1) if word_count else 0.0
        if em_dash_rate > EM_DASH_RATE_THRESHOLD_PER_1000W:
            flags.append(
                Flag(
                    "em_dash_density",
                    "Elevated em dash rate",
                    f"{em_dash_rate}/1000w",
                    0,
                    0,
                    f"Document-level: {em_dash_rate} em dashes per 1000 words, "
                    f"above the {EM_DASH_RATE_THRESHOLD_PER_1000W} threshold",
                )
            )

        bold_pair_count = normalized.count("**") // 2
        bold_rate = round(bold_pair_count / word_count * 1000, 1) if word_count else 0.0
        if bold_rate > BOLDFACE_RATE_THRESHOLD_PER_1000W:
            flags.append(
                Flag(
                    "boldface_overuse",
                    "Elevated boldface rate",
                    f"{bold_rate}/1000w",
                    0,
                    0,
                    f"Document-level: {bold_rate} bolded phrases per 1000 words, "
                    f"above the {BOLDFACE_RATE_THRESHOLD_PER_1000W} threshold",
                )
            )

        flags.sort(key=lambda f: f.start)
        return AnalysisResult(text=normalized, word_count=word_count, flags=flags, em_dash_rate_per_1000w=em_dash_rate)
