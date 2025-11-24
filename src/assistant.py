"""
This module serves as an AI-powered text optimization tool specifically designed
for research recruitment materials. It leverages OpenAI's language models to
transform complex, jargon-heavy research study descriptions into clear, plain
language that an average participant can easily understand.
"""

import re
import os
import requests

from connect import connect_openai

class RfMOptimization:
    """
    Optimizes text from research recruitment listings using Generative AI.
    """
    SYSTEM_PROMPT = (
        "Write short, plain language text. The goal is to help potential research study participants quickly understand\n"
        "what a study is about and why it matters. Use plain language throughout. That means using common words familiar\n"
        "to readers and that users can relate to, keeping sentences short and containing only one idea, and\n"
        "writing in the active voice so that the subject of the sentence performs the action.\n\n"
        
        "REQUIREMENTS:\n"
        "- Clearly define complex terminology in context rather than using the dictionary definition\n"
        "- Write in friendly, conversational language — language that sounds like a verbal conversation between friends\n"
        "- Use second-person pronouns (e.g., “you” and “your”) to address readers directly while avoiding gendered language\n"
        "- Give context before introducing new information\n"
        "- Keep information direct and to the point\n"
        "- Make numbers easy to understand. That means using whole numbers, providing context for numbers, or providing a non-number example\n\n"
        
        "OUTPUT FORMAT:\n"
        "- Return ONLY the optimized text for the given field\n"
        "- No additional commentary, explanations, or formatting\n"
        "- No bullet points, lists, or section headers\n"
        "- Plain text that can be directly copied into forms\n\n"
        
        "Field-specific guidance:\n"
        "- Study Title: Keep it short and engaging.\n"
        "- Purpose: Explain why this study might be important or relevant to potential participants (i.e., why should they care?).\n"
        "- Pitch: Make it compelling and personal. Focus on what participants might gain whether that is direct benefits such as\n"
        "compensation or indirect contributions like helping doctors address a health challenge, understand more about a specific\n"
        "health condition, improve outcomes for their community, etc. Determine benefits in context.\n"
        "- Participant Tasks: Describe what participation in the study would look like.\n"
        "- Compensation: Be clear about amounts, timing, and any conditions.\n\n"
        
        "Stay focused only on this task."
    )

    def __init__(self, study_title: str = "", purpose: str = "", pitch: str = "",
                 participant_tasks: str = "", compensation: str = "") -> None:
        """
        Initialize listing details.

        Args:
            study_title (str): Short study title.
            purpose (str): Study purpose.
            pitch (str): Recruitment pitch.
            participant_tasks (str): What participants will do.
            compensation (str): Compensation and incentives.
        """
        self.study_title = study_title or ""
        self.purpose = purpose or ""
        self.pitch = pitch or ""
        self.participant_tasks = participant_tasks or ""
        self.compensation = compensation or ""
        self.connection = connect_openai()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

    def optimize(self, text, field_type="general"):
        """
        Use Generative AI to rewrite a specific listing field.

        Args:
            text (str): The original text to optimize.
            field_type (str): The type of field (e.g., "study_title", "purpose", "pitch", "participant_tasks", "compensation").

        Returns:
            str: The optimized version of the input text, rewritten in clear, plain language.
        """
        user_content = f"Field type: {field_type}\n\nText to optimize:\n{text}"

        payload = {
            "model": self.connection['model'],
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ]
        }

        response = requests.post(
            f"https://api.openai.com/{self.connection['version']}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.text}")

        raw = response.json()['choices'][0]['message']['content']
        cleaned = re.sub(r"[*_]{1,3}", "", raw)
        return cleaned
    
    def generate_optimized_listing(self):
        """
        Generate a dictionary of optimized text for each non-empty field.

        Returns:
            dict: Optimized plain text for each field.
        """
        fields = {
            "study_title": self.study_title,
            "purpose": self.purpose,
            "pitch": self.pitch,
            "participant_tasks": self.participant_tasks,
            "compensation": self.compensation
        }
        return {k: self.optimize(v, k) for k, v in fields.items() if v.strip()}
        