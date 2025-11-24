"""
Module initialization for RfM Optimization tool with OpenAI integration.
"""

__version__ = "1.0.0"

from connect import connect_openai
from assistant import RfMOptimization

__all__ = ["connect_openai", "RfMOptimization"]