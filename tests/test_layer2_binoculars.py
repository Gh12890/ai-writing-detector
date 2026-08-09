"""
Tests for layer2_binoculars.py's pure scoring math, using fully
synthetic fake models -- no real weights, no network access, no GPU.

This deliberately does NOT test load_models() -- that needs real
network access to Hugging Face and downloads ~3GB, which would make CI
slow and flaky (or fail outright in restricted environments) if it ran
automatically on every push. load_models() can only be verified by a
human running it somewhere with a real GPU/network, same as the rest
of this project's Layer 2 work has been from the start.
"""

import torch

from layer2_binoculars import binoculars_score_full_document, binoculars_score

VOCAB = 50


class FakeOutput:
    def __init__(self, logits):
        self.logits = logits


class FakeModel:
    def __init__(self, seed):
        self.seed = seed

    def __call__(self, input_ids=None, **kwargs):
        torch.manual_seed(self.seed)
        seq_len = input_ids.shape[1]
        logits = torch.randn(1, seq_len, VOCAB)
        return FakeOutput(logits)


class _FakeBatchEncoding(dict):
    def to(self, device):
        return self


class FakeTokenizer:
    def __call__(self, text, return_tensors=None, truncation=False, max_length=None):
        n = len(text)
        if truncation and max_length:
            n = min(n, max_length)
        ids = torch.arange(1, n + 1) % VOCAB
        return _FakeBatchEncoding(input_ids=ids.unsqueeze(0))


def test_full_document_chunks_correctly():
    observer, performer, tok = FakeModel(1), FakeModel(2), FakeTokenizer()
    text = "x" * 25
    result = binoculars_score_full_document(
        text, observer, performer, tok, "cpu", chunk_size=10, min_chunk_tokens=1
    )
    assert result["num_chunks"] == 3
    assert result["total_tokens_scored"] == 22
    assert len(result["per_chunk_scores"]) == 3


def test_small_trailing_chunk_is_dropped():
    observer, performer, tok = FakeModel(1), FakeModel(2), FakeTokenizer()
    text = "x" * 21
    result = binoculars_score_full_document(
        text, observer, performer, tok, "cpu", chunk_size=10, min_chunk_tokens=2
    )
    assert result["num_chunks"] == 2


def test_pooled_score_is_positive_number():
    observer, performer, tok = FakeModel(1), FakeModel(2), FakeTokenizer()
    text = "x" * 30
    result = binoculars_score_full_document(text, observer, performer, tok, "cpu", chunk_size=10)
    assert result["pooled_score"] > 0


def test_empty_text_returns_none_score_not_a_crash():
    observer, performer, tok = FakeModel(1), FakeModel(2), FakeTokenizer()
    result = binoculars_score_full_document("", observer, performer, tok, "cpu")
    assert result["pooled_score"] is None
    assert result["num_chunks"] == 0


def test_truncated_score_runs_without_error():
    observer, performer, tok = FakeModel(1), FakeModel(2), FakeTokenizer()
    text = "x" * 600
    score = binoculars_score(text, observer, performer, tok, "cpu")
    assert isinstance(score, float)
    assert score > 0