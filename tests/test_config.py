"""
Tests for the configuration module.

These tests verify that the configuration system loads and validates
settings correctly under different environments and scenarios.
"""

import os
from unittest import mock

import pytest
from pydantic import ValidationError

from app.config import Environment, LogLevel, Settings


class TestConfigBasics:
    """Test basic configuration loading and defaults."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = Settings()
        assert settings.APP_NAME == "SentimentFlow API"
        assert settings.ENVIRONMENT == Environment.DEVELOPMENT
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == LogLevel.INFO
        assert settings.DEFAULT_MODEL == "distilbert-base-uncased-finetuned-sst-2-english"
    
    def test_env_variable_override(self):
        """Test that environment variables override defaults."""
        with mock.patch.dict(os.environ, {"APP_NAME": "Test API", "DEBUG": "false"}):
            settings = Settings()
            assert settings.APP_NAME == "Test API"
            assert settings.DEBUG is False


class TestConfigValidation:
    """Test configuration validation rules."""
    
    def test_environment_validation(self):
        """Test environment validation and normalization."""
        with mock.patch.dict(os.environ, {
            "ENVIRONMENT": "PRODUCTION", 
            "MONGODB_URL": "mongodb://localhost:27017"  # Add this to pass validation
        }):
            settings = Settings()
            assert settings.ENVIRONMENT == Environment.PRODUCTION
    
    def test_workers_count_validation(self):
        """Test workers count validation and adjustment."""
        # Test negative value (should raise error)
        with mock.patch.dict(os.environ, {"WORKERS_COUNT": "-1"}):
            with pytest.raises(ValidationError):
                Settings()
        
        # Test zero value (should use CPU count)
        import multiprocessing
        expected_cpu_count = multiprocessing.cpu_count()
        with mock.patch.dict(os.environ, {"WORKERS_COUNT": "0"}):
            settings = Settings()
            assert settings.WORKERS_COUNT == expected_cpu_count
    
    def test_mongodb_url_required_in_production(self):
        """Test that MONGODB_URL is required in production."""
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(ValidationError):
                Settings()
            
        # Should work with URL provided
        with mock.patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "MONGODB_URL": "mongodb://localhost:27017"
        }):
            settings = Settings()
            assert settings.MONGODB_URL == "mongodb://localhost:27017"


class TestSecuritySettings:
    """Test security-related settings validation."""
    
    def test_secret_key_warning_in_production(self, caplog):
        """Test warning is logged when using default secret key in production."""
        with mock.patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "MONGODB_URL": "mongodb://localhost:27017",
            "SECRET_KEY": "development_secret_key"
        }):
            Settings()
            assert "Using default SECRET_KEY in production" in caplog.text
