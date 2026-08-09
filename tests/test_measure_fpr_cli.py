import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from measure_fpr import main


def test_main_prints_full_report(tmp_path, capsys):
    (tmp_path / "clean.txt").write_text("An ordinary sentence with nothing unusual in it at all.")
    (tmp_path / "flagged.txt").write_text(
        "This groundbreaking approach serves as a testament to innovation."
    )

    main(str(tmp_path))
    output = capsys.readouterr().out

    assert "Corpus: 2 documents" in output
    assert "Documents with >=1 false-positive flag" in output
    assert "Per-document breakdown" in output
    assert "flagged.txt" in output
    assert "<-- flagged" in output
    assert "False positives by rule" in output


def test_main_no_files_prints_warning(tmp_path, capsys):
    main(str(tmp_path))
    output = capsys.readouterr().out
    assert "No .txt files found" in output


def test_main_no_flags_prints_clean_message(tmp_path, capsys):
    (tmp_path / "clean.txt").write_text("An ordinary sentence with nothing unusual in it at all.")
    main(str(tmp_path))
    output = capsys.readouterr().out
    assert "No false positives at all on this corpus." in output