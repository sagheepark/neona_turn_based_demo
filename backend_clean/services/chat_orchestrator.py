"""
Chat Orchestrator Service
Combines Knowledge, Conversation, Persona, and Selective Memory services for complete chat functionality
"""

from typing import Dict, List, Optional
from .knowledge_service import KnowledgeService
from .conversation_service import ConversationService
from .persona_service import PersonaService
from .selective_memory_service import SelectiveMemoryService
from .config_parser_service import ConfigParserService
from .database_service import DatabaseService


class ChatOrchestrator:
    """
    Orchestrates all services to provide complete chat functionality
    integrating knowledge retrieval, conversation history, persona context, and selective memory
    """
    
    def __init__(self, database_service: Optional[DatabaseService] = None):
        self.knowledge_service = KnowledgeService()
        self.conversation_service = ConversationService()
        self.persona_service = PersonaService()
        self.selective_memory_service = SelectiveMemoryService(database_service)
        self.config_parser_service = ConfigParserService()
        self.database_service = database_service
    
    def start_chat_session(self, user_id: str, character_id: str, persona_id: Optional[str] = None) -> Dict:
        """
        Start a new chat session or offer to continue existing ones
        
        Args:
            user_id: ID of the user
            character_id: ID of the character to chat with
            persona_id: Optional persona ID (will use active persona if not provided)
            
        Returns:
            Dictionary with session options and context
        """
        # Get previous sessions for continuation option
        previous_sessions = self.conversation_service.get_previous_sessions(user_id, character_id)
        
        # Get active persona if not specified
        if not persona_id:
            active_persona = self.persona_service.get_active_persona(user_id)
            if active_persona:
                persona_id = active_persona["id"]
        
        # Filter sessions with messages (non-empty sessions)
        sessions_with_messages = [s for s in previous_sessions if s["message_count"] > 0]
        
        return {
            "previous_sessions": sessions_with_messages,
            "can_continue": len(sessions_with_messages) > 0,
            "active_persona_id": persona_id,
            "character_id": character_id,
            "user_id": user_id
        }
    
    def create_new_session(self, user_id: str, character_id: str, persona_id: Optional[str] = None) -> Dict:
        """
        Create a new conversation session
        
        Args:
            user_id: ID of the user
            character_id: ID of the character
            persona_id: Optional persona ID
            
        Returns:
            New session data
        """
        # Ensure persona exists or use default
        if not persona_id:
            active_persona = self.persona_service.get_active_persona(user_id)
            persona_id = active_persona["id"] if active_persona else "default"
        
        # Create new session
        session = self.conversation_service.create_session(user_id, character_id, persona_id)
        
        return {
            "session": session,
            "persona_context": self.persona_service.generate_persona_context(user_id)
        }
    
    def continue_session(self, session_id: str, user_id: str) -> Dict:
        """
        Continue an existing conversation session
        
        Args:
            session_id: ID of the session to continue
            user_id: ID of the user (for validation)
            
        Returns:
            Session data with full message history and context
        """
        # Load session with all messages
        session = self.conversation_service.load_session_messages(session_id, user_id)
        
        # Get persona context
        persona_context = self.persona_service.generate_persona_context(user_id)
        
        # Extract last user input and last AI output for simplified UI
        last_user_input = ""
        last_ai_output = ""
        
        if session.get("messages"):
            messages = session["messages"]
            # Find last user message and last assistant message
            for msg in reversed(messages):
                if msg["role"] == "user" and not last_user_input:
                    last_user_input = msg["content"]
                elif msg["role"] == "assistant" and not last_ai_output:
                    last_ai_output = msg["content"]
                
                # Stop when we have both
                if last_user_input and last_ai_output:
                    break
        
        return {
            "session": session,
            "persona_context": persona_context,
            "last_qa": session.get("last_message_pair", {}),
            "last_user_input": last_user_input,
            "last_ai_output": last_ai_output
        }
    
    def process_message(self, session_id: str, user_id: str, message: str, character_id: str) -> Dict:
        """
        Process a user message in a conversation
        
        Args:
            session_id: ID of the current session
            user_id: ID of the user
            message: User's message
            character_id: ID of the character
            
        Returns:
            Response data including knowledge used and AI response preparation
        """
        # Add user message to session
        self.conversation_service.add_message_to_session(session_id, "user", message, user_id)
        
        # Search for relevant knowledge
        relevant_knowledge = self.knowledge_service.search_relevant_knowledge(
            message, character_id, max_results=3
        )
        
        # Get persona context for response generation
        persona_context = self.persona_service.generate_persona_context(user_id)
        
        # Prepare data for AI response generation
        response_data = {
            "user_message": message,
            "relevant_knowledge": relevant_knowledge,
            "persona_context": persona_context,
            "knowledge_ids": [k.get("id", "") for k in relevant_knowledge],
            "session_id": session_id
        }
        
        return response_data
    
    def save_ai_response(self, session_id: str, user_id: str, response: str, knowledge_used: List[str] = None) -> Dict:
        """
        Save AI response to conversation session
        
        Args:
            session_id: ID of the session
            user_id: ID of the user
            response: AI's response text
            knowledge_used: List of knowledge IDs that were used
            
        Returns:
            Updated session data
        """
        # Add AI response to session
        updated_session = self.conversation_service.add_message_to_session(
            session_id, "assistant", response, user_id
        )
        
        # Track knowledge usage (could be enhanced to store in session metadata)
        if knowledge_used:
            # This could be extended to track knowledge usage statistics
            pass
        
        return updated_session
    
    def get_session_summaries(self, user_id: str, character_id: Optional[str] = None) -> List[Dict]:
        """
        Get all session summaries for a user
        
        Args:
            user_id: ID of the user
            character_id: Optional character filter
            
        Returns:
            List of session summaries
        """
        all_sessions = []
        
        if character_id:
            # Get sessions for specific character
            sessions = self.conversation_service.get_previous_sessions(user_id, character_id)
            all_sessions.extend(sessions)
        else:
            # Get sessions for all characters (would need enhancement in conversation_service)
            # For now, return empty list as this needs implementation
            pass
        
        return all_sessions
    
    def create_persona(self, user_id: str, persona_data: Dict) -> Dict:
        """
        Create a new user persona
        
        Args:
            user_id: ID of the user
            persona_data: Persona attributes
            
        Returns:
            Created persona data
        """
        return self.persona_service.create_persona(user_id, persona_data)
    
    def set_active_persona(self, user_id: str, persona_id: str) -> Dict:
        """
        Set active persona for user
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to activate
            
        Returns:
            Updated personas data
        """
        return self.persona_service.set_active_persona(user_id, persona_id)
    
    def get_active_persona(self, user_id: str) -> Optional[Dict]:
        """
        Get current active persona for user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Active persona data or None
        """
        return self.persona_service.get_active_persona(user_id)
    
    async def process_chat_with_memory(self, user_id: str, character_id: str, 
                                      user_message: str, session_id: str,
                                      character_prompt: str) -> Dict:
        """
        Process a chat message with selective memory integration
        
        Args:
            user_id: ID of the user
            character_id: ID of the character
            user_message: User's message
            session_id: Current session ID
            character_prompt: Character's base prompt
            
        Returns:
            Enhanced context with memory integration
        """
        # Ensure database is connected
        if self.database_service and not self.database_service.is_connected():
            await self.database_service.connect()
        
        # Get character configuration
        config = self.config_parser_service.parse_configuration(
            self.config_parser_service.generate_default_config()
        )
        
        # Get or initialize core memory
        core_memory = await self.selective_memory_service.get_core_memory(user_id, character_id)
        if not core_memory:
            core_memory = await self.selective_memory_service.initialize_memory(
                user_id, character_id, config
            )
        
        # Search for relevant knowledge
        relevant_knowledge = self.knowledge_service.search_relevant_knowledge(
            user_message, character_id
        )
        
        # Get persona context
        persona_context = self.persona_service.generate_persona_context(user_id)
        
        # Format memory for prompt injection
        memory_prompt = ""
        if config.get("prompt_injection_template"):
            memory_prompt = self.selective_memory_service.format_for_prompt(
                core_memory, config["prompt_injection_template"]
            )
        
        # Detect events from user message
        events_to_add = []
        status_updates = {}
        
        # Simple event detection (can be enhanced with NLP)
        message_lower = user_message.lower()
        if any(word in message_lower for word in ["좋아", "사랑", "고마워", "최고"]):
            events_to_add.append({
                "event_type": "user_compliment",
                "description": "사용자가 긍정적인 반응을 보임",
                "impact": {"affection": 5}
            })
            status_updates["affection"] = 5
        
        if any(word in message_lower for word in ["싫어", "나빠", "별로", "안좋"]):
            events_to_add.append({
                "event_type": "user_criticism",
                "description": "사용자가 부정적인 반응을 보임",
                "impact": {"affection": -3, "stress": 5}
            })
            status_updates["affection"] = -3
            status_updates["stress"] = 5
        
        # Apply status updates
        if status_updates:
            await self.selective_memory_service.update_status_values(
                user_id, character_id, status_updates, config
            )
        
        # Add events
        for event in events_to_add:
            await self.selective_memory_service.add_event(user_id, character_id, event)
        
        # Check for milestone achievements
        context = {
            "message_count": core_memory.get("conversation_count", 0) + 1,
            "user_message": user_message
        }
        achieved_milestones = await self.selective_memory_service.check_milestones(
            user_id, character_id, config, context
        )
        
        # Build enhanced prompt
        enhanced_prompt = f"{character_prompt}\n\n"
        
        if memory_prompt:
            enhanced_prompt += f"[Character Memory State]\n{memory_prompt}\n\n"
        
        if relevant_knowledge:
            knowledge_text = "\n".join([f"- {k['title']}: {k['content']}" for k in relevant_knowledge])
            enhanced_prompt += f"[Relevant Knowledge]\n{knowledge_text}\n\n"
        
        if persona_context:
            enhanced_prompt += f"[User Persona]\n{persona_context}\n\n"
        
        if achieved_milestones:
            milestone_text = ", ".join([m["description"] for m in achieved_milestones])
            enhanced_prompt += f"[New Achievements]\n{milestone_text}\n\n"
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "core_memory": core_memory,
            "relevant_knowledge": relevant_knowledge,
            "achieved_milestones": achieved_milestones,
            "status_updates": status_updates
        }
    
    def get_user_personas(self, user_id: str) -> List[Dict]:
        """
        Get all personas for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of user's personas
        """
        return self.persona_service.get_user_personas(user_id)
    
    def update_persona(self, user_id: str, persona_id: str, persona_data: Dict) -> Dict:
        """
        Update an existing persona
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to update
            persona_data: Updated persona attributes
            
        Returns:
            Updated persona data
        """
        return self.persona_service.update_persona(user_id, persona_id, persona_data)
    
    def delete_persona(self, user_id: str, persona_id: str) -> bool:
        """
        Delete a persona
        
        Args:
            user_id: ID of the user
            persona_id: ID of the persona to delete
            
        Returns:
            True if deleted successfully
        """
        return self.persona_service.delete_persona(user_id, persona_id)
    
    def delete_session(self, session_id: str, user_id: str) -> Dict:
        """
        Delete a conversation session
        
        Args:
            session_id: ID of the session to delete
            user_id: ID of the user (for security validation)
            
        Returns:
            Dictionary indicating success/failure of deletion
        """
        return self.conversation_service.delete_session(session_id, user_id)
    
    def generate_response(self, user_id: str, character_id: str, message: str, character_prompt: str) -> Dict:
        """
        Generate chat response with knowledge feedback - minimal implementation for tests
        
        Args:
            user_id: ID of the user
            character_id: ID of the character
            message: User's message
            character_prompt: Character's prompt
            
        Returns:
            Response with knowledge_used field for visual feedback
        """
        # Search for relevant knowledge
        relevant_knowledge = self.knowledge_service.search_relevant_knowledge(
            message, character_id, max_results=3
        )
        
        # Prepare knowledge_used field for visual feedback
        knowledge_used = []
        for knowledge_item in relevant_knowledge:
            knowledge_used.append({
                "id": knowledge_item.get("id", ""),
                "title": knowledge_item.get("title", ""),
                "relevance_score": knowledge_item.get("relevance_score", 0.0)
            })
        
        # Basic response structure with knowledge feedback
        response = {
            "message": "Response generated", # Minimal response for testing
            "character_id": character_id,
            "knowledge_used": knowledge_used
        }
        
        return response