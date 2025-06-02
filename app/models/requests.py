"""
Request models for the SentimentFlow API.

This module defines Pydantic models for validating incoming requests
to the sentiment analysis endpoints.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated


class SentimentAnalysisRequest(BaseModel):
    """
    Request model for single text sentiment analysis.
    """
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=10000,
        description="Text to analyze for sentiment"
    )
    model_name: Optional[str] = Field(
        None,
        description="Optional model name to use for analysis"
    )
    include_raw_output: bool = Field(
        default=False,
        description="Whether to include raw model output in response"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Validate that text is not just whitespace."""
        if not v.strip():
            raise ValueError('Text cannot be empty or just whitespace')
        return v.strip()


class BatchSentimentRequest(BaseModel):
    """
    Request model for batch sentiment analysis.
    """
    texts: Annotated[List[str], Field(min_length=1, max_length=100)] = Field(
        ...,
        description="List of texts to analyze"
    )
    model_name: Optional[str] = Field(
        None,
        description="Optional model name to use for analysis"
    )
    batch_size: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Batch size for processing"
    )
    include_raw_output: bool = Field(
        default=False,
        description="Whether to include raw model output in response"
    )
    
    @field_validator('texts')
    @classmethod
    def validate_texts(cls, v):
        """Validate that all texts are non-empty."""
        validated_texts = []
        for i, text in enumerate(v):
            if not text.strip():
                raise ValueError(f'Text at index {i} cannot be empty or just whitespace')
            validated_texts.append(text.strip())
        return validated_texts