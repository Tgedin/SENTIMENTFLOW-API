"""
Integration tests for API endpoints.

These tests verify that the API endpoints work correctly by making
actual HTTP requests to the API.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    with TestClient(app) as c:
        yield c


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
