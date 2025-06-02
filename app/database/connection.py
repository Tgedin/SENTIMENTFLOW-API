"""
Database connection management for MongoDB.

This module provides async MongoDB connection handling using Motor,
the async driver for MongoDB in Python.
"""

import logging
from typing import Optional
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages MongoDB connections and provides database access.
    """
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connect_lock: Optional[asyncio.Lock] = None  # Will be created lazily
    
    def _get_or_create_lock(self) -> asyncio.Lock:
        """Get the connect lock, creating it if it doesn't exist."""
        if self._connect_lock is None:
            self._connect_lock = asyncio.Lock()
        return self._connect_lock
    
    async def connect(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Connect to MongoDB database.
        Optionally accepts an event loop.
        """
        async with self._get_or_create_lock():
            try:
                # Check if already connected and healthy
                if self.client is not None and self.database is not None:
                    try:
                        await self.client.admin.command('ping')
                        logger.info("Already connected to MongoDB and connection is healthy.")
                        return
                    except ConnectionFailure:
                        logger.warning("Existing MongoDB connection is unhealthy. Reconnecting.")
                        # await self.disconnect() # Disconnect before reconnecting - disconnect is called implicitly by closing client
                        if self.client:
                            self.client.close()
                        self.client = None
                        self.database = None
                    except Exception as e: # Catch other potential errors during ping
                        logger.warning(f"Error checking existing MongoDB connection health: {e}. Attempting to reconnect...")
                        if self.client:
                            self.client.close()
                        self.client = None
                        self.database = None

                mongodb_url = settings.MONGODB_URL or "mongodb://localhost:27017"
                db_name = settings.MONGODB_DB_NAME or "sentimentflow" # Corrected attribute
                
                logger.info(f"Attempting to connect to MongoDB at {mongodb_url} and database {db_name}")
                
                # Don't bind to a specific event loop - let motor figure it out at runtime
                # This prevents "Event loop is closed" errors in testing environments
                self.client = AsyncIOMotorClient(
                    mongodb_url,
                    serverSelectionTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                    uuidRepresentation='standard'
                    # Removed io_loop parameter to let motor handle event loop automatically
                )
                
                # Verify connection using 'ismaster' as in user's active file context
                await self.client.admin.command('ismaster') 
                logger.info("Successfully established new connection to MongoDB server")

                self.database = self.client.get_database(db_name) # Use get_database as in user's active file
                logger.info(f"Successfully connected to MongoDB database: {db_name}")

            except (ConnectionFailure, ServerSelectionTimeoutError) as e: # Combined specific exceptions
                logger.error(f"MongoDB connection failed: {e}")
                if self.client:
                    self.client.close()
                self.client = None
                self.database = None
                raise  # Re-raise the exception to be handled by the caller
            except Exception as e:
                logger.error(f"An unexpected error occurred during MongoDB connection: {e}")
                if self.client:
                    self.client.close()
                self.client = None
                self.database = None
                raise # Re-raise the exception

    async def disconnect(self) -> None:
        """
        Disconnect from MongoDB database.
        """
        async with self._get_or_create_lock():
            if self.client:
                self.client.close()
                logger.info("Disconnected from MongoDB")
            self.client = None
            self.database = None

    def get_database(self) -> AsyncIOMotorDatabase:
        """
        Get the database instance.
        
        Returns:
            AsyncIOMotorDatabase: The database instance
            
        Raises:
            RuntimeError: If not connected to database
        """
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database
    
    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # Simple ping to check connection
            await self.client.admin.command('ping')
            return True
            
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False


# Global database manager instance
database_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get database instance.
    
    Returns:
        AsyncIOMotorDatabase: The database instance
    """
    return database_manager.get_database()