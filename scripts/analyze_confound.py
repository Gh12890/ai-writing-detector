"""
Tests the formality confound flagged in FINDINGS.md and LAYER2_FINDINGS.md
directly, with a number, instead of eyeballing a small table.

Run this against corpus/ (human-only text) specifically. Every document
in that folder has the same authorship label -- human -- by
construction. If flag density still correlates strongly with formality
proxies WITHIN that human-only set, there's no authorship variation left
to explain the correlation except register itself.

Usage:
    python scripts/analyze_confound.py corpus/
"""

import sys
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from layer1 import PatternScorer
from scripts.register_proxy import avg_sentence_length, contraction_rate_per_1000w


def analyze(corpus_dir: str) -> dict:
    txt_files = sorted(Path(corpus_dir).glob("*.txt"))
    if len(txt_files) < 3:
        print(f"Need at least 3 documents for a meaningful correlation; found {len(txt_files)}.")
        return {}

    rows = []
    for f in txt_files:
        text = f.read_text(encoding="utf-8")
        result = PatternScorer().analyze(text)
        rows.append({
            "name": f.name,
            "density": result.density_per_1000w,
            "structural_density": result.structural_density_per_1000w,
            "lexical_density": result.lexical_density_per_1000w,
            "avg_sentence_length": avg_sentence_length(text),
            "contraction_rate": contraction_rate_per_1000w(text),
        })

    asls = [r["avg_sentence_length"] for r in rows]
    crs = [r["contraction_rate"] for r in rows]

    print(f"\n{'Document':20} {'Total':>8} {'Struct':>8} {'Lex':>8} {'AvgSentLen':>12} {'Contr/1000w':>12}")
    for r in rows:
        print(f"{r['name']:20} {r['density']:>8} {r['structural_density']:>8} {r['lexical_density']:>8} "
              f"{r['avg_sentence_length']:>12} {r['contraction_rate']:>12}")

    def safe_corr(a, b):
        try:
            return round(statistics.correlation(a, b), 3)
        except statistics.StatisticsError:
            return None

    densities = [r["density"] for r in rows]
    structural_densities = [r["structural_density"] for r in rows]
    lexical_densities = [r["lexical_density"] for r in rows]

    print(f"\n--- Overall density (old behavior, kept for comparison) ---")
    print(f"Correlation vs. avg sentence length: {safe_corr(densities, asls)}")
    print(f"Correlation vs. contraction rate:     {safe_corr(densities, crs)}")

    print(f"\n--- Structural tier only ---")
    corr_struct_asl = safe_corr(structural_densities, asls)
    corr_struct_cr = safe_corr(structural_densities, crs)
    print(f"Correlation vs. avg sentence length: {corr_struct_asl}")
    print(f"Correlation vs. contraction rate:     {corr_struct_cr}")
    if corr_struct_asl is None:
        print("(None = no structural flags fired anywhere in this corpus -- no variance to correlate.")
        print(" This is NOT the same as 'proven confound-free' -- it means untested, not clean.)")

    print(f"\n--- Lexical tier only ---")
    corr_lex_asl = safe_corr(lexical_densities, asls)
    corr_lex_cr = safe_corr(lexical_densities, crs)
    print(f"Correlation vs. avg sentence length: {corr_lex_asl}")
    print(f"Correlation vs. contraction rate:     {corr_lex_cr}")

    print("\nInterpretation guide:")
    print("  |r| > 0.6   -- strong correlation, real confound risk")
    print("  |r| 0.3-0.6 -- moderate, worth investigating further")
    print("  |r| < 0.3   -- weak, confound less likely to explain the pattern")
    print("If the tier split is doing its job: lexical correlations should stay")
    print("high (this is the known, already-measured problem), while structural")
    print("correlations should be weaker, None (no data yet), or lower than lexical.")

    return {
        "rows": rows,
        "corr_sentence_length": safe_corr(densities, asls),
        "corr_contraction_rate": safe_corr(densities, crs),
        "corr_structural_sentence_length": corr_struct_asl,
        "corr_structural_contraction_rate": corr_struct_cr,
        "corr_lexical_sentence_length": corr_lex_asl,
        "corr_lexical_contraction_rate": corr_lex_cr,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_confound.py <corpus_directory>")
        sys.exit(1)
    analyze(sys.argv[1])