"""
Database Service for MongoDB Integration
Minimal implementation to make TDD tests pass (GREEN phase)
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    MongoDB database service - minimal implementation for TDD
    """
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URI", 
            "mongodb://localhost:27017/neona_chat_db"
        )
        self.client = None
        self.db = None
        self._connected = False
        
    async def connect(self):
        """
        Connect to MongoDB - minimal implementation to pass tests
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.client = AsyncIOMotorClient(self.connection_string, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            await self.client.admin.command('ping')
            
            # Set database
            db_name = self.connection_string.split('/')[-1] or "neona_chat_db"
            self.db = self.client[db_name]
            
            self._connected = True
            logger.info(f"✅ Connected to MongoDB database: {db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected MongoDB error: {str(e)}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to MongoDB
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected
    
    async def get_database_info(self) -> dict:
        """
        Get database information - minimal implementation for tests
        
        Returns:
            dict: Database information
        """
        if not self.is_connected():
            raise Exception("Not connected to MongoDB")
            
        try:
            # Extract database name from connection string
            db_name = self.connection_string.split('/')[-1] or "neona_chat_db"
            
            # Get basic database stats
            stats = await self.db.command("dbstats")
            
            return {
                "name": db_name,
                "collections": stats.get("collections", 0),
                "dataSize": stats.get("dataSize", 0),
                "indexSize": stats.get("indexSize", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get database info: {str(e)}")
            raise
    
    async def close(self):
        """
        Close MongoDB connection
        """
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔒 MongoDB connection closed")
    
    # Collection access methods for future use
    @property
    def conversations(self):
        """Access to conversations collection"""
        if self.db is None:
            raise Exception("Not connected to database")
        return self.db.conversations
    
    @property
    def personas(self):
        """Access to personas collection"""
        if self.db is None:
            raise Exception("Not connected to database")
        return self.db.personas
    
    @property 
    def knowledge(self):
        """Access to knowledge collection"""
        if self.db is None:
            raise Exception("Not connected to database")
        return self.db.knowledge
    
    @property
    def users(self):
        """Access to users collection"""
        if self.db is None:
            raise Exception("Not connected to database")
        return self.db.users
    
    @property
    def characters(self):
        """Access to characters collection"""
        if self.db is None:
            raise Exception("Not connected to database")
        return self.db.characters