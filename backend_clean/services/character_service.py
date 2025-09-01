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
            
            # Add default temperature for existing characters without it
            if character and "temperature" not in character:
                character["temperature"] = 0.7
                # Update the database with the default
                await self.database_service.characters.update_one(
                    {"character_id": character_id},
                    {"$set": {"temperature": 0.7}}
                )
            
            return character
            
        except Exception as e:
            logger.error(f"Failed to get character: {str(e)}")
            raise
    
    async def create_character(self, character_data: Dict) -> Dict:
        """
        Create a new character with temperature validation
        
        Args:
            character_data: Character data dictionary
            
        Returns:
            Created character document
        """
        try:
            # Validate temperature if provided
            if "temperature" in character_data:
                temp = character_data["temperature"]
                if not (0.0 <= temp <= 1.0):
                    raise ValueError("Temperature must be between 0.0 and 1.0")
            else:
                # Set default temperature
                character_data["temperature"] = 0.7
            
            # Add timestamps
            character_data["created_at"] = datetime.now()
            character_data["updated_at"] = datetime.now()
            
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            # Insert character
            result = await self.database_service.characters.insert_one(character_data)
            
            # Return the created character
            character = await self.database_service.characters.find_one({"_id": result.inserted_id})
            return character
            
        except Exception as e:
            logger.error(f"Failed to create character: {str(e)}")
            raise
    
    async def update_character(self, character_id: str, update_data: Dict) -> Dict:
        """
        Update an existing character
        
        Args:
            character_id: Character ID to update
            update_data: Data to update
            
        Returns:
            Updated character document
        """
        try:
            # Validate temperature if provided
            if "temperature" in update_data:
                temp = update_data["temperature"]
                if not (0.0 <= temp <= 1.0):
                    raise ValueError("Temperature must be between 0.0 and 1.0")
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.now()
            
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            # Update character
            result = await self.database_service.characters.update_one(
                {"character_id": character_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise ValueError(f"Character with ID {character_id} not found")
            
            # Return updated character
            character = await self.database_service.characters.find_one({"character_id": character_id})
            return character
            
        except Exception as e:
            logger.error(f"Failed to update character: {str(e)}")
            raise
    
    async def delete_character(self, character_id: str) -> bool:
        """
        Delete a character
        
        Args:
            character_id: Character ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            result = await self.database_service.characters.delete_one({"character_id": character_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete character: {str(e)}")
            raise
    
    def _invalidate_cache(self):
        """Invalidate any caches - placeholder for future implementation"""
        pass