import html

import streamlit as st

from layer1 import PatternScorer

st.set_page_config(page_title="Draft Audit", layout="centered")

st.title("Draft Audit")
st.caption("Pattern and statistical review, span by span")

st.info(
    "Statistical layer (Binoculars) is not built into this app yet -- "
    "see layer2_binoculars.py, run separately, GPU required. Everything "
    "below is Layer 1 pattern signal only. Treat any result here as "
    "partial, not a final human/machine verdict."
)

text = st.text_area("Paste text to analyze", height=250, key="input_text")
run_clicked = st.button("Run analysis")


def render_highlighted(document, flags, excluded_spans=()):
    def safe(s):
        escaped = html.escape(s)
        for ch in ("*", "_", "`", "#"):
            escaped = escaped.replace(ch, f"\\{ch}")
        return escaped

    markers = [
        (f.start, f.end, "background:#f8d7da;", html.escape(f.rule_name))
        for f in flags if f.end > f.start
    ] + [
        (es, ee, "background:#e2e3e5;color:#6c757d;", "Excluded: legal boilerplate")
        for es, ee in excluded_spans
    ]
    markers.sort(key=lambda m: m[0])

    pieces = []
    cursor = 0
    for start, end, style, title in markers:
        if start < cursor:
            continue
        pieces.append(safe(document[cursor:start]))
        pieces.append(
            f'<span style="{style}border-radius:3px;padding:1px 2px;" '
            f'title="{title}">{safe(document[start:end])}</span>'
        )
        cursor = end
    pieces.append(safe(document[cursor:]))
    return "".join(pieces).replace("\n", "<br>")


if run_clicked:
    if not text.strip():
        st.warning("Paste some text first.")
    else:
        result = PatternScorer().analyze(text)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Word count", result.word_count)
        col2.metric("Flags", result.flag_count)
        col3.metric("Density /1000w", result.density_per_1000w)
        col4.metric("Suppressed (legal)", result.suppressed_count)

        st.subheader("Annotated text")
        st.markdown(
            render_highlighted(text, result.flags, result.excluded_spans),
            unsafe_allow_html=True,
        )

        st.subheader(f"Flagged spans ({result.flag_count})")
        if not result.flags:
            st.write("No pattern flags found.")
        else:
            for flag in result.flags:
                label = f"[{flag.rule_id}] {flag.match_text[:60]!r}"
                with st.expander(label):
                    st.write(f"**Rule:** {flag.rule_name}")
                    st.write(f"**Why flagged:** {flag.explanation}")