import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from layer1 import PatternScorer

MUMMY_TEXT = """Because in that final moment Imhotep understands something brutal about his whole story.
At the end of The Mummy Returns, Rick is hanging over the pit and Evelyn risks her life to pull him up. Imhotep is in the same position and calls to Anck-su-namun to save him \u2014 but she runs instead. Then he looks at Rick and Evie, and he sees the contrast immediately:

* Rick and Evie's love is real and mutual \u2014 each is willing to die for the other.
* Imhotep's love is not what he thought it was \u2014 he would have saved Anck-su-namun, but she would not save him.

So that little laugh / smile before he lets go is usually read as a mix of:

1. Recognition of betrayal
He realizes Anck-su-namun never loved him the way he loved her.
2. Bitter irony
The man he hates, Rick, actually has the thing Imhotep thought he had: genuine love.
3. Acceptance of defeat
Once Anck-su-namun abandons him, Imhotep loses the main reason he came back. He stops fighting and just lets go.

So the short answer is:
He laughs because he suddenly sees the truth \u2014 Rick and Evie's love is real, his own isn't, and the whole thing has become tragically ironic. It's not a happy laugh. It's more of a broken, bitter realization right before he gives up.
If you want, I can also give you a scene-by-scene psychological breakdown of Imhotep in The Mummy and The Mummy Returns, because his ending is actually more tragic than it looks."""

# A normal, informal, human note with none of the target patterns.
# No detector is worth anything if it lights up on ordinary writing.
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
    text = "* Love is real \u2014 they'd die for each other.\n* His love wasn't real \u2014 she ran."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "parallel_bullet_em_dash" for f in result.flags)


def test_rule_of_three_outline_regression():
    """This is the exact bug found live: the original regex only matched
    2-word numbered headers and missed 'Recognition of betrayal' (3 words)."""
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


def test_em_dash_density_flagged():
    text = "One \u2014 two \u2014 three \u2014 four \u2014 five \u2014 six words here total count."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "em_dash_density" for f in result.flags)


def test_mummy_passage_full_regression():
    """Locks in the real result from the live run earlier in the
    conversation: 5 distinct rule categories firing on this exact text."""
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
    """Ordinary informal human writing should not light up like a machine
    draft. Zero tolerance isn't realistic for a regex layer, but it should
    stay well below the Mummy passage's density."""
    result = PatternScorer().analyze(HUMAN_CONTROL_TEXT)
    assert result.flag_count <= 1, f"Too many false positives on human control: {result.flags}"


def test_legal_boilerplate_not_over_flagged():
    """Formulaic legal citation language should not trip the same rules as
    chatbot-style AI writing. This isn't the exclusion filter from the
    design doc (that's separate work) -- it's a check that Layer 1's
    *current* rules don't already misfire on this domain."""
    result = PatternScorer().analyze(LEGAL_BOILERPLATE_TEXT)
    assert result.flag_count == 0, f"Unexpected flags on legal boilerplate: {result.flags}"
