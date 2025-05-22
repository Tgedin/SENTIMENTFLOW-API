"""
Unit tests for the text preprocessing service.

These tests cover various aspects of text preprocessing for sentiment analysis,
including different preprocessing levels, model-specific behaviors, and edge cases.
"""

import pytest
from app.services.text_processor import (
    TextProcessor, 
    PreprocessingLevel, 
    get_processor_for_model, 
    default_processor
)

class TestTextProcessorInitialization:
    """Tests for TextProcessor initialization and basic properties."""
    
    def test_default_initialization(self):
        """Test that TextProcessor initializes with default values."""
        processor = TextProcessor()
        assert processor.preprocessing_level == PreprocessingLevel.STANDARD
        assert processor.model_name is not None
        assert processor.max_length > 0
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        processor = TextProcessor(
            model_name="custom-model",
            max_length=128,
            preprocessing_level=PreprocessingLevel.AGGRESSIVE
        )
        assert processor.model_name == "custom-model"
        assert processor.max_length == 128
        assert processor.preprocessing_level == PreprocessingLevel.AGGRESSIVE
        
    def test_model_property_detection(self):
        """Test that model properties are correctly detected from model name."""
        # Test uncased model detection
        processor = TextProcessor(model_name="bert-base-uncased")
        assert processor.is_uncased is True
        
        # Test multilingual model detection
        processor = TextProcessor(model_name="bert-base-multilingual-uncased")
        assert processor.is_multilingual is True
        
        # Test social media model detection
        processor = TextProcessor(model_name="roberta-twitter-sentiment")
        assert processor.is_social_media is True


class TestBasicPreprocessing:
    """Tests for basic text preprocessing functionality."""
    
    def test_empty_input(self):
        """Test handling of empty input."""
        processor = TextProcessor()
        assert processor.preprocess("") == ""
        assert processor.preprocess(None) == ""
    
    def test_whitespace_normalization(self):
        """Test that whitespace is properly normalized."""
        processor = TextProcessor()
        text = "This    has \t\tmultiple\n\nspaces."
        expected = "this has multiple spaces."  # Changed to lowercase
        assert processor.preprocess(text) == expected
    
    def test_basic_clean(self):
        """Test basic text cleaning functionality."""
        processor = TextProcessor()
        text = "This'll be cleaned. It's a test."
        # With standard preprocessing, contractions should be expanded
        expected = "this will be cleaned. it is a test."  # Changed to lowercase
        assert processor.preprocess(text) == expected
        
    def test_html_removal(self):
        """Test that HTML tags and entities are removed."""
        processor = TextProcessor()
        text = "<p>This is a <b>test</b> with &quot;HTML&quot; entities.</p>"
        expected = "this is a test with \"html\" entities."  # Changed to lowercase
        assert processor.preprocess(text) == expected
        
    def test_special_token_handling(self):
        """Test that special tokens like URLs are properly handled."""
        processor = TextProcessor()
        text = "Check out https://example.com or email user@example.com"
        processed = processor.preprocess(text)
        assert "https://example.com" not in processed
        assert "user@example.com" not in processed
        assert "[URL]" in processed
        assert "[EMAIL]" in processed


class TestPreprocessingLevels:
    """Tests for different preprocessing levels."""
    
    def test_minimal_preprocessing(self):
        """Test minimal preprocessing that preserves most features."""
        processor = TextProcessor(preprocessing_level=PreprocessingLevel.MINIMAL)
        text = "<p>This is a test with a URL: https://example.com and email@test.com</p>"
        processed = processor.preprocess(text)
        # Minimal shouldn't remove HTML or replace URLs
        assert "https://example.com" in processed
        assert "email@test.com" in processed
        
    def test_standard_preprocessing(self):
        """Test standard preprocessing level."""
        processor = TextProcessor(preprocessing_level=PreprocessingLevel.STANDARD)
        text = "I can't believe #awesome 😊 https://example.com"
        processed = processor.preprocess(text)
        # Standard should replace URLs and handle social media features
        # For default (uncased) model, text content will be lowercase
        assert "https://example.com" not in processed
        assert "[URL]" in processed 
        # Check for expanded contraction in lowercase
        assert "can not" in processed or "cannot" in processed # Already lowercase due to is_uncased
        
    def test_aggressive_preprocessing(self):
        """Test aggressive preprocessing that maximizes normalization."""
        processor = TextProcessor(preprocessing_level=PreprocessingLevel.AGGRESSIVE)
        text = "I can't believe #awesome 😊 https://example.com 123"
        processed = processor.preprocess(text)
        # Aggressive should normalize aggressively
        # For default (uncased) model, text content will be lowercase
        assert "[URL]" in processed
        assert "can not" in processed or "cannot" in processed # Already lowercase due to is_uncased
        assert "123" not in processed 
        assert "[NUMBER]" in processed
        
    def test_preserve_preprocessing(self):
        """Test preserve preprocessing that keeps original features."""
        processor = TextProcessor(preprocessing_level=PreprocessingLevel.PRESERVE)
        text = "I can't believe #awesome 😊"
        processed = processor.preprocess(text)
        # Preserve should keep contractions and emojis
        assert "can't" in processed
        assert "😊" in processed


class TestModelSpecificBehavior:
    """Tests for model-specific preprocessing behavior."""
    
    def test_uncased_model_processing(self):
        """Test that text is lowercased for uncased models."""
        processor = TextProcessor(model_name="bert-base-uncased")
        text = "This Has Mixed CASE"
        processed = processor.preprocess(text)
        assert processed == processed.lower()
        
    def test_cased_model_processing(self):
        """Test that case is preserved for cased models."""
        processor = TextProcessor(model_name="bert-base-cased")
        text = "This Has Mixed CASE"
        processed = processor.preprocess(text)
        assert "Mixed" in processed
        assert "CASE" in processed
        
    def test_social_media_model_processing(self):
        """Test special handling for social media models."""
        processor = TextProcessor(model_name="twitter-roberta")
        text = "@user This is #awesome! 😊"
        processed = processor.preprocess(text)
        # Should handle mentions, hashtags, and emojis appropriately
        assert "@user" not in processed
        assert "[USER]" in processed
        
    def test_get_processor_for_model(self):
        """Test the factory function for getting model-specific processors."""
        # Test with known model
        processor = get_processor_for_model("distilbert-base-uncased-finetuned-sst-2-english")
        assert processor.model_name == "distilbert-base-uncased-finetuned-sst-2-english"
        assert processor.is_uncased is True
        
        # Test with unknown model (should use defaults)
        processor = get_processor_for_model("unknown-model")
        assert processor.model_name == "unknown-model"
        assert processor.preprocessing_level == PreprocessingLevel.STANDARD


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""
    
    def test_long_text_truncation(self):
        """Test that long texts are properly truncated."""
        max_length = 20
        processor = TextProcessor(max_length=max_length)
        text = "This is a very long text that should be truncated to the maximum length."
        processed = processor.preprocess(text)
        assert len(processed) <= max_length
        
    def test_extreme_text(self):
        """Test processing of text with extreme characteristics."""
        processor = TextProcessor()
        
        # Text with lots of emojis
        text_with_emojis = "😊😂🤣😍😒👍🎉" * 10
        assert processor.preprocess(text_with_emojis) != ""
        
        # Text with unusual characters
        text_with_unusual_chars = "∑∫∂∇∆√∞≈≠≡≤≥±÷×"
        assert processor.preprocess(text_with_unusual_chars) != ""
        
        # Text with control characters
        text_with_control_chars = "This has \x00\x01\x02\x03 control chars"
        processed = processor.preprocess(text_with_control_chars)
        assert "\x00" not in processed
        assert "\x01" not in processed
        
    def test_encoding_issues(self):
        """Test that encoding issues are properly fixed."""
        processor = TextProcessor()
        # Text with encoding issues
        text_with_encoding_issues = "This text has mojibake: café"
        processed = processor.preprocess(text_with_encoding_issues)
        assert "café" in processed
        
    def test_batch_processing(self):
        """Test batch processing functionality."""
        processor = TextProcessor()
        texts = ["Text one", "Text two", "Text three"]
        processed = processor.batch_preprocess(texts)
        assert len(processed) == 3
        assert all(isinstance(text, str) for text in processed)


class TestSocialMediaFeatures:
    """Tests specifically for social media text processing."""
    
    def test_mentions_handling(self):
        """Test handling of @mentions."""
        processor = TextProcessor(model_name="twitter-model")
        text = "@user1 and @user2 are discussing #AI"
        processed = processor.preprocess(text)
        assert "@user1" not in processed
        assert "@user2" not in processed
        assert "[USER]" in processed
        
    def test_hashtags_handling(self):
        """Test handling of #hashtags."""
        processor = TextProcessor(model_name="twitter-model")
        text = "This is a #greatidea and #innovation"
        processed = processor.preprocess(text)
        # Hashtags should be preserved but possibly transformed
        assert "#greatidea" not in processed
        assert "greatidea" in processed or "[HASHTAG]" in processed
        
    def test_emoji_handling(self):
        """Test handling of emojis."""
        processor = TextProcessor(model_name="twitter-model")
        text = "I love this! 😊 It's amazing 🎉"
        processed = processor.preprocess(text)
        # Emojis might be removed, replaced, or kept depending on preprocessing level
        assert processed != ""
