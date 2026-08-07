"""
Compares two corpora directly -- typically a known-human corpus against
a known-AI-generated one -- and reports the false-positive vs
true-positive rates side by side, plus which rules are actually pulling
their weight (firing more on AI than human) versus which aren't.

Usage:
    python scripts/compare_corpora.py corpus/ ai_corpus/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.measure_fpr import compute_fpr_stats


def compare(human_dir: str, ai_dir: str) -> None:
    human_files = sorted(Path(human_dir).glob("*.txt"))
    ai_files = sorted(Path(ai_dir).glob("*.txt"))

    if not human_files or not ai_files:
        print(f"Need .txt files in both folders. Human: {len(human_files)}, AI: {len(ai_files)}")
        return

    human_stats = compute_fpr_stats(human_files)
    ai_stats = compute_fpr_stats(ai_files)

    print(f"\n{'':25} {'HUMAN':>12} {'AI':>12}")
    print(f"{'Documents':25} {human_stats['n_docs']:>12} {ai_stats['n_docs']:>12}")
    print(f"{'Total words':25} {human_stats['total_words']:>12} {ai_stats['total_words']:>12}")
    print(f"{'Total flags':25} {human_stats['total_flags']:>12} {ai_stats['total_flags']:>12}")
    print(f"{'Flags per 1000w':25} {human_stats['flags_per_1000w']:>12} {ai_stats['flags_per_1000w']:>12}")
    print(f"{'% docs with any flag':25} {human_stats['docs_with_flags_pct']:>11}% {ai_stats['docs_with_flags_pct']:>11}%")

    if human_stats["flags_per_1000w"] > 0:
        ratio = round(ai_stats["flags_per_1000w"] / human_stats["flags_per_1000w"], 2)
        print(f"\nAI rate is {ratio}x the human rate")
    elif ai_stats["flags_per_1000w"] > 0:
        print("\nHuman rate is 0 -- AI rate is nonzero, ratio is undefined (infinitely discriminative on this data)")
    else:
        print("\nBoth rates are 0 -- no signal either direction yet")

    all_rules = set(human_stats["rule_counts"]) | set(ai_stats["rule_counts"])
    print(f"\n{'Rule':30} {'Human':>8} {'AI':>8}  Verdict")
    print("-" * 65)
    for rule in sorted(all_rules):
        h = human_stats["rule_counts"].get(rule, 0)
        a = ai_stats["rule_counts"].get(rule, 0)
        if h == 0 and a > 0:
            verdict = "AI-only so far -- promising"
        elif h > 0 and a == 0:
            verdict = "human-only so far -- concerning"
        elif a > h:
            verdict = "fires more on AI"
        elif h > a:
            verdict = "fires more on human"
        else:
            verdict = "equal"
        print(f"{rule:30} {h:>8} {a:>8}  {verdict}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_corpora.py <human_dir> <ai_dir>")
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])