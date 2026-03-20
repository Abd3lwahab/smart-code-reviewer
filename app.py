"""Smart Code Reviewer — AI-powered code review assistant."""

import streamlit as st
from reviewer import review_code, detect_language, FOCUS_DESCRIPTIONS
from sample_code import SAMPLES

# ──────────────────────────── Page Config ────────────────────────────

st.set_page_config(
    page_title="Smart Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── Custom CSS ─────────────────────────────

st.markdown("""
<style>
    /* Score badge */
    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin: 8px auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .score-high { background: linear-gradient(135deg, #1B5E20, #2E7D32); color: #A5D6A7; }
    .score-mid  { background: linear-gradient(135deg, #E65100, #F57C00); color: #FFE0B2; }
    .score-low  { background: linear-gradient(135deg, #B71C1C, #D32F2F); color: #FFCDD2; }

    /* Severity pills */
    .severity-critical {
        background: #B71C1C; color: #FFCDD2; padding: 3px 12px;
        border-radius: 12px; font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }
    .severity-warning {
        background: #E65100; color: #FFE0B2; padding: 3px 12px;
        border-radius: 12px; font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }
    .severity-suggestion {
        background: #1A237E; color: #C5CAE9; padding: 3px 12px;
        border-radius: 12px; font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }

    /* Positive note card */
    .positive-note {
        background: #1B5E20; border-left: 4px solid #4CAF50;
        padding: 12px 16px; border-radius: 6px; margin: 8px 0;
        font-size: 0.95rem;
    }

    /* Category grid */
    .cat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
        margin: 12px 0;
    }
    .cat-card {
        background: #1A1D23;
        border-radius: 10px;
        padding: 20px 12px;
        text-align: center;
        border: 1px solid #2A2D33;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .cat-card .cat-score { font-size: 1.8rem; font-weight: 700; line-height: 1; }
    .cat-card .cat-name {
        font-size: 0.8rem; color: #CCC; margin-top: 8px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        max-width: 100%;
    }
    .cat-card .cat-bar {
        width: 80%; height: 4px; border-radius: 2px;
        background: #333; margin-top: 10px; overflow: hidden;
    }
    .cat-card .cat-bar-fill { height: 100%; border-radius: 2px; }
    .bar-high { background: #4CAF50; }
    .bar-mid  { background: #FF9800; }
    .bar-low  { background: #F44336; }
    .cat-score-high { color: #4CAF50; }
    .cat-score-mid  { color: #FF9800; }
    .cat-score-low  { color: #F44336; }

    /* Issue count summary */
    .issue-summary {
        display: flex; gap: 24px; margin: 12px 0 20px 0;
    }
    .issue-chip {
        padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9rem;
    }
    .chip-critical { background: #B71C1C33; color: #EF9A9A; border: 1px solid #B71C1C; }
    .chip-warning  { background: #E6510033; color: #FFCC80; border: 1px solid #E65100; }
    .chip-suggestion { background: #1A237E33; color: #9FA8DA; border: 1px solid #3949AB; }

    /* Expander styling */
    div[data-testid="stExpander"] details summary p {
        font-size: 1rem;
    }

    /* Footer */
    .footer {
        text-align: center; color: #666; font-size: 0.8rem;
        padding: 20px 0; border-top: 1px solid #2A2D33; margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── Session defaults ───────────────────────

if "code_input" not in st.session_state:
    st.session_state["code_input"] = ""

# ──────────────────────────── Sidebar ────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Review Settings")
    st.markdown("### 🎯 Focus Areas *(optional)*")
    st.caption("Leave empty for a comprehensive review using our full checklist.")

    focus_areas = st.multiselect(
        "Select specific areas to deep-dive",
        options=list(FOCUS_DESCRIPTIONS.keys()),
        default=[],
        label_visibility="collapsed",
    )

    if not focus_areas:
        st.info("✅ **Comprehensive mode** — reviewing against all 10 quality checks.")
    else:
        st.success(f"🎯 **Focused mode** — deep-diving into {', '.join(focus_areas)}.")

    st.markdown("---")
    st.markdown("### 📋 Quick Demo")
    st.caption("Load a sample with intentional issues into the editor:")

    for name in SAMPLES:
        if st.button(f"📄 {name}", use_container_width=True, key=f"sample_{name}"):
            st.session_state["code_input"] = SAMPLES[name]["code"]
            if "review_result" in st.session_state:
                del st.session_state["review_result"]
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#666; font-size:0.75rem;">'
        "Powered by Llama 3.3 70B via Groq<br>Built for Careem AI Challenge"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────── Main Area ──────────────────────────────

st.markdown("# 🔍 Smart Code Reviewer")
st.markdown(
    "*AI-powered code review for readability, structure, and maintainability "
    "— paste your code and get instant feedback.*"
)
st.markdown("---")

# Code input — reads from session_state["code_input"]
code_input = st.text_area(
    "Paste your code here:",
    value=st.session_state.get("code_input", ""),
    height=350,
    placeholder="Paste your code here, or load a sample from the sidebar →",
)

# Auto-detect language from the code
lang_to_use = detect_language(code_input) if code_input.strip() else "Python"

col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
with col1:
    review_clicked = st.button(
        "🚀 Review Code", type="primary", use_container_width=True
    )
with col2:
    if code_input.strip():
        st.markdown(f"🗂️ Detected: **{lang_to_use}**")
    else:
        st.caption("Language auto-detected from code")
with col3:
    if not focus_areas:
        st.caption("Comprehensive review (10 quality checks)")
    else:
        st.caption(f"Focused on: {', '.join(focus_areas)}")
with col4:
    if "review_result" in st.session_state:
        if st.button("🗑️ Clear Results", use_container_width=True):
            del st.session_state["review_result"]
            st.rerun()

# ──────────────────────────── Review Logic ───────────────────────────

if review_clicked:
    if not code_input or not code_input.strip():
        st.warning("⚠️ Please paste some code or load a sample first.")
    else:
        progress_bar = st.progress(0, text="🤖 Sending code to AI reviewer...")
        try:
            progress_bar.progress(20, text="🔍 Analyzing code structure...")
            result = review_code(code_input.strip(), lang_to_use, focus_areas)
            progress_bar.progress(80, text="📝 Formatting review results...")
            st.session_state["review_result"] = result
            progress_bar.progress(100, text="✅ Review complete!")
            import time
            time.sleep(0.5)
            progress_bar.empty()
            st.rerun()
        except Exception as e:
            progress_bar.empty()
            error_msg = str(e)
            if "429" in error_msg or "rate" in error_msg.lower():
                st.error(
                    "⏳ **Rate limit reached.** The free API tier has usage limits. "
                    "Please wait 30-60 seconds and try again."
                )
            elif "API" in error_msg or "key" in error_msg.lower():
                st.error(f"🔑 **API Configuration Error:** {error_msg}")
            else:
                st.error(f"❌ **Review failed:** {error_msg}")
            st.stop()

# ──────────────────────────── Display Results ────────────────────────

if "review_result" in st.session_state:
    result = st.session_state["review_result"]
    st.markdown("---")

    # ── Overall Score ──
    score = result["overall_score"]
    if score >= 7:
        css_class = "score-high"
        score_label = "Good"
    elif score >= 4:
        css_class = "score-mid"
        score_label = "Needs Work"
    else:
        css_class = "score-low"
        score_label = "Poor"

    score_col, summary_col = st.columns([1, 3])
    with score_col:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div class="score-badge {css_class}">{score}/10</div>'
            f'<div style="color:#AAA; font-size:0.85rem; margin-top:4px">{score_label}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with summary_col:
        st.markdown("### 📊 Assessment")
        st.markdown(result["summary"])

    st.markdown("---")

    # ── Category Breakdown ──
    st.markdown("### 📈 Category Breakdown")
    categories = result.get("categories", [])

    if categories:
        cards_html = '<div class="cat-grid">'
        for cat in categories:
            cat_score = cat["score"]
            if cat_score >= 7:
                color_class = "cat-score-high"
                bar_class = "bar-high"
            elif cat_score >= 4:
                color_class = "cat-score-mid"
                bar_class = "bar-mid"
            else:
                color_class = "cat-score-low"
                bar_class = "bar-low"

            pct = int(cat_score * 10)
            cards_html += (
                f'<div class="cat-card">'
                f'<div class="cat-score {color_class}">{cat_score}/10</div>'
                f'<div class="cat-name">{cat["name"]}</div>'
                f'<div class="cat-bar"><div class="cat-bar-fill {bar_class}" style="width:{pct}%"></div></div>'
                f"</div>"
            )
        cards_html += "</div>"
        st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── Issues ──
    issues = result.get("issues", [])
    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    suggestions = [i for i in issues if i["severity"] == "suggestion"]

    st.markdown(f"### 🐛 Issues Found ({len(issues)})")

    st.markdown(
        f'<div class="issue-summary">'
        f'<span class="issue-chip chip-critical">🔴 {len(critical)} Critical</span>'
        f'<span class="issue-chip chip-warning">🟡 {len(warnings)} Warnings</span>'
        f'<span class="issue-chip chip-suggestion">🔵 {len(suggestions)} Suggestions</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Sort: critical first, then warnings, then suggestions
    severity_order = {"critical": 0, "warning": 1, "suggestion": 2}
    sorted_issues = sorted(issues, key=lambda x: severity_order.get(x["severity"], 3))

    for issue in sorted_issues:
        sev = issue["severity"]
        icon = {"critical": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(sev, "⚪")
        sev_class = f"severity-{sev}"

        with st.expander(
            f"{icon} **{issue['title']}** — Line {issue.get('line_ref', '?')}",
            expanded=(sev == "critical"),
        ):
            st.markdown(
                f'<span class="{sev_class}">{sev.upper()}</span> &nbsp; '
                f'📂 {issue.get("category", "")}',
                unsafe_allow_html=True,
            )
            st.markdown("")
            st.markdown(f"**Problem:** {issue['description']}")
            st.markdown(f"**Suggestion:** {issue['suggestion']}")

            original = issue.get("original_code", "")
            fixed = issue.get("fixed_code", "")

            if original or fixed:
                st.markdown("---")
                diff_left, diff_right = st.columns(2)
                with diff_left:
                    st.markdown("**❌ Original Code:**")
                    if original:
                        st.code(original, language=lang_to_use.lower())
                with diff_right:
                    st.markdown("**✅ Suggested Fix:**")
                    if fixed:
                        st.code(fixed, language=lang_to_use.lower())

    st.markdown("---")

    # ── Positive Notes ──
    st.markdown("### ✅ What's Done Well")
    for note in result.get("positive_notes", []):
        st.markdown(
            f'<div class="positive-note">👍 {note}</div>', unsafe_allow_html=True
        )

    # ── Footer ──
    st.markdown(
        '<div class="footer">'
        "Powered by Llama 3.3 70B via Groq · Built for Careem AI Challenge"
        "</div>",
        unsafe_allow_html=True,
    )
