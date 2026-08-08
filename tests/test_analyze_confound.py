from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from analyze_confound import analyze


def test_analyze_detects_known_confound_direction(tmp_path):
    docs = {
        "formal1.txt": (
            "This groundbreaking initiative serves as a testament to institutional "
            "resolve, and it stands as a revolutionary framework that leverages "
            "robust methodologies across multiple sectors of governance and policy "
            "formation within the broader administrative landscape."
        ),
        "formal2.txt": (
            "The committee, having deliberated extensively over several sessions, "
            "ultimately concluded that the proposed amendments represented a "
            "seamless and comprehensive approach to addressing longstanding "
            "structural deficiencies within the existing regulatory apparatus."
        ),
        "casual1.txt": "hey so I didn't go today. wasn't feeling it. we'll catch up tomorrow I guess, don't worry about it.",
        "casual2.txt": "can't believe it's already friday. isn't the weather great though. I'm heading out, we're grabbing food later.",
    }
    for name, text in docs.items():
        (tmp_path / name).write_text(text)

    result = analyze(str(tmp_path))
    assert result["corr_sentence_length"] > 0.5
    assert result["corr_contraction_rate"] < -0.5


def test_tier_split_isolates_lexical_confound_from_untested_structural(tmp_path):
    docs = {
        "formal1.txt": (
            "This groundbreaking initiative serves as a testament to institutional "
            "resolve, and it stands as a revolutionary framework that leverages "
            "robust methodologies across multiple sectors of governance and policy "
            "formation within the broader administrative landscape."
        ),
        "formal2.txt": (
            "The committee, having deliberated extensively over several sessions, "
            "ultimately concluded that the proposed amendments represented a "
            "seamless and comprehensive approach to addressing longstanding "
            "structural deficiencies within the existing regulatory apparatus."
        ),
        "casual1.txt": "hey so I didn't go today. wasn't feeling it. we'll catch up tomorrow I guess, don't worry about it.",
        "casual2.txt": "can't believe it's already friday. isn't the weather great though. I'm heading out, we're grabbing food later.",
    }
    for name, text in docs.items():
        (tmp_path / name).write_text(text)

    result = analyze(str(tmp_path))
    assert result["corr_structural_sentence_length"] is None
    assert result["corr_structural_contraction_rate"] is None
    assert result["corr_lexical_sentence_length"] == result["corr_sentence_length"]
    assert result["corr_lexical_contraction_rate"] == result["corr_contraction_rate"]


def test_analyze_returns_empty_on_too_few_documents(tmp_path):
    (tmp_path / "only_one.txt").write_text("Just one document here.")
    result = analyze(str(tmp_path))
    assert result == {}