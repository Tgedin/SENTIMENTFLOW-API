"""
Base repository class for MongoDB operations.

This module provides a generic base repository that can be extended
for specific document types with common CRUD operations.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, TypeVar, Generic
from bson import ObjectId

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.database.connection import get_database

logger = logging.getLogger(__name__)

# Type variable for the model class
ModelType = TypeVar('ModelType')


class BaseRepository(Generic[ModelType], ABC):
    """
    Abstract base repository providing common MongoDB operations.
    """
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """
        Get the MongoDB collection instance.
        
        Returns:
            AsyncIOMotorCollection: The collection instance
        """
        if self._collection is None:
            database = await get_database()
            self._collection = database[self.collection_name]
        return self._collection
    
    @abstractmethod
    def _to_document(self, model: ModelType) -> Dict[str, Any]:
        """
        Convert model instance to MongoDB document.
        
        Args:
            model: The model instance to convert
            
        Returns:
            Dict[str, Any]: MongoDB document
        """
        pass
    
    @abstractmethod
    def _from_document(self, document: Dict[str, Any]) -> ModelType:
        """
        Convert MongoDB document to model instance.
        
        Args:
            document: The MongoDB document
            
        Returns:
            ModelType: The model instance
        """
        pass
    
    async def create(self, model: ModelType) -> ModelType:
        """
        Create a new document in the collection.
        
        Args:
            model: The model instance to create
            
        Returns:
            ModelType: The created model instance
            
        Raises:
            DuplicateKeyError: If document with same ID already exists
        """
        try:
            collection = await self.get_collection()
            document = self._to_document(model)
            
            result = await collection.insert_one(document)
            
            if result.inserted_id:
                logger.debug(f"Created document with ID: {result.inserted_id}")
                return model
            else:
                raise RuntimeError("Failed to create document")
                
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error creating document: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error creating document: {e}")
            raise
    
    async def get_by_id(self, document_id: str) -> Optional[ModelType]:
        """
        Get a document by its ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            Optional[ModelType]: The model instance if found, None otherwise
        """
        try:
            collection = await self.get_collection()
            # If your MongoDB _id is a string (e.g., UUID), do not convert to ObjectId
            document = await collection.find_one({"_id": document_id})
            if document:
                return self._from_document(document)
            return None
        except PyMongoError as e:
            logger.error(f"MongoDB error getting document by ID {document_id}: {e}")
            raise

    async def delete(self, document_id: str) -> bool:
        """
        Delete a document by its ID.

        Args:
            document_id: The document ID to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            collection = await self.get_collection()
            result = await collection.delete_one({"_id": document_id})
            if result.deleted_count > 0:
                logger.debug(f"Deleted document with ID: {document_id}")
                return True
            logger.warning(f"Document with ID {document_id} not found for deletion.")
            return False
        except PyMongoError as e:
            logger.error(f"MongoDB error deleting document by ID {document_id}: {e}")
            raise

    async def get_many(
        self,
        filter_dict: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort: Optional[List[tuple]] = None
    ) -> List[ModelType]:
        """
        Get multiple documents with optional filtering, pagination, and sorting.
        
        Args:
            filter_dict: MongoDB filter criteria
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List[ModelType]: List of model instances
        """
        try:
            collection = await self.get_collection()
            
            # Build the query
            query = collection.find(filter_dict or {})
            
            # Apply sorting
            if sort:
                query = query.sort(sort)
            
            # Apply pagination
            if skip:
                query = query.skip(skip)
            if limit:
                query = query.limit(limit)
            
            # Execute query and convert documents
            documents = await query.to_list(length=limit)
            return [self._from_document(doc) for doc in documents]
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting multiple documents: {e}")
            raise
    
    async def update_by_id(
        self, 
        document_id: str, 
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a document by its ID.
        
        Args:
            document_id: The document ID
            update_data: Dictionary of fields to update
            
        Returns:
            bool: True if document was updated, False if not found
        """
        try:
            collection = await self.get_collection()
            update_data["updated_at"] = datetime.now(timezone.utc)
            result = await collection.update_one(
                {"_id": document_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"MongoDB error updating document {document_id}: {e}")
            raise

    async def delete_by_id(self, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            document_id: The document ID
            
        Returns:
            bool: True if document was deleted, False if not found
        """
        try:
            collection = await self.get_collection()
            result = await collection.delete_one({"_id": document_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"MongoDB error deleting document {document_id}: {e}")
            raise
    
    async def count(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching the filter.
        
        Args:
            filter_dict: MongoDB filter criteria
            
        Returns:
            int: Number of matching documents
        """
        try:
            collection = await self.get_collection()
            return await collection.count_documents(filter_dict or {})
            
        except PyMongoError as e:
            logger.error(f"MongoDB error counting documents: {e}")
            raise
    
    async def create_index(
        self, 
        keys: List[tuple], 
        unique: bool = False,
        background: bool = True
    ) -> None:
        """
        Create an index on the collection.
        
        Args:
            keys: List of (field, direction) tuples
            unique: Whether the index should enforce uniqueness
            background: Whether to create index in background
        """
        try:
            collection = await self.get_collection()
            await collection.create_index(
                keys, 
                unique=unique, 
                background=background
            )
            logger.info(f"Created index on {self.collection_name}: {keys}")
            
        except PyMongoError as e:
            logger.error(f"MongoDB error creating index: {e}")
            raise