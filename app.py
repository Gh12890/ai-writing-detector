import html
import io

import streamlit as st

from layer1 import PatternScorer

st.set_page_config(page_title="Draft Audit", layout="centered")

# Google Analytics
GA_MEASUREMENT_ID = "G-7HP14P92V2"

st.markdown(
    f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_MEASUREMENT_ID}');
    </script>
    """,
    unsafe_allow_html=True,
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #15120F;
    --ink-surface: #1F1A16;
    --ink-border: #332C26;
    --accent-red: #B23A2E;
    --accent-red-soft: rgba(178, 58, 46, 0.16);
    --accent-gray: #8A8580;
    --accent-gray-soft: rgba(138, 133, 128, 0.18);
    --accent-amber: #C98A3E;
    --accent-amber-soft: rgba(201, 138, 62, 0.14);
    --text-primary: #F2EFEA;
    --text-muted: #B5AFA7;
}

.stApp {
    background-color: var(--ink);
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Source Serif 4', serif !important;
    color: var(--text-primary) !important;
}

code, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Hero */
.da-hero {
    padding: 12px 0 34px 0;
    animation: da-fade-in 0.5s ease-out;
}
@keyframes da-fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.da-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-red);
    margin-bottom: 10px;
}
.da-hero h1 {
    font-size: 3.1rem;
    margin: 0 0 10px 0;
    letter-spacing: -0.015em;
    line-height: 1.05;
}
.da-hero p.tagline {
    color: var(--text-muted);
    font-size: 1.2rem;
    line-height: 1.5;
    max-width: 640px;
    margin-bottom: 22px;
}

/* Legend -- replaces the old quoted example */
.da-legend {
    display: flex;
    gap: 28px;
    flex-wrap: wrap;
}
.da-legend-item {
    display: flex;
    align-items: center;
    gap: 9px;
    color: var(--text-muted);
    font-size: 0.98rem;
}
.da-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.da-dot.red { background: var(--accent-red); }
.da-dot.gray { background: var(--accent-gray); }
.da-legend-item strong {
    color: var(--text-primary);
    font-weight: 600;
    margin-right: 4px;
}

/* Results box (real annotated output after running analysis) */
.da-example {
    background: var(--ink-surface);
    border: 1px solid var(--ink-border);
    border-radius: 10px;
    padding: 20px 22px;
    font-size: 1.02rem;
    line-height: 1.8;
    color: var(--text-muted);
}
.da-example .flag-red {
    background: var(--accent-red-soft);
    color: var(--text-primary);
    border-bottom: 2px solid var(--accent-red);
    border-radius: 3px;
    padding: 1px 4px;
}
.da-example .flag-gray {
    background: var(--accent-gray-soft);
    color: var(--text-muted);
    border-bottom: 2px solid var(--accent-gray);
    border-radius: 3px;
    padding: 1px 4px;
}

/* Cards */
.da-cards {
    display: flex;
    gap: 20px;
    margin: 36px 0 10px 0;
}
.da-card {
    flex: 1;
    background: var(--ink-surface);
    border: 1px solid var(--ink-border);
    border-radius: 12px;
    padding: 24px 26px;
    transition: border-color 0.2s ease;
}
.da-card:hover {
    border-color: var(--accent-red);
}
.da-card h3 {
    font-size: 1.3rem !important;
    margin: 0 0 12px 0 !important;
}
.da-card ul {
    margin: 0 0 18px 0;
    padding-left: 18px;
    color: var(--text-muted);
    font-size: 0.95rem;
    line-height: 1.7;
}
.da-card ul li strong { color: var(--text-primary); }
.da-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--accent-red);
    background: var(--accent-red-soft);
    padding: 4px 9px;
    border-radius: 5px;
    margin-bottom: 12px;
}
.da-badge.gray {
    color: var(--accent-gray);
    background: var(--accent-gray-soft);
}
.da-badge.badge-elevated {
    color: var(--accent-amber);
    background: var(--accent-amber-soft);
}
.da-badge.badge-high {
    color: var(--accent-red);
    background: var(--accent-red-soft);
    font-weight: 700;
}
.da-cta {
    display: inline-block;
    width: 100%;
    text-align: center;
    background: var(--accent-red);
    color: #fff !important;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 11px 0;
    border-radius: 8px;
    text-decoration: none !important;
    transition: background 0.15s ease;
    box-sizing: border-box;
}
.da-cta:hover { background: #943025; }
.da-cta.ghost {
    background: transparent;
    border: 1px solid var(--ink-border);
    color: var(--text-muted) !important;
}
.da-cta.ghost:hover {
    border-color: var(--accent-gray);
    background: transparent;
}

/* How it works */
.da-steps {
    margin: 36px 0 12px 0;
}
.da-steps h3 { margin-bottom: 18px !important; font-size: 1.3rem !important; }
.da-step {
    display: flex;
    gap: 16px;
    margin-bottom: 18px;
    align-items: flex-start;
}
.da-step-num {
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-red);
    font-weight: 500;
    font-size: 0.9rem;
    padding-top: 2px;
    min-width: 24px;
}
.da-step-text { color: var(--text-muted); font-size: 1rem; line-height: 1.6; }
.da-step-text strong { color: var(--text-primary); }

.da-divider {
    border: none;
    border-top: 1px solid var(--ink-border);
    margin: 34px 0;
}

.da-source-note {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin: 4px 0 14px 0;
}

/* Streamlit widget restyle */
.stTextArea textarea {
    background: var(--ink-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--ink-border) !important;
    font-size: 1rem !important;
}
.stButton button {
    background: var(--accent-red) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 8px 22px !important;
}
.stButton button:hover {
    background: #943025 !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: var(--accent-amber-soft) !important;
    border: 2px dashed var(--accent-amber) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span {
    color: var(--text-primary) !important;
}
[data-testid="stFileUploader"] button {
    background: var(--accent-amber) !important;
    color: #1A1207 !important;
    border: none !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #B37A32 !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="da-hero">
        <div class="da-eyebrow">AI-writing detector</div>
        <h1>Draft Audit</h1>
        <p class="tagline">Pattern and statistical review, span by span -- shows its reasoning, not just a verdict.</p>
        <div class="da-legend">
            <div class="da-legend-item"><span class="da-dot red"></span><strong>AI-flag</strong> a pattern common in AI-generated text</div>
            <div class="da-legend-item"><span class="da-dot gray"></span><strong>Excluded</strong> legal boilerplate, not scored</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="da-cards">
        <div class="da-card">
            <span class="da-badge">Live &middot; instant &middot; free</span>
            <h3>Layer 1 -- Pattern Rules</h3>
            <ul>
                <li><strong>25 readable rules</strong>, split into structural and lexical tiers</li>
                <li><strong>No GPU, no wait</strong> -- runs right here in your browser</li>
                <li><strong>Every flag explained</strong> -- click any flag to see exactly why</li>
            </ul>
            <a class="da-cta" href="#draft-audit">Try it below &darr;</a>
        </div>
        <div class="da-card">
            <span class="da-badge gray">Free &middot; your own GPU &middot; ~5 min setup</span>
            <h3>Layers 2 & 3 -- Colab</h3>
            <ul>
                <li><strong>Statistical scorer</strong> (Binoculars method) plus an <strong>adversarial robustness check</strong></li>
                <li><strong>Runs on your own free Google account</strong> -- no cost, no load on this page</li>
                <li><strong>Clones this repo directly</strong> -- no manual setup beyond opening the link</li>
            </ul>
            <a class="da-cta ghost" href="https://colab.research.google.com/github/Gh12890/ai-writing-detector/blob/master/colab_demo.ipynb" target="_blank">Open Layer 2 &amp; 3 in Colab &rarr;</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="da-steps">
        <h3>How to get started</h3>
        <div class="da-step"><div class="da-step-num">01</div><div class="da-step-text"><strong>Paste your text or upload a PDF</strong> below.</div></div>
        <div class="da-step"><div class="da-step-num">02</div><div class="da-step-text"><strong>Click Run analysis</strong> -- Layer 1 runs instantly, no setup needed.</div></div>
        <div class="da-step"><div class="da-step-num">03</div><div class="da-step-text"><strong>Read the flagged spans</strong> -- formatting patterns and word-choice patterns are reported separately, since measurement showed they behave differently.</div></div>
        <div class="da-step"><div class="da-step-num">04</div><div class="da-step-text"><strong>Go deeper, optionally</strong> -- open the Colab link above for the statistical scorer and the robustness check, free, on your own GPU.</div></div>
    </div>
    <hr class="da-divider">
    """,
    unsafe_allow_html=True,
)

st.markdown('<a name="draft-audit"></a>', unsafe_allow_html=True)

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
st.markdown(
    '<div class="da-source-note">PDF text extraction only -- scanned or image-only PDFs '
    "aren't supported (no OCR). If a PDF returns no text, try pasting the text directly instead.</div>",
    unsafe_allow_html=True,
)

text = st.text_area("Or paste text to analyze", height=250, key="input_text")
run_clicked = st.button("Run analysis")


def extract_pdf_text(uploaded_file) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def render_highlighted(document: str, flags, excluded_spans=()) -> str:
    def safe(s: str) -> str:
        return html.escape(s)

    markers = [
        (f.start, f.end, "flag-red", html.escape(f.rule_name))
        for f in flags if f.end > f.start
    ] + [
        (es, ee, "flag-gray", "Excluded: legal boilerplate")
        for es, ee in excluded_spans
    ]
    markers.sort(key=lambda m: m[0])

    pieces = []
    cursor = 0
    for start, end, css_class, title in markers:
        if start < cursor:
            continue
        pieces.append(safe(document[cursor:start]))
        pieces.append(
            f'<span class="{css_class}" title="{title}">{safe(document[start:end])}</span>'
        )
        cursor = end
    pieces.append(safe(document[cursor:]))
    return f'<div class="da-example">{"".join(pieces).replace(chr(10), "<br>")}</div>'


def density_zone(rate: float) -> tuple[str, str]:
    """
    Coarse Low/Elevated/High label based on this project's own measured
    corpus averages (human ~0.67/1000w, AI ~3.09/1000w -- see FINDINGS.md's
    compare_corpora.py run). NOT a calibrated probability, NOT a claim
    about authorship -- just where this document's flag rate sits
    relative to a small, evolving reference corpus. Same boundary is
    applied to both structural and lexical rates as an approximation;
    the two tiers weren't measured separately at this resolution yet.
    """
    if rate <= 0.67:
        return "Low", "gray"
    elif rate < 3.09:
        return "Elevated", "badge-elevated"
    else:
        return "High", "badge-high"


HUMAN_ANCHOR_PER_1000W = 0.67
AI_ANCHOR_PER_1000W = 3.09


def density_percent(rate: float) -> int:
    """
    Expresses a document's flag rate as a percentage of the way from
    this project's measured human corpus average to its measured AI
    corpus average, clamped to 0-100. Rescaling of the same real,
    already-measured density_zone anchors -- NOT a calibrated
    probability of AI authorship.
    """
    span = AI_ANCHOR_PER_1000W - HUMAN_ANCHOR_PER_1000W
    pct = (rate - HUMAN_ANCHOR_PER_1000W) / span * 100
    return max(0, min(100, round(pct)))


COLAB_URL = "https://colab.research.google.com/github/Gh12890/ai-writing-detector/blob/master/colab_demo.ipynb"


def render_colab_box():
    st.markdown(
        f"""
        <div class="da-card" style="margin-top:28px;">
            <span class="da-badge gray">Free &middot; your own GPU</span>
            <h3>Want the full picture? Run Layer 2 & 3 in Colab</h3>
            <p style="color:var(--text-muted);font-size:0.95rem;line-height:1.6;">
                Layer 2 (statistical scorer) and Layer 3 (adversarial robustness
                check) need more compute than this free page offers. The notebook
                runs on <strong style="color:var(--text-primary);">your own free Google account</strong> --
                no cost, no wait, no load on your device.
            </p>
            <a class="da-cta" href="{COLAB_URL}" target="_blank">Open Layer 2 &amp; 3 in Colab</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if run_clicked:
    source_text = None
    source_label = None

    if uploaded_pdf is not None:
        try:
            source_text = extract_pdf_text(uploaded_pdf)
            source_label = f"PDF: {uploaded_pdf.name}"
            if not source_text:
                st.warning(
                    "Couldn't extract any text from this PDF -- it may be a scanned "
                    "image without a text layer (no OCR support). Try pasting the "
                    "text directly instead."
                )
        except Exception as e:
            st.error(f"Couldn't read this PDF: {e}")

    if not source_text and text.strip():
        source_text = text
        source_label = "pasted text"

    if not source_text:
        st.warning("Paste some text or upload a PDF first.")
        render_colab_box()
    else:
        st.caption(f"Analyzing: {source_label}")
        result = PatternScorer().analyze(source_text)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Word count", result.word_count)
        col2.metric("Total flags", result.flag_count)
        col3.metric("Formatting patterns /1000w", result.structural_density_per_1000w)
        col4.metric("Word choice patterns /1000w", result.lexical_density_per_1000w)



        struct_label, struct_class = density_zone(result.structural_density_per_1000w)
        lex_label, lex_class = density_zone(result.lexical_density_per_1000w)
        struct_pct = density_percent(result.structural_density_per_1000w)
        lex_pct = density_percent(result.lexical_density_per_1000w)
        st.markdown(
            f"""
            <div style="display:flex; gap:12px; margin: 6px 0 18px 0;">
                <span class="da-badge {struct_class}">Formatting patterns: {struct_label} ({struct_pct}%)</span>
                <span class="da-badge {lex_class}">Word choice patterns: {lex_label} ({lex_pct}%)</span>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "These zones are relative to this project's own small, evolving corpus "
            "(see FINDINGS.md) -- not a calibrated probability, and not a claim about "
            "who or what wrote this text. Treat as a rough orientation, not a verdict."
        )

        st.caption(
            "Formatting patterns (called 'structural' in this project's findings "
            "docs) and word choice patterns (called 'lexical') are reported "
            "separately, not blended into one score. Real measurement (see "
            "FINDINGS.md) found word-choice flag density correlated strongly "
            "with formal writing register (r=0.722 with sentence length) on "
            "confirmed human text -- formatting rules showed no such "
            "correlation across the same corpus. Treat word-choice flags as "
            "weaker, register-confounded signal, and formatting flags as the "
            "more reliable evidence, until further measurement says otherwise."
        )
        if result.suppressed_count:
            st.caption(f"{result.suppressed_count} flag(s) suppressed as legal boilerplate.")

        st.subheader("Annotated text")
        st.markdown(
            render_highlighted(source_text, result.flags, result.excluded_spans),
            unsafe_allow_html=True,
        )

        by_tier = result.flags_by_tier()
        st.subheader(f"Formatting-pattern flags ({len(by_tier['structural'])})")
        if not by_tier["structural"]:
            st.write("None found.")
        else:
            for flag in by_tier["structural"]:
                label = f"[{flag.rule_id}] {flag.match_text[:60]!r}"
                with st.expander(label):
                    st.write(f"**Rule:** {flag.rule_name}")
                    st.write(f"**Why flagged:** {flag.explanation}")

        st.subheader(f"Word-choice flags ({len(by_tier['lexical'])})")
        if not by_tier["lexical"]:
            st.write("None found.")
        else:
            for flag in by_tier["lexical"]:
                label = f"[{flag.rule_id}] {flag.match_text[:60]!r}"
                with st.expander(label):
                    st.write(f"**Rule:** {flag.rule_name}")
                    st.write(f"**Why flagged:** {flag.explanation}")

        render_colab_box()
