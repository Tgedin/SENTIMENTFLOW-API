# filepath: /home/theo-gedin/sentimentflow-api/app/models/responses.py
"""
Response models for the SentimentFlow API.

This module defines Pydantic models for API responses from the
sentiment analysis endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class SentimentScore(BaseModel):
    """Individual sentiment score with label and confidence."""
    label: str = Field(..., description="Sentiment label (e.g., 'POSITIVE', 'NEGATIVE')")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class SentimentResult(BaseModel):
    """Complete sentiment analysis result for a single text."""
    text: str = Field(..., description="The analyzed text")
    sentiment: str = Field(..., description="Primary sentiment classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the prediction")
    scores: List[SentimentScore] = Field(..., description="All sentiment scores from the model")
    model_name: str = Field(..., description="Name of the model used for analysis")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(..., description="When the analysis was performed")
    raw_output: Optional[Dict[str, Any]] = Field(None, description="Raw model output if requested")


class SentimentAnalysisResponse(BaseModel):
    """Response for single sentiment analysis."""
    success: bool = Field(True, description="Whether the analysis was successful")
    result: SentimentResult = Field(..., description="The sentiment analysis result")
    session_id: str = Field(..., description="Unique session identifier")


class BatchSentimentResponse(BaseModel):
    """Response for batch sentiment analysis."""
    success: bool = Field(True, description="Whether the batch analysis was successful")
    results: List[SentimentResult] = Field(..., description="List of sentiment analysis results")
    session_id: str = Field(..., description="Unique session identifier")
    total_texts: int = Field(..., description="Total number of texts processed")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    failed_count: int = Field(default=0, description="Number of texts that failed to process")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    models_loaded: List[str] = Field(..., description="List of loaded models")
    database_connected: bool = Field(..., description="Database connection status")


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = Field(False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="When the error occurred")


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")


class SessionInfo(BaseModel):
    """Information about a user session."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="When the session was created")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    request_count: int = Field(..., description="Total number of requests in this session")
    client_ip: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")


class ModelStats(BaseModel):
    """Statistics for a specific model."""
    model_name: str = Field(..., description="Name of the model")
    total_requests: int = Field(..., description="Total requests processed by this model")
    average_confidence: float = Field(..., description="Average confidence score")
    last_used: datetime = Field(..., description="When the model was last used")


class SentimentDistribution(BaseModel):
    """Distribution of sentiment classifications."""
    positive: int = Field(..., description="Number of positive sentiments")
    negative: int = Field(..., description="Number of negative sentiments")
    neutral: int = Field(default=0, description="Number of neutral sentiments")
    total: int = Field(..., description="Total number of analyses")


class ConfidenceDistribution(BaseModel):
    """Distribution of confidence scores."""
    high_confidence: int = Field(..., description="Number of high confidence predictions (>0.8)")
    medium_confidence: int = Field(..., description="Number of medium confidence predictions (0.5-0.8)")
    low_confidence: int = Field(..., description="Number of low confidence predictions (<0.5)")
    average_confidence: float = Field(..., description="Average confidence across all predictions")