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
    assert len(at.metric) == 3
    assert int(at.metric[1].value) > 0


def test_empty_input_shows_warning():
    at = AppTest.from_file("../app.py")
    at.run()
    at.button[0].click()
    at.run()
    assert not at.exception
    assert len(at.warning) == 1
