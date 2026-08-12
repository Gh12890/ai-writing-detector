"""
Layer 3: adversarial robustness testing.

Not a user-facing "humanize this text" feature. This module exists to
answer one question honestly: if a document is flagged by Layers 1/2,
how much does that verdict survive a paraphrase attack?

Uses the Claude API for paraphrase generation -- no local model loading,
no GPU, no Colab session fragility. This is a genuinely different, and
likely stronger, attacker than the local Qwen2.5-1.5B approach this
module used previously (see LAYER3_FINDINGS.md for those results,
kept as a separate, labeled comparison, not overwritten).

Real, non-trivial change from the earlier version: this now costs money
per call (Anthropic API usage) and sends document text to a third-party
API. Same consent-scope question already applied to Quillbot testing
applies here -- verify before running on real corpus documents, not
just test text.
"""

from layer1 import PatternScorer


PARAPHRASE_PROMPT = (
    "Rewrite the following text in your own words. Keep the meaning, "
    "length, and tone the same -- do not summarize or shorten it. "
    "Output only the rewritten text, with no commentary, headers, or "
    "explanation.\n\n{text}"
)


def generate_paraphrase(text: str, client, model: str = "claude-sonnet-5") -> str:
    """
    Paraphrases text via the Claude API. Unlike the earlier local-model
    version, this does not require chunking for length fidelity --
    Claude follows the length-preservation instruction directly. If you
    observe compression on long documents in practice, chunking can be
    reintroduced the same way as before; not done here until there's a
    real measured reason to.
    """
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": PARAPHRASE_PROMPT.format(text=text)}],
    )
    return response.content[0].text.strip()


def run_adversarial_test(text: str, client, observer=None, performer=None, tok=None, device=None) -> dict:
    """
    Runs Layer 1 on the original and on a Claude-generated paraphrase.
    If observer/performer/tok/device are all provided (Layer 2's loaded
    models), also runs Layer 2 (Binoculars) on both -- fully optional,
    Layer 3 no longer depends on Layer 2 being loaded at all.
    """
    original_result = PatternScorer().analyze(text)
    paraphrase = generate_paraphrase(text, client)
    paraphrase_result = PatternScorer().analyze(paraphrase)

    out = {
        "original_flags": original_result.flag_count,
        "original_word_count": original_result.word_count,
        "original_rules": sorted({f.rule_id for f in original_result.flags}),
        "paraphrase_flags": paraphrase_result.flag_count,
        "paraphrase_word_count": paraphrase_result.word_count,
        "paraphrase_rules": sorted({f.rule_id for f in paraphrase_result.flags}),
        "paraphrase_text": paraphrase,
        "word_count_ratio": (
            paraphrase_result.word_count / original_result.word_count
            if original_result.word_count else 0
        ),
    }

    if all(x is not None for x in (observer, performer, tok, device)):
        from layer2_binoculars import binoculars_score
        out["original_binoculars"] = binoculars_score(text, observer, performer, tok, device)
        out["paraphrase_binoculars"] = binoculars_score(paraphrase, observer, performer, tok, device)

    return out


if __name__ == "__main__":
    import sys
    import os
    import anthropic

    if len(sys.argv) != 2:
        print("Usage: python layer3_adversarial.py <path_to_text_file>")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY as an environment variable first.")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    client = anthropic.Anthropic(api_key=api_key)
    result = run_adversarial_test(text, client)

    print(f"\nOriginal: {result['original_flags']} flags on {result['original_word_count']} words")
    print(f"  Rules: {result['original_rules']}")
    print(f"Paraphrase: {result['paraphrase_flags']} flags on {result['paraphrase_word_count']} words")
    print(f"  Rules: {result['paraphrase_rules']}")
    print(f"Word count ratio: {result['word_count_ratio']:.2f}")