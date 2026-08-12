import html

import streamlit as st

from layer1 import PatternScorer

st.set_page_config(page_title="Draft Audit", layout="centered")

st.title("Draft Audit")
st.caption("Pattern and statistical review, span by span")

st.info(
    "Layer 1 (pattern rules) runs instantly and offline, right here. "
    "Layer 2 (statistical scorer) and Layer 3 (adversarial robustness check) "
    "need more compute than this free page offers -- see the box below your "
    "results to run all three layers together, free, on your own Google "
    "account, via Colab."
)

text = st.text_area("Paste text to analyze", height=250, key="input_text")
run_clicked = st.button("Run analysis")


def render_highlighted(document: str, flags, excluded_spans=()) -> str:
    def safe(s: str) -> str:
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


COLAB_URL = "https://colab.research.google.com/github/Gh12890/ai-writing-detector/blob/master/colab_demo.ipynb"


def render_colab_box():
    st.markdown(
        f"""
        <div style="border:1px solid #ffe08a;background:#fffaf0;
                    border-radius:10px;padding:20px 22px;margin-top:28px;">
            <h4 style="margin-top:0;">Want the full picture? Run Layer 2 & 3 in Colab</h4>
            <p style="font-size:0.9rem;color:#5c4a1a;line-height:1.55;">
                Layer 2 (statistical scorer) and Layer 3 (adversarial robustness
                check) need more compute than this free page offers. The notebook
                below runs on <strong>your own free Google account</strong> --
                no cost, no wait, no load on your device. Paste the same text in
                and get all three layers together, including how well this
                document's flags survive a paraphrase attack.
            </p>
            <a href="{COLAB_URL}" target="_blank"
               style="display:inline-flex;align-items:center;gap:8px;
                      background:#f9ab00;color:#1a1a1a;font-weight:600;
                      font-size:0.9rem;padding:10px 18px;border-radius:6px;
                      text-decoration:none;">
                Open Layer 2 & 3 in Colab
            </a>
            <div style="font-size:0.78rem;color:#8a7233;margin-top:10px;">
                Opens Google Colab in a new tab &middot; runs on a free T4 GPU
                &middot; no Draft Audit account or payment needed
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if run_clicked:
    if not text.strip():
        st.warning("Paste some text first.")
        render_colab_box()
    else:
        result = PatternScorer().analyze(text)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Word count", result.word_count)
        col2.metric("Total flags", result.flag_count)
        col3.metric("Structural /1000w", result.structural_density_per_1000w)
        col4.metric("Lexical /1000w", result.lexical_density_per_1000w)

        st.caption(
            "Structural (formatting/syntax patterns) and lexical (word/phrase "
            "lists) are reported separately, not blended into one score. "
            "Real measurement (see FINDINGS.md) found lexical flag density "
            "correlated strongly with formal writing register (r=0.722 with "
            "sentence length) on confirmed human text -- structural rules "
            "showed no such correlation across the same corpus. Treat "
            "lexical flags as weaker, register-confounded signal, and "
            "structural flags as the more reliable evidence, until further "
            "measurement says otherwise."
        )
        if result.suppressed_count:
            st.caption(f"{result.suppressed_count} flag(s) suppressed as legal boilerplate.")

        st.subheader("Annotated text")
        st.markdown(
            render_highlighted(text, result.flags, result.excluded_spans),
            unsafe_allow_html=True,
        )

        by_tier = result.flags_by_tier()
        st.subheader(f"Structural flags ({len(by_tier['structural'])})")
        if not by_tier["structural"]:
            st.write("None found.")
        else:
            for flag in by_tier["structural"]:
                label = f"[{flag.rule_id}] {flag.match_text[:60]!r}"
                with st.expander(label):
                    st.write(f"**Rule:** {flag.rule_name}")
                    st.write(f"**Why flagged:** {flag.explanation}")

        st.subheader(f"Lexical flags ({len(by_tier['lexical'])})")
        if not by_tier["lexical"]:
            st.write("None found.")
        else:
            for flag in by_tier["lexical"]:
                label = f"[{flag.rule_id}] {flag.match_text[:60]!r}"
                with st.expander(label):
                    st.write(f"**Rule:** {flag.rule_name}")
                    st.write(f"**Why flagged:** {flag.explanation}")

        render_colab_box()