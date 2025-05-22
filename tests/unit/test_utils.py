"""
Tests for the utility functions in the utils module.

These tests verify the text analysis and processing utilities
that support the sentiment analysis functionality.
"""

import pytest
from app.utils.text_utils import (
    is_social_media_text,
    extract_hashtags,
    extract_mentions,
    extract_urls,
    contains_emojis
)


class TestSocialMediaDetection:
    """Tests for social media text detection."""
    
    def test_detect_twitter_style_text(self):
        """Test detection of Twitter-style text."""
        # Should be detected as social media text
        assert is_social_media_text("@user This is #awesome! 😊")
        assert is_social_media_text("RT @someone: Check out this link https://example.com #cool")
        
        # Should not be detected as social media text
        assert not is_social_media_text("This is a normal sentence without special features.")
        assert not is_social_media_text("This text contains https://example.com but not enough social features.")
    
    def test_emoji_density_detection(self):
        """Test that high emoji density is detected as social media text."""
        # High emoji density
        assert is_social_media_text("I love this! 😊😍🎉🔥")
        assert is_social_media_text("Short 😊😍")
        
        # Low emoji density
        assert not is_social_media_text("Just one emoji in long text 😊 is not enough to qualify as social media.")
    
    def test_slang_detection(self):
        """Test that high slang density is detected as social media text."""
        # High slang density
        assert is_social_media_text("omg lol that's so funny tbh")
        assert is_social_media_text("idk what to do smh")
        
        # Low slang density
        assert not is_social_media_text("I'm not sure lol what to do with this lengthy non-social media text.")


class TestExtraction:
    """Tests for extraction utilities."""
    
    def test_hashtag_extraction(self):
        """Test extraction of hashtags from text."""
        text = "This is a #test with #multiple hashtags #123 but not #"
        hashtags = extract_hashtags(text)
        assert hashtags == ["test", "multiple", "123"]
        assert extract_hashtags("No hashtags here") == []
    
    def test_mention_extraction(self):
        """Test extraction of @mentions from text."""
        text = "@user1 mentioned @user2 and @user_3 but not @ user"
        mentions = extract_mentions(text)
        assert mentions == ["user1", "user2", "user_3"]
        assert extract_mentions("No mentions here") == []
    
    def test_url_extraction(self):
        """Test extraction of URLs from text."""
        text = "Check out https://example.com and http://test.org/page and www.simple.com"
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org/page" in urls
        assert "www.simple.com" in urls
        assert len(urls) == 3
        assert extract_urls("No URLs here") == []


class TestEmojiDetection:
    """Tests for emoji detection."""
    
    def test_contains_emojis(self):
        """Test detection of emojis in text."""
        assert contains_emojis("This contains an emoji 😊")
        assert contains_emojis("Multiple emojis 🎉🔥😍")
        assert not contains_emojis("No emojis here")
        assert not contains_emojis("Just text with :) symbols")
