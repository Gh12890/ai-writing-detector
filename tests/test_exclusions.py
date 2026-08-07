from layer1.exclusions import find_excluded_spans, _overlaps, is_excluded
from layer1 import PatternScorer


def test_statute_citation_detected():
    spans = find_excluded_spans("Section 138 of the Negotiable Instruments Act, 1881 applies here.")
    assert len(spans) == 1


def test_case_citation_air_detected():
    spans = find_excluded_spans("The court in AIR 1973 SC 157 held that...")
    assert len(spans) == 1


def test_case_citation_scc_detected():
    spans = find_excluded_spans("As held in (2019) 4 SCC 1, the principle applies.")
    assert len(spans) == 1


def test_standard_phrase_detected():
    spans = find_excluded_spans("WHEREAS the parties agree to the following terms.")
    assert len(spans) == 1


def test_no_excluded_spans_in_plain_text():
    spans = find_excluded_spans("This is just a normal sentence about nothing legal at all.")
    assert spans == []


def test_overlaps_function():
    assert _overlaps(10, 20, 15, 25) is True
    assert _overlaps(10, 20, 12, 18) is True
    assert _overlaps(10, 20, 25, 30) is False
    assert _overlaps(10, 20, 20, 30) is False
    assert _overlaps(10, 20, 0, 10) is False


def test_flag_outside_excluded_span_still_fires():
    text = "Section 138 of the Negotiable Instruments Act, 1881 functions as a deterrent."
    result = PatternScorer().analyze(text)
    assert any(f.rule_id == "copula_avoidance" for f in result.flags)


def test_flag_inside_excluded_span_is_suppressed():
    text = "Section 5 of the Serves As A Model Act, 2020 governs procedure."
    result = PatternScorer().analyze(text)
    assert not any(f.rule_id == "copula_avoidance" for f in result.flags)
    assert result.suppressed_count >= 1


def test_legal_boilerplate_fixture_has_excluded_spans():
    from tests.test_layer1 import LEGAL_BOILERPLATE_TEXT
    result = PatternScorer().analyze(LEGAL_BOILERPLATE_TEXT)
    assert len(result.excluded_spans) >= 1