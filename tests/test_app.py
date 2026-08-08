import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from streamlit.testing.v1 import AppTest


def test_app_loads_without_error():
    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception


def test_run_analysis_shows_flags():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "So the short answer is: it isn't real. It's fake. "
        "If you want, I can also give you more."
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    assert len(at.metric) == 4
    assert int(at.metric[1].value) > 0


def test_suppressed_flags_shown_as_caption():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "Section 5 of the Serves As A Model Act, 2020 governs procedure."
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    caption_texts = [c.value for c in at.caption]
    assert any("suppressed" in c.lower() for c in caption_texts)


def test_empty_input_shows_warning():
    at = AppTest.from_file("../app.py")
    at.run()
    at.button[0].click()
    at.run()
    assert not at.exception
    assert len(at.warning) == 1


def test_structural_and_lexical_sections_both_render():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "This groundbreaking approach serves as a testament to innovation.\n\n"
        "1. First Point\n2. Second Point\n3. Third Point"
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    headers = [h.value for h in at.subheader]
    assert any("Structural flags (3)" in h for h in headers)
    assert any("Lexical flags (3)" in h for h in headers)