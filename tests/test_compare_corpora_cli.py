import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from compare_corpora import compare


def test_compare_prints_full_table(tmp_path, capsys):
    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()

    (human_dir / "h1.txt").write_text(
        "This tool serves as a bridge between two systems, in order to simplify the process."
    )
    (ai_dir / "a1.txt").write_text(
        "1. Purpose of this Report\n2. Historical Background\n3. Current Status\n"
        "This groundbreaking approach serves as a testament to innovation."
    )

    compare(str(human_dir), str(ai_dir))
    output = capsys.readouterr().out

    assert "HUMAN" in output
    assert "AI" in output
    assert "Documents" in output
    assert "rule_of_three_outline" in output
    assert "x the human rate" in output


def test_compare_missing_files_prints_warning(tmp_path, capsys):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    (other_dir / "a1.txt").write_text("Some text here.")

    compare(str(empty_dir), str(other_dir))
    output = capsys.readouterr().out

    assert "Need .txt files in both folders" in output


def test_compare_zero_human_rate_prints_undefined_ratio(tmp_path, capsys):
    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()

    (human_dir / "h1.txt").write_text("A plain sentence with nothing unusual in it whatsoever.")
    (ai_dir / "a1.txt").write_text(
        "1. Purpose\n2. Background\n3. Status\nThis groundbreaking effort serves as a testament."
    )

    compare(str(human_dir), str(ai_dir))
    output = capsys.readouterr().out

    assert "ratio is undefined" in output


def test_compare_both_zero_prints_no_signal(tmp_path, capsys):
    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()

    (human_dir / "h1.txt").write_text("A plain sentence with nothing unusual in it whatsoever.")
    (ai_dir / "a1.txt").write_text("Another plain sentence with nothing unusual in it either.")

    compare(str(human_dir), str(ai_dir))
    output = capsys.readouterr().out

    assert "Both rates are 0" in output

def test_compare_verdict_branches(tmp_path, capsys, monkeypatch):
    import compare_corpora

    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()
    (human_dir / "h1.txt").write_text("placeholder")
    (ai_dir / "a1.txt").write_text("placeholder")

    def fake_stats(files):
        parent = files[0].parent.name
        if parent == "human":
            return {
                "n_docs": 1, "total_words": 100, "total_flags": 12,
                "docs_with_flags_pct": 100.0, "flags_per_1000w": 120.0,
                "rule_counts": {
                    "human_only_rule": 2,
                    "fires_more_human": 5,
                    "equal_rule": 3,
                    "fires_more_ai_rule": 2,
                },
            }
        else:
            return {
                "n_docs": 1, "total_words": 100, "total_flags": 9,
                "docs_with_flags_pct": 100.0, "flags_per_1000w": 90.0,
                "rule_counts": {
                    "fires_more_human": 1,
                    "equal_rule": 3,
                    "fires_more_ai_rule": 5,
                },
            }

    monkeypatch.setattr(compare_corpora, "compute_fpr_stats", fake_stats)

    compare_corpora.compare(str(human_dir), str(ai_dir))
    output = capsys.readouterr().out

    assert "human_only_rule" in output
    assert "human-only so far -- concerning" in output
    assert "fires_more_human" in output
    assert "fires more on human" in output
    assert "fires_more_ai_rule" in output
    assert "fires more on AI" in output
    assert "equal_rule" in output


def test_compare_cli_usage_error_with_wrong_args(monkeypatch, capsys):
    import runpy
    import sys

    monkeypatch.setattr(sys, "argv", ["compare_corpora.py", "only_one_arg"])

    try:
        runpy.run_path("scripts/compare_corpora.py", run_name="__main__")
    except SystemExit as e:
        assert e.code == 1
    else:
        assert False, "expected SystemExit"

    output = capsys.readouterr().out
    assert "Usage: python scripts/compare_corpora.py" in output

def test_compare_cli_runs_with_correct_args(monkeypatch, tmp_path, capsys):
    import runpy
    import sys

    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()
    (human_dir / "h1.txt").write_text("A plain sentence with nothing unusual in it whatsoever.")
    (ai_dir / "a1.txt").write_text("Another plain sentence with nothing unusual in it either.")

    monkeypatch.setattr(sys, "argv", ["compare_corpora.py", str(human_dir), str(ai_dir)])

    runpy.run_path("scripts/compare_corpora.py", run_name="__main__")

    output = capsys.readouterr().out
    assert "HUMAN" in output
    assert "AI" in output