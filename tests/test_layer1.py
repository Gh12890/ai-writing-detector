import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from layer1 import PatternScorer

MUMMY_TEXT = """Because in that final moment Imhotep understands something brutal about his whole story.
At the end of The Mummy Returns, Rick is hanging over the pit and Evelyn risks her life to pull him up. Imhotep is in the same position and calls to Anck-su-namun to save him — but she runs instead. Then he looks at Rick and Evie, and he sees the contrast immediately:

* Rick and Evie's love is real and mutual — each is willing to die for the other.
* Imhotep's love is not what he thought it was — he would have saved Anck-su-namun, but she would not save him.

So that little laugh / smile before he lets go is usually read as a mix of:

1. Recognition of betrayal
He realizes Anck-su-namun never loved him the way he loved her.
2. Bitter irony
The man he hates, Rick, actually has the thing Imhotep thought he had: genuine love.
3. Acceptance of defeat
Once Anck-su-namun abandons him, Imhotep loses the main reason he came back. He stops fighting and just lets go.

So the short answer is:
He laughs because he suddenly sees the truth — Rick and Evie's love is real, his own isn't, and the whole thing has become tragically ironic. It's not a happy laugh. It's more of a broken, bitter realization right before he gives up.
If you want, I can also give you a scene-by-scene psychological breakdown of Imhotep in The Mummy and The Mummy Returns, because his ending is actually more tragic than it looks."""

HUMAN_CONTROL_TEXT = """ok so I watched the ending again last night. imhotep's little smile
right before he falls always gets me. I think he just realizes anck-su-namun
was never going to jump in after him like evie did for rick. kind of sad
honestly. anyway I'm going to bed, long day tomorrow."""

LEGAL_BOILERPLATE_TEXT = """As per Section 138 of the Negotiable Instruments Act, 1881, the drawer
of the cheque shall be deemed to have committed an offence. Notice under
Section 138 was duly served upon the respondent on the aforementioned date.
The respondent failed to make payment within the statutory period of fifteen
days from the date of receipt of demand notice."""


def test_chatbot_artifact_detected():
    result = PatternScorer().analyze("If you want, I can also give you more detail.")
    assert any(f.rule_id == "chatbot_artifact" for f in result.flags)


def test_meta_summary_detected():
    result = PatternScorer().analyze("So the short answer is: yes.")
    assert any(f.rule_id == "meta_summary_framing" for f in result.flags)


def test_negative_parallelism_detected():
    result = PatternScorer().analyze("It's not a happy laugh. It's more of a bitter one.")
    assert any(f.rule_id == "negative_parallelism" for f in result.flags)


def test_parallel_bullets_detected():
    text = "* Love is real — they'd die for each other.\n* His love wasn't real — she ran."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "parallel_bullet_em_dash" for f in result.flags)


def test_rule_of_three_outline_regression():
    text = "1. Recognition of betrayal\n2. Bitter irony\n3. Acceptance of defeat\n"
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "rule_of_three_outline" for f in result.flags), (
        "Regression: rule-of-three outline should fire on 3-word numbered headers"
    )


def test_filler_phrase_detected():
    result = PatternScorer().analyze("In order to achieve this, due to the fact that it rained.")
    ids = [f.rule_id for f in result.flags]
    assert ids.count("filler_phrase") == 2


def test_hedge_stacking_detected():
    result = PatternScorer().analyze("It could potentially be argued that this matters.")
    assert any(f.rule_id == "hedge_stacking" for f in result.flags)


def test_promotional_language_detected():
    result = PatternScorer().analyze("This is a groundbreaking, revolutionary approach.")
    assert any(f.rule_id == "promotional_language" for f in result.flags)


def test_ai_vocabulary_detected():
    result = PatternScorer().analyze("Let's delve into this robust, multifaceted topic.")
    assert any(f.rule_id == "ai_vocabulary" for f in result.flags)


def test_false_ranges_detected():
    result = PatternScorer().analyze(
        "This affects industries from healthcare to finance, from small startups to global enterprises."
    )
    assert any(f.rule_id == "false_ranges" for f in result.flags)


def test_curly_quotes_function_still_detects_correctly():
    from layer1.rules import _find_curly_quotes
    matches = _find_curly_quotes("This isn\u2019t a straight quote, it\u2019s curly.")
    assert len(matches) == 2


def test_curly_quotes_not_scored_by_pattern_scorer():
    result = PatternScorer().analyze("This isn\u2019t a straight quote, it\u2019s curly.")
    assert not any(f.rule_id == "curly_quotes" for f in result.flags)


def test_negative_parallelism_still_fires_on_curly_quoted_text():
    result = PatternScorer().analyze("It\u2019s not a happy laugh. It\u2019s more of a sad one.")
    fired = {f.rule_id for f in result.flags}
    assert "negative_parallelism" in fired
    assert "curly_quotes" not in fired


def test_emoji_detected():
    result = PatternScorer().analyze("This is great! \U0001F600 Really happy about it.")
    assert any(f.rule_id == "emoji" for f in result.flags)


def test_no_emoji_no_false_positive():
    result = PatternScorer().analyze("This is a plain sentence with no emoji at all.")
    assert not any(f.rule_id == "emoji" for f in result.flags)


def test_vague_attribution_detected():
    result = PatternScorer().analyze("Industry observers say this trend will continue.")
    assert any(f.rule_id == "vague_attribution" for f in result.flags)


def test_sycophantic_tone_detected():
    result = PatternScorer().analyze("Great question! I'd be happy to help with that.")
    assert any(f.rule_id == "sycophantic_tone" for f in result.flags)


def test_knowledge_cutoff_disclaimer_detected():
    result = PatternScorer().analyze("As of my last update, I don't have access to real-time data.")
    assert any(f.rule_id == "knowledge_cutoff_disclaimer" for f in result.flags)


def test_significance_inflation_detected():
    result = PatternScorer().analyze("This event stands as a testament to human perseverance.")
    assert any(f.rule_id == "significance_inflation" for f in result.flags)


def test_superficial_ing_analysis_detected():
    result = PatternScorer().analyze("The results improved sharply, underscoring the strategy's success.")
    assert any(f.rule_id == "superficial_ing_analysis" for f in result.flags)


def test_generic_positive_conclusion_detected():
    result = PatternScorer().analyze("Moving forward, this marks an exciting new chapter for the team.")
    assert any(f.rule_id == "generic_positive_conclusion" for f in result.flags)


def test_boldface_overuse_flagged():
    text = "This is **bold** and **bold** and **bold** and **bold** and **bold** again in ten words total here now."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "boldface_overuse" for f in result.flags)


def test_no_boldface_no_false_positive():
    result = PatternScorer().analyze("This is a plain sentence with no bold formatting anywhere in it at all.")
    assert not any(f.rule_id == "boldface_overuse" for f in result.flags)


def test_notability_emphasis_detected():
    result = PatternScorer().analyze("The startup has been featured in major publications worldwide.")
    assert any(f.rule_id == "notability_emphasis" for f in result.flags)


def test_outline_challenges_section_detected():
    result = PatternScorer().analyze("Some intro text.\n\nChallenges and Future Prospects\n\nMore text here.")
    assert any(f.rule_id == "outline_challenges_section" for f in result.flags)


def test_outline_challenges_section_not_triggered_by_mention():
    result = PatternScorer().analyze("There are many challenges and future prospects worth discussing in detail here.")
    assert not any(f.rule_id == "outline_challenges_section" for f in result.flags)


def test_copula_avoidance_detected():
    result = PatternScorer().analyze("This tool serves as a bridge between two systems.")
    assert any(f.rule_id == "copula_avoidance" for f in result.flags)


def test_inline_header_list_detected():
    result = PatternScorer().analyze("* **Speed:** the system responds quickly.\n* **Cost:** it is affordable.")
    assert any(f.rule_id == "inline_header_list" for f in result.flags)


def test_em_dash_density_flagged():
    text = "One — two — three — four — five — six words here total count."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "em_dash_density" for f in result.flags)


def test_mummy_passage_full_regression():
    result = PatternScorer().analyze(MUMMY_TEXT)
    fired_rules = {f.rule_id for f in result.flags}
    expected = {
        "chatbot_artifact",
        "meta_summary_framing",
        "negative_parallelism",
        "parallel_bullet_em_dash",
        "rule_of_three_outline",
        "em_dash_density",
    }
    assert expected.issubset(fired_rules), f"Missing: {expected - fired_rules}"


def test_human_control_low_false_positives():
    result = PatternScorer().analyze(HUMAN_CONTROL_TEXT)
    assert result.flag_count <= 1, f"Too many false positives on human control: {result.flags}"


REAL_PASTED_TEXT_WITH_MARKDOWN_AND_SMART_QUOTES = """Because in that final moment **Imhotep understands something brutal about his whole story**.
At the end of *The Mummy Returns*, Rick is hanging over the pit and **Evelyn risks her life to pull him up**. Imhotep is in the same position and calls to **Anck-su-namun** to save him — but **she runs instead**. Then he looks at Rick and Evie, and he sees the contrast immediately:
* **Rick and Evie's love is real and mutual** — each is willing to die for the other.
* **Imhotep's love is not what he thought it was** — he would have saved Anck-su-namun, but she would not save him.
So that little laugh / smile before he lets go is usually read as a mix of:
1. **Recognition of betrayal**
   He realizes Anck-su-namun never loved him the way he loved her.
2. **Bitter irony**
   The man he hates, Rick, actually has the thing Imhotep thought he had: genuine love.
3. **Acceptance of defeat**
   Once Anck-su-namun abandons him, Imhotep loses the main reason he came back. He stops fighting and just lets go.
So the short answer is:
**He laughs because he suddenly sees the truth — Rick and Evie's love is real, his own isn't, and the whole thing has become tragically ironic.** It's not a happy laugh. It's more of a **broken, bitter realization** right before he gives up.
If you want, I can also give you a **scene-by-scene psychological breakdown of Imhotep in *The Mummy* and *The Mummy Returns***, because his ending is actually more tragic than it looks."""


def test_real_pasted_text_regression():
    result = PatternScorer().analyze(REAL_PASTED_TEXT_WITH_MARKDOWN_AND_SMART_QUOTES)
    fired_rules = {f.rule_id for f in result.flags}
    assert "negative_parallelism" in fired_rules, "Smart-quote regression: negative_parallelism should still fire"
    assert "rule_of_three_outline" in fired_rules, "Markdown regression: rule_of_three_outline should still fire"
    rule_of_three_count = sum(1 for f in result.flags if f.rule_id == "rule_of_three_outline")
    assert rule_of_three_count == 3, f"Expected all 3 numbered items to fire, got {rule_of_three_count}"


def test_mask_excluded_blanks_out_span():
    from layer1.scorer import _mask_excluded
    masked = _mask_excluded("abcdefghij", [(2, 5)])
    assert masked == "ab   fghij"
    assert len(masked) == 10


def test_mask_excluded_no_spans_returns_unchanged():
    from layer1.scorer import _mask_excluded
    assert _mask_excluded("hello world", []) == "hello world"


def test_em_dash_inside_citation_does_not_trigger_document_flag():
    text = (
        "Section 5 of the Model Act — Amendment — Title — Provisions Act, 2020 "
        "governs this narrow procedural matter for the parties involved today."
    )
    result = PatternScorer().analyze(text)
    assert not any(f.rule_id == "em_dash_density" for f in result.flags)
    assert result.em_dash_rate_per_1000w == 0.0


def test_em_dash_outside_citation_still_triggers_document_flag():
    text = (
        "This is a short sentence — with an em dash — and another "
        "— right here — too, plainly."
    )
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "em_dash_density" for f in result.flags)


def test_flags_by_tier_splits_correctly():
    text = (
        "This groundbreaking approach serves as a testament to innovation.\n\n"
        "1. First Point\n2. Second Point\n3. Third Point"
    )
    result = PatternScorer().analyze(text)
    by_tier = result.flags_by_tier()
    assert len(by_tier["structural"]) == 3
    assert len(by_tier["lexical"]) == 3
    assert {f.rule_id for f in by_tier["structural"]} == {"rule_of_three_outline"}
    assert {f.rule_id for f in by_tier["lexical"]} == {
        "promotional_language", "copula_avoidance", "ai_vocabulary"
    }


def test_tier_densities_computed_independently():
    text = (
        "This groundbreaking approach serves as a testament to innovation.\n\n"
        "1. First Point\n2. Second Point\n3. Third Point"
    )
    result = PatternScorer().analyze(text)
    assert result.structural_density_per_1000w > 0
    assert result.lexical_density_per_1000w > 0
    combined = result.structural_density_per_1000w + result.lexical_density_per_1000w
    assert abs(combined - result.density_per_1000w) < 0.2


def test_em_dash_density_and_boldface_overuse_tagged_structural():
    text = "One — two — three — four — five — six words here total count."
    result = PatternScorer().analyze(text)
    by_tier = result.flags_by_tier()
    assert any(f.rule_id == "em_dash_density" for f in by_tier["structural"])
    assert not any(f.rule_id == "em_dash_density" for f in by_tier["lexical"])


def test_no_flags_gives_zero_tier_densities():
    result = PatternScorer().analyze("A plain, ordinary sentence with nothing unusual in it.")
    assert result.structural_density_per_1000w == 0.0
    assert result.lexical_density_per_1000w == 0.0


def test_chatbot_artifact_catches_sure_heres_em_dash():
    result = PatternScorer().analyze("Sure — here's a deliberately very AI-sounding version.")
    assert any(f.rule_id == "chatbot_artifact" for f in result.flags)


def test_chatbot_artifact_catches_sure_heres_comma():
    result = PatternScorer().analyze("Sure, here's the summary you asked for.")
    assert any(f.rule_id == "chatbot_artifact" for f in result.flags)


def test_repeated_transitions_detected():
    text = "Therefore, this matters. The weather was nice. Therefore, that also matters. Therefore, we conclude it does."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "repeated_transitions" for f in result.flags)


def test_repeated_transitions_not_triggered_by_two_uses():
    text = "Therefore, this matters. The weather was nice. It rained later that day."
    result = PatternScorer().analyze(text)
    assert not any(f.rule_id == "repeated_transitions" for f in result.flags)

def test_repeated_transitions_scales_threshold_with_document_length():
    long_doc = "The committee reviewed several proposals in detail. " * 200
    long_doc += "However, the budget remained a concern throughout the process. "
    long_doc += "Additional context was provided for each section under review. " * 200
    long_doc += "However, further discussion was postponed to the next session. "
    long_doc += "The report was circulated among all relevant departments. " * 200
    long_doc += "However, no final decision was reached by the end of the meeting."
    result = PatternScorer().analyze(long_doc)
    assert not any(f.rule_id == "repeated_transitions" for f in result.flags), (
        "Regression: repeated_transitions should not fire on ordinary "
        "repetition rates in long documents, only on short-document overuse"
    )

def test_repeated_transitions_first_fix_was_insufficient_second_fix_holds():
    stress_doc = "This section discusses the relevant background information in detail. " * 100
    for i in range(14):
        stress_doc += f"However, point number {i} requires further consideration. "
        stress_doc += "This section discusses the relevant background information in detail. " * 40
    result = PatternScorer().analyze(stress_doc)
    assert not any(f.rule_id == "repeated_transitions" for f in result.flags), (
        "Regression: the first length-scaling fix let this exact pattern "
        "through (14 uses / ~6000 words); the rate-based fix must not."
    )


def test_prose_tricolon_detected():
    text = "India's policy can be described as one of strategic autonomy, pragmatism, and national interest."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "prose_tricolon" for f in result.flags)


def test_prose_tricolon_not_triggered_without_framing_verb():
    text = "I bought bread, milk, and eggs at the store today."
    result = PatternScorer().analyze(text)
    assert not any(f.rule_id == "prose_tricolon" for f in result.flags)


REAL_AI_ESSAY_INDIA_US_IRAN = """Sure — here's a deliberately very AI-sounding version, with formal wording, repetitive transitions, and textbook-style phrasing:
India–US–Iran Relationship
The relationship between India, the United States, and Iran is a significant and complex aspect of contemporary international relations. These three countries have different strategic interests, yet India maintains important relations with both the United States and Iran. Therefore, India has to follow a balanced and pragmatic foreign policy.

India and the United States have developed a strong and comprehensive strategic partnership. Their cooperation includes areas such as defence, trade, technology, energy, and regional security. The United States considers India an important partner in the Indo-Pacific region. At the same time, India benefits from cooperation with the United States in economic, technological, and strategic fields.

On the other hand, Iran is also important for India because of geographical, economic, and strategic reasons. India has historical and cultural relations with Iran. The Chabahar Port in Iran is particularly important for India because it provides connectivity with Afghanistan and Central Asia. Iran has also been an important source of energy for India.

However, India's relationship with Iran is complicated by the tensions between Iran and the United States. American sanctions on Iran can create difficulties for Indian businesses and energy interests. India therefore has to carefully manage its relations with both countries. India generally avoids taking extreme positions and instead focuses on its national interests.

In conclusion, the India–US–Iran relationship represents the complexity of modern international diplomacy. India's policy can be described as one of strategic autonomy, pragmatism, and national interest. India seeks to maintain friendly relations with the United States while continuing its important engagement with Iran. Therefore, balancing these relationships is an important challenge as well as an opportunity for India's foreign policy."""


def test_real_ai_essay_regression_all_three_new_rules_fire():
    result = PatternScorer().analyze(REAL_AI_ESSAY_INDIA_US_IRAN)
    fired = {f.rule_id for f in result.flags}
    assert "chatbot_artifact" in fired, "Missed the 'Sure -- here's' preamble"
    assert "repeated_transitions" in fired, "Missed the 3x 'therefore' repetition"
    assert "prose_tricolon" in fired, "Missed the 'described as one of X, Y, and Z' tricolon"
    assert result.flag_count >= 4


def test_legal_boilerplate_not_over_flagged():
    result = PatternScorer().analyze(LEGAL_BOILERPLATE_TEXT)
    assert result.flag_count == 0, f"Unexpected flags on legal boilerplate: {result.flags}"