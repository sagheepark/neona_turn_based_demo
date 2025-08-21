"""
TDD Test Group 5: Session Continuation Fixes
Testing that session continuation properly loads messages and handles deletion
"""

import pytest
import json
import os
from services.conversation_service import ConversationService

class TestSessionLoadingFix:
    def setup_method(self):
        """Set up test environment"""
        self.conversation_service = ConversationService()
        self.test_user_id = "test_user_session_fix"
        self.test_character_id = "dr_python"
        
    def test_should_load_previous_messages_when_continuing_session(self):
        """
        Test 5.1: Session message loading
        FAILING - Sessions currently load with 0 messages despite having content
        """
        # Given: Create a session with actual conversation messages
        session_data = self.conversation_service.create_session(
            self.test_user_id, 
            self.test_character_id, 
            None
        )
        session_id = session_data["session_id"]
        
        # Add some messages to the session
        self.conversation_service.add_message_to_session(
            session_id, 
            "user", 
            "안녕하세요", 
            self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, 
            "assistant", 
            "안녕하세요! 파이썬에 대해 궁금한 것이 있으시면 언제든 물어보세요!", 
            self.test_user_id
        )
        
        # When: Load session messages (since continue_session doesn't exist yet)
        continued_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Then: Previous messages should be loaded
        assert "messages" in continued_session
        assert len(continued_session["messages"]) > 0  # Should not be empty!
        assert continued_session["messages"][0]["content"] == "안녕하세요"
        assert continued_session["messages"][1]["content"] == "안녕하세요! 파이썬에 대해 궁금한 것이 있으시면 언제든 물어보세요!"
        
    def test_should_allow_user_to_delete_old_sessions(self):
        """
        Test 5.2: Session deletion
        NOT IMPLEMENTED - Need to add session deletion functionality
        """
        # Given: User has multiple sessions
        session1 = self.conversation_service.create_session(self.test_user_id, self.test_character_id, None)
        session2 = self.conversation_service.create_session(self.test_user_id, self.test_character_id, None)
        
        # Verify sessions exist
        sessions = self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        assert len(sessions) >= 2
        
        # When: User deletes a session
        delete_result = self.conversation_service.delete_session(session1["session_id"], self.test_user_id)
        
        # Then: Session should be removed
        assert delete_result["success"] == True
        remaining_sessions = self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        session_ids = [s["session_id"] for s in remaining_sessions]
        assert session1["session_id"] not in session_ids
        assert session2["session_id"] in session_ids