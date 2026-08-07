"""
Measures an approximate false-positive rate for Layer 1 against a corpus
of KNOWN-HUMAN text. Every flag produced on this corpus is, by
definition, a false positive -- the corpus should contain only text
you're confident a real person wrote (your own past writing, Wikipedia
articles, published essays, etc.), not text you're unsure about.

This is deliberately simple and not a substitute for a real labeled
benchmark like RAID or HC3 -- it's the honest version of what's
achievable without one: a real number, on real text, computed
transparently, instead of two control texts standing in for a rate.

Usage:
    python scripts/measure_fpr.py corpus/

Expects a directory of .txt files, one document per file, UTF-8 encoded.
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from layer1 import PatternScorer


def compute_fpr_stats(txt_files: list) -> dict:
    total_words = 0
    total_flags = 0
    docs_with_flags = 0
    rule_counter: Counter = Counter()
    per_doc = []

    for f in txt_files:
        text = f.read_text(encoding="utf-8")
        result = PatternScorer().analyze(text)
        total_words += result.word_count
        total_flags += result.flag_count
        if result.flag_count > 0:
            docs_with_flags += 1
        for flag in result.flags:
            rule_counter[flag.rule_id] += 1
        per_doc.append((f.name, result.word_count, result.flag_count))

    n = len(txt_files)
    return {
        "n_docs": n,
        "total_words": total_words,
        "total_flags": total_flags,
        "docs_with_flags": docs_with_flags,
        "docs_with_flags_pct": round(docs_with_flags / n * 100, 1) if n else 0.0,
        "flags_per_1000w": round(total_flags / total_words * 1000, 2) if total_words else 0.0,
        "rule_counts": dict(rule_counter),
        "per_doc": per_doc,
    }


def main(corpus_dir: str) -> None:
    corpus_path = Path(corpus_dir)
    txt_files = sorted(corpus_path.glob("*.txt"))
    if not txt_files:
        print(f"No .txt files found in {corpus_path}")
        return

    stats = compute_fpr_stats(txt_files)

    print(f"\nCorpus: {stats['n_docs']} documents, {stats['total_words']} total words\n")
    print(f"Documents with >=1 false-positive flag: {stats['docs_with_flags']}/{stats['n_docs']} "
          f"({stats['docs_with_flags_pct']}%)")
    print(f"Total false-positive flags: {stats['total_flags']}")
    print(f"False positives per 1000 words: {stats['flags_per_1000w']}")

    print("\nPer-document breakdown:")
    for name, wc, fc in stats["per_doc"]:
        marker = "  <-- flagged" if fc > 0 else ""
        print(f"  {name}: {wc} words, {fc} flags{marker}")

    if stats["rule_counts"]:
        print("\nFalse positives by rule (which rules are the least reliable):")
        for rule_id, count in sorted(stats["rule_counts"].items(), key=lambda x: -x[1]):
            print(f"  {rule_id}: {count}")
    else:
        print("\nNo false positives at all on this corpus.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/measure_fpr.py <corpus_directory>")
        sys.exit(1)
    main(sys.argv[1])