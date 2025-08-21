"""
TDD Tests for Session Continuation State Management
RED PHASE: Write failing tests for the session continuation issues
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import json
from services.conversation_service import ConversationService

class TestSessionContinuationStateManagement:
    def setup_method(self):
        self.conversation_service = ConversationService()
        self.test_user_id = "test_user_continuation"
        self.test_character_id = "test_character_continuation"
        
    def test_should_maintain_active_session_after_continuation(self):
        """
        Test 13.1: Session continuation should maintain active session
        
        RED PHASE: This test fails because session continuation creates new session
        instead of maintaining the continued session as active
        """
        # Given: User has an existing session with messages
        initial_session = self.conversation_service.create_session(
            self.test_user_id, 
            self.test_character_id, 
            "test_persona_id"
        )
        
        # Add some messages to the session
        self.conversation_service.add_message_to_session(
            initial_session["session_id"],
            "user",
            "Hello, this is my first message",
            self.test_user_id
        )
        
        self.conversation_service.add_message_to_session(
            initial_session["session_id"], 
            "assistant",
            "Hello! Nice to meet you.",
            self.test_user_id
        )
        
        # When: Session is continued (frontend would call this with existing session_id)
        continued_session = self.conversation_service.continue_session(initial_session["session_id"])
        
        # Then: The continued session should maintain the same session_id
        assert continued_session["session_id"] == initial_session["session_id"], \
            "Continued session should maintain same session_id"
        
        # And: Backend should recognize this as the active session for subsequent messages
        # This simulates what happens when user makes first input after continuing
        try:
            # This should NOT create a new session - should use existing one
            updated_session = self.conversation_service.add_message_to_session(
                continued_session["session_id"],
                "user", 
                "This is my second message after continuing",
                self.test_user_id
            )
            
            # Verify it's still the same session
            assert updated_session["session_id"] == initial_session["session_id"], \
                "Should update existing session, not create new one"
            
            # Verify message count increased (not reset to 1)
            assert len(updated_session["messages"]) == 3, \
                "Should have 3 messages total (2 initial + 1 new)"
            
            print("✅ GREEN PHASE: Session continuation maintains active session correctly")
            return  # Test passes
            
        except Exception as e:
            print(f"🔴 RED PHASE: Session continuation issue - {str(e)}")
        
        # EXPECTED FAILURE: Current system likely creates new session after continuation
        # This test documents the requirement for maintaining session state
        assert False, "Session continuation should maintain active session, not create new one"
        
    def test_should_prevent_duplicate_session_creation_after_continuation(self):
        """
        Test 13.1b: Verify no duplicate sessions created after continuation
        
        RED PHASE: This test fails because system creates multiple sessions
        instead of updating the continued session
        """
        # Given: User starts with one session
        initial_session = self.conversation_service.create_session(
            self.test_user_id, 
            self.test_character_id, 
            "test_persona_id"
        )
        
        initial_sessions_count = len(
            self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        )
        
        # When: User continues session and makes input (simulating frontend behavior)
        continued_session = self.conversation_service.continue_session(initial_session["session_id"])
        
        # Simulate first user input after continuation - this should NOT create new session
        self.conversation_service.add_message_to_session(
            continued_session["session_id"],
            "user",
            "First message after continuation",
            self.test_user_id
        )
        
        # Then: Session count should remain the same
        final_sessions_count = len(
            self.conversation_service.get_previous_sessions(self.test_user_id, self.test_character_id)
        )
        
        assert final_sessions_count == initial_sessions_count, \
            f"Session count should remain {initial_sessions_count}, got {final_sessions_count}. No duplicate sessions should be created."
            
        print("✅ Session continuation does not create duplicate sessions")