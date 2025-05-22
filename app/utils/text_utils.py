"""
Text utility functions for the SentimentFlow API.

Contains helper functions for text analysis and processing.
"""

import re
from typing import List, Optional, Set
import emoji

# Regular expressions for detecting text types
SOCIAL_MEDIA_PATTERN = re.compile(r'(^|\s)(@\w+|#\w+|https?://\S+|\S+\.\S+/\S+|[^\w\s,.!?]){3,}')
EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]')

def is_social_media_text(text: str) -> bool:
    """
    Detect if the text appears to be from social media (Twitter, Instagram, etc.)
    by checking for typical patterns like mentions, hashtags, and emojis.
    
    Args:
        text: The input text to analyze
        
    Returns:
        bool: True if the text matches social media patterns, False otherwise
    """
    # Check for mentions (@user)
    has_mention = bool(re.search(r'@\w+', text))
    
    # Check for hashtags (#topic)
    has_hashtag = bool(re.search(r'#\w+', text))
    
    # These patterns strongly indicate social media text regardless of length
    if has_mention or has_hashtag:
        return True
    
    # Check for high emoji density
    emoji_density = calculate_emoji_density(text)
    has_high_emoji_density = emoji_density > 0.05  # Consider high if >5% of text is emojis
    if has_high_emoji_density:
        return True
    
    # Check for slang density
    slang_count, slang_density = calculate_slang_density(text)
    
    # High slang density indicates social media text
    # Consider high density if >15% of words are slang or if there are multiple slang terms
    # in a relatively short text
    word_count = len(text.split())
    if (slang_density > 0.15) or (slang_count >= 2 and word_count < 10):
        return True
    
    return False

def contains_emojis(text: str) -> bool:
    """
    Check if the text contains any emojis.
    
    Args:
        text: The input text to analyze
        
    Returns:
        bool: True if the text contains at least one emoji, False otherwise
    """
    return any(c in emoji.EMOJI_DATA for c in text)

def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List of hashtags without the # symbol
    """
    hashtags = re.findall(r'#(\w+)', text)
    return hashtags

def extract_mentions(text: str) -> List[str]:
    """
    Extract @mentions from text.
    
    Args:
        text: Text to extract mentions from
        
    Returns:
        List of mentions without the @ symbol
    """
    mentions = re.findall(r'@(\w+)', text)
    return mentions

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of URLs
    """
    urls = re.findall(r'https?://\S+|www\.\S+', text)
    return urls

def calculate_emoji_density(text: str) -> float:
    """
    Calculate the density of emojis in the text (emojis per character).
    
    Args:
        text: The input text to analyze
        
    Returns:
        float: Ratio of emoji characters to total characters
    """
    if not text:
        return 0.0
        
    emoji_count = sum(c in emoji.EMOJI_DATA for c in text)
    return emoji_count / len(text)

def calculate_slang_density(text: str, slang_terms: list = None) -> tuple:
    """
    Calculate the density of slang terms in the text (slang terms per word).
    
    Args:
        text: The input text to analyze
        slang_terms: Optional list of slang terms to check against
        
    Returns:
        tuple: (slang_count, slang_density)
    """
    if not text:
        return 0, 0.0
    
    if slang_terms is None:
        # Common social media slang/abbreviations
        slang_terms = [
            r'\blol\b', r'\bromfl\b', r'\bbrb\b', r'\bbtw\b', r'\bidk\b',
            r'\bomg\b', r'\bimo\b', r'\bftw\b', r'\bafaik\b', r'\bafk\b',
            r'\bty\b', r'\bthx\b', r'\btysm\b', r'\byolo\b', r'\bfomo\b',
            r'\bsmh\b', r'\btbh\b', r'\bfyi\b', r'\bimho\b', r'\bttyl\b'
        ]
    
    # Convert text to lowercase for case-insensitive matching
    lower_text = text.lower()
    
    # Count slang occurrences
    slang_count = sum(1 for term in slang_terms if re.search(term, lower_text))
    
    # Calculate density (slang terms per word)
    word_count = len(text.split())
    slang_density = slang_count / word_count if word_count > 0 else 0
    
    return slang_count, slang_density

def detect_slang(text: str, slang_terms: list = None) -> bool:
    """
    Detect if the text contains common social media slang.
    
    Args:
        text: The input text to analyze
        slang_terms: Optional list of slang terms to check against
        
    Returns:
        bool: True if slang terms are detected, False otherwise
    """
    slang_count, _ = calculate_slang_density(text, slang_terms)
    return slang_count > 0
