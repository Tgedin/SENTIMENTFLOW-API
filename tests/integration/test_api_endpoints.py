"""
Integration tests for API endpoints.

These tests verify that the API endpoints work correctly by making
actual HTTP requests to the API.
"""

import pytest


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_endpoint(self, client):
        """Test that the health endpoint returns a successful response."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data
        assert "server_time" in data


class TestSentimentEndpoint:
    """Tests for the sentiment analysis endpoint."""

    def test_analyze_sentiment_success(self, client):
        """Test successful sentiment analysis."""
        payload = {
            "text": "This is a test sentence.",
            "model_name": "distilbert-base-uncased-finetuned-sst-2-english"
        }
        response = client.post("/api/v1/sentiment/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level response structure
        assert "success" in data
        assert "result" in data
        assert "session_id" in data
        assert data["success"] is True
        
        # Check result structure
        result = data["result"]
        assert "text" in result
        assert "sentiment" in result
        assert "confidence" in result
        assert "model_name" in result
        assert "scores" in result
        assert "processing_time_ms" in result
        
        # Check values
        assert result["text"] == "This is a test sentence."
        assert result["model_name"] == "distilbert-base-uncased-finetuned-sst-2-english"
        assert result["sentiment"] in ["positive", "negative"]  # Binary model
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0
        assert isinstance(result["scores"], list)
        assert len(result["scores"]) > 0
