import pytest
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app as fastapi_app
from app.database.connection import database_manager
from app.database.repositories.sentiment_repository import sentiment_repository
from app.database.repositories.user_repository import user_session_repository


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Specify the anyio backend for the test session.
    FastAPI's TestClient uses anyio.
    """
    return "asyncio"


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient with test database isolation.
    TestClient handles the application lifespan (startup/shutdown events)
    and allows making requests directly to the app.
    """
    # Reset the database manager completely before each test to avoid event loop issues
    database_manager.client = None
    database_manager.database = None
    database_manager._connect_lock = None  # Reset the lock so it gets recreated with new event loop
    
    # Reset repository collection caches to ensure they get fresh connections
    sentiment_repository._collection = None
    user_session_repository._collection = None
    
    with TestClient(fastapi_app) as tc:
        yield tc
    
    # Clean up after each test
    database_manager.client = None
    database_manager.database = None
    database_manager._connect_lock = None
    sentiment_repository._collection = None
    user_session_repository._collection = None