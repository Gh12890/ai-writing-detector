import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from streamlit.testing.v1 import AppTest


def test_app_loads_without_error():
    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception

def test_hero_mentions_colab():
    at = AppTest.from_file("../app.py")
    at.run()
    assert not at.exception
    markdown_texts = [m.value for m in at.markdown]
    assert any("Colab" in m for m in markdown_texts)

def test_colab_box_renders_after_analysis():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input("A short piece of sample text to analyze.")
    at.button[0].click()
    at.run()
    assert not at.exception
    markdown_texts = [m.value for m in at.markdown]
    assert any("Open Layer 2 &amp; 3 in Colab" in m for m in markdown_texts)

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
    warning_texts = [w.value for w in at.warning]
    assert any("Paste some text or upload a PDF first" in w for w in warning_texts)


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
    assert any("Formatting-pattern flags (3)" in h for h in headers)
    assert any("Word-choice flags (3)" in h for h in headers)
def test_density_zone_boundaries():
    from app import density_zone

    assert density_zone(0.0) == ("Low", "gray")
    assert density_zone(0.67) == ("Low", "gray")
    assert density_zone(0.68) == ("Elevated", "badge-elevated")
    assert density_zone(3.0) == ("Elevated", "badge-elevated")
    assert density_zone(3.09) == ("High", "badge-high")
    assert density_zone(10.0) == ("High", "badge-high")


def test_density_badges_render_low_for_plain_text():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "The cat sat quietly on the warm windowsill each afternoon, "
        "watching the birds outside."
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    markdown_texts = [m.value for m in at.markdown]
    assert any("Formatting patterns: Low" in m for m in markdown_texts)
    assert any("Word choice patterns: Low" in m for m in markdown_texts)


def test_density_badges_render_high_for_flag_heavy_text():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "This groundbreaking approach serves as a testament to innovation.\n\n"
        "1. First Point\n2. Second Point\n3. Third Point"
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    markdown_texts = [m.value for m in at.markdown]
    assert any("Formatting patterns: High" in m for m in markdown_texts)
    assert any("Word choice patterns: High" in m for m in markdown_texts)
def test_density_percent_boundaries():
    from app import density_percent

    assert density_percent(0.0) == 0
    assert density_percent(0.67) == 0
    assert density_percent(1.88) == 50
    assert density_percent(3.09) == 100
    assert density_percent(10.0) == 100


def test_density_percent_shown_in_badges():
    at = AppTest.from_file("../app.py")
    at.run()
    at.text_area(key="input_text").input(
        "This groundbreaking approach serves as a testament to innovation.\n\n"
        "1. First Point\n2. Second Point\n3. Third Point"
    )
    at.button[0].click()
    at.run()
    assert not at.exception
    markdown_texts = [m.value for m in at.markdown]
    assert any("(100%)" in m for m in markdown_texts)

