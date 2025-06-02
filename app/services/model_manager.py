import logging
import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)
from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils import PreTrainedTokenizer

from app.config import settings

logger = logging.getLogger(__name__)


class ModelMetadata:
    """Class to store model metadata information."""

    def __init__(
        self,
        model_id: str,
        version: str = "latest",
        task: str = "sentiment-analysis",
        classes: Optional[List[str]] = None,
        language: str = "en",
        description: Optional[str] = None,
    ):
        self.model_id = model_id
        self.version = version
        self.task = task
        self.classes = classes or []
        self.language = language
        self.description = description
        self.load_time: Optional[float] = None
        self.last_used: Optional[float] = None
        self.size_mb: Optional[float] = None
        
        # Version-specific metadata
        self.created_at: str = datetime.now().isoformat()
        self.performance_metrics: Dict[str, float] = {}
        self.commit_hash: Optional[str] = None
        self.is_active: bool = True
        self.parent_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "model_id": self.model_id,
            "version": self.version,
            "task": self.task,
            "classes": self.classes,
            "language": self.language,
            "description": self.description,
            "load_time": self.load_time,
            "last_used": self.last_used,
            "size_mb": self.size_mb,
            "created_at": self.created_at,
            "performance_metrics": self.performance_metrics,
            "commit_hash": self.commit_hash,
            "is_active": self.is_active,
            "parent_version": self.parent_version,
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Create a ModelMetadata object from a dictionary."""
        metadata = cls(
            model_id=data["model_id"],
            version=data["version"],
            task=data.get("task", "sentiment-analysis"),
            classes=data.get("classes", []),
            language=data.get("language", "en"),
            description=data.get("description"),
        )
        metadata.load_time = data.get("load_time")
        metadata.last_used = data.get("last_used")
        metadata.size_mb = data.get("size_mb")
        metadata.created_at = data.get("created_at", metadata.created_at)
        metadata.performance_metrics = data.get("performance_metrics", {})
        metadata.commit_hash = data.get("commit_hash")
        metadata.is_active = data.get("is_active", True)
        metadata.parent_version = data.get("parent_version")
        return metadata

    def __repr__(self) -> str:
        return f"ModelMetadata(model_id={self.model_id}, version={self.version})"


class ModelVersionHistory:
    """Class to track version history for a model."""
    
    def __init__(self, model_id: str, metadata_dir: Optional[str] = None):
        self.model_id = model_id
        self.metadata_dir = metadata_dir or os.path.join(settings.MODEL_PATH, "metadata")
        self.versions: Dict[str, ModelMetadata] = {}
        self.active_version: str = "latest"
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Load existing version history if available
        self._load_version_history()
    
    def _get_metadata_path(self) -> str:
        """Get path to metadata file for this model."""
        return os.path.join(self.metadata_dir, f"{self.model_id.replace('/', '_')}_versions.json")
    
    def _load_version_history(self) -> None:
        """Load version history from file."""
        metadata_path = self._get_metadata_path()
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    data = json.load(f)
                    
                self.active_version = data.get("active_version", "latest")
                for version_id, version_data in data.get("versions", {}).items():
                    self.versions[version_id] = ModelMetadata.from_dict(version_data)
                    
                logger.debug(f"Loaded version history for {self.model_id}: {len(self.versions)} versions")
            except Exception as e:
                logger.error(f"Error loading version history for {self.model_id}: {str(e)}")
                # Initialize with empty versions if loading fails
                self.versions = {}
                self.active_version = "latest"
    
    def _save_version_history(self) -> None:
        """Save version history to file."""
        metadata_path = self._get_metadata_path()
        try:
            data = {
                "model_id": self.model_id,
                "active_version": self.active_version,
                "versions": {version_id: metadata.to_dict() for version_id, metadata in self.versions.items()}
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved version history for {self.model_id}")
        except Exception as e:
            logger.error(f"Error saving version history for {self.model_id}: {str(e)}")
    
    def add_version(self, metadata: ModelMetadata) -> None:
        """Add a new version to the history."""
        # If adding the "latest" version, check if we already have one
        if metadata.version == "latest":
            # Check if we already have a "latest" version
            if "latest" in self.versions:
                # Update existing "latest" version instead of creating new one
                logger.debug(f"Updating existing 'latest' version for model {self.model_id}")
                self.versions["latest"] = metadata
                self.active_version = "latest"
                self._save_version_history()
                return
            
            # Only create timestamp version if we need a specific versioned copy
            # For normal use, keep it as "latest"
            # timestamp_version = f"v_{int(time.time())}"
            # metadata.version = timestamp_version
        
        self.versions[metadata.version] = metadata
        self.active_version = metadata.version  # Make this the active version
        self._save_version_history()
        logger.info(f"Added version {metadata.version} to model {self.model_id}")
    
    def get_version(self, version: Optional[str] = None) -> Optional[ModelMetadata]:
        """Get metadata for a specific version."""
        version = version or self.active_version
        return self.versions.get(version)
    
    def set_active_version(self, version: str) -> bool:
        """Set the active version."""
        if version in self.versions:
            self.active_version = version
            self._save_version_history()
            logger.info(f"Set active version to {version} for model {self.model_id}")
            return True
        return False
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all versions with their metadata."""
        return [
            {
                "version": version,
                "is_active": version == self.active_version,
                "created_at": metadata.created_at,
                **metadata.to_dict()
            }
            for version, metadata in self.versions.items()
        ]
        
    def delete_version(self, version: str) -> bool:
        """Delete a version from the history."""
        if version in self.versions:
            # Don't allow deleting the active version
            if version == self.active_version:
                logger.warning(f"Cannot delete active version {version} for model {self.model_id}")
                return False
            
            del self.versions[version]
            self._save_version_history()
            logger.info(f"Deleted version {version} from model {self.model_id}")
            return True
        return False


class ModelManager:
    """
    Manages NLP models with lazy loading to optimize memory usage.
    
    Only loads models when they are first requested and keeps them cached
    for future use. Provides model metadata and versioning support.
    """

    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize the model manager.
        
        Args:
            models_dir: Directory to store downloaded models. If None, uses config setting.
        """
        self.models_dir = models_dir or settings.MODEL_PATH
        self._ensure_models_dir()
        
        # Cache for loaded models and tokenizers
        self._models: Dict[str, Dict[str, PreTrainedModel]] = {}  # model_id -> {version -> model}
        self._tokenizers: Dict[str, Dict[str, PreTrainedTokenizer]] = {}  # model_id -> {version -> tokenizer}
        self._metadata: Dict[str, ModelMetadata] = {}
        
        # Version history tracking
        self._version_history: Dict[str, ModelVersionHistory] = {}
        
        # Register default models with metadata
        self._register_default_models()
        
        logger.info(f"ModelManager initialized with models directory: {self.models_dir}")

    def _ensure_models_dir(self) -> None:
        """Ensure the models directory exists."""
        os.makedirs(self.models_dir, exist_ok=True)
        metadata_dir = os.path.join(self.models_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        logger.debug(f"Ensured models directory exists: {self.models_dir}")

    def _register_default_models(self) -> None:
        """Register default models with their metadata."""
        # Register the default model from settings
        self.register_model(
            model_id=settings.DEFAULT_MODEL,
            metadata=ModelMetadata(
                model_id=settings.DEFAULT_MODEL,
                classes=["negative", "positive"],
                description="Default sentiment analysis model - DistilBERT fine-tuned on SST-2",
            )
        )
        
        # Register additional models that we support
        self.register_model(
            model_id="cardiffnlp/twitter-roberta-base-sentiment",
            metadata=ModelMetadata(
                model_id="cardiffnlp/twitter-roberta-base-sentiment",
                classes=["negative", "neutral", "positive"],
                description="RoBERTa model fine-tuned for sentiment analysis on tweets",
            )
        )
        
        self.register_model(
            model_id="nlptown/bert-base-multilingual-uncased-sentiment",
            metadata=ModelMetadata(
                model_id="nlptown/bert-base-multilingual-uncased-sentiment",
                classes=["1 star", "2 stars", "3 stars", "4 stars", "5 stars"],
                language="multilingual",
                description="Multilingual BERT model fine-tuned for sentiment analysis on product reviews",
            )
        )

    def register_model(self, model_id: str, metadata: Optional[ModelMetadata] = None, 
                      version: str = "latest") -> None:
        """
        Register a model with the manager.
        
        Args:
            model_id: The Hugging Face model ID or local path
            metadata: Optional metadata for the model
            version: Version identifier for this model
        """
        if not metadata:
            metadata = ModelMetadata(model_id=model_id, version=version)
        else:
            metadata.version = version
            
        # Ensure we have a version history for this model
        if model_id not in self._version_history:
            self._version_history[model_id] = ModelVersionHistory(model_id)
        
        # Add this version to the history
        self._version_history[model_id].add_version(metadata)
        
        # Initialize model and tokenizer caches if needed
        if model_id not in self._models:
            self._models[model_id] = {}
        if model_id not in self._tokenizers:
            self._tokenizers[model_id] = {}
            
        self._metadata[model_id] = metadata
        logger.info(f"Registered model: {model_id} version: {version}")

    def get_model(self, model_id: Optional[str] = None, 
                 version: Optional[str] = None) -> Tuple[PreTrainedModel, PreTrainedTokenizer, ModelMetadata]:
        """
        Get a model and its tokenizer. Implements lazy loading.
        
        Args:
            model_id: The model ID to load. If None, uses the default model.
            version: The model version to load. If None, uses the active version.
            
        Returns:
            Tuple of (model, tokenizer, metadata)
            
        Raises:
            ValueError: If the model is not registered or fails to load
        """
        model_id = model_id or settings.DEFAULT_MODEL
        
        if model_id not in self._version_history:
            raise ValueError(f"Model {model_id} is not registered. Register it first.")
        
        # Get the appropriate version to load
        history = self._version_history[model_id]
        version = version or history.active_version
        
        # Make sure this version exists
        metadata = history.get_version(version)
        if not metadata:
            raise ValueError(f"Version {version} of model {model_id} is not available")
        
        # Update the last used timestamp
        metadata.last_used = time.time()
        
        # Lazy loading: only load if not already loaded
        if model_id not in self._models or version not in self._models[model_id]:
            logger.info(f"Lazy loading model: {model_id} version: {version}")
            self._load_model(model_id, version, metadata)
        else:
            logger.debug(f"Using cached model: {model_id} version: {version}")
        
        return self._models[model_id][version], self._tokenizers[model_id][version], metadata

    def _load_model(self, model_id: str, version: str, metadata: ModelMetadata) -> None:
        """
        Load a model and its tokenizer from Hugging Face or local path.
        
        Args:
            model_id: The model ID to load
            version: The version to load
            metadata: The model metadata
            
        Raises:
            RuntimeError: If loading fails
        """
        start_time = time.time()
        
        try:
            # Construct the local path for this version
            local_path = os.path.join(
                self.models_dir, 
                f"{model_id.replace('/', '_')}_{version}"
            )
            
            # Check if model exists locally
            if os.path.exists(local_path):
                logger.info(f"Loading model from local path: {local_path}")
                model = AutoModelForSequenceClassification.from_pretrained(local_path)
                tokenizer = AutoTokenizer.from_pretrained(local_path)
            else:
                logger.info(f"Downloading model from Hugging Face: {model_id}")
                model = AutoModelForSequenceClassification.from_pretrained(model_id)
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                
                # Save the model locally for future use
                os.makedirs(local_path, exist_ok=True)
                model.save_pretrained(local_path)
                tokenizer.save_pretrained(local_path)
            
            # Store in cache
            if model_id not in self._models:
                self._models[model_id] = {}
            if model_id not in self._tokenizers:
                self._tokenizers[model_id] = {}
                
            self._models[model_id][version] = model
            self._tokenizers[model_id][version] = tokenizer
            
            # Update metadata
            load_time = time.time() - start_time
            metadata.load_time = load_time
            metadata.last_used = time.time()
            
            # Get model size
            model_size_bytes = sum(
                os.path.getsize(os.path.join(dirpath, filename)) 
                for dirpath, _, filenames in os.walk(local_path) 
                for filename in filenames
            ) if os.path.exists(local_path) else 0
            metadata.size_mb = model_size_bytes / (1024 * 1024)
            
            logger.info(f"Model {model_id} version {version} loaded in {load_time:.2f} seconds")
            
            # If the model doesn't have classes in metadata, try to extract them
            if not metadata.classes and hasattr(model.config, "id2label"):
                metadata.classes = list(model.config.id2label.values())
                
            # Update the version history with the latest metadata
            self._version_history[model_id].add_version(metadata)
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id} version {version}: {str(e)}")
            raise RuntimeError(f"Failed to load model {model_id} version {version}: {str(e)}")

    def get_model_metadata(self, model_id: Optional[str] = None, 
                          version: Optional[str] = None) -> ModelMetadata:
        """
        Get metadata for a model.
        
        Args:
            model_id: The model ID. If None, uses the default model.
            version: The version to get metadata for. If None, uses the active version.
            
        Returns:
            ModelMetadata object
            
        Raises:
            ValueError: If the model is not registered
        """
        model_id = model_id or settings.DEFAULT_MODEL
        
        if model_id not in self._version_history:
            raise ValueError(f"Model {model_id} is not registered")
        
        history = self._version_history[model_id]
        metadata = history.get_version(version)
        
        if not metadata:
            available_versions = [v["version"] for v in history.list_versions()]
            raise ValueError(f"Version {version} of model {model_id} not found. Available versions: {available_versions}")
            
        return metadata

    def list_available_models(self, include_versions: bool = False) -> List[Dict[str, Any]]:
        """
        List all available models with their metadata.
        
        Args:
            include_versions: Whether to include all versions in the output
            
        Returns:
            List of model metadata dictionaries
        """
        result = []
        
        for model_id, history in self._version_history.items():
            active_metadata = history.get_version()
            
            if not active_metadata:
                continue
                
            model_info = {
                "model_id": model_id,
                "active_version": history.active_version,
                "metadata": active_metadata.to_dict(),
            }
            
            if include_versions:
                model_info["versions"] = history.list_versions()
                
            result.append(model_info)
            
        return result

    def set_active_version(self, model_id: str, version: str) -> bool:
        """
        Set the active version for a model.
        
        Args:
            model_id: The model ID
            version: The version to set as active
            
        Returns:
            True if successful, False otherwise
        """
        if model_id not in self._version_history:
            return False
            
        return self._version_history[model_id].set_active_version(version)

    def add_model_version(self, model_id: str, version: str, 
                         performance_metrics: Optional[Dict[str, float]] = None,
                         description: Optional[str] = None) -> ModelMetadata:
        """
        Add a new version of an existing model.
        
        Args:
            model_id: The model ID
            version: The version identifier
            performance_metrics: Optional performance metrics to store
            description: Optional description of this version
            
        Returns:
            The metadata for the new version
            
        Raises:
            ValueError: If the model is not registered
        """
        if model_id not in self._version_history:
            raise ValueError(f"Model {model_id} is not registered. Register it first.")
            
        # Get the base metadata from the active version
        base_metadata = self._version_history[model_id].get_version()
        if not base_metadata:
            raise ValueError(f"No active version found for model {model_id}")
            
        # Create new metadata for this version
        new_metadata = ModelMetadata(
            model_id=model_id,
            version=version,
            task=base_metadata.task,
            classes=base_metadata.classes.copy() if base_metadata.classes else None,
            language=base_metadata.language,
            description=description or base_metadata.description
        )
        
        # Add performance metrics if provided
        if performance_metrics:
            new_metadata.performance_metrics = performance_metrics
            
        # Record parent version
        new_metadata.parent_version = base_metadata.version
        
        # Add to version history
        self._version_history[model_id].add_version(new_metadata)
        
        return new_metadata

    def unload_model(self, model_id: str, version: Optional[str] = None) -> bool:
        """
        Unload a model from memory to free resources.
        
        Args:
            model_id: The model ID to unload
            version: The version to unload. If None, unloads all versions.
            
        Returns:
            True if unloaded, False if not loaded
        """
        if model_id not in self._models:
            return False
            
        if version:
            # Unload specific version
            if version in self._models[model_id]:
                del self._models[model_id][version]
                if version in self._tokenizers[model_id]:
                    del self._tokenizers[model_id][version]
                logger.info(f"Unloaded model: {model_id} version: {version}")
                return True
            return False
        else:
            # Unload all versions
            del self._models[model_id]
            if model_id in self._tokenizers:
                del self._tokenizers[model_id]
            logger.info(f"Unloaded all versions of model: {model_id}")
            return True

    def unload_unused_models(self, threshold_seconds: int = 3600) -> int:
        """
        Unload models that haven't been used recently.
        
        Args:
            threshold_seconds: Time threshold in seconds
            
        Returns:
            Number of models unloaded
        """
        current_time = time.time()
        unloaded_count = 0
        
        for model_id in list(self._models.keys()):
            history = self._version_history.get(model_id)
            if not history:
                continue
                
            for version in list(self._models[model_id].keys()):
                metadata = history.get_version(version)
                if (metadata and metadata.last_used and 
                    current_time - metadata.last_used > threshold_seconds):
                    if self.unload_model(model_id, version):
                        unloaded_count += 1
        
        return unloaded_count


# Create a singleton instance to be imported by other modules
model_manager = ModelManager()
