import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from measure_fpr import compute_fpr_stats


def test_compute_fpr_stats_all_clean(tmp_path):
    (tmp_path / "a.txt").write_text("This is a plain sentence with nothing unusual in it at all today.")
    (tmp_path / "b.txt").write_text("Another perfectly ordinary sentence about the weather this week.")
    files = sorted(tmp_path.glob("*.txt"))
    stats = compute_fpr_stats(files)
    assert stats["n_docs"] == 2
    assert stats["total_flags"] == 0
    assert stats["docs_with_flags"] == 0
    assert stats["docs_with_flags_pct"] == 0.0
    assert stats["rule_counts"] == {}


def test_compute_fpr_stats_detects_flags(tmp_path):
    (tmp_path / "clean.txt").write_text("An ordinary sentence with nothing notable in it whatsoever today.")
    (tmp_path / "flagged.txt").write_text(
        "This groundbreaking approach serves as a testament to innovation."
    )
    files = sorted(tmp_path.glob("*.txt"))
    stats = compute_fpr_stats(files)
    assert stats["n_docs"] == 2
    assert stats["total_flags"] > 0
    assert stats["docs_with_flags"] == 1
    assert stats["docs_with_flags_pct"] == 50.0
    assert "promotional_language" in stats["rule_counts"]


def test_compute_fpr_stats_empty_list():
    stats = compute_fpr_stats([])
    assert stats["n_docs"] == 0
    assert stats["total_words"] == 0
    assert stats["docs_with_flags_pct"] == 0.0