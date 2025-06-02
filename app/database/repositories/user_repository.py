# filepath: /home/theo-gedin/sentimentflow-api/app/database/repositories/user_repository.py
"""
Repository for user sessions.
"""

import logging
from typing import Dict, Any, Optional, List

from app.database.repositories.base import BaseRepository
from app.models.database import UserSession
from pymongo import DESCENDING # Import DESCENDING

logger = logging.getLogger(__name__)

class UserSessionRepository(BaseRepository[UserSession]):
    """
    Repository for user session data with specialized query methods.
    """

    def __init__(self):
        super().__init__("user_sessions")

    def _to_document(self, model: UserSession) -> Dict[str, Any]:
        """Convert UserSession to MongoDB document."""
        return model.model_dump(by_alias=True)

    def _from_document(self, document: Dict[str, Any]) -> UserSession:
        """Convert MongoDB document to UserSession."""
        if "_id" in document and "id" not in document:
            document["id"] = str(document["_id"])
        document.setdefault("ip_address", None)  # Ensure ip_address is always present
        return UserSession(**document)

    async def get_by_session_id(self, session_id: str) -> Optional[UserSession]:
        """
        Get a user session by its session_id.

        Args:
            session_id: The session identifier.

        Returns:
            Optional[UserSession]: The user session if found, None otherwise.
        """
        try:
            collection = await self.get_collection()
            document = await collection.find_one({"session_id": session_id})
            if document:
                return self._from_document(document)
            return None
        except Exception as e:
            logger.error(f"Error fetching user session by session_id {session_id}: {e}")
            raise

    async def get_all_sessions(
        self,
        limit: Optional[int] = 100,
        skip: Optional[int] = 0,
        sort_by: str = "last_activity",
        sort_order: int = DESCENDING  # Use the imported DESCENDING
    ) -> List[UserSession]:
        """
        Get all user sessions with pagination and sorting.

        Args:
            limit: Maximum number of sessions to return.
            skip: Number of sessions to skip.
            sort_by: Field to sort by.
            sort_order: Sort order (DESCENDING or ASCENDING).

        Returns:
            List[UserSession]: List of user sessions.
        """
        return await self.get_many(
            limit=limit,
            skip=skip,
            sort=[(sort_by, sort_order)]
        )

    async def count_all_sessions(self) -> int:
        """
        Count all user sessions.

        Returns:
            int: Total number of user sessions.
        """
        try:
            collection = await self.get_collection()
            count = await collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error counting user sessions: {e}")
            raise

    async def get_or_create_session(
        self,
        session_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """
        Get an existing session or create a new one.
        
        Args:
            session_id: The session identifier
            user_agent: Optional user agent string
            ip_address: Optional IP address
            
        Returns:
            UserSession: The existing or newly created session
        """
        try:
            # Try to find existing session
            existing_session = await self.get_by_session_id(session_id)
            
            if existing_session:
                # Update last activity time
                await self.update_session_activity(
                    session_id=session_id,
                    model_name=None  # Will be updated later when we know the model
                )
                return existing_session
            else:
                # Create new session
                new_session = UserSession(
                    session_id=session_id,
                    user_agent=user_agent,
                    ip_address=ip_address
                )
                return await self.create(new_session)
                
        except Exception as e:
            logger.error(f"Error getting or creating session {session_id}: {e}")
            raise

    async def update_session_activity(
        self,
        session_id: str,
        model_name: Optional[str] = None
    ) -> None:
        """
        Update session activity timestamp and model usage.
        
        Args:
            session_id: The session identifier
            model_name: Optional model name to add to models_used list
        """
        try:
            from datetime import datetime, timezone
            
            update_data = {"last_activity": datetime.now(timezone.utc)}
            
            if model_name:
                # Add model to models_used if not already present
                session = await self.get_by_session_id(session_id)
                if session and model_name not in session.models_used:
                    update_data["models_used"] = session.models_used + [model_name]
                
                # Increment total analyses count
                if session:
                    update_data["total_analyses"] = session.total_analyses + 1
            
            collection = await self.get_collection()
            await collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
        except Exception as e:
            logger.error(f"Error updating session activity for {session_id}: {e}")
            raise

    async def initialize_indexes(self) -> None:
        """
        Create indexes for optimal query performance on user sessions.
        """
        try:
            # Index for fast session_id lookups
            await self.create_index([("session_id", 1)], unique=True)
            
            # Index for sorting by last_activity (e.g., for cleanup)
            await self.create_index([("last_activity", DESCENDING)])
            
            # Index for sorting by creation date
            await self.create_index([("created_at", DESCENDING)])
            
            logger.info(f"Indexes for '{self.collection_name}' created successfully.")
            
        except Exception as e:
            logger.error(f"Error creating indexes for '{self.collection_name}': {e}")
            # Optionally re-raise or handle as appropriate for your application
            raise

# Instantiate the repository
user_session_repository = UserSessionRepository()
