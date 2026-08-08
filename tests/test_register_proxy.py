from scripts.register_proxy import avg_sentence_length, contraction_rate_per_1000w


def test_avg_sentence_length_short_sentences():
    text = "I went out. It was fun. We left early."
    result = avg_sentence_length(text)
    assert result == 3.0


def test_avg_sentence_length_long_sentence():
    text = "This is a considerably longer sentence with many more words in it than usual."
    result = avg_sentence_length(text)
    assert result > 10


def test_avg_sentence_length_empty_text():
    assert avg_sentence_length("") == 0.0


def test_contraction_rate_detects_contractions():
    text = "I don't know if we're ready, but I'll try. It isn't easy."
    rate = contraction_rate_per_1000w(text)
    assert rate > 0


def test_contraction_rate_zero_on_formal_text():
    text = "This report does not contain any informal contractions whatsoever in its construction."
    rate = contraction_rate_per_1000w(text)
    assert rate == 0.0


def test_contraction_rate_empty_text():
    assert contraction_rate_per_1000w("") == 0.0