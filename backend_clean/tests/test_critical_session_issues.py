"""
TDD Tests for Critical Session Issues
RED PHASE: Write failing tests for the 3 reported issues
"""

import pytest
import json
from services.conversation_service import ConversationService

class TestCriticalSessionIssues:
    def setup_method(self):
        self.conversation_service = ConversationService()
        self.test_user_id = "demo_user"
        self.test_character_id = "dr_python"
        
    def test_delete_session_endpoint_should_work_with_correct_url_format(self):
        """
        Test Issue 1: Session deletion 404 error
        Testing that DELETE endpoint accepts correct URL format
        """
        # Given: Create a session that actually exists
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id, 
            None
        )
        session_id = session_data["session_id"]
        
        # When: Delete session using the service (simulating API call)
        delete_result = self.conversation_service.delete_session(session_id, self.test_user_id)
        
        # Then: Deletion should succeed
        assert delete_result["success"] == True
        
        # And session should no longer exist
        sessions = self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        session_ids = [s["session_id"] for s in sessions]
        assert session_id not in session_ids
        
    def test_sessions_should_show_actual_message_count_not_zero(self):
        """
        Test Issue 2: Sessions showing 0 messages despite having content
        Testing that get_previous_sessions returns correct message counts
        """
        # Given: Create session with actual messages
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add multiple messages
        self.conversation_service.add_message_to_session(session_id, "user", "첫 번째 질문", self.test_user_id)
        self.conversation_service.add_message_to_session(session_id, "assistant", "첫 번째 답변", self.test_user_id)
        self.conversation_service.add_message_to_session(session_id, "user", "두 번째 질문", self.test_user_id)
        self.conversation_service.add_message_to_session(session_id, "assistant", "두 번째 답변", self.test_user_id)
        
        # When: Get previous sessions
        sessions = self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        
        # Then: Should find the session with correct message count
        found_session = next((s for s in sessions if s["session_id"] == session_id), None)
        assert found_session is not None
        assert found_session["message_count"] == 4  # Should not be 0!
        
    def test_current_chat_should_save_messages_to_session(self):
        """
        Test Issue 3: Messages not being saved when leaving chat
        Testing that the current chat flow actually saves messages
        
        This test simulates what should happen when user sends message in current chat:
        1. User starts conversation via regular chat
        2. Messages get exchanged
        3. Session is automatically created and messages saved
        4. User can return later and see the session in previous sessions list
        """
        # GIVEN: User starts a chat conversation (simulating the current flow)
        # We need to simulate what should happen in the chat endpoint
        
        # Step 1: Create a session (this should happen automatically in chat)
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Step 2: Add messages to the session (this should happen in chat endpoint)
        self.conversation_service.add_message_to_session(
            session_id, "user", "안녕하세요, 파이썬 질문이 있어요", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "안녕하세요! 파이썬 질문을 언제든지 말씀해주세요.", self.test_user_id
        )
        
        # WHEN: User leaves and comes back (checking previous sessions)
        previous_sessions = self.conversation_service.get_previous_sessions(
            self.test_user_id, self.test_character_id
        )
        
        # THEN: Session should exist with the messages
        found_session = next((s for s in previous_sessions if s["session_id"] == session_id), None)
        assert found_session is not None, "Session should be found in previous sessions"
        assert found_session["message_count"] == 2, f"Expected 2 messages, got {found_session['message_count']}"
        
        # AND: Session should have meaningful summary data
        assert "session_summary" in found_session, "Session should have session_summary field"
        assert found_session.get("last_message_pair"), "Session should have last message pair"
        
        # AND: Last message pair should contain the conversation
        last_pair = found_session["last_message_pair"]
        assert last_pair.get("user_message") == "안녕하세요, 파이썬 질문이 있어요"
        assert last_pair.get("assistant_message") == "안녕하세요! 파이썬 질문을 언제든지 말씀해주세요."