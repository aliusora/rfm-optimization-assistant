"""
Streamlit web app for optimizing research recruitment listings using Generative AI.
Users paste their REDCap fields, click a button, and get clear, easy-to-read text for each section.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
from assistant import RfMOptimization

st.set_page_config(
        page_title="RfM Optimization Assistant",
        layout="wide"
)

st.title("RfM Optimization Assistant")

# Initialize session state for tracking optimization status
if 'optimizing' not in st.session_state:
    st.session_state.optimizing = False
if 'results' not in st.session_state:
    st.session_state.results = None

st.header("Paste your REDCap fields below")
study_title = st.text_area(
    "Short Study Title",
    height=100,
    placeholder="Enter the short study title here",
    key="study_title"
)
purpose = st.text_area(
    "Study Purpose",
    height=100,
    placeholder="Enter the study purpose here",
    key="purpose"
)
pitch = st.text_area(
    "Recruitment Pitch",
    height=100,
    placeholder="Enter the recruitment pitch here",
    key="pitch"
)
participant_tasks = st.text_area(
    "What will you ask of the participant?",
    height=100,
    placeholder="Enter participant tasks here",
    key="participant_tasks"
)
compensation = st.text_area(
    "Describe compensation and incentives",
    height=100,
    placeholder="Enter compensation details here",
    key="compensation"
)

# Only show Optimize button if not currently optimizing and no results
if not st.session_state.optimizing and st.session_state.results is None:
    if st.button("Optimize!"):
        input_fields = [study_title, purpose, pitch, participant_tasks, compensation]
        if not any(field.strip() for field in input_fields):
            st.error("Please enter content in at least one field before optimizing.")
        else:
            st.session_state.optimizing = True
            st.rerun()

# Show spinner and process optimization
if st.session_state.optimizing:
    with st.spinner("Optimizing your recruitment listing... please wait."):
        try:
            bot = RfMOptimization(
                study_title=study_title,
                purpose=purpose,
                pitch=pitch,
                participant_tasks=participant_tasks,
                compensation=compensation
            )
            st.session_state.results = bot.generate_optimized_listing()
            st.session_state.optimizing = False
            st.rerun()
        except Exception as e:
            st.session_state.optimizing = False
            st.error(f"An error occurred during optimization: {str(e)}")
            st.info("Please check your OpenAI API key is set correctly and try again.")
            st.session_state.results = None

# Display results if available
if st.session_state.results:
    st.success(f"Optimized {len(st.session_state.results)} field(s) (copy into REDCap):")
    
    # Display each optimized field in a text area for easy copying.
    for field, block in st.session_state.results.items():
        st.subheader(field.replace("_", " ").title())
        st.text_area(f"{field} - Optimized", block, height=100, key=f"optimized_{field}")
    
    # Reset button to clear everything
    if st.button("Start New Optimization", type="primary"):
        # Clear session state
        st.session_state.results = None
        st.session_state.optimizing = False
        # Clear all text area values
        for key in ['study_title', 'purpose', 'pitch', 'participant_tasks', 'compensation']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
elif st.session_state.results is not None and not st.session_state.results:
    st.warning("No fields were optimized. Please enter content in at least one field.")
    if st.button("Try Again"):
        st.session_state.results = None
        st.rerun()
