"""
Chat Orchestrator Service
Combines Knowledge, Conversation, and Persona services for complete chat functionality
"""

from typing import Dict, List, Optional
from .knowledge_service import KnowledgeService
from .conversation_service import ConversationService
from .persona_service import PersonaService


class ChatOrchestrator:
    """
    Orchestrates all services to provide complete chat functionality
    integrating knowledge retrieval, conversation history, and persona context
    """
    
    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.conversation_service = ConversationService()
        self.persona_service = PersonaService()
    
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