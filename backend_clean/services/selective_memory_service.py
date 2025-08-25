"""
Selective Memory Service for Simulation-like Chat System
Manages character-specific status values, events, milestones, and core memory
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class SelectiveMemoryService:
    """
    Service for managing selective knowledge/memory system
    Tracks status values, milestones, events, and persistent facts
    """
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        self.memory_cache = {}  # In-memory cache for active sessions
        
    async def initialize_memory(self, user_id: str, character_id: str, config: Dict) -> Dict:
        """
        Initialize core memory for a new user-character pair
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            config: Parsed character configuration
            
        Returns:
            Initialized core memory object
        """
        try:
            # Check if memory already exists
            existing = await self.get_core_memory(user_id, character_id)
            if existing:
                return existing
            
            # Create new core memory with default values
            core_memory = {
                "status_values": {},
                "milestones": [],
                "event_log": [],
                "persistent_facts": [],
                "compressed_history": "",
                "conversation_count": 0,
                "last_interaction": datetime.utcnow().isoformat()
            }
            
            # Initialize status values from config
            if "status_values" in config:
                for status_name, status_def in config["status_values"].items():
                    core_memory["status_values"][status_name] = status_def.get("default", 50)
            
            # Save to database if available
            if self.database_service and self.database_service.is_connected():
                await self.database_service.selective_memories.insert_one({
                    "user_id": user_id,
                    "character_id": character_id,
                    "core_memory": core_memory,
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "version": 1
                })
            
            # Cache the memory
            cache_key = f"{user_id}_{character_id}"
            self.memory_cache[cache_key] = core_memory
            
            logger.info(f"Initialized core memory for user {user_id} with character {character_id}")
            return core_memory
            
        except Exception as e:
            logger.error(f"Failed to initialize memory: {str(e)}")
            raise
    
    async def get_core_memory(self, user_id: str, character_id: str) -> Optional[Dict]:
        """
        Retrieve core memory for a user-character pair
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            
        Returns:
            Core memory object or None if not found
        """
        try:
            # Check cache first
            cache_key = f"{user_id}_{character_id}"
            if cache_key in self.memory_cache:
                return self.memory_cache[cache_key]
            
            # Fetch from database
            if self.database_service and self.database_service.is_connected():
                memory_doc = await self.database_service.selective_memories.find_one({
                    "user_id": user_id,
                    "character_id": character_id
                })
                
                if memory_doc:
                    core_memory = memory_doc["core_memory"]
                    self.memory_cache[cache_key] = core_memory
                    return core_memory
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get core memory: {str(e)}")
            return None
    
    async def update_status_values(self, user_id: str, character_id: str, 
                                  updates: Dict[str, float], config: Dict) -> Dict:
        """
        Update status values with boundary checking
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            updates: Dictionary of status updates {status_name: delta_value}
            config: Character configuration for validation
            
        Returns:
            Updated core memory
        """
        try:
            core_memory = await self.get_core_memory(user_id, character_id)
            if not core_memory:
                core_memory = await self.initialize_memory(user_id, character_id, config)
            
            # Apply updates with boundary checking
            for status_name, delta in updates.items():
                if status_name in core_memory["status_values"]:
                    current = core_memory["status_values"][status_name]
                    new_value = current + delta
                    
                    # Apply boundaries from config
                    if "status_values" in config and status_name in config["status_values"]:
                        status_def = config["status_values"][status_name]
                        min_val = status_def.get("min", 0)
                        max_val = status_def.get("max", 100)
                        new_value = max(min_val, min(new_value, max_val))
                    
                    core_memory["status_values"][status_name] = new_value
                    logger.debug(f"Updated {status_name}: {current} -> {new_value}")
            
            # Update timestamp
            core_memory["last_interaction"] = datetime.utcnow().isoformat()
            
            # Save to database
            await self._save_core_memory(user_id, character_id, core_memory)
            
            return core_memory
            
        except Exception as e:
            logger.error(f"Failed to update status values: {str(e)}")
            raise
    
    async def add_event(self, user_id: str, character_id: str, event: Dict) -> Dict:
        """
        Add an event to the event log
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            event: Event dictionary with type, description, impact
            
        Returns:
            Updated core memory
        """
        try:
            core_memory = await self.get_core_memory(user_id, character_id)
            if not core_memory:
                raise ValueError("Core memory not found")
            
            # Add timestamp if not present
            if "timestamp" not in event:
                event["timestamp"] = datetime.utcnow().isoformat()
            
            # Add to event log
            core_memory["event_log"].append(event)
            
            # Keep only last 100 events to prevent unbounded growth
            if len(core_memory["event_log"]) > 100:
                core_memory["event_log"] = core_memory["event_log"][-100:]
            
            # Save to database
            await self._save_core_memory(user_id, character_id, core_memory)
            
            logger.info(f"Added event for {user_id}/{character_id}: {event.get('event_type', 'unknown')}")
            return core_memory
            
        except Exception as e:
            logger.error(f"Failed to add event: {str(e)}")
            raise
    
    async def check_milestones(self, user_id: str, character_id: str, 
                              config: Dict, context: Dict) -> List[Dict]:
        """
        Check if any milestones have been achieved
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            config: Character configuration with milestone definitions
            context: Current conversation context
            
        Returns:
            List of newly achieved milestones
        """
        try:
            core_memory = await self.get_core_memory(user_id, character_id)
            if not core_memory:
                return []
            
            achieved_milestones = []
            existing_milestone_ids = {m["id"] for m in core_memory["milestones"]}
            
            # Check each milestone definition
            if "milestones" in config:
                for milestone_id, milestone_def in config["milestones"].items():
                    if milestone_id not in existing_milestone_ids:
                        # Check if conditions are met
                        if self._check_milestone_conditions(milestone_def, core_memory, context):
                            milestone = {
                                "id": milestone_id,
                                "achieved_at": datetime.utcnow().isoformat(),
                                "description": milestone_def.get("description", ""),
                                "rewards": milestone_def.get("rewards", {})
                            }
                            
                            # Add to memory
                            core_memory["milestones"].append(milestone)
                            achieved_milestones.append(milestone)
                            
                            # Apply rewards (status updates)
                            if "rewards" in milestone_def:
                                await self.update_status_values(
                                    user_id, character_id, 
                                    milestone_def["rewards"], config
                                )
                            
                            logger.info(f"Milestone achieved: {milestone_id} for {user_id}/{character_id}")
            
            if achieved_milestones:
                await self._save_core_memory(user_id, character_id, core_memory)
            
            return achieved_milestones
            
        except Exception as e:
            logger.error(f"Failed to check milestones: {str(e)}")
            return []
    
    def _check_milestone_conditions(self, milestone_def: Dict, 
                                   core_memory: Dict, context: Dict) -> bool:
        """
        Check if milestone conditions are met
        
        Args:
            milestone_def: Milestone definition with conditions
            core_memory: Current core memory state
            context: Current conversation context
            
        Returns:
            True if conditions are met
        """
        try:
            conditions = milestone_def.get("conditions", {})
            
            # Check conversation count
            if "conversation_count" in conditions:
                if core_memory.get("conversation_count", 0) < conditions["conversation_count"]:
                    return False
            
            # Check status thresholds
            if "status_thresholds" in conditions:
                for status_name, threshold in conditions["status_thresholds"].items():
                    current_value = core_memory["status_values"].get(status_name, 0)
                    if current_value < threshold:
                        return False
            
            # Check event count
            if "event_type_count" in conditions:
                for event_type, required_count in conditions["event_type_count"].items():
                    event_count = sum(1 for e in core_memory["event_log"] 
                                    if e.get("event_type") == event_type)
                    if event_count < required_count:
                        return False
            
            # Check custom conditions from context
            if "context_conditions" in conditions:
                for key, expected_value in conditions["context_conditions"].items():
                    if context.get(key) != expected_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking milestone conditions: {str(e)}")
            return False
    
    async def add_persistent_fact(self, user_id: str, character_id: str, fact: str) -> Dict:
        """
        Add a persistent fact to memory
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            fact: Fact to remember
            
        Returns:
            Updated core memory
        """
        try:
            core_memory = await self.get_core_memory(user_id, character_id)
            if not core_memory:
                raise ValueError("Core memory not found")
            
            # Add fact if not already present
            if fact not in core_memory["persistent_facts"]:
                core_memory["persistent_facts"].append(fact)
                
                # Limit to 50 facts
                if len(core_memory["persistent_facts"]) > 50:
                    core_memory["persistent_facts"] = core_memory["persistent_facts"][-50:]
                
                await self._save_core_memory(user_id, character_id, core_memory)
                logger.info(f"Added persistent fact for {user_id}/{character_id}")
            
            return core_memory
            
        except Exception as e:
            logger.error(f"Failed to add persistent fact: {str(e)}")
            raise
    
    async def compress_history(self, user_id: str, character_id: str, 
                             messages: List[Dict], compression_prompt: str) -> str:
        """
        Compress conversation history using character-specific prompt
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            messages: Conversation messages to compress
            compression_prompt: Character-specific compression prompt
            
        Returns:
            Compressed history summary
        """
        try:
            # This would normally use an LLM to compress
            # For now, we'll do a simple extraction
            summary_parts = []
            
            # Extract key information
            for msg in messages[-10:]:  # Last 10 messages
                if msg.get("role") == "user":
                    # Look for important patterns
                    text = msg.get("content", "")
                    
                    # Extract personal information
                    if any(keyword in text.lower() for keyword in ["저는", "제가", "my", "i am", "i'm"]):
                        summary_parts.append(f"User: {text[:100]}")
                    
                    # Extract preferences
                    if any(keyword in text.lower() for keyword in ["좋아", "싫어", "like", "hate", "prefer"]):
                        summary_parts.append(f"Preference: {text[:100]}")
            
            compressed = " | ".join(summary_parts) if summary_parts else "No significant history"
            
            # Update core memory with compressed history
            core_memory = await self.get_core_memory(user_id, character_id)
            if core_memory:
                core_memory["compressed_history"] = compressed
                core_memory["conversation_count"] = core_memory.get("conversation_count", 0) + 1
                await self._save_core_memory(user_id, character_id, core_memory)
            
            return compressed
            
        except Exception as e:
            logger.error(f"Failed to compress history: {str(e)}")
            return ""
    
    def format_for_prompt(self, core_memory: Dict, template: str) -> str:
        """
        Format core memory for injection into LLM prompt
        
        Args:
            core_memory: Core memory object
            template: Prompt template with placeholders
            
        Returns:
            Formatted prompt section
        """
        try:
            # Replace placeholders in template
            formatted = template
            
            # Format status values
            status_text = ", ".join([f"{k}: {v}" for k, v in core_memory.get("status_values", {}).items()])
            formatted = formatted.replace("{status_values}", status_text)
            
            # Format milestones
            milestone_text = ", ".join([m["description"] for m in core_memory.get("milestones", [])])
            formatted = formatted.replace("{milestones}", milestone_text or "없음")
            
            # Format persistent facts
            facts_text = " / ".join(core_memory.get("persistent_facts", []))
            formatted = formatted.replace("{persistent_facts}", facts_text or "없음")
            
            # Add compressed history
            formatted = formatted.replace("{compressed_history}", 
                                        core_memory.get("compressed_history", ""))
            
            # Add any status value placeholders
            for status_name, value in core_memory.get("status_values", {}).items():
                formatted = formatted.replace(f"{{{status_name}}}", str(value))
            
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to format memory for prompt: {str(e)}")
            return ""
    
    async def _save_core_memory(self, user_id: str, character_id: str, core_memory: Dict):
        """
        Save core memory to database and cache
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            core_memory: Core memory object to save
        """
        try:
            # Update cache
            cache_key = f"{user_id}_{character_id}"
            self.memory_cache[cache_key] = core_memory
            
            # Save to database if available
            if self.database_service and self.database_service.is_connected():
                await self.database_service.selective_memories.update_one(
                    {
                        "user_id": user_id,
                        "character_id": character_id
                    },
                    {
                        "$set": {
                            "core_memory": core_memory,
                            "last_updated": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
        except Exception as e:
            logger.error(f"Failed to save core memory: {str(e)}")
            raise
    
    async def reset_memory(self, user_id: str, character_id: str, config: Dict) -> Dict:
        """
        Reset core memory to initial state
        
        Args:
            user_id: User identifier
            character_id: Character identifier
            config: Character configuration
            
        Returns:
            Reset core memory
        """
        try:
            # Delete existing memory
            if self.database_service and self.database_service.is_connected():
                await self.database_service.selective_memories.delete_one({
                    "user_id": user_id,
                    "character_id": character_id
                })
            
            # Remove from cache
            cache_key = f"{user_id}_{character_id}"
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            # Initialize fresh memory
            return await self.initialize_memory(user_id, character_id, config)
            
        except Exception as e:
            logger.error(f"Failed to reset memory: {str(e)}")
            raise