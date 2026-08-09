"""
Layer 2: statistical scorer (Binoculars method).

This is CPU/GPU-heavy and network-dependent (downloads ~3GB of model
weights on first use) -- deliberately kept separate from Layer 1, which
is instant, offline, and free. Not imported by anything automatically;
app.py loads this lazily, only when the user explicitly asks for it.

Two scoring functions exist because both were tested and neither is
clearly better -- see LAYER2_FINDINGS.md for the actual numbers:

- binoculars_score(): truncates to the first 512 tokens. Simple, fast,
  matches the original design. Only sees a document's opening section.
- binoculars_score_full_document(): chunks the whole document into
  512-token windows and pools them into one score. Tested against the
  real corpus and found to REDUCE human/AI separation, not improve it
  (LAYER2_FINDINGS.md, "full-document pooling... made it worse").

Neither is validated enough to trust as an authoritative verdict. Both
are shown, with that caveat, when this runs in the app.
"""

import math

MODEL_NAME = "Qwen/Qwen2.5-1.5B"
INSTRUCT_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


def load_models():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    observer = AutoModelForCausalLM.from_pretrained(MODEL_NAME).eval()
    performer = AutoModelForCausalLM.from_pretrained(INSTRUCT_NAME).eval()
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    observer, performer = observer.to(device), performer.to(device)

    return observer, performer, tok, device


def binoculars_score(text: str, observer, performer, tok, device) -> float:
    import torch

    ids = tok(text, return_tensors="pt", truncation=True, max_length=512).to(device)

    with torch.no_grad():
        obs_logits = observer(**ids).logits
        perf_logits = performer(**ids).logits

    labels = ids["input_ids"][:, 1:]
    obs_logits = obs_logits[:, :-1, :]
    perf_logits = perf_logits[:, :-1, :]

    ce = torch.nn.functional.cross_entropy(
        obs_logits.reshape(-1, obs_logits.size(-1)), labels.reshape(-1), reduction="mean"
    )
    ppl = torch.exp(ce)

    perf_probs = torch.nn.functional.softmax(perf_logits, dim=-1)
    obs_logprobs = torch.nn.functional.log_softmax(obs_logits, dim=-1)
    x_ce = -(perf_probs * obs_logprobs).sum(-1).mean()
    x_ppl = torch.exp(x_ce)

    return (ppl / x_ppl).item()


def binoculars_score_full_document(
    text: str, observer, performer, tok, device, chunk_size: int = 512, min_chunk_tokens: int = 20
) -> dict:
    import torch

    all_ids = tok(text, return_tensors="pt")["input_ids"][0]
    total_tokens = len(all_ids)

    chunks = [all_ids[i:i + chunk_size] for i in range(0, total_tokens, chunk_size)]
    if len(chunks) > 1 and len(chunks[-1]) < min_chunk_tokens:
        chunks = chunks[:-1]

    total_ce_sum = 0.0
    total_xce_sum = 0.0
    total_scored_tokens = 0
    chunk_scores = []

    for chunk_ids in chunks:
        ids = chunk_ids.unsqueeze(0).to(device)
        with torch.no_grad():
            obs_logits = observer(input_ids=ids).logits
            perf_logits = performer(input_ids=ids).logits

        labels = ids[:, 1:]
        obs_logits_shifted = obs_logits[:, :-1, :]
        perf_logits_shifted = perf_logits[:, :-1, :]

        n_tokens = labels.numel()
        if n_tokens == 0:
            continue

        ce_sum = torch.nn.functional.cross_entropy(
            obs_logits_shifted.reshape(-1, obs_logits_shifted.size(-1)),
            labels.reshape(-1), reduction="sum"
        ).item()

        perf_probs = torch.nn.functional.softmax(perf_logits_shifted, dim=-1)
        obs_logprobs = torch.nn.functional.log_softmax(obs_logits_shifted, dim=-1)
        xce_sum = -(perf_probs * obs_logprobs).sum(-1).sum().item()

        total_ce_sum += ce_sum
        total_xce_sum += xce_sum
        total_scored_tokens += n_tokens
        chunk_scores.append(round(math.exp(ce_sum / n_tokens) / math.exp(xce_sum / n_tokens), 4))

    if total_scored_tokens == 0:
        return {"pooled_score": None, "num_chunks": 0, "total_tokens_scored": 0, "per_chunk_scores": []}

    pooled_ppl = math.exp(total_ce_sum / total_scored_tokens)
    pooled_xppl = math.exp(total_xce_sum / total_scored_tokens)

    return {
        "pooled_score": pooled_ppl / pooled_xppl,
        "num_chunks": len(chunks),
        "total_tokens_scored": total_scored_tokens,
        "per_chunk_scores": chunk_scores,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python layer2_binoculars.py <path_to_text_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    print("Loading models (this downloads ~3GB on first run)...")
    observer, performer, tok, device = load_models()
    print(f"Running on {device}")

    truncated = binoculars_score(text, observer, performer, tok, device)
    print(f"\nTruncated (512 tok) score: {truncated:.4f}")

    full = binoculars_score_full_document(text, observer, performer, tok, device)
    print(f"Full-document pooled score: {full['pooled_score']:.4f}")
    print(f"  ({full['num_chunks']} chunks, {full['total_tokens_scored']} tokens)")