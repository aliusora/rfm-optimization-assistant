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

st.header("Paste your REDCap fields below")
study_title = st.text_area(
    "Short Study Title",
    height=100,
    placeholder="Enter the short study title here"
)
purpose = st.text_area(
    "Study Purpose",
    height=100,
    placeholder="Enter the study purpose here"
)
pitch = st.text_area(
    "Recruitment Pitch",
    height=100,
    placeholder="Enter the recruitment pitch here"
)
participant_tasks = st.text_area(
    "What will you ask of the participant?",
    height=100,
    placeholder="Enter participant tasks here"
)
compensation = st.text_area(
    "Describe compensation and incentives",
    height=100,
    placeholder="Enter compensation details here"
)

if st.button("Optimize!"):
    """
    Optimize the recruitment listing when the user clicks the 'Optimize!' button.
    Creates an RfMOptimization object with the provided inputs, calls generate_optimized_listing,
    and displays the optimized text for each field that had content.
    """
    input_fields = [study_title, purpose, pitch, participant_tasks, compensation]
    if not any(field.strip() for field in input_fields):
        st.error("Please enter content in at least one field before optimizing.")
    else:
        with st.spinner("Optimizing your recruitment listing... please wait."):
            try:
                bot = RfMOptimization(
                    study_title=study_title,
                    purpose=purpose,
                    pitch=pitch,
                    participant_tasks=participant_tasks,
                    compensation=compensation
                )
                results = bot.generate_optimized_listing()

                if results:
                    st.success(f"Optimized {len(results)} field(s) (copy into REDCap):")

                    # Display each optimized field in a text area for easy copying.
                    for field, block in results.items():
                        st.subheader(field.replace("_", " ").title())
                        st.text_area(f"{field} - Optimized", block, height=100, key=f"optimized_{field}")

                    if st.button("Start New Optimization", type="primary"):
                        st.rerun()

                else:
                    st.warning("No fields were optimized. Please enter content in at least one field.")
            except Exception as e:
                st.error(f"An error occurred during optimization: {str(e)}")
                st.info("Please check your OpenAI API key is set correctly and try again.")
