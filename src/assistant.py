"""
Builds the prompt, sends text to OpenAI, and strips formatting
from the response. Each field gets one API call.
"""

import os
import re
import requests

from connect import connect_openai

# One shared prompt for all fields. Field-specific guidance is built in.
SYSTEM_PROMPT = (
    "Write short, plain language text. The goal is to help potential "
    "research study participants quickly understand what a study is about "
    "and why it matters.\n\n"
    "RULES:\n"
    "- Use common, everyday words.\n"
    "- Keep sentences short. One idea per sentence.\n"
    "- Write in active voice.\n"
    "- Use 'you' and 'your' to speak directly to the reader.\n"
    "- Avoid gendered language.\n"
    "- Define technical terms in context, not with dictionary definitions.\n"
    "- Make numbers easy to understand with whole numbers or examples.\n\n"
    "OUTPUT FORMAT:\n"
    "- Return ONLY the rewritten text. No commentary, no bullet points, "
    "no headers, no formatting. Plain text only.\n\n"
    "FIELD GUIDANCE:\n"
    "- study_title: Keep it short and engaging.\n"
    "- purpose: Explain why this study matters to the reader.\n"
    "- pitch: Make it personal and compelling. Focus on what participants "
    "gain, whether direct benefits or meaningful contributions.\n"
    "- participant_tasks: Describe what participation looks like.\n"
    "- compensation: Be clear about amounts, timing, and conditions.\n"
)


class RfMOptimization:
    """Optimizes research listing fields using OpenAI."""

    FIELDS = [
        "study_title",
        "purpose",
        "pitch",
        "participant_tasks",
        "compensation",
    ]

    def __init__(self, **fields):
        """
        Accept any combination of the five listing fields.

        Args:
            **fields: Keyword arguments matching FIELDS above.
                      Missing or empty fields are ignored.
        """
        self.fields = {
            k: fields.get(k, "").strip() for k in self.FIELDS
        }
        self.config = connect_openai()
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _call_api(self, text, field_type):
        """Send one field to OpenAI and return the cleaned response."""
        payload = {
            "model": self.config["model"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Field type: {field_type}\n\n"
                        f"Text to optimize:\n{text}"
                    ),
                },
            ],
        }

        response = requests.post(
            f"https://api.openai.com/{self.config['version']}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.text}")

        raw = response.json()["choices"][0]["message"]["content"]
        # Strip any markdown bold/italic the model might add.
        return re.sub(r"[*_]{1,3}", "", raw).strip()

    def optimize_all(self):
        """
        Optimize every non-empty field.

        Returns:
            dict mapping field names to their rewritten text.
            Only includes fields that had content.
        """
        return {
            name: self._call_api(text, name)
            for name, text in self.fields.items()
            if text
        }