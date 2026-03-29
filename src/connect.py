"""
Checks the OpenAI API key and verifies the model is available.
"""

import os
import requests


def connect_openai(model="gpt-4o", version="v1"):
    """
    Verify the API key is set and the requested model is available.

    Args:
        model: Name of the OpenAI model to use.
        version: API version string.

    Returns:
        dict with provider, model, version, and status.

    Raises:
        ValueError: If the key is missing or the model is not available.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key is not set. "
            "Run: export OPENAI_API_KEY='your-key-here'"
        )

    url = f"https://api.openai.com/{version}/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise ValueError(f"Could not connect to OpenAI: {response.text}")

    available = [m["id"] for m in response.json().get("data", [])]
    if model not in available:
        raise ValueError(
            f"Model '{model}' is not available on your account. "
            f"You may need a paid API plan."
        )

    return {
        "model": model,
        "version": version,
        "status": "connected",
    }