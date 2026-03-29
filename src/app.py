"""
Streamlit web app for the RfM Optimization Assistant.
Three screens: input → loading → results.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from assistant import RfMOptimization

# --- Page config ---
st.set_page_config(page_title="RfM Optimization Assistant", layout="wide")
st.title("RfM Optimization Assistant")

# --- Session state defaults ---
FIELD_KEYS = ["study_title", "purpose", "pitch", "participant_tasks", "compensation"]

for key in FIELD_KEYS:
    if key not in st.session_state:
        st.session_state[key] = ""

if "optimizing" not in st.session_state:
    st.session_state.optimizing = False
if "results" not in st.session_state:
    st.session_state.results = None
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

# --- Handle reset before widgets render ---
if st.session_state.reset_flag:
    for key in FIELD_KEYS:
        st.session_state[key] = ""
    st.session_state.results = None
    st.session_state.optimizing = False
    st.session_state.reset_flag = False

# --- Field labels (display name → session key) ---
FIELD_LABELS = {
    "study_title": "Short Study Title",
    "purpose": "Study Purpose",
    "pitch": "Recruitment Pitch",
    "participant_tasks": "What Will You Ask of the Participant?",
    "compensation": "Describe Compensation and Incentives",
}


def _copy_button(text):
    """Render a small copy-to-clipboard button via an HTML component."""
    safe = json.dumps(text)
    components.html(
        f"""
        <style>
            button {{
                background: transparent;
                border: 1px solid rgba(128,128,128,0.3);
                border-radius: 6px;
                padding: 4px 14px;
                font-size: 13px;
                cursor: pointer;
                color: #FFFFFF;
            }}
        </style>
        <button id="copybtn">Copy to clipboard</button>
        <script>
            var btn = document.getElementById("copybtn");
            var content = {safe};
            btn.addEventListener("click", function() {{
                navigator.clipboard.writeText(content).then(function() {{
                    btn.textContent = "Copied!";
                    setTimeout(function() {{ btn.textContent = "Copy to clipboard"; }}, 1500);
                }});
            }});
        </script>""",
        height=38,
    )


# ============================================================
# SCREEN 1: Input
# ============================================================
st.header("Paste your REDCap fields below")

for key, label in FIELD_LABELS.items():
    st.text_area(label, height=100, key=key)

# --- Optimize button (hidden during processing or when results exist) ---
if not st.session_state.optimizing and st.session_state.results is None:
    if st.button("Optimize!"):
        filled = {k: st.session_state[k] for k in FIELD_KEYS if st.session_state[k].strip()}
        if not filled:
            st.error("Please enter content in at least one field before optimizing.")
        else:
            st.session_state.optimizing = True
            st.rerun()

# ============================================================
# SCREEN 2: Loading
# ============================================================
if st.session_state.optimizing:
    with st.spinner("Optimizing your listing… this takes a few seconds per field."):
        try:
            bot = RfMOptimization(
                **{k: st.session_state[k] for k in FIELD_KEYS}
            )
            st.session_state.results = bot.optimize_all()
            st.session_state.optimizing = False
            st.rerun()
        except Exception as e:
            st.session_state.optimizing = False
            st.session_state.results = None
            st.error(f"Something went wrong: {e}")
            st.info(
                "Check that your OPENAI_API_KEY is set correctly "
                "and that your account has access to the GPT-4o model."
            )

# ============================================================
# SCREEN 3: Results (editable + copy button)
# ============================================================
if st.session_state.results:
    count = len(st.session_state.results)
    st.success(f"Done! {count} field{'s' if count != 1 else ''} optimized. Edit if needed, then copy into REDCap.")

    for key, optimized_text in st.session_state.results.items():
        label = FIELD_LABELS.get(key, key.replace("_", " ").title())
        result_key = f"result_{key}"

        # Seed each result field once; after that, edits persist.
        if result_key not in st.session_state:
            st.session_state[result_key] = optimized_text

        st.subheader(label)
        st.text_area("", height=120, key=result_key)
        _copy_button(st.session_state[result_key])

    if st.button("Start New Optimization", type="primary"):
        for key in st.session_state.results:
            st.session_state.pop(f"result_{key}", None)
        st.session_state.reset_flag = True
        st.rerun()