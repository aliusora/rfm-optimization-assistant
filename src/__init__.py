"""
RfM Optimization Assistant — rewrites research study listings
in plain language using OpenAI.
"""

__version__ = "2.0.0"

from connect import connect_openai
from assistant import RfMOptimization

__all__ = ["connect_openai", "RfMOptimization"]