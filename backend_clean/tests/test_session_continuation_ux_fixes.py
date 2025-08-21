"""
TDD Test Group 7: Session Continuation UX Fixes
RED PHASE: Write failing tests for session continuation issues
"""

import pytest
import json
from services.chat_orchestrator import ChatOrchestrator

class TestSessionContinuationUXFixes:
    def setup_method(self):
        self.chat_orchestrator = ChatOrchestrator()
        self.test_user_id = "demo_user"
        self.test_character_id = "dr_python"
        
    def test_should_display_previous_messages_when_continuing_session(self):
        """
        Test 7.1: Session continuation should display previous chat messages
        FAILING - Messages loaded in state but not displayed in UI
        """
        # Given: Create session with multiple messages
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # Add several messages to simulate conversation
        messages = [
            ("user", "안녕하세요, 파이썬을 배우고 싶어요"),
            ("assistant", "안녕! 파이썬을 배우고 싶구나?"),
            ("user", "뭐라고"),
            ("assistant", "어이, 잼민이! 무슨 일이야?"),
            ("user", "안녕하세요"),
            ("assistant", "안녕 잰민이! 코딩 배우고 싶구나?")
        ]
        
        for role, content in messages:
            self.chat_orchestrator.conversation_service.add_message_to_session(
                session_id, role, content, self.test_user_id
            )
        
        # When: Continue session (this loads messages for frontend)
        continued_session = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        
        # Then: All messages should be available for UI display
        assert len(continued_session["session"]["messages"]) == 6
        assert continued_session["session"]["messages"][0]["content"] == "안녕하세요, 파이썬을 배우고 싶어요"
        assert continued_session["session"]["messages"][-1]["content"] == "안녕 잰민이! 코딩 배우고 싶구나?"
        
        # And: Last Q&A pair should be extracted for UI
        assert "last_qa" in continued_session
        assert continued_session["last_qa"]["user_message"] == "안녕하세요"
        assert "잰민이" in continued_session["last_qa"]["assistant_message"]
        
    def test_should_provide_tts_audio_data_when_continuing_session(self):
        """
        Test 7.2: Session continuation should provide TTS audio capability
        FAILING - No audio playback after continuation
        """
        # Given: Session with last assistant message
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # Add messages ending with assistant message
        self.chat_orchestrator.conversation_service.add_message_to_session(
            session_id, "user", "안녕하세요", self.test_user_id
        )
        self.chat_orchestrator.conversation_service.add_message_to_session(
            session_id, "assistant", "안녕! 반가워!", self.test_user_id
        )
        
        # When: Continue session
        continued_session = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        
        # Then: Should provide last assistant message for TTS generation
        last_message = continued_session["session"]["messages"][-1]
        assert last_message["role"] == "assistant"
        assert last_message["content"] == "안녕! 반가워!"
        
        # And: Should have character_id available for TTS voice selection
        assert continued_session["session"]["character_id"] == self.test_character_id
        
        # NOTE: Actual TTS generation will be handled in frontend
        # This test ensures backend provides necessary data for TTS
        
    def test_session_continuation_flow_integration(self):
        """
        Test 7.3: Complete session continuation integration
        Tests the full flow from session creation to continuation
        """
        # Given: Session with conversation history
        session_result = self.chat_orchestrator.create_new_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_result["session"]["session_id"]
        
        # Simulate conversation
        self.chat_orchestrator.process_message(
            session_id, self.test_user_id, "파이썬 기초를 알려주세요", self.test_character_id
        )
        
        # When: Get sessions for modal display
        sessions = self.chat_orchestrator.get_session_summaries(
            self.test_user_id, self.test_character_id
        )
        
        # Then: Session should appear with message count
        assert len(sessions) > 0
        found_session = None
        for session in sessions:
            if session["session_id"] == session_id:
                found_session = session
                break
        
        assert found_session is not None
        assert found_session["message_count"] > 0
        
        # And: When continuing, should load all conversation data
        continued = self.chat_orchestrator.continue_session(session_id, self.test_user_id)
        assert continued["session"]["message_count"] == found_session["message_count"]
        assert len(continued["session"]["messages"]) == found_session["message_count"]