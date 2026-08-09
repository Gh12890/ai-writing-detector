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