"""
Repository for sentiment analysis results.

This module provides data access methods specifically for sentiment
analysis results, including historical queries and analytics.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from pymongo import DESCENDING

from app.database.repositories.base import BaseRepository
from app.models.database import SentimentResult
from app.database.repositories.user_repository import user_session_repository

logger = logging.getLogger(__name__)


class SentimentRepository(BaseRepository[SentimentResult]):
    """
    Repository for sentiment analysis results with specialized query methods.
    """
    
    def __init__(self):
        super().__init__("sentiment_results")
    
    def _to_document(self, model: SentimentResult) -> Dict[str, Any]:
        """Convert SentimentResult to MongoDB document."""
        return model.model_dump(by_alias=True)
    
    def _from_document(self, document: Dict[str, Any]) -> SentimentResult:
        """Convert MongoDB document to SentimentResult."""
        return SentimentResult(**document)
    
    async def get_by_session_id(
        self, 
        session_id: str,
        limit: Optional[int] = 100,
        skip: Optional[int] = None
    ) -> List[SentimentResult]:
        """
        Get sentiment results for a specific session.
        
        Args:
            session_id: The session identifier
            limit: Maximum number of results to return
            skip: Number of results to skip
            
        Returns:
            List[SentimentResult]: List of sentiment results ordered by timestamp (newest first)
        """
        return await self.get_many(
            filter_dict={"session_id": session_id},
            limit=limit,
            skip=skip,
            sort=[("timestamp", DESCENDING)]
        )
    
    async def get_recent_results(
        self,
        hours: int = 24,
        limit: Optional[int] = 100
    ) -> List[SentimentResult]:
        """
        Get recent sentiment analysis results.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of results to return
            
        Returns:
            List[SentimentResult]: Recent sentiment results
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            collection = await self.get_collection()
            
            # Debug log the cutoff time
            logger.debug(f"Looking for results newer than: {cutoff_time.isoformat()}")
            
            # Query with explicit timestamp comparison
            query = {"timestamp": {"$gte": cutoff_time}}
            
            # Execute query
            cursor = collection.find(query)
            cursor = cursor.sort("timestamp", DESCENDING)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            # Debug log the number of found documents
            logger.debug(f"Found {len(documents)} recent results")
            if documents:
                logger.debug(f"First result timestamp: {documents[0].get('timestamp')}")
                
            # Transform documents to models
            results = []
            for doc in documents:
                try:
                    results.append(self._from_document(doc))
                except Exception as e:
                    logger.error(f"Error converting document to model: {e}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error getting recent results: {e}", exc_info=True)
            return []
    
    async def get_by_model_name(
        self,
        model_name: str,
        limit: Optional[int] = 100
    ) -> List[SentimentResult]:
        """
        Get sentiment results for a specific model.
        
        Args:
            model_name: Name of the ML model
            limit: Maximum number of results to return
            
        Returns:
            List[SentimentResult]: Results from the specified model
        """
        return await self.get_many(
            filter_dict={"model_name": model_name},
            limit=limit,
            sort=[("timestamp", DESCENDING)]
        )
    
    async def get_sentiment_distribution(
        self,
        session_id: Optional[str] = None,
        hours: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Get distribution of sentiment labels.
        
        Args:
            session_id: Optional session filter
            hours: Optional time filter (hours back from now)
            
        Returns:
            Dict[str, int]: Count of each sentiment label
        """
        try:
            collection = await self.get_collection()
            
            # Build match stage for aggregation
            match_stage = {}
            if session_id:
                match_stage["session_id"] = session_id
            if hours:
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
                match_stage["timestamp"] = {"$gte": cutoff_time}
            
            # Aggregation pipeline
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {"$group": {"_id": "$label", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ])
            
            # Execute aggregation
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Convert to dictionary
            return {result["_id"]: result["count"] for result in results}
            
        except Exception as e:
            logger.error(f"Error getting sentiment distribution: {e}")
            return {}
    
    async def get_model_performance_stats(
        self,
        model_name: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get performance statistics for a specific model.
        
        Args:
            model_name: Name of the ML model
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, Any]: Performance statistics
        """
        try:
            collection = await self.get_collection()
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            match_stage = {
                "model_name": model_name,
                "timestamp": {"$gte": cutoff_time}
            }
            
            # Aggregation pipeline for statistics
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "avg_processing_time": {"$avg": "$processing_time_ms"},
                    "min_processing_time": {"$min": "$processing_time_ms"},
                    "max_processing_time": {"$max": "$processing_time_ms"},
                    "avg_confidence": {"$avg": "$confidence"},
                    "avg_text_length": {"$avg": "$text_length"}
                }}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                del stats["_id"]  # Remove the grouping key
                # Keep original field name to match test expectations
                return stats
            else:
                return {
                    "total_requests": 0,  # Match test expectations
                    "avg_processing_time": 0,
                    "min_processing_time": 0,
                    "max_processing_time": 0,
                    "avg_confidence": 0,
                    "avg_text_length": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting model performance stats: {e}")
            return {}
    
    async def get_confidence_distribution(
        self,
        model_name: Optional[str] = None,
        bins: int = 10
    ) -> Dict[str, int]:
        """
        Get distribution of confidence scores in bins.
        
        Args:
            model_name: Optional model filter
            bins: Number of confidence bins (0.0-1.0 divided into bins)
            
        Returns:
            Dict[str, int]: Count of results in each confidence range
        """
        try:
            collection = await self.get_collection()
            
            # Build match stage
            match_stage = {}
            if model_name:
                match_stage["model_name"] = model_name
            
            # Create confidence range buckets
            bin_size = 1.0 / bins
            bucket_boundaries = [i * bin_size for i in range(bins + 1)]
            
            # Aggregation pipeline
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$bucket": {
                        "groupBy": "$confidence",
                        "boundaries": bucket_boundaries,
                        "default": "other",
                        "output": {"count": {"$sum": 1}}
                    }
                }
            ])
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Convert to readable format
            distribution = {}
            for result in results:
                if result["_id"] == "other":
                    distribution["other"] = result["count"]
                else:
                    lower = result["_id"]
                    upper = min(lower + bin_size, 1.0)
                    range_key = f"{lower:.1f}-{upper:.1f}"
                    distribution[range_key] = result["count"]
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting confidence distribution: {e}")
            return {}

    async def get_confidence_overview(self) -> Dict[str, Any]:
        """
        Get overview statistics for confidence scores across all analyses.
        
        Returns:
            Dict[str, Any]: Confidence overview statistics
        """
        try:
            collection = await self.get_collection()
            
            # Aggregation pipeline for confidence statistics
            pipeline = [
                {"$group": {
                    "_id": None,
                    "total_analyses_considered": {"$sum": 1},
                    "average_confidence": {"$avg": "$confidence"},
                    "min_confidence": {"$min": "$confidence"},
                    "max_confidence": {"$max": "$confidence"},
                    "std_dev_confidence": {"$stdDevPop": "$confidence"}
                }}
            ]
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            
            if results:
                stats = results[0]
                del stats["_id"]  # Remove the grouping key
                
                # Round values for better readability
                stats["average_confidence"] = round(stats["average_confidence"], 4)
                stats["min_confidence"] = round(stats["min_confidence"], 4)
                stats["max_confidence"] = round(stats["max_confidence"], 4)
                stats["std_dev_confidence"] = round(stats["std_dev_confidence"], 4)
                
                # Get confidence distribution for overview
                distribution = await self.get_confidence_distribution(bins=5)
                stats["confidence_distribution"] = distribution
                
                return stats
            else:
                return {
                    "total_analyses_considered": 0,
                    "average_confidence": 0,
                    "min_confidence": 0,
                    "max_confidence": 0,
                    "std_dev_confidence": 0,
                    "confidence_distribution": {}
                }
                
        except Exception as e:
            logger.error(f"Error getting confidence overview: {e}")
            return {
                "total_analyses_considered": 0,
                "average_confidence": 0,
                "min_confidence": 0,
                "max_confidence": 0,
                "std_dev_confidence": 0,
                "confidence_distribution": {}
            }
    
    async def initialize_indexes(self) -> None:
        """
        Create indexes for optimal query performance.
        """
        try:
            # Index for session-based queries
            await self.create_index([("session_id", 1), ("timestamp", -1)])
            
            # Index for time-based queries
            await self.create_index([("timestamp", -1)])
            
            # Index for model-based queries
            await self.create_index([("model_name", 1), ("timestamp", -1)])
            
            # Index for sentiment label analysis
            await self.create_index([("label", 1)])
            
            # Compound index for analytics
            await self.create_index([
                ("model_name", 1), 
                ("label", 1), 
                ("timestamp", -1)
            ])
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise


# Repository instances
sentiment_repository = SentimentRepository()
