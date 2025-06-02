"""
History API endpoints for retrieving sentiment analysis data.

This module provides endpoints for accessing historical sentiment analysis
results, session data, and analytics.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.database.repositories.sentiment_repository import sentiment_repository, user_session_repository
from app.models.database import SentimentResult, UserSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/results/{session_id}")
async def get_session_history(
    session_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of results to return"),
    skip: int = Query(default=0, ge=0, description="Number of results to skip for pagination")
) -> Dict[str, Any]:
    """
    Get sentiment analysis history for a specific session.
    
    Args:
        session_id: The session identifier
        limit: Maximum number of results to return (1-1000)
        skip: Number of results to skip for pagination
        
    Returns:
        Dict containing the results and pagination info
    """
    try:
        # Get sentiment results for the session
        results = await sentiment_repository.get_by_session_id(
            session_id=session_id,
            limit=limit,
            skip=skip
        )
        
        # Convert to response format
        response_results = []
        for result in results:
            response_results.append({
                "id": result.id,
                "text": result.text,
                "model_name": result.model_name,
                "label": result.label,
                "confidence": result.confidence,
                "scores": result.scores,
                "text_length": result.text_length,
                "processing_time_ms": result.processing_time_ms,
                "timestamp": result.timestamp.isoformat()
            })
        
        # Get session info
        sessions = await user_session_repository.get_many(
            filter_dict={"session_id": session_id},
            limit=1
        )
        
        session_info = None
        if sessions:
            session = sessions[0]
            session_info = {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "total_analyses": session.total_analyses,
                "models_used": session.models_used
            }
        
        return {
            "session_id": session_id,
            "session_info": session_info,
            "results": response_results,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "count": len(response_results),
                "has_more": len(response_results) == limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve session history"
        )


@router.get("/results/recent")
async def get_recent_results(
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to look back (max 1 week)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of results to return")
) -> Dict[str, Any]:
    """
    Get recent sentiment analysis results across all sessions.
    
    Args:
        hours: Number of hours to look back (1-168 hours, max 1 week)
        limit: Maximum number of results to return
        
    Returns:
        Dict containing recent results
    """
    try:
        results = await sentiment_repository.get_recent_results(
            hours=hours,
            limit=limit
        )
        
        # Convert to response format
        response_results = []
        for result in results:
            response_results.append({
                "id": result.id,
                "session_id": result.session_id,
                "text": result.text[:100] + "..." if len(result.text) > 100 else result.text,  # Truncate for overview
                "model_name": result.model_name,
                "label": result.label,
                "confidence": result.confidence,
                "processing_time_ms": result.processing_time_ms,
                "timestamp": result.timestamp.isoformat()
            })
        
        return {
            "hours_back": hours,
            "results": response_results,
            "count": len(response_results)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving recent results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recent results"
        )


@router.get("/analytics/sentiment-distribution")
async def get_sentiment_distribution(
    session_id: Optional[str] = Query(None, description="Optional session ID filter"),
    hours: Optional[int] = Query(None, ge=1, le=168, description="Optional time filter in hours")
) -> Dict[str, Any]:
    """
    Get distribution of sentiment labels.
    
    Args:
        session_id: Optional session ID to filter by
        hours: Optional number of hours to look back
        
    Returns:
        Dict containing sentiment label distribution
    """
    try:
        distribution = await sentiment_repository.get_sentiment_distribution(
            session_id=session_id,
            hours=hours
        )
        
        total_count = sum(distribution.values())
        
        # Calculate percentages
        percentages = {}
        if total_count > 0:
            percentages = {
                label: round((count / total_count) * 100, 1)
                for label, count in distribution.items()
            }
        
        return {
            "distribution": distribution,
            "percentages": percentages,
            "total_count": total_count,
            "filters": {
                "session_id": session_id,
                "hours_back": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving sentiment distribution: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve sentiment distribution"
        )


@router.get("/analytics/model-performance/{model_name}")
async def get_model_performance(
    model_name: str,
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to analyze")
) -> Dict[str, Any]:
    """
    Get performance statistics for a specific model.
    
    Args:
        model_name: Name of the ML model to analyze
        hours: Number of hours to look back for analysis
        
    Returns:
        Dict containing model performance statistics
    """
    try:
        stats = await sentiment_repository.get_model_performance_stats(
            model_name=model_name,
            hours=hours
        )
        
        return {
            "model_name": model_name,
            "hours_analyzed": hours,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model performance: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model performance statistics"
        )


@router.get("/analytics/confidence-distribution")
async def get_confidence_distribution(
    model_name: Optional[str] = Query(None, description="Optional model name filter"),
    bins: int = Query(default=10, ge=5, le=20, description="Number of confidence bins")
) -> Dict[str, Any]:
    """
    Get distribution of confidence scores.
    
    Args:
        model_name: Optional model name to filter by
        bins: Number of confidence bins (5-20)
        
    Returns:
        Dict containing confidence score distribution
    """
    try:
        distribution = await sentiment_repository.get_confidence_distribution(
            model_name=model_name,
            bins=bins
        )
        
        total_count = sum(distribution.values())
        
        return {
            "distribution": distribution,
            "total_count": total_count,
            "bins": bins,
            "model_name": model_name
        }
        
    except Exception as e:
        logger.error(f"Error retrieving confidence distribution: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve confidence distribution"
        )


@router.get("/analytics/confidence-overview")
async def get_confidence_overview() -> Dict[str, Any]:
    """
    Get overview of confidence statistics across all models.
    
    Returns:
        Dict containing confidence overview statistics
    """
    try:
        # Get confidence overview stats from repository
        overview = await sentiment_repository.get_confidence_overview()
        
        return overview
        
    except Exception as e:
        logger.error(f"Error retrieving confidence overview: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve confidence overview"
        )


@router.get("/sessions")
async def get_active_sessions(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of sessions to return")
) -> Dict[str, Any]:
    """
    Get list of active sessions with basic statistics.
    
    Args:
        limit: Maximum number of sessions to return
        
    Returns:
        Dict containing active sessions list
    """
    try:
        # Get recent sessions (active in last 24 hours)
        from datetime import datetime, timezone, timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        sessions = await user_session_repository.get_many(
            filter_dict={"last_activity": {"$gte": cutoff_time}},
            limit=limit,
            sort=[("last_activity", -1)]
        )
        
        # Convert to response format
        session_list = []
        for session in sessions:
            session_list.append({
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "total_analyses": session.total_analyses,
                "models_used": session.models_used,
                "user_agent": session.user_agent,
                "ip_address": session.ip_address
            })
        
        return {
            "sessions": session_list,
            "count": len(session_list),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error retrieving active sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve active sessions"
        )


@router.get("/models/usage")
async def get_model_usage(
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours to analyze")
) -> Dict[str, Any]:
    """
    Get usage statistics for all models.
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        Dict containing model usage statistics
    """
    try:
        from datetime import datetime, timezone, timedelta
        
        # Get recent results
        results = await sentiment_repository.get_recent_results(
            hours=hours,
            limit=10000  # High limit to get comprehensive data
        )
        
        # Calculate model usage statistics
        model_stats = {}
        
        for result in results:
            model_name = result.model_name
            if model_name not in model_stats:
                model_stats[model_name] = {
                    "total_requests": 0,
                    "avg_confidence": 0,
                    "avg_processing_time": 0,
                    "sentiment_counts": {}
                }
            
            stats = model_stats[model_name]
            stats["total_requests"] += 1
            
            # Update averages (simple running average)
            n = stats["total_requests"]
            stats["avg_confidence"] = ((stats["avg_confidence"] * (n-1)) + result.confidence) / n
            stats["avg_processing_time"] = ((stats["avg_processing_time"] * (n-1)) + result.processing_time_ms) / n
            
            # Count sentiment labels
            label = result.label
            if label not in stats["sentiment_counts"]:
                stats["sentiment_counts"][label] = 0
            stats["sentiment_counts"][label] += 1
        
        # Round averages for better readability
        for model_name, stats in model_stats.items():
            stats["avg_confidence"] = round(stats["avg_confidence"], 3)
            stats["avg_processing_time"] = round(stats["avg_processing_time"], 2)
        
        return {
            "hours_analyzed": hours,
            "models": model_stats,
            "total_models": len(model_stats)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving model usage: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model usage statistics"
        )