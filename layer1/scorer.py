"""Layer 1: runs all registered rules over a document and produces a result."""

from dataclasses import dataclass, field

from .rules import REGISTRY, Flag
from .exclusions import find_excluded_spans, is_excluded

EM_DASH_RATE_THRESHOLD_PER_1000W = 3.0
BOLDFACE_RATE_THRESHOLD_PER_1000W = 5.0

# em_dash_density and boldface_overuse are document-level checks computed
# directly below, not Rule objects in REGISTRY, so they don't carry a
# .tier attribute the way registry rules do. Both are format/rate checks,
# not vocabulary lists, so they belong in the same "structural" bucket --
# this map is how flags_by_tier() knows that despite them living outside
# the Rule system.
_RULE_TIER = {rule.rule_id: rule.tier for rule in REGISTRY}
_RULE_TIER["em_dash_density"] = "structural"
_RULE_TIER["boldface_overuse"] = "structural"

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
    excluded_spans: list[tuple[int, int]] = field(default_factory=list)
    suppressed_count: int = 0

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

    def flags_by_tier(self) -> dict[str, list[Flag]]:
        grouped: dict[str, list[Flag]] = {"structural": [], "lexical": []}
        for flag in self.flags:
            tier = _RULE_TIER.get(flag.rule_id, "lexical")
            grouped[tier].append(flag)
        return grouped

    def _tier_density(self, tier: str) -> float:
        if self.word_count == 0:
            return 0.0
        count = len(self.flags_by_tier()[tier])
        return round(count / self.word_count * 1000, 1)

    @property
    def structural_density_per_1000w(self) -> float:
        return self._tier_density("structural")

    @property
    def lexical_density_per_1000w(self) -> float:
        return self._tier_density("lexical")


def _mask_excluded(text: str, excluded_spans: list[tuple[int, int]]) -> str:
    if not excluded_spans:
        return text
    chars = list(text)
    for start, end in excluded_spans:
        for i in range(start, min(end, len(chars))):
            chars[i] = " "
    return "".join(chars)


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

        excluded_spans = find_excluded_spans(normalized)
        masked_for_counts = _mask_excluded(normalized, excluded_spans)

        em_dash_count = masked_for_counts.count("\u2014")
        em_dash_rate = round(em_dash_count / word_count * 1000, 1) if word_count else 0.0
        if em_dash_rate > EM_DASH_RATE_THRESHOLD_PER_1000W:
            flags.append(
                Flag(
                    "em_dash_density",
                    "Elevated em dash rate",
                    f"{em_dash_rate}/1000w",
                    0,
                    0,
                    f"Document-level: {em_dash_rate} em dashes per 1000 words "
                    f"(excluding legal boilerplate), above the "
                    f"{EM_DASH_RATE_THRESHOLD_PER_1000W} threshold",
                )
            )

        bold_pair_count = masked_for_counts.count("**") // 2
        bold_rate = round(bold_pair_count / word_count * 1000, 1) if word_count else 0.0
        if bold_rate > BOLDFACE_RATE_THRESHOLD_PER_1000W:
            flags.append(
                Flag(
                    "boldface_overuse",
                    "Elevated boldface rate",
                    f"{bold_rate}/1000w",
                    0,
                    0,
                    f"Document-level: {bold_rate} bolded phrases per 1000 words "
                    f"(excluding legal boilerplate), above the "
                    f"{BOLDFACE_RATE_THRESHOLD_PER_1000W} threshold",
                )
            )

        kept_flags = []
        suppressed_count = 0
        for f in flags:
            if f.end > f.start and is_excluded(f.start, f.end, excluded_spans):
                suppressed_count += 1
                continue
            kept_flags.append(f)

        kept_flags.sort(key=lambda f: f.start)
        return AnalysisResult(
            text=normalized,
            word_count=word_count,
            flags=kept_flags,
            em_dash_rate_per_1000w=em_dash_rate,
            excluded_spans=excluded_spans,
            suppressed_count=suppressed_count,
        )