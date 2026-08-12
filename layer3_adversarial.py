"""
Layer 3: adversarial robustness testing.

Not a user-facing "humanize this text" feature. This module exists to
answer one question honestly: if a document is flagged by Layers 1/2,
how much does that verdict survive a cheap, automated paraphrase attack?

Reuses the Qwen2.5-1.5B-Instruct model already loaded for Layer 2's
performer -- no extra model download, no extra GPU memory beyond what
Layer 2 already needs.

Important limitation, stated up front: a locally-run 1.5B-parameter
model doing a single prompted paraphrase is a WEAK attack compared to
a purpose-built commercial paraphraser (e.g. Quillbot -- see
HUMANIZER_FINDINGS.md for those manually-run numbers). This module
measures robustness against a cheap, automatable attack, not the
strongest attack possible. The two results are not equivalent and
should never be reported as if they were.

Chunking, and why it's necessary: a single-shot "paraphrase this whole
document" prompt to a 1.5B model reliably collapses into summarization
instead of paraphrase, regardless of max_new_tokens -- confirmed by
direct measurement (word count ratio dropped to 0.18-0.25 on a
1222-word document, even at max_new_tokens=2048). Splitting into
~120-word sentence-aligned chunks and paraphrasing each independently
restored length fidelity to 0.93-1.08 across every document tested.
See LAYER3_FINDINGS.md for the full account.
"""

import re

from layer1 import PatternScorer


PARAPHRASE_PROMPT = (
    "Rewrite the following text in your own words. Keep the meaning, "
    "length, and tone the same. Do not add commentary, headers, or "
    "explanation -- output only the rewritten text.\n\n{text}"
)


def generate_paraphrase(text: str, performer, tok, device, max_new_tokens: int = 400) -> str:
    """
    Paraphrases a single, short (~chunk-sized) piece of text in one
    generation call. NOT reliable on whole documents -- see module
    docstring. Use chunked_paraphrase() for anything longer than a
    couple of sentences.
    """
    import torch

    messages = [{"role": "user", "content": PARAPHRASE_PROMPT.format(text=text)}]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tok(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output = performer.generate(
            **ids,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tok.eos_token_id,
        )

    generated = output[0][ids["input_ids"].shape[1]:]
    return tok.decode(generated, skip_special_tokens=True).strip()


def sentence_chunks(text: str, target_words: int = 120) -> list:
    """Splits text into chunks of roughly target_words, breaking only at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current = []
    current_words = 0
    for sent in sentences:
        w = len(sent.split())
        if current_words + w > target_words and current:
            chunks.append(' '.join(current))
            current = []
            current_words = 0
        current.append(sent)
        current_words += w
    if current:
        chunks.append(' '.join(current))
    return chunks


def chunked_paraphrase(text: str, performer, tok, device, target_words: int = 120) -> str:
    """
    The actual attack: splits text into sentence-aligned chunks and
    paraphrases each independently, then rejoins. Restores length
    fidelity that whole-document generate_paraphrase() cannot achieve
    -- see module docstring.
    """
    chunks = sentence_chunks(text, target_words)
    paraphrased_chunks = [
        generate_paraphrase(c, performer, tok, device, max_new_tokens=300)
        for c in chunks
    ]
    return ' '.join(paraphrased_chunks)


def run_adversarial_test(text: str, performer, tok, device, observer=None) -> dict:
    """
    Runs Layer 1 on the original and on a chunked paraphrase.
    If `observer` is provided, also runs Layer 2 (Binoculars) on both.
    Reports the comparison; does not judge or modify anything.
    """
    from layer2_binoculars import binoculars_score

    original_result = PatternScorer().analyze(text)
    paraphrase = chunked_paraphrase(text, performer, tok, device)
    paraphrase_result = PatternScorer().analyze(paraphrase)

    out = {
        "original_flags": original_result.flag_count,
        "original_word_count": original_result.word_count,
        "original_rules": sorted({f.rule_id for f in original_result.flags}),
        "paraphrase_flags": paraphrase_result.flag_count,
        "paraphrase_word_count": paraphrase_result.word_count,
        "paraphrase_rules": sorted({f.rule_id for f in paraphrase_result.flags}),
        "paraphrase_text": paraphrase,
    }

    if observer is not None:
        out["original_binoculars"] = binoculars_score(text, observer, performer, tok, device)
        out["paraphrase_binoculars"] = binoculars_score(paraphrase, observer, performer, tok, device)

    return out


if __name__ == "__main__":
    import sys
    from layer2_binoculars import load_models

    if len(sys.argv) != 2:
        print("Usage: python layer3_adversarial.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    print("Loading models (downloads ~3GB on first run if not cached)...")
    observer, performer, tok, device = load_models()
    print(f"Running on {device}")

    result = run_adversarial_test(text, performer, tok, device, observer=observer)

    print(f"\nOriginal: {result['original_flags']} flags on {result['original_word_count']} words")
    print(f"  Rules: {result['original_rules']}")
    print(f"Paraphrase: {result['paraphrase_flags']} flags on {result['paraphrase_word_count']} words")
    print(f"  Rules: {result['paraphrase_rules']}")
    print(f"\nOriginal Binoculars score: {result['original_binoculars']:.4f}")
    print(f"Paraphrase Binoculars score: {result['paraphrase_binoculars']:.4f}")