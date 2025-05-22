"""
Text preprocessing service for sentiment analysis.

This module provides functions to clean, normalize and prepare
text for sentiment analysis models, with specific handling for
transformer-based models like DistilBERT.
"""

import html
import logging
import re
import string
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

import emoji
import ftfy
from app.config import settings
from app.models.enums import PreprocessingLevel
from app.utils.text_utils import is_social_media_text

# Configure logging
logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Text preprocessing pipeline for sentiment analysis models.
    
    Provides various text cleaning and normalization functions
    that can be applied based on the specific model requirements.
    """
    
    def __init__(self, 
                 model_name: str = settings.DEFAULT_MODEL,
                 max_length: int = settings.TEXT_MAX_LENGTH,
                 preprocessing_level: PreprocessingLevel = PreprocessingLevel.STANDARD):
        """
        Initialize the text processor with model-specific settings.
        
        Args:
            model_name: Name of the model this processor will prepare text for
            max_length: Maximum text length for the model
            preprocessing_level: How aggressive the preprocessing should be
        """
        self.model_name = model_name
        self.max_length = max_length
        self.preprocessing_level = preprocessing_level
        self.is_uncased = "uncased" in model_name
        self.is_multilingual = "multilingual" in model_name
        self.is_social_media = "twitter" in model_name or "social" in model_name
        
        logger.info(f"Initialized TextProcessor for model: {model_name} "
                   f"with {preprocessing_level} preprocessing")

    def preprocess(self, text: str) -> str:
        """
        Apply the full preprocessing pipeline to the input text.
        
        Args:
            text: The raw input text to process
            
        Returns:
            Preprocessed text ready for the model
        """
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid input text: {text}")
            return ""
            
        # Apply the preprocessing pipeline
        processed_text = text
        
        # Fix encoding issues first
        processed_text = self._fix_encoding(processed_text)

        # If the model is uncased, convert to lowercase early.
        # This ensures subsequent steps operate on the correctly cased text
        # and special tokens inserted later retain their intended casing.
        if self.is_uncased:
            processed_text = processed_text.lower()
        
        # Basic cleaning is always applied
        processed_text = self._basic_clean(processed_text)
        
        # Apply model-specific and level-specific preprocessing
        if self.preprocessing_level != PreprocessingLevel.MINIMAL:
            # Standard preprocessing steps
            processed_text = self._remove_html(processed_text)
            processed_text = self._handle_special_tokens(processed_text)
            
            # Handle social media features if appropriate
            if self.is_social_media or is_social_media_text(processed_text):
                processed_text = self._process_social_media_text(processed_text)
            
            # More aggressive normalization if requested
            if self.preprocessing_level == PreprocessingLevel.AGGRESSIVE:
                processed_text = self._normalize_text(processed_text)
        
        # Ensure text doesn't exceed maximum length
        processed_text = self._truncate_text(processed_text)
        
        return processed_text
    
    def _fix_encoding(self, text: str) -> str:
        """Fix mojibake and other encoding issues."""
        return ftfy.fix_text(text)
    
    def _basic_clean(self, text: str) -> str:
        """
        Perform basic text cleaning.
        
        - Remove excessive whitespace
        - Fix common contractions
        - Normalize quotation marks
        - Strip control characters
        """
        # Strip control characters
        text = "".join(ch for ch in text if ch >= " " or ch in ["\n", "\t"])
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix contractions (examples)
        contractions = {
            r"won\'t": "will not",
            r"can\'t": "cannot",
            r"n\'t": " not",
            r"\'re": " are",
            r"\'s": " is",
            r"\'d": " would",
            r"\'ll": " will",
            r"\'t": " not",
            r"\'ve": " have",
            r"\'m": " am"
        }
        
        # Only fix contractions for models that benefit from it
        if self.preprocessing_level != PreprocessingLevel.PRESERVE:
            for contraction, expansion in contractions.items():
                text = re.sub(contraction, expansion, text)
                
        # Normalize quotes
        text = re.sub(r'[''´`]', "'", text)
        text = re.sub(r'["""]', '"', text)
        
        return text.strip()
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags and decode HTML entities."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = html.unescape(text)
        return text
    
    def _handle_special_tokens(self, text: str) -> str:
        """
        Handle special tokens in text.
        
        For example, URLs, email addresses, phone numbers, etc.
        """
        # Replace URLs with a token (uppercase as required by tests)
        text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
        
        # Replace email addresses with a token (uppercase as required by tests)
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        
        # Replace phone numbers with a token
        text = re.sub(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]', text)
        
        return text
    
    def _process_social_media_text(self, text: str) -> str:
        """
        Process social media specific text elements.
        
        Handles @mentions, #hashtags, emojis, etc.
        """
        # Replace @mentions with a token (uppercase as required by tests)
        text = re.sub(r'@\w+', '[USER]', text)
        
        # Replace #hashtags with just the word or a token based on level
        if self.preprocessing_level == PreprocessingLevel.AGGRESSIVE:
            text = re.sub(r'#(\w+)', r'\1', text)  # Just keep the word without #
        else:
            text = re.sub(r'#(\w+)', r'[HASHTAG] \1', text)  # Mark as hashtag but keep word
        
        # Handle emojis - replace with text description or token based on level
        if self.preprocessing_level == PreprocessingLevel.AGGRESSIVE:
            # Remove emojis
            text = emoji.replace_emoji(text, replace='')
        elif self.preprocessing_level == PreprocessingLevel.STANDARD:
            # Replace emojis with their textual description
            text = emoji.demojize(text)
        # For PRESERVE level, keep emojis as is
        
        return text
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text with more aggressive transformations.
        
        Only used with AGGRESSIVE preprocessing level.
        """
        # Define placeholders for special tokens that might be present before this step
        # These placeholders must not contain any characters from string.punctuation
        placeholder_map = {
            "[URL]": "TEMPURLTOKENXYZ",
            "[EMAIL]": "TEMPEMAILTOKENXYZ",
            "[PHONE]": "TEMPPHONETOKENXYZ",
            "[USER]": "TEMPUSERTOKENXYZ",
            # Note: [HASHTAG] is not converted to a token in AGGRESSIVE mode by _process_social_media_text,
            # and [NUMBER] is added after punctuation removal.
        }

        # Replace special tokens with placeholders
        for token, placeholder in placeholder_map.items():
            text = text.replace(token, placeholder)
        
        # Remove punctuation
        if self.preprocessing_level == PreprocessingLevel.AGGRESSIVE:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Replace numbers with a token
        text = re.sub(r'\d+', '[NUMBER]', text)

        # Restore special tokens from placeholders
        for token, placeholder in placeholder_map.items():
            text = text.replace(placeholder, token)
        
        # Remove extra spaces again after all the replacements
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to maximum length.
        
        This is a simple character-based truncation. For token-based
        truncation, you would need the actual model tokenizer.
        """
        # Simple truncation based on character count
        # A more sophisticated approach would use the model tokenizer
        if len(text) > self.max_length:
            logger.debug(f"Truncating text from {len(text)} to {self.max_length} characters")
            return text[:self.max_length]
        return text
    
    def batch_preprocess(self, texts: List[str]) -> List[str]:
        """
        Process a batch of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of processed texts
        """
        return [self.preprocess(text) for text in texts]


# Model-specific text processors
MODEL_PROCESSORS = {
    "distilbert-base-uncased-finetuned-sst-2-english": {
        "description": "Binary sentiment model (positive/negative)",
        "preprocessing_level": PreprocessingLevel.STANDARD,
        "uncased": True,
        "max_length": 512,
    },
    "cardiffnlp/twitter-roberta-base-sentiment": {
        "description": "Twitter sentiment model (positive/neutral/negative)",
        "preprocessing_level": PreprocessingLevel.PRESERVE,
        "uncased": False,
        "max_length": 512,
        "social_media": True,
    },
    "nlptown/bert-base-multilingual-uncased-sentiment": {
        "description": "Multilingual sentiment model (1-5 stars)",
        "preprocessing_level": PreprocessingLevel.STANDARD,
        "uncased": True,
        "max_length": 512,
        "multilingual": True,
    }
}


def get_processor_for_model(model_name: str) -> TextProcessor:
    """
    Get a text processor configured for a specific model.
    
    Args:
        model_name: The model to get a processor for
        
    Returns:
        A configured TextProcessor instance
    """
    model_config = MODEL_PROCESSORS.get(model_name, {})
    preprocessing_level = model_config.get("preprocessing_level", PreprocessingLevel.STANDARD)
    max_length = model_config.get("max_length", settings.TEXT_MAX_LENGTH)
    
    return TextProcessor(
        model_name=model_name,
        max_length=max_length,
        preprocessing_level=preprocessing_level
    )


# Default processor instance using the configured default model
default_processor = get_processor_for_model(settings.DEFAULT_MODEL)
