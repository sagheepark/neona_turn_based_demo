"""
TDD Test Group 9: Critical Session Flow Fixes
RED PHASE: Write failing tests for reported critical issues
"""

import pytest
import json
from services.chat_orchestrator import ChatOrchestrator

class TestCriticalSessionFlowFixes:
    def setup_method(self):
        self.chat_orchestrator = ChatOrchestrator()
        self.test_user_id = "test_user_critical_fixes"
        self.test_character_id = "dr_python"
        
    def test_should_properly_persist_messages_after_conversation(self):
        """
        Test 9.1: Session messages should persist properly after user inputs and outputs
        FAILING - Sessions show 0 messages despite conversation happening
        """
        # Given: User starts new session
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # When: User has conversation with 2 exchanges (4 messages total)
        # First exchange
        self.chat_orchestrator.process_message(
            session_id, self.test_user_id, "첫 번째 질문입니다", self.test_character_id
        )
        self.chat_orchestrator.save_ai_response(
            session_id, self.test_user_id, "첫 번째 답변입니다", []
        )
        
        # Second exchange  
        self.chat_orchestrator.process_message(
            session_id, self.test_user_id, "두 번째 질문입니다", self.test_character_id
        )
        self.chat_orchestrator.save_ai_response(
            session_id, self.test_user_id, "두 번째 답변입니다", []
        )
        
        # Then: Session should show correct message count when user returns
        sessions = self.chat_orchestrator.get_session_summaries(
            self.test_user_id, self.test_character_id
        )
        
        # Find our session
        our_session = None
        for session in sessions:
            if session["session_id"] == session_id:
                our_session = session
                break
                
        assert our_session is not None, "Session should be found in summaries"
        assert our_session["message_count"] == 4, f"Expected 4 messages, got {our_session['message_count']}"
        assert our_session["message_count"] > 0, "Session should not show 0 messages after conversation"
        
        # And: Session continuation should load actual messages
        continued_session = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        assert len(continued_session["session"]["messages"]) == 4
        assert continued_session["last_user_input"] == "두 번째 질문입니다"
        assert continued_session["last_ai_output"] == "두 번째 답변입니다"
        
    def test_should_support_fresh_session_creation_for_greeting(self):
        """
        Test 9.2: New session creation should support greeting generation
        Tests backend capability to provide clean session for frontend greeting
        """
        # Given: Fresh session creation (simulating "Start New Chat")
        fresh_session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        
        # Then: Should provide completely clean session state
        fresh_session = fresh_session_result["session"]
        assert fresh_session["message_count"] == 0
        assert len(fresh_session["messages"]) == 0
        assert fresh_session["status"] == "active"
        
        # And: Should be ready for greeting generation
        # Frontend should detect empty session and trigger greeting
        assert "session_id" in fresh_session
        assert fresh_session["session_id"].startswith("sess_")
        
        # When: Greeting message is added (simulating frontend greeting generation)
        greeting_message = "안녕하세요! 저는 파이썬 튜터입니다."
        self.chat_orchestrator.conversation_service.add_message_to_session(
            fresh_session["session_id"], "assistant", greeting_message, self.test_user_id
        )
        
        # Then: Session should now have the greeting
        updated_session = self.chat_orchestrator.continue_session(
            fresh_session["session_id"], self.test_user_id
        )
        assert len(updated_session["session"]["messages"]) == 1
        assert updated_session["session"]["messages"][0]["role"] == "assistant"
        assert updated_session["session"]["messages"][0]["content"] == greeting_message
        
    def test_should_handle_mixed_session_types(self):
        """
        Test 9.3: Should distinguish between empty sessions and sessions with content
        Critical for modal display logic
        """
        # Given: Multiple sessions - some empty, some with content
        
        # Create empty session (never used)
        empty_session = self.chat_orchestrator.create_new_session(
            self.test_user_id, self.test_character_id, None
        )
        
        # Create session with content
        content_session = self.chat_orchestrator.create_new_session(
            self.test_user_id, self.test_character_id, None  
        )
        content_session_id = content_session["session"]["session_id"]
        
        # Add content to one session
        self.chat_orchestrator.conversation_service.add_message_to_session(
            content_session_id, "user", "Hello", self.test_user_id
        )
        self.chat_orchestrator.conversation_service.add_message_to_session(
            content_session_id, "assistant", "Hi there!", self.test_user_id
        )
        
        # When: Get session summaries
        summaries = self.chat_orchestrator.get_session_summaries(
            self.test_user_id, self.test_character_id
        )
        
        # Then: Should be able to distinguish content vs empty sessions
        content_sessions = [s for s in summaries if s["message_count"] > 0]
        assert len(content_sessions) >= 1, "Should have at least one session with content"
        
        # Content session should be properly identified
        our_content_session = None
        for session in content_sessions:
            if session["session_id"] == content_session_id:
                our_content_session = session
                break
                
        assert our_content_session is not None
        assert our_content_session["message_count"] == 2