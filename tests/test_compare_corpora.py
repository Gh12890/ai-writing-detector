import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from measure_fpr import compute_fpr_stats


def test_ai_folder_scores_higher_than_human_folder(tmp_path):
    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()

    (human_dir / "h1.txt").write_text(
        "An ordinary paragraph about daily life, with no unusual structure "
        "or vocabulary, written the way a person naturally writes."
    )
    (ai_dir / "a1.txt").write_text(
        "1. Purpose of this Report\n2. Historical Background\n3. Current Status\n"
        "This groundbreaking approach serves as a testament to innovation."
    )

    human_stats = compute_fpr_stats(sorted(human_dir.glob("*.txt")))
    ai_stats = compute_fpr_stats(sorted(ai_dir.glob("*.txt")))

    assert ai_stats["flags_per_1000w"] > human_stats["flags_per_1000w"]


def test_rule_of_three_only_fires_on_structured_ai_style_text(tmp_path):
    ai_dir = tmp_path / "ai"
    ai_dir.mkdir()
    (ai_dir / "a1.txt").write_text(
        "1. First Point\n2. Second Point\n3. Third Point\nPlain conclusion text."
    )
    stats = compute_fpr_stats(sorted(ai_dir.glob("*.txt")))
    assert "rule_of_three_outline" in stats["rule_counts"]
    assert stats["rule_counts"]["rule_of_three_outline"] == 3