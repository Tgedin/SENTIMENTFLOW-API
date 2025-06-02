import logging
import time
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import torch
from transformers.pipelines.base import Pipeline
from transformers.pipelines import pipeline

from app.config import settings
from app.models.enums import SentimentLabel
from app.services.model_manager import ModelManager
from app.services.text_processor import TextProcessor, get_processor_for_model

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Service that orchestrates the sentiment analysis pipeline.
    
    This class integrates model management, text preprocessing, 
    and result processing to provide a complete sentiment analysis solution.
    """
    
    def __init__(
        self, 
        model_name: str = settings.DEFAULT_MODEL,
        model_manager: Optional[ModelManager] = None,
        text_processor: Optional[TextProcessor] = None
    ):
        """
        Initialize the sentiment analyzer with model management and text processing.
        
        Args:
            model_name: The name of the sentiment model to use (from Hugging Face Hub)
            model_manager: Optional ModelManager instance (will create if None)
            text_processor: Optional TextProcessor instance (will create if None)
        """
        self.model_name = model_name
        self.model_manager = model_manager or ModelManager()
        self.text_processor = text_processor or TextProcessor()
        self.pipeline = None
        self.model_meta = None
        
        # Cache for model output labels mapping
        self._output_labels = {}
        
        logger.info(f"SentimentAnalyzer initialized with model: {model_name}")
    
    async def load_model(self) -> None:
        """
        Load the sentiment analysis model asynchronously.
        """
        if self.pipeline is None:
            logger.info(f"Loading sentiment analysis model: {self.model_name}")
            # Get the model metadata to understand its output format
            self.model_meta = self.model_manager.get_model_metadata(self.model_name)
            
            # Load the actual model and tokenizer
            model, tokenizer, metadata = self.model_manager.get_model(self.model_name)
            
            # Create a pipeline from the model and tokenizer
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                top_k=None  # Return all scores instead of deprecated return_all_scores
            )
            
            # Cache the output labels for this model
            self._output_labels[self.model_name] = self._get_model_labels()
            
            logger.info(f"Model {self.model_name} loaded successfully")
    
    def _get_model_labels(self) -> List[str]:
        """
        Get the output labels for the current model.
        
        Returns:
            List of label strings for the model.
        """
        # Try to get labels from the pipeline config
        if (self.pipeline is not None and 
            hasattr(self.pipeline, "model") and 
            hasattr(self.pipeline.model, "config")):
            if hasattr(self.pipeline.model.config, "id2label"):
                return list(self.pipeline.model.config.id2label.values())
        
        # Fallback based on known models
        if self.model_name == "distilbert-base-uncased-finetuned-sst-2-english":
            return ["negative", "positive"]
        elif self.model_name == "cardiffnlp/twitter-roberta-base-sentiment":
            return ["negative", "neutral", "positive"]
        elif self.model_name == "nlptown/bert-base-multilingual-uncased-sentiment":
            return ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
        
        # Generic fallback
        return ["negative", "positive"]
    
    async def analyze_text(
        self, 
        text: str, 
        model_name: Optional[str] = None,
        include_raw_output: bool = False
    ) -> Dict:
        """
        Analyze the sentiment of a single text input.
        
        Args:
            text: The text to analyze
            model_name: Optional model name to override the default
            include_raw_output: Whether to include the raw model output in the result
            
        Returns:
            Dict containing sentiment analysis results with confidence scores
        """
        if model_name and model_name != self.model_name:
            # Switch to a different model if requested
            self.model_name = model_name
            self.pipeline = None
            
        # Make sure the model is loaded
        if self.pipeline is None:
            await self.load_model()
        
        # Preprocess the text
        preprocessed_text = self.text_processor.preprocess(text)
        
        # Log the inference attempt
        logger.debug(f"Analyzing sentiment for text: {preprocessed_text[:50]}...")
        
        try:
            # Run the model inference
            if self.pipeline is None:
                raise RuntimeError("Pipeline not loaded. Call load_model() first.")
            raw_result = self.pipeline(preprocessed_text)
            
            # Process and validate the results
            result = self._process_result(text, preprocessed_text, raw_result)
            
            # Add the raw output if requested
            if include_raw_output:
                result["raw_output"] = raw_result
                
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
            raise
    
    async def analyze_texts(
        self, 
        texts: List[str], 
        model_name: Optional[str] = None,
        batch_size: int = settings.BATCH_SIZE
    ) -> List[Dict]:
        """
        Analyze the sentiment of multiple texts efficiently.
        
        Args:
            texts: List of texts to analyze
            model_name: Optional model name to override the default
            batch_size: Batch size for processing multiple texts
            
        Returns:
            List of dicts containing sentiment analysis results
        """
        if model_name and model_name != self.model_name:
            # Switch to a different model if requested
            self.model_name = model_name
            self.pipeline = None
            
        # Make sure the model is loaded
        if self.pipeline is None:
            await self.load_model()
        
        # Preprocess all texts
        preprocessed_texts = [self.text_processor.preprocess(text) for text in texts]
        
        results = []
        # Process in batches
        for i in range(0, len(preprocessed_texts), batch_size):
            batch_texts = preprocessed_texts[i:i+batch_size]
            original_texts = texts[i:i+batch_size]
            try:
                # Run batch inference
                if self.pipeline is None:
                    raise RuntimeError("Pipeline not loaded. Call load_model() first.")
                raw_results = self.pipeline(batch_texts)
                # Defensive: handle None, Tensor, or other non-iterable results
                if raw_results is None:
                    processed_results = []
                elif isinstance(raw_results, list):
                    processed_results = raw_results
                elif hasattr(raw_results, '__iter__') and not isinstance(raw_results, (str, bytes, dict)):
                    try:
                        processed_results = list(raw_results)
                    except Exception as convert_error:
                        logger.error(f"Failed to convert results to list: {convert_error}")
                        processed_results = []
                else:
                    processed_results = [raw_results]

                # Process each result in the batch
                for j, raw_result in enumerate(processed_results):
                    if j < len(original_texts):  # Safety check
                        result = self._process_result(
                            original_texts[j], 
                            batch_texts[j], 
                            raw_result
                        )
                        results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing batch: {str(e)}", exc_info=True)
                # Add error results for this batch
                for j in range(len(batch_texts)):
                    results.append({
                        "text": original_texts[j],
                        "error": str(e),
                        "success": False
                    })
        
        return results
    
    def _process_result(self, original_text: str, preprocessed_text: str, raw_result: Any) -> Dict:
        """
        Process and validate the raw model output into a standardized format.
        
        Args:
            original_text: The original input text
            preprocessed_text: The preprocessed text sent to the model
            raw_result: The raw output from the model pipeline
            
        Returns:
            Dict with standardized sentiment analysis results
        """
        # Start with basic info
        result = {
            "text": original_text,
            "success": True,
            "model": self.model_name
        }
        
        # For single result format (common in HF pipelines)
        if isinstance(raw_result, dict):
            raw_result = [raw_result]
            
        # Extract the primary sentiment and confidence
        # When using top_k=None, the result is a list of all score dicts
        logger.debug(f"Raw result type: {type(raw_result)}, content: {raw_result}")
        
        if isinstance(raw_result, list) and len(raw_result) > 0:
            # Check what type of items are in the list
            first_item = raw_result[0]
            logger.debug(f"First item type: {type(first_item)}, content: {first_item}")
            
            # Handle nested list format: [[{'label': 'POSITIVE', 'score': 0.999}]]
            if isinstance(first_item, list) and len(first_item) > 0:
                logger.debug("Detected nested list format, flattening...")
                raw_result = first_item  # Flatten the nested list
                first_item = raw_result[0]
                logger.debug(f"After flattening - first item: {first_item}")
            
            if isinstance(first_item, dict):
                # Sort by score to get the highest confidence prediction
                sorted_results = sorted(raw_result, key=lambda x: x["score"], reverse=True)
                primary_sentiment = sorted_results[0]
            else:
                # If it's not a dict, log the issue
                logger.warning(f"Unexpected item format in results: {first_item}")
                primary_sentiment = {"label": "unknown", "score": 0.0}
        else:
            # Fallback for unexpected format
            logger.warning(f"Unexpected result format: {raw_result}")
            primary_sentiment = {"label": "unknown", "score": 0.0}
        
        # Add the primary sentiment details
        result["sentiment"] = self._normalize_sentiment_label(primary_sentiment["label"])
        result["confidence"] = round(float(primary_sentiment["score"]), 4)
        
        # Add all sentiment scores for multi-class models
        result["scores"] = {}
        
        # If we have multiple results, add them all
        for item in raw_result:
            label = self._normalize_sentiment_label(item["label"])
            result["scores"][label] = round(float(item["score"]), 4)
            
        # For binary models, ensure we have both positive and negative scores
        if self.model_name == "distilbert-base-uncased-finetuned-sst-2-english":
            if "positive" in result["scores"] and "negative" not in result["scores"]:
                result["scores"]["negative"] = round(1.0 - result["scores"]["positive"], 4)
            elif "negative" in result["scores"] and "positive" not in result["scores"]:
                result["scores"]["positive"] = round(1.0 - result["scores"]["negative"], 4)
        
        # Validate the result
        result["valid"] = self._validate_result(result)
        
        return result
    
    def _normalize_sentiment_label(self, label: str) -> str:
        """
        Normalize model-specific sentiment labels to standard format.
        
        Args:
            label: The raw label from the model
            
        Returns:
            Normalized label string
        """
        # Handle CardiffNLP Twitter RoBERTa model labels
        if label.lower() in ["label_0"]:
            return SentimentLabel.NEGATIVE.value
        elif label.lower() in ["label_1"]:
            return SentimentLabel.NEUTRAL.value
        elif label.lower() in ["label_2"]:
            return SentimentLabel.POSITIVE.value
            
        # Handle star-based labels (convert to positive/negative/neutral)
        if label in ["1 star", "2 stars"]:
            return SentimentLabel.NEGATIVE.value
        elif label in ["4 stars", "5 stars"]:
            return SentimentLabel.POSITIVE.value
        elif label == "3 stars":
            return SentimentLabel.NEUTRAL.value
            
        # Return the label as is for standard models
        return label.lower()
    
    def _validate_result(self, result: Dict) -> bool:
        """
        Validate the analysis result to ensure it's reasonable.
        
        Args:
            result: The processed result dictionary
            
        Returns:
            Boolean indicating if the result is valid
        """
        # Check if confidence is reasonable (not too extreme)
        confidence = result["confidence"]
        if confidence > 0.99 or confidence < 0.01:
            # Extremely high/low confidence can indicate issues
            if len(result["text"]) < 5:  # Very short text
                return False
        
        # Check if text was too short for meaningful analysis
        if len(result["text"].strip()) == 0:
            return False
            
        return True
    
    async def get_available_models(self) -> List[Dict]:
        """
        Get a list of available sentiment analysis models.
        
        Returns:
            List of dicts with model information
        """
        return [
            {
                "name": "distilbert-base-uncased-finetuned-sst-2-english",
                "description": "General purpose binary sentiment analysis (positive/negative)",
                "languages": ["english"],
                "classes": ["positive", "negative"],
                "is_default": self.model_name == "distilbert-base-uncased-finetuned-sst-2-english"
            },
            {
                "name": "cardiffnlp/twitter-roberta-base-sentiment",
                "description": "Social media focused sentiment analysis with 3 classes",
                "languages": ["english"],
                "classes": ["positive", "neutral", "negative"],
                "is_default": self.model_name == "cardiffnlp/twitter-roberta-base-sentiment"
            },
            {
                "name": "nlptown/bert-base-multilingual-uncased-sentiment",
                "description": "Multilingual sentiment analysis with 5-star rating",
                "languages": ["english", "french", "german", "dutch", "italian", "spanish"],
                "classes": ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
                "is_default": self.model_name == "nlptown/bert-base-multilingual-uncased-sentiment"
            }
        ]
