"""
Sentiment analysis API endpoints.

This module provides the main sentiment analysis functionality with
database storage for results and session tracking.
"""

import logging
import time
import uuid
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse

from datetime import datetime, timezone

from app.models.requests import SentimentAnalysisRequest, BatchSentimentRequest
from app.models.responses import (
    SentimentAnalysisResponse, 
    BatchSentimentResponse,
    HealthResponse,
    SentimentResult as SentimentResultResponse,
    SentimentScore
)
from app.models.database import SentimentResult as SentimentResultDB
from app.database.repositories.sentiment_repository import sentiment_repository, user_session_repository
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def get_session_id(request: Request) -> str:
    """
    Extract or generate a session ID for the request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Session ID (from header or newly generated)
    """
    # Try to get session ID from header
    session_id = request.headers.get("X-Session-ID")
    
    if not session_id:
        # Generate a new session ID
        session_id = str(uuid.uuid4())
        logger.debug(f"Generated new session ID: {session_id}")
    
    return session_id


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract client information from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        tuple: (user_agent, ip_address)
    """
    user_agent = request.headers.get("User-Agent")
    
    # Get IP address, considering proxy headers
    ip_address = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
        request.headers.get("X-Real-IP") or
        request.client.host if request.client else None
    )
    
    return user_agent, ip_address


@router.post("/analyze")
async def analyze_sentiment(
    request_data: SentimentAnalysisRequest,
    request: Request,
    session_id: str = Depends(get_session_id)
) -> SentimentAnalysisResponse:
    """
    Analyze sentiment of a single text input.
    
    Args:
        request_data: The sentiment analysis request
        request: FastAPI request object
        session_id: Session identifier
        
    Returns:
        SentimentAnalysisResponse: Analysis results with confidence scores
    """
    start_time = time.time()
    
    try:
        # Get client information
        user_agent, ip_address = get_client_info(request)
        
        # Create or update user session
        await user_session_repository.get_or_create_session(
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer(
            model_name=request_data.model_name or settings.DEFAULT_MODEL
        )
        
        # Perform sentiment analysis
        result = await analyzer.analyze_text(
            text=request_data.text,
            model_name=request_data.model_name
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Store result in database
        try:
            sentiment_result = SentimentResultDB(
                session_id=session_id,
                text=request_data.text,
                model_name=result.get("model", analyzer.model_name),
                label=result["sentiment"],
                confidence=result["confidence"],
                scores=result.get("scores", {}),
                text_length=len(request_data.text),
                processing_time_ms=processing_time_ms,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            await sentiment_repository.create(sentiment_result)
            
            # Update session activity
            await user_session_repository.update_session_activity(
                session_id=session_id,
                model_name=analyzer.model_name
            )
            
            logger.info(f"Stored sentiment result for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store sentiment result: {e}")
            # Continue without failing the request
        
        # Prepare response
        sentiment_result_response = SentimentResultResponse(
            text=request_data.text,
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            scores=[
                SentimentScore(label=k, score=v) 
                for k, v in result.get("scores", {}).items()
            ],
            model_name=analyzer.model_name,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now(timezone.utc),
            raw_output=result.get("raw_output") if request_data.include_raw_output else None
        )
        
        response = SentimentAnalysisResponse(
            success=True,
            result=sentiment_result_response,
            session_id=session_id
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze sentiment: {str(e)}"
        )


@router.post("/analyze/batch")
async def analyze_sentiment_batch(
    request_data: BatchSentimentRequest,
    request: Request,
    session_id: str = Depends(get_session_id)
) -> BatchSentimentResponse:
    """
    Analyze sentiment of multiple texts in batch.
    
    Args:
        request_data: The batch sentiment analysis request
        request: FastAPI request object
        session_id: Session identifier
        
    Returns:
        BatchSentimentResponse: Analysis results for all texts
    """
    start_time = time.time()
    
    try:
        # Validate batch size
        if len(request_data.texts) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum of {settings.MAX_BATCH_SIZE}"
            )
        
        # Get client information
        user_agent, ip_address = get_client_info(request)
        
        # Create or update user session
        await user_session_repository.get_or_create_session(
            session_id=session_id,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer(
            model_name=request_data.model_name or settings.DEFAULT_MODEL
        )
        
        # Perform batch sentiment analysis
        results = await analyzer.analyze_texts(
            texts=request_data.texts,
            model_name=request_data.model_name,
            batch_size=request_data.batch_size or settings.BATCH_SIZE
        )
        
        # Calculate total processing time
        total_processing_time_ms = (time.time() - start_time) * 1000
        
        # Store results in database
        stored_results = []
        for i, (text, result) in enumerate(zip(request_data.texts, results)):
            try:
                if result.get("success", True):  # Only store successful results
                    sentiment_result = SentimentResultDB(
                        session_id=session_id,
                        text=text,
                        model_name=result.get("model", analyzer.model_name),
                        label=result["sentiment"],
                        confidence=result["confidence"],
                        scores=result.get("scores", {}),
                        text_length=len(text),
                        processing_time_ms=total_processing_time_ms / len(request_data.texts),  # Approximate per-text time
                        user_agent=user_agent,
                        ip_address=ip_address
                    )
                    
                    stored_result = await sentiment_repository.create(sentiment_result)
                    stored_results.append(stored_result)
                    
            except Exception as e:
                logger.error(f"Failed to store batch result {i}: {e}")
                # Continue with other results
        
        # Update session activity
        try:
            await user_session_repository.update_session_activity(
                session_id=session_id,
                model_name=analyzer.model_name
            )
        except Exception as e:
            logger.error(f"Failed to update session activity: {e}")
        
        # Prepare response
        analysis_results = []
        for text, result in zip(request_data.texts, results):
            if result.get("success", True):
                sentiment_result = SentimentResultResponse(
                    text=text,
                    sentiment=result["sentiment"],
                    confidence=result["confidence"],
                    scores=[
                        SentimentScore(label=k, score=v) 
                        for k, v in result.get("scores", {}).items()
                    ],
                    model_name=analyzer.model_name,
                    processing_time_ms=total_processing_time_ms / len(request_data.texts),
                    timestamp=datetime.now(timezone.utc),
                    raw_output=result.get("raw_output") if request_data.include_raw_output else None
                )
                analysis_results.append(sentiment_result)
        
        response = BatchSentimentResponse(
            success=True,
            results=analysis_results,
            session_id=session_id,
            total_texts=len(request_data.texts),
            processing_time_ms=total_processing_time_ms,
            failed_count=len(request_data.texts) - len(analysis_results)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze batch sentiment: {str(e)}"
        )


@router.get("/models")
async def list_available_models() -> Dict[str, Any]:
    """
    Get list of available sentiment analysis models.
    
    Returns:
        Dict containing available models and their information
    """
    try:
        analyzer = SentimentAnalyzer()
        models = await analyzer.get_available_models()
        
        return {
            "models": models,
            "default_model": settings.DEFAULT_MODEL,
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve available models"
        )


@router.get("/health")
async def sentiment_health_check() -> HealthResponse:
    """
    Health check endpoint for sentiment analysis service.
    
    Returns:
        HealthResponse: Service health status
    """
    health_start_time = time.time()
    
    try:
        # Test basic model loading
        analyzer = SentimentAnalyzer()
        await analyzer.load_model()
        
        # Test database connectivity
        db_healthy = False
        try:
            # Try to get a count from the database
            recent_results = await sentiment_repository.get_recent_results(hours=1, limit=1)
            db_healthy = True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version=settings.API_VERSION,
            uptime_seconds=time.time() - health_start_time,
            models_loaded=[analyzer.model_name] if analyzer.pipeline is not None else [],
            database_connected=db_healthy
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )