"""
Database initialization and migration script.

This module handles database setup, index creation, and any necessary
data migrations for the SentimentFlow API.
"""

import asyncio
import logging
from typing import List

from app.database.connection import database_manager
from app.database.repositories.sentiment_repository import sentiment_repository
from app.database.repositories.user_repository import user_session_repository

logger = logging.getLogger(__name__)


async def create_indexes() -> None:
    """
    Create all necessary database indexes for optimal performance.
    """
    logger.info("Creating database indexes...")
    
    try:
        # Initialize repository indexes
        await sentiment_repository.initialize_indexes()
        await user_session_repository.initialize_indexes()
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")
        raise


async def verify_collections() -> None:
    """
    Verify that all required collections exist and are accessible.
    """
    logger.info("Verifying database collections...")
    
    try:
        # Use the global, already connected database_manager
        db = database_manager.get_database() # Removed await
        
        # List all collections
        collections = await db.list_collection_names()
        logger.info(f"Existing collections: {collections}")
        
        # Check if our main collections exist (they'll be created on first insert)
        required_collections = ["sentiment_results", "user_sessions"]
        
        for collection_name in required_collections:
            collection = db[collection_name]
            # This will create the collection if it doesn't exist
            await collection.count_documents({})
            logger.info(f"Collection '{collection_name}' is ready")
        
        logger.info("Database collections verified successfully")
        
    except Exception as e:
        logger.error(f"Error verifying database collections: {e}")
        raise


async def run_migrations() -> None:
    """
    Run any necessary data migrations.
    Currently placeholder for future migrations.
    """
    logger.info("Running database migrations...")
    
    try:
        # Placeholder for future migrations
        # Example:
        # await migrate_v1_to_v2()
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error running database migrations: {e}")
        raise


async def initialize_database() -> None:
    """
    Complete database initialization process.
    """
    logger.info("Starting database initialization...")
    
    try:
        logger.info("Attempting database health check...")
        health_check_passed = False # Default to false
        try:
            # Ensure the database_manager instance is the one from app.database.connection
            health_check_passed = await database_manager.health_check()
            logger.info(f"Database health check result: {'PASSED' if health_check_passed else 'FAILED'}")
        except Exception as hc_exc:
            logger.error(f"Exception during database_manager.health_check() call: {type(hc_exc).__name__} - {hc_exc}", exc_info=True)
            # Treat an exception during health_check as a failure.
            raise ConnectionError(f"Health check itself failed with an exception: {hc_exc}") from hc_exc

        if not health_check_passed:
            # This log should appear if health_check_passed is False and no exception occurred during the call.
            logger.error("Database health check reported failure (returned False). Raising ConnectionError.")
            raise ConnectionError("Failed to connect to database (health check returned false)")

        # If health_check_passed, proceed with DB operations
        logger.info("Health check passed. Proceeding with getting database instance.")
        # db = await database_manager.get_database() # This was an error, get_database is sync
        db = database_manager.get_database() # Corrected: get_database is synchronous
        if db is None:
            logger.error("database_manager.get_database() returned None after successful health check.")
            raise ConnectionError("Failed to get database instance after health check.")
        
        logger.info(f"Successfully got database instance: {db.name}. Creating collections...")

        await verify_collections()
        await create_indexes()
        await run_migrations()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def cleanup_old_sessions(days: int = 30) -> int:
    """
    Clean up old inactive sessions.
    
    Args:
        days: Number of days after which sessions are considered old
        
    Returns:
        int: Number of sessions cleaned up
    """
    logger.info(f"Cleaning up sessions older than {days} days...")
    
    try:
        from datetime import datetime, timezone, timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get sessions to delete using the global, already connected database_manager
        db = database_manager.get_database() # Removed await
        sessions_collection = db["user_sessions"]
        
        # Count old sessions
        old_sessions_count = await sessions_collection.count_documents({
            "last_activity": {"$lt": cutoff_date}
        })
        
        if old_sessions_count == 0:
            logger.info("No old sessions found to clean up")
            return 0
        
        # Delete old sessions
        result = await sessions_collection.delete_many({
            "last_activity": {"$lt": cutoff_date}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old sessions")
        return result.deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up old sessions: {e}")
        return 0


if __name__ == "__main__":
    # Run initialization if script is called directly
    async def main():
        logging.basicConfig(level=logging.INFO)
        await initialize_database()
    
    asyncio.run(main())
