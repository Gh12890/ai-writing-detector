import html

import streamlit as st

from layer1 import PatternScorer

st.set_page_config(page_title="Draft Audit", layout="centered")

st.title("Draft Audit")
st.caption("Pattern and statistical review, span by span")

st.info(
    "Layer 1 (pattern rules) runs instantly and offline. Layer 2 "
    "(statistical scorer) is opt-in below -- it downloads ~3GB of model "
    "weights on first use, needs internet access, and runs on CPU here "
    "(no GPU), so expect anywhere from ~10 seconds to a couple of "
    "minutes per document. See LAYER2_FINDINGS.md before trusting any "
    "Layer 2 number: it's small-sample, unvalidated, and one of its two "
    "scoring methods was tested and found not to help."
)
st.warning(
    "If you're using the hosted version of this app (not running it locally "
    "or in Colab), Layer 2 and Layer 3 may fail or crash the app entirely due "
    "to free-tier memory limits -- two 1.5B-parameter models don't reliably "
    "fit. For real Layer 2/3 results, see LAYER2_FINDINGS.md, "
    "HUMANIZER_FINDINGS.md, and LAYER3_FINDINGS.md in the repo, which contain "
    "actual measured results from local/GPU runs."
)
text = st.text_area("Paste text to analyze", height=250, key="input_text")
run_layer2 = st.checkbox(
    "Also run Layer 2 (statistical scorer) -- slow, downloads models on first use"
)
run_clicked = st.button("Run analysis")


@st.cache_resource(show_spinner=False)
def _load_layer2_models():
    from layer2_binoculars import load_models
    return load_models()


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


if run_clicked:
    if not text.strip():
        st.warning("Paste some text first.")
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

        observer = performer = tok = device = None
        truncated_score = None

        if run_layer2:
            st.subheader("Layer 2: statistical scorer")
            try:
                with st.spinner("Loading models (first run downloads ~3GB, then cached)..."):
                    observer, performer, tok, device = _load_layer2_models()
                st.caption(f"Models loaded. Running on: {device}")

                from layer2_binoculars import binoculars_score, binoculars_score_full_document

                with st.spinner("Scoring (truncated, first ~400 words)..."):
                    truncated_score = binoculars_score(text, observer, performer, tok, device)

                with st.spinner("Scoring (full document, pooled across chunks)..."):
                    full_result = binoculars_score_full_document(text, observer, performer, tok, device)

                l2col1, l2col2 = st.columns(2)
                l2col1.metric("Truncated score", f"{truncated_score:.4f}")
                l2col1.caption(f"Distance from 1.0: {abs(truncated_score - 1.0):.4f}")
                if full_result["pooled_score"] is not None:
                    l2col2.metric("Full-document pooled score", f"{full_result['pooled_score']:.4f}")
                    l2col2.caption(
                        f"Distance from 1.0: {abs(full_result['pooled_score'] - 1.0):.4f} "
                        f"({full_result['num_chunks']} chunks, {full_result['total_tokens_scored']} tokens)"
                    )
                else:
                    l2col2.write("Full-document score unavailable (empty or unscoreable text).")

                st.caption(
                    "Closer to 1.0 = more machine-like, further = more human-like, per the "
                    "Binoculars paper's convention. NEITHER score here is validated or "
                    "calibrated -- there is no threshold that means 'this is AI.' Full-document "
                    "pooling was tested against this project's real corpus and found to REDUCE "
                    "human/AI separation, not improve it (see LAYER2_FINDINGS.md). Both numbers "
                    "are shown because neither method is currently trusted over the other."
                )
            except Exception as e:
                st.error(
                    f"Layer 2 failed to load or run: {e}\n\n"
                    "Common causes: missing dependencies (run `pip install -r requirements.txt` "
                    "to get torch and transformers), no internet connection (needed to download "
                    "model weights the first time), or insufficient memory for two "
                    "1.5B-parameter models on CPU."
                )

        run_layer3 = st.checkbox(
            "Also check detection robustness (Layer 3) -- runs a local paraphrase "
            "attack and re-scores the result. SLOW on CPU: expect several minutes, "
            "not seconds, even for short text. Requires Layer 2 checked above."
        )

        if run_layer3:
            if not run_layer2 or observer is None:
                st.warning("Check the Layer 2 box above first -- Layer 3 reuses those models.")
            else:
                st.subheader("Layer 3: detection robustness check")
                st.caption(
                    "This is NOT a tool to help evade detection. It exists to answer one "
                    "question honestly: if this text is flagged, how much does that verdict "
                    "survive a cheap, automated paraphrase? A local, free, ~1.5B-parameter "
                    "model performs the paraphrase -- a much weaker attack than a commercial "
                    "humanizer (see HUMANIZER_FINDINGS.md for real Quillbot-based numbers). "
                    "On this project's own test data, results were inconsistent: sometimes "
                    "the paraphrase reduced flags, sometimes it increased them (see "
                    "LAYER3_FINDINGS.md). Treat any single result below as one data point, "
                    "not a reliable prediction."
                )
                try:
                    from layer3_adversarial import chunked_paraphrase
                    from layer2_binoculars import binoculars_score

                    with st.spinner(
                        "Generating local paraphrase attack (CPU -- this may take "
                        "several minutes)..."
                    ):
                        paraphrase = chunked_paraphrase(text, performer, tok, device)

                    para_result = PatternScorer().analyze(paraphrase)

                    l3col1, l3col2 = st.columns(2)
                    l3col1.metric("Original flags", result.flag_count)
                    l3col2.metric("Post-paraphrase flags", para_result.flag_count)

                    word_ratio = (
                        para_result.word_count / result.word_count
                        if result.word_count else 0
                    )
                    st.caption(
                        f"Paraphrase word count: {para_result.word_count} "
                        f"(original: {result.word_count}, ratio: {word_ratio:.2f}). "
                        f"Ratios well below ~0.7 mean the model compressed rather than "
                        f"paraphrased -- treat the flag comparison above as less reliable "
                        f"if so."
                    )

                    with st.spinner("Scoring paraphrase with Layer 2..."):
                        para_binoculars = binoculars_score(
                            paraphrase, observer, performer, tok, device
                        )

                    if truncated_score is not None:
                        l3col1.metric("Original Binoculars", f"{truncated_score:.4f}")
                    l3col2.metric("Post-paraphrase Binoculars", f"{para_binoculars:.4f}")

                    with st.expander("View generated paraphrase (diagnostic only)"):
                        st.write(paraphrase)

                except Exception as e:
                    st.error(f"Layer 3 failed to run: {e}")
