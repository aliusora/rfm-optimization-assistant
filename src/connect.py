"""
This module functions as a connection verification and model availability
checker for OpenAI's application programming interface (API).
"""

import os
import requests

def connect_openai(model: str = "gpt-4o", version: str = "v1") -> dict[str, str]:
    """
    Test connectivity to OpenAI and check if the chosen model is available.

    Args:
        model (str): The name of the OpenAI model. Default is "gpt-4o".
        version (str): The API version to test. Default is "v1".

    Returns:
        dict: Information about the connection, including model, version, and status.

    Raises:
        ValueError: If the API key is missing or the model is not available.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

    url = f"https://api.openai.com/{version.strip('/')}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Error connecting to OpenAI: {response.text}")

    models_data = response.json()
    available_models = [m['id'] for m in models_data.get('data', [])]

    if model not in available_models:
        raise ValueError(f"Model '{model}' is not available. Available models: {available_models}")

    return {
        "provider": "OpenAI",
        "model": model,
        "version": version,
        "status": "connected",
        "api_key_last4": api_key[-4:],
    }
