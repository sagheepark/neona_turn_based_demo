import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class PersonaService:
    def __init__(self, storage_type: str = "file", database_service=None):
        self.storage_type = storage_type
        self.database_service = database_service
        
        # Initialize file storage (existing behavior)
        self.personas_path = Path("personas")
        self.personas_path.mkdir(exist_ok=True)
    
    def create_persona(self, user_id: str, persona_data: Dict) -> Dict:
        """
        Create new user persona - minimal implementation to pass test
        
        Args:
            user_id: ID of the user creating the persona
            persona_data: Dictionary containing persona attributes
            
        Returns:
            Dictionary containing created persona with unique ID
        """
        # Generate unique persona ID
        persona_id = f"persona_{uuid.uuid4().hex[:8]}"
        
        # Create persona structure
        persona = {
            "id": persona_id,
            "name": persona_data.get("name", ""),
            "description": persona_data.get("description", ""),
            "attributes": persona_data.get("attributes", {}),
            "created_at": datetime.now().isoformat(),
            "is_active": False
        }
        
        # Load or create user's personas file
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if user_personas_file.exists():
            with open(user_personas_file, 'r', encoding='utf-8') as f:
                user_personas = json.load(f)
        else:
            user_personas = {
                "personas": [],
                "active_persona_id": None
            }
        
        # Add new persona
        user_personas["personas"].append(persona)
        
        # Save to file
        with open(user_personas_file, 'w', encoding='utf-8') as f:
            json.dump(user_personas, f, ensure_ascii=False, indent=2)
        
        return persona
    
    def set_active_persona(self, user_id: str, persona_id: str) -> Dict:
        """
        Set active persona for user
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to set as active
            
        Returns:
            Updated user personas data
        """
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if not user_personas_file.exists():
            raise ValueError(f"No personas found for user {user_id}")
        
        with open(user_personas_file, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
        
        # Verify persona exists
        persona_found = False
        for persona in user_personas["personas"]:
            if persona["id"] == persona_id:
                persona_found = True
                persona["is_active"] = True
            else:
                persona["is_active"] = False
        
        if not persona_found:
            raise ValueError(f"Persona {persona_id} not found for user {user_id}")
        
        # Update active persona ID
        user_personas["active_persona_id"] = persona_id
        
        # Save updated data
        with open(user_personas_file, 'w', encoding='utf-8') as f:
            json.dump(user_personas, f, ensure_ascii=False, indent=2)
        
        return user_personas
    
    def get_active_persona(self, user_id: str) -> Optional[Dict]:
        """
        Get active persona for user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Active persona data or None if no active persona
        """
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if not user_personas_file.exists():
            return None
        
        with open(user_personas_file, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
        
        active_persona_id = user_personas.get("active_persona_id")
        if not active_persona_id:
            return None
        
        for persona in user_personas["personas"]:
            if persona["id"] == active_persona_id and persona.get("is_active", False):
                return persona
        
        return None
    
    def generate_persona_context(self, user_id: str) -> str:
        """
        Generate persona context string for chat prompts
        
        Args:
            user_id: ID of the user
            
        Returns:
            Formatted context string for AI character to understand user's persona
        """
        active_persona = self.get_active_persona(user_id)
        
        if not active_persona:
            return ""
        
        # Extract persona information
        name = active_persona.get("name", "")
        description = active_persona.get("description", "")
        attributes = active_persona.get("attributes", {})
        
        # Build context string for AI character
        context_parts = []
        
        # Basic persona introduction
        if name and description:
            context_parts.append(f"사용자는 '{name}' 페르소나로 대화하고 있습니다: {description}.")
        
        # User characteristics
        user_info = []
        if attributes.get("age"):
            user_info.append(f"나이 {attributes['age']}")
        if attributes.get("occupation"):
            user_info.append(f"직업/상황은 {attributes['occupation']}")
        
        if user_info:
            context_parts.append(f"사용자 배경: {', '.join(user_info)}.")
        
        # Personality and communication style
        personality_info = []
        if attributes.get("personality"):
            personality_info.append(f"성격: {attributes['personality']}")
        if attributes.get("speaking_style"):
            personality_info.append(f"말하는 방식: {attributes['speaking_style']}")
        
        if personality_info:
            context_parts.append(f"사용자 특성: {', '.join(personality_info)}.")
        
        # Current situation and interests
        situation_info = []
        if attributes.get("background"):
            situation_info.append(f"현재 상황: {attributes['background']}")
        if attributes.get("current_mood"):
            situation_info.append(f"감정 상태: {attributes['current_mood']}")
        if attributes.get("interests"):
            interests = attributes["interests"]
            if isinstance(interests, list):
                situation_info.append(f"관심사: {', '.join(interests)}")
            else:
                situation_info.append(f"관심사: {interests}")
        
        if situation_info:
            context_parts.append(f"사용자 상황: {', '.join(situation_info)}.")
        
        # Instructions for character response
        context_parts.append("이 페르소나 정보를 바탕으로 사용자에게 적절하게 반응하고 도움을 제공하세요.")
        
        return " ".join(context_parts)
    
    def get_user_personas(self, user_id: str) -> List[Dict]:
        """
        Get all personas for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of user's personas
        """
        # Get from file system (existing behavior for backward compatibility)
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if not user_personas_file.exists():
            return []
        
        with open(user_personas_file, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
        
        return user_personas.get("personas", [])
    
    async def get_user_personas_async(self, user_id: str) -> List[Dict]:
        """
        Async version for MongoDB compatibility
        """
        if self.storage_type == "mongodb" and self.database_service:
            # Get from MongoDB
            if not self.database_service.is_connected():
                await self.database_service.connect()
            
            personas = await self.database_service.personas.find({"user_id": user_id}).to_list(length=None)
            return personas
        else:
            # Get from file system (fallback behavior)
            user_personas_file = self.personas_path / f"{user_id}.json"
            
            if not user_personas_file.exists():
                return []
            
            with open(user_personas_file, 'r', encoding='utf-8') as f:
                user_personas = json.load(f)
            
            return user_personas.get("personas", [])
    
    def update_persona(self, user_id: str, persona_id: str, persona_data: Dict) -> Dict:
        """
        Update an existing persona
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to update
            persona_data: Dictionary containing updated persona attributes
            
        Returns:
            Updated persona dictionary
        """
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if not user_personas_file.exists():
            raise ValueError(f"No personas found for user {user_id}")
        
        with open(user_personas_file, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
        
        # Find and update the persona
        persona_found = False
        for i, persona in enumerate(user_personas["personas"]):
            if persona["id"] == persona_id:
                persona_found = True
                # Update persona data
                updated_persona = {
                    "id": persona_id,
                    "name": persona_data.get("name", persona["name"]),
                    "description": persona_data.get("description", persona["description"]),
                    "attributes": persona_data.get("attributes", persona.get("attributes", {})),
                    "created_at": persona.get("created_at", datetime.now().isoformat()),
                    "updated_at": datetime.now().isoformat(),
                    "is_active": persona.get("is_active", False)
                }
                user_personas["personas"][i] = updated_persona
                break
        
        if not persona_found:
            raise ValueError(f"Persona {persona_id} not found for user {user_id}")
        
        # Save updated data
        with open(user_personas_file, 'w', encoding='utf-8') as f:
            json.dump(user_personas, f, ensure_ascii=False, indent=2)
        
        return updated_persona
    
    def delete_persona(self, user_id: str, persona_id: str) -> bool:
        """
        Delete a persona
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to delete
            
        Returns:
            True if deleted successfully
        """
        user_personas_file = self.personas_path / f"{user_id}.json"
        
        if not user_personas_file.exists():
            raise ValueError(f"No personas found for user {user_id}")
        
        with open(user_personas_file, 'r', encoding='utf-8') as f:
            user_personas = json.load(f)
        
        # Find and remove the persona
        persona_found = False
        was_active = False
        
        for i, persona in enumerate(user_personas["personas"]):
            if persona["id"] == persona_id:
                persona_found = True
                was_active = persona.get("is_active", False)
                user_personas["personas"].pop(i)
                break
        
        if not persona_found:
            raise ValueError(f"Persona {persona_id} not found for user {user_id}")
        
        # If deleted persona was active, clear active persona
        if was_active:
            user_personas["active_persona_id"] = None
        
        # Save updated data
        with open(user_personas_file, 'w', encoding='utf-8') as f:
            json.dump(user_personas, f, ensure_ascii=False, indent=2)
        
        return True
    
    def generate_selective_persona_context(self, user_id: str, character_preferences: Dict) -> str:
        """
        Generate persona context with selective field inclusion
        
        Args:
            user_id: ID of the user
            character_preferences: Dictionary defining which fields to include
                {
                    "character_id": "character_name",
                    "required_fields": ["age", "occupation", "name"],
                    "optional_fields": ["personality"],
                    "excluded_fields": ["interests", "speaking_style"]
                }
        
        Returns:
            Selective persona context string
        """
        active_persona = self.get_active_persona(user_id)
        if not active_persona:
            return ""
        
        name = active_persona.get("name", "")
        description = active_persona.get("description", "")
        attributes = active_persona.get("attributes", {})
        
        context_parts = []
        
        # Always include basic persona info
        if name and description:
            context_parts.append(f"사용자는 '{name}' 페르소나로 대화하고 있습니다: {description}.")
        
        # Get field preferences
        required_fields = character_preferences.get("required_fields", ["age", "occupation", "name"])
        optional_fields = character_preferences.get("optional_fields", [])
        excluded_fields = character_preferences.get("excluded_fields", [])
        
        # Include required and optional fields, exclude explicitly excluded ones
        included_fields = set(required_fields + optional_fields) - set(excluded_fields)
        
        # Build context based on included fields
        user_info = []
        if "age" in included_fields and attributes.get("age"):
            user_info.append(f"나이 {attributes['age']}")
        if "occupation" in included_fields and attributes.get("occupation"):
            user_info.append(f"직업/상황은 {attributes['occupation']}")
        if "name" in included_fields and attributes.get("name"):
            user_info.append(f"이름은 {attributes['name']}")
        
        if user_info:
            context_parts.append(f"사용자 배경: {', '.join(user_info)}.")
        
        # Conditional personality and communication style
        personality_info = []
        if "personality" in included_fields and attributes.get("personality"):
            personality_info.append(f"성격: {attributes['personality']}")
        if "speaking_style" in included_fields and attributes.get("speaking_style"):
            personality_info.append(f"말하는 방식: {attributes['speaking_style']}")
        
        if personality_info:
            context_parts.append(f"사용자 특성: {', '.join(personality_info)}.")
        
        # Conditional interests and background
        situation_info = []
        if "background" in included_fields and attributes.get("background"):
            situation_info.append(f"현재 상황: {attributes['background']}")
        if "interests" in included_fields and attributes.get("interests"):
            interests = attributes["interests"]
            if isinstance(interests, list):
                situation_info.append(f"관심사: {', '.join(interests)}")
            else:
                situation_info.append(f"관심사: {interests}")
        
        if situation_info:
            context_parts.append(f"사용자 상황: {', '.join(situation_info)}.")
        
        # Instructions for character response
        context_parts.append("이 페르소나 정보를 바탕으로 사용자에게 적절하게 반응하고 도움을 제공하세요.")
        
        return " ".join(context_parts)
    
    def generate_identity_preserving_context(self, user_id: str, character_identity: Dict, selected_user_fields: List[str]) -> str:
        """
        Generate context that preserves character identity while adding selective user persona info
        
        Args:
            user_id: ID of the user
            character_identity: Character's core identity to preserve
            selected_user_fields: List of user persona fields to include
        
        Returns:
            Identity-preserving context string
        """
        active_persona = self.get_active_persona(user_id)
        
        context_parts = []
        
        # ALWAYS preserve character identity first
        context_parts.append(f"당신은 {character_identity.get('name', 'Assistant')}입니다.")
        
        if character_identity.get("personality"):
            context_parts.append(f"성격: {character_identity['personality']}")
        
        if character_identity.get("role"):
            context_parts.append(f"역할: {character_identity['role']}")
        
        if character_identity.get("speaking_style"):
            context_parts.append(f"말하는 방식: {character_identity['speaking_style']}")
        
        # Add ONLY selected user persona fields (minimal user context)
        if active_persona:
            attributes = active_persona.get("attributes", {})
            user_context = []
            
            for field in selected_user_fields:
                if field in attributes and attributes[field]:
                    if field == "age":
                        user_context.append(f"사용자 나이: {attributes[field]}")
                    elif field == "occupation":
                        user_context.append(f"사용자 직업: {attributes[field]}")
                    elif field == "name":
                        user_context.append(f"사용자 이름: {attributes[field]}")
            
            if user_context:
                context_parts.append(f"사용자 정보: {', '.join(user_context)}.")
        
        # Clear instruction to maintain character identity
        context_parts.append("위 사용자 정보를 참고하되, 항상 당신의 캐릭터 정체성을 유지하며 대화하세요.")
        
        return " ".join(context_parts)