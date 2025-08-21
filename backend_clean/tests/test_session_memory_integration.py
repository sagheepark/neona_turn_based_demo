"""
TDD Tests for Session Memory Integration
Following TDD: Red → Green → Refactor
Testing the critical session memory issue - Test Group 27
"""

import pytest
import json
from pathlib import Path
from services.conversation_service import ConversationService

class TestSessionMemoryIntegration:
    """
    Test session memory integration to fix the critical character memory issue
    These tests verify that chat messages persist to sessions for story continuity
    """
    
    def setup_method(self):
        self.conversation_service = ConversationService()
        self.test_user_id = "demo_user"
        self.test_character_id = "dr_python"
        
    def test_should_persist_chat_messages_to_sessions(self):
        """
        Test 27.1: Chat messages should persist to sessions
        
        RED PHASE: This test will fail until we connect chat API to sessions
        """
        # Given: A new conversation session is created
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # When: User sends a message (simulating chat API behavior)
        user_message = "Hello, I want to learn Python!"
        message_result = self.conversation_service.add_message_to_session(
            session_id, 
            "user", 
            user_message, 
            self.test_user_id
        )
        
        # And: Character responds (simulating AI response)
        ai_response = "Hello! I'm Dr. Python, and I'd love to help you learn Python programming!"
        ai_result = self.conversation_service.add_message_to_session(
            session_id,
            "assistant", 
            ai_response,
            self.test_user_id
        )
        
        # Then: Both messages should be persisted in the session
        session_messages = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        assert len(session_messages["messages"]) == 2
        assert session_messages["messages"][0]["role"] == "user"
        assert session_messages["messages"][0]["content"] == user_message
        assert session_messages["messages"][1]["role"] == "assistant" 
        assert session_messages["messages"][1]["content"] == ai_response
        assert session_messages["message_count"] == 2
        
        # This test passes because ConversationService works
        # But the real issue is that /api/chat doesn't use this service!
    
    def test_should_load_previous_messages_on_session_continuation(self):
        """
        Test 27.2: Session continuation should load message history
        
        RED PHASE: This test documents what session continuation should do
        """
        # Given: A session with previous conversation history
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add some conversation history
        self.conversation_service.add_message_to_session(
            session_id, "user", "What's a Python list?", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "A Python list is a collection of items in a particular order.", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "user", "How do I create one?", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "You can create a list using square brackets: my_list = [1, 2, 3]", self.test_user_id
        )
        
        # When: Session is continued (loaded for context)
        loaded_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Then: All previous messages should be available for context
        assert loaded_session["message_count"] == 4
        assert len(loaded_session["messages"]) == 4
        
        # And: Last Q&A pair should be available for immediate context
        assert "last_message_pair" in loaded_session
        last_pair = loaded_session["last_message_pair"]
        assert last_pair["user_message"] == "How do I create one?"
        assert "square brackets" in last_pair["assistant_message"]
        
        # This test passes but represents what chat continuation SHOULD do
        
    def test_should_support_multiple_sessions_per_character(self):
        """
        Test 27.3: Multiple sessions per character should be supported
        
        RED PHASE: This test verifies session isolation and management
        """
        # Given: User creates multiple sessions with the same character
        session1 = self.conversation_service.create_session(
            self.test_user_id, self.test_character_id, None
        )
        session2 = self.conversation_service.create_session(
            self.test_user_id, self.test_character_id, None
        )
        
        # When: Different conversations happen in each session
        self.conversation_service.add_message_to_session(
            session1["session_id"], "user", "Teach me about Python functions", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session2["session_id"], "user", "Help me with Python data structures", self.test_user_id
        )
        
        # Then: Each session should maintain separate conversation threads
        session1_messages = self.conversation_service.load_session_messages(
            session1["session_id"], self.test_user_id
        )
        session2_messages = self.conversation_service.load_session_messages(
            session2["session_id"], self.test_user_id
        )
        
        assert session1_messages["messages"][0]["content"] == "Teach me about Python functions"
        assert session2_messages["messages"][0]["content"] == "Help me with Python data structures"
        assert session1_messages["message_count"] == 1
        assert session2_messages["message_count"] == 1
        
        # And: User should be able to get all sessions for this character
        all_sessions = self.conversation_service.get_previous_sessions(
            self.test_user_id, self.test_character_id
        )
        assert len(all_sessions) >= 2
        
        session_ids = [s["session_id"] for s in all_sessions]
        assert session1["session_id"] in session_ids
        assert session2["session_id"] in session_ids
        
    def test_should_track_conversation_metadata_in_sessions(self):
        """
        Test 27.4: Session metadata should track conversation context
        
        RED PHASE: This test verifies session metadata functionality
        """
        # Given: A conversation session with multiple exchanges
        session_data = self.conversation_service.create_session(
            self.test_user_id, self.test_character_id, None
        )
        session_id = session_data["session_id"]
        
        # When: Multiple messages are exchanged
        for i in range(3):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Question {i+1} about Python", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Answer {i+1} about Python concepts", self.test_user_id
            )
        
        # Then: Session metadata should be tracked correctly
        loaded_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        assert loaded_session["message_count"] == 6  # 3 user + 3 assistant messages
        assert "last_updated" in loaded_session
        assert "created_at" in loaded_session
        
        # And: Session should be retrievable in session list with correct metadata
        sessions = self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        current_session = next(s for s in sessions if s["session_id"] == session_id)
        
        assert current_session["message_count"] == 6
        assert current_session["status"] == "active"
        
    def test_should_have_session_api_endpoints_available(self):
        """
        Test 27.5: Session API endpoints should be available
        
        RED PHASE: This test will fail because session endpoints don't exist in main.py
        """
        # This test documents what API endpoints should exist
        required_endpoints = [
            "/api/sessions/create",                    # Create new session
            "/api/sessions/{user_id}/{character_id}",  # Get sessions for user+character  
            "/api/chat-with-session",                  # Chat with session persistence
            "/api/sessions/{session_id}/messages",     # Get session message history
            "/api/sessions/{session_id}",             # Delete session
        ]
        
        # Check if main.py has these endpoints defined
        main_py_path = Path("main.py")
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            missing_endpoints = []
            for endpoint in required_endpoints:
                # Extract just the endpoint pattern for checking
                endpoint_pattern = endpoint.split('/')[-1].split('{')[0]
                if endpoint_pattern not in main_content and len(endpoint_pattern) > 2:
                    missing_endpoints.append(endpoint)
            
            # This assertion will fail, showing us what needs to be implemented
            assert len(missing_endpoints) == 0, f"Missing session API endpoints in main.py: {missing_endpoints}"
        else:
            pytest.fail("main.py not found - cannot verify API endpoints")
    
    def test_should_have_chat_with_session_models_defined(self):
        """
        Test 27.6: ChatWithSession models should be defined
        
        RED PHASE: This test will fail because ChatWithSession models don't exist
        """
        # Check if main.py has the required models for session-aware chat
        main_py_path = Path("main.py")
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            required_models = [
                "ChatWithSessionRequest",    # Request model with session_id, user_id
                "ChatWithSessionResponse",   # Response model with session metadata
            ]
            
            missing_models = []
            for model in required_models:
                if model not in main_content:
                    missing_models.append(model)
            
            # This assertion will fail, showing us what models need to be created
            assert len(missing_models) == 0, f"Missing session-aware chat models in main.py: {missing_models}"
        else:
            pytest.fail("main.py not found - cannot verify chat models")