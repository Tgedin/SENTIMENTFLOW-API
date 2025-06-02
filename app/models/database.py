"""
Database models for MongoDB collections.

This module defines Pydantic models that map to MongoDB documents
for storing sentiment analysis results and related data.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_serializer


class SentimentResult(BaseModel):
    """
    Model representing a sentiment analysis result stored in MongoDB.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    session_id: str = Field(..., description="User session identifier")
    text: str = Field(..., description="Original text that was analyzed")
    model_name: str = Field(..., description="Name of the ML model used")
    
    # Sentiment results
    label: str = Field(..., description="Predicted sentiment label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    scores: Dict[str, float] = Field(..., description="All label scores from the model")
    
    # Metadata
    text_length: int = Field(..., description="Length of the analyzed text")
    processing_time_ms: float = Field(..., description="Time taken to process in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Additional context (optional)
    user_agent: Optional[str] = Field(None, description="User agent from request")
    ip_address: Optional[str] = Field(None, description="Client IP address")

    @field_serializer('timestamp', when_used='json')
    def serialize_dt_to_json(self, dt: datetime) -> str:
        return dt.isoformat()
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class UserSession(BaseModel):
    """
    Model representing a user session for tracking analysis history.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    session_id: str = Field(..., description="Unique session identifier")
    
    # Session metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Usage statistics
    total_analyses: int = Field(default=0, description="Total number of analyses in this session")
    models_used: List[str] = Field(default_factory=list, description="List of models used in this session")
    
    # Optional user context
    user_agent: Optional[str] = Field(None, description="User agent from first request")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    
    @field_serializer('created_at', 'last_activity', when_used='json')
    def serialize_dt_to_json(self, dt: datetime) -> str:
        return dt.isoformat()
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class AnalyticsEvent(BaseModel):
    """
    Model for storing analytics events and usage patterns.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    event_type: str = Field(..., description="Type of analytics event")
    session_id: str = Field(..., description="Session identifier")
    
    # Event data
    data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Optional context
    user_agent: Optional[str] = Field(None, description="User agent")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    
    @field_serializer('timestamp', when_used='json')
    def serialize_dt_to_json(self, dt: datetime) -> str:
        return dt.isoformat()
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class ModelPerformanceMetric(BaseModel):
    """
    Model for storing model performance metrics and comparisons.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    model_name: str = Field(..., description="Name of the ML model")
    
    # Performance metrics
    avg_processing_time_ms: float = Field(..., description="Average processing time")
    total_requests: int = Field(..., description="Total number of requests processed")
    error_count: int = Field(default=0, description="Number of errors encountered")
    
    # Time period for these metrics
    period_start: datetime = Field(..., description="Start of measurement period")
    period_end: datetime = Field(..., description="End of measurement period")
    
    # Additional metrics
    memory_usage_mb: Optional[float] = Field(None, description="Average memory usage")
    confidence_distribution: Optional[Dict[str, int]] = Field(
        None, 
        description="Distribution of confidence scores"
    )
    
    @field_serializer('period_start', 'period_end', when_used='json')
    def serialize_dt_to_json(self, dt: datetime) -> str:
        return dt.isoformat()
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }