"""
Enumeration types used throughout the application.

This module defines standardized enums to ensure consistent
values are used for categorical data across the application.
"""

from enum import Enum, auto


class SentimentLabel(str, Enum):
    """
    Standard sentiment labels returned by the sentiment analysis models.
    
    These values normalize the different outputs from various models
    into a consistent set of sentiment categories.
    """
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    VERY_POSITIVE = "very_positive"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"


class AnalysisStatus(str, Enum):
    """Status of a sentiment analysis request."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PreprocessingLevel(str, Enum):
    """Different levels of text preprocessing."""
    MINIMAL = "minimal"     # Only basic cleaning
    STANDARD = "standard"   # Standard preprocessing for most models
    AGGRESSIVE = "aggressive"  # Maximum cleaning and normalization
    PRESERVE = "preserve"   # Preserve most original features (for context-aware models)


class ModelSource(str, Enum):
    """Source of a model."""
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    CUSTOM = "custom"
