"""
Integration tests for database operations.

These tests verify the direct interactions with the database via repository classes,
ensuring that CRUD operations and specialized queries work as expected.
"""
import pytest
import pytest_asyncio
import uuid
import logging
import asyncio
from datetime import datetime, timedelta, timezone

from app.models.database import SentimentResult, UserSession
from app.database.repositories.sentiment_repository import sentiment_repository
from app.database.repositories.user_repository import user_session_repository
from app.database.connection import database_manager

# Set up logger for debugging
logger = logging.getLogger(__name__)

# Fixture to ensure database is connected for tests
@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_connection():
    """Connect to database before each test and disconnect after."""
    logger.info("Setting up database connection for test")
    current_loop = asyncio.get_running_loop()
    try:
        await database_manager.connect(loop=current_loop)  # Pass the loop here
        # Verify connection was successful
        connected = await database_manager.health_check()
        if not connected:
            logger.error("Database health check failed after connect")
            raise RuntimeError("Database health check failed")
        logger.info("Database connected successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    finally:
        logger.info("Disconnecting database after test")
        await database_manager.disconnect()
        # Reset cached collections in repositories after disconnect
        sentiment_repository._collection = None
        user_session_repository._collection = None

@pytest.mark.asyncio
async def test_create_and_get_sentiment_result():
    """Test creating and retrieving a SentimentResult."""
    session_id = str(uuid.uuid4())
    test_result = SentimentResult(
        session_id=session_id,
        text="This is a test sentiment.",
        model_name="test-model",
        label="positive",
        confidence=0.99,
        scores={"positive": 0.99, "negative": 0.01},
        text_length=len("This is a test sentiment."),
        processing_time_ms=10.5,
        timestamp=datetime.now(timezone.utc),
        user_agent="pytest-test-agent",  # Added user_agent
        ip_address="127.0.0.1"  # Added ip_address
    )
    
    created_result = await sentiment_repository.create(test_result)
    assert created_result is not None
    assert created_result.id is not None
    assert created_result.session_id == session_id
    assert created_result.text == "This is a test sentiment."

    retrieved_result = await sentiment_repository.get_by_id(created_result.id)
    assert retrieved_result is not None
    assert retrieved_result.id == created_result.id
    assert retrieved_result.label == "positive"

    # Clean up
    await sentiment_repository.delete(created_result.id)

@pytest.mark.asyncio
async def test_create_and_get_user_session():
    """Test creating and retrieving a UserSession."""
    session_id = str(uuid.uuid4())
    user_session = UserSession(
        session_id=session_id,
        user_agent="pytest-test-agent",
        ip_address="127.0.0.1"
    )

    created_session = await user_session_repository.create(user_session)
    assert created_session is not None
    assert created_session.session_id == session_id
    assert created_session.user_agent == "pytest-test-agent"

    retrieved_session = await user_session_repository.get_by_session_id(session_id)
    assert retrieved_session is not None
    assert retrieved_session.session_id == created_session.session_id
    assert retrieved_session.ip_address == "127.0.0.1"
    
    # Clean up
    await user_session_repository.delete(retrieved_session.id)


@pytest.mark.asyncio
async def test_get_sentiment_results_by_session_id():
    """Test retrieving multiple sentiment results for a specific session ID."""
    session_id = str(uuid.uuid4())
    
    result1 = SentimentResult(
        session_id=session_id, text="First test", model_name="test-model",
        label="positive", confidence=0.8, scores={"positive": 0.8, "negative": 0.2},
        text_length=10, processing_time_ms=5.0,
        user_agent="pytest-test-agent", ip_address="127.0.0.1"
    )
    result2 = SentimentResult(
        session_id=session_id, text="Second test", model_name="test-model",
        label="negative", confidence=0.9, scores={"negative": 0.9, "positive": 0.1},
        text_length=11, processing_time_ms=6.0,
        user_agent="pytest-test-agent", ip_address="127.0.0.1"
    )
    
    await sentiment_repository.create(result1)
    await sentiment_repository.create(result2)
    
    results = await sentiment_repository.get_by_session_id(session_id, limit=5)
    assert len(results) == 2
    assert all(r.session_id == session_id for r in results)
    
    # Clean up
    for r in results:
        await sentiment_repository.delete(r.id)

@pytest.mark.asyncio
async def test_get_recent_sentiment_results():
    """Test retrieving recent sentiment results."""
    session_id = str(uuid.uuid4())
    old_timestamp = datetime.now(timezone.utc) - timedelta(days=2)
    
    result_recent = SentimentResult(
        session_id=session_id, text="Recent test", model_name="test-model",
        label="neutral", confidence=0.7, scores={"neutral": 0.7},
        text_length=11, processing_time_ms=7.0, timestamp=datetime.now(timezone.utc),
        user_agent="pytest-test-agent", ip_address="127.0.0.1"
    )
    result_old = SentimentResult(
        session_id=session_id, text="Old test", model_name="test-model",
        label="positive", confidence=0.6, scores={"positive": 0.6},
        text_length=8, processing_time_ms=4.0, timestamp=old_timestamp,
        user_agent="pytest-test-agent", ip_address="127.0.0.1"  # Added missing arguments
    )
    
    await sentiment_repository.create(result_recent)
    await sentiment_repository.create(result_old)
    
    # Get results from last 24 hours
    recent_results = await sentiment_repository.get_recent_results(hours=24, limit=5)
    assert len(recent_results) >= 1
    assert any(r.text == "Recent test" for r in recent_results)
    assert not any(r.text == "Old test" for r in recent_results)
    
    # Clean up
    await sentiment_repository.delete(result_recent.id)
    await sentiment_repository.delete(result_old.id)

# Add more tests for UserSessionRepository updates and other specialized queries as needed.
