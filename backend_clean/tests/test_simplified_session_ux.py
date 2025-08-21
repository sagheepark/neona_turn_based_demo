"""
TDD Test Group 8: Simplified Session UX
RED PHASE: Write failing tests for simplified session requirements
"""

import pytest
import json
from services.chat_orchestrator import ChatOrchestrator

class TestSimplifiedSessionUX:
    def setup_method(self):
        self.chat_orchestrator = ChatOrchestrator()
        self.test_user_id = "test_user_simplified_ux"  # Unique user ID for these tests
        self.test_character_id = "dr_python"
        
    def test_should_restore_exact_session_state_when_continuing(self):
        """
        Test 8.1: Session continuation should restore exact state
        FAILING - Currently shows full history, need only last states
        """
        # Given: User had conversation with multiple exchanges
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # Simulate conversation with final state
        messages = [
            ("user", "첫 번째 질문"),
            ("assistant", "첫 번째 답변"),
            ("user", "두 번째 질문"),
            ("assistant", "두 번째 답변"),
            ("user", "마지막 질문입니다"),  # Last user input
            ("assistant", "마지막 답변입니다. 추가 질문이 있으면 언제든지 물어보세요!")  # Last AI output
        ]
        
        for role, content in messages:
            self.chat_orchestrator.conversation_service.add_message_to_session(
                session_id, role, content, self.test_user_id
            )
        
        # When: Continue session
        continued_session = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        
        # Then: Should provide exact last state for restoration
        assert "last_user_input" in continued_session
        assert "last_ai_output" in continued_session
        assert continued_session["last_user_input"] == "마지막 질문입니다"
        assert continued_session["last_ai_output"] == "마지막 답변입니다. 추가 질문이 있으면 언제든지 물어보세요!"
        
        # And: Should NOT require full message history for UI
        # Frontend should only use last states, not full messages array
        assert len(continued_session["session"]["messages"]) == 6  # Backend keeps full history
        
    def test_should_detect_sessions_for_modal_trigger(self):
        """
        Test 8.2: Should detect when user has previous sessions
        Backend should provide session existence check
        """
        # Given: Fresh user with no previous sessions initially
        import uuid
        fresh_user_id = f"test_user_modal_trigger_check_{uuid.uuid4().hex[:8]}"
        sessions_empty = self.chat_orchestrator.get_session_summaries(
            fresh_user_id, self.test_character_id
        )
        assert len(sessions_empty) == 0
        
        # When: User creates and uses a session
        session_result = self.chat_orchestrator.create_new_session(
            fresh_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # Add at least one user input (to make it saveable)
        self.chat_orchestrator.conversation_service.add_message_to_session(
            session_id, "user", "안녕하세요", fresh_user_id
        )
        
        # Then: Should detect previous sessions
        sessions_with_content = self.chat_orchestrator.get_session_summaries(
            fresh_user_id, self.test_character_id
        )
        assert len(sessions_with_content) == 1
        assert sessions_with_content[0]["message_count"] >= 1
        
        # Frontend can use this to decide whether to show modal
        
    def test_should_prepare_new_session_state_for_greeting(self):
        """
        Test 8.3: New conversation should prepare clean state for greeting
        When user chooses "Start New", should reset to initial state
        """
        # Given: User has previous sessions but chooses new conversation
        # This tests the backend's ability to provide clean session state
        
        # When: Create new session (simulating "Start New Chat")
        new_session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        
        # Then: Should provide clean session state
        new_session = new_session_result["session"]
        assert new_session["message_count"] == 0
        assert len(new_session["messages"]) == 0
        assert new_session["status"] == "active"
        
        # And: Should indicate this is a fresh session (for greeting trigger)
        assert "session_id" in new_session
        assert new_session["session_id"].startswith("sess_")
        
        # Frontend should detect empty session and trigger greeting
        
    def test_session_auto_save_capability(self):
        """
        Test 8.4: Backend should support session auto-save functionality
        Tests that sessions persist when user makes input
        """
        # Given: Fresh session created
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # When: User makes first input (auto-save trigger point)
        self.chat_orchestrator.conversation_service.add_message_to_session(
            session_id, "user", "첫 번째 입력", self.test_user_id
        )
        
        # Then: Session should be discoverable in summaries
        sessions = self.chat_orchestrator.get_session_summaries(
            self.test_user_id, self.test_character_id
        )
        
        saved_session = None
        for session in sessions:
            if session["session_id"] == session_id:
                saved_session = session
                break
                
        assert saved_session is not None
        assert saved_session["message_count"] >= 1
        
        # And: Should be continuable
        continued = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        assert continued["session"]["session_id"] == session_id
        assert len(continued["session"]["messages"]) >= 1