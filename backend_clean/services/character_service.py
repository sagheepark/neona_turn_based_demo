"""
Character Service for MongoDB Character Management
Minimal implementation to make TDD tests pass (GREEN phase)
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CharacterService:
    """
    Service for managing characters in MongoDB - minimal TDD implementation
    """
    
    def __init__(self, database_service):
        self.database_service = database_service
        
    async def get_character_with_knowledge(self, character_id: str) -> Optional[Dict]:
        """
        Get character with their knowledge base - minimal implementation for tests
        
        Args:
            character_id: Character ID to retrieve
            
        Returns:
            Dict with character and knowledge_items, or None if not found
        """
        try:
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            # Get character
            character = await self.database_service.characters.find_one({"character_id": character_id})
            if not character:
                return None
            
            # Get knowledge items for this character
            knowledge_items = await self.database_service.knowledge.find(
                {"character_id": character_id}
            ).to_list(length=None)
            
            return {
                "character": character,
                "knowledge_items": knowledge_items
            }
            
        except Exception as e:
            logger.error(f"Failed to get character with knowledge: {str(e)}")
            raise
    
    async def get_all_characters(self) -> List[Dict]:
        """
        Get all characters from database
        
        Returns:
            List of character documents
        """
        try:
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            characters = await self.database_service.characters.find({}).to_list(length=None)
            return characters
            
        except Exception as e:
            logger.error(f"Failed to get characters: {str(e)}")
            raise
    
    async def get_character(self, character_id: str) -> Optional[Dict]:
        """
        Get single character by ID
        
        Args:
            character_id: Character ID to retrieve
            
        Returns:
            Character document or None if not found
        """
        try:
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            character = await self.database_service.characters.find_one({"character_id": character_id})
            return character
            
        except Exception as e:
            logger.error(f"Failed to get character: {str(e)}")
            raise