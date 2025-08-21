"""
TDD Test for Character Persona Independence
Following TDD: Red → Green → Refactor
Testing that each character maintains independent persona and greetings - Test Group 32
"""

import pytest
import sys
from pathlib import Path
import os
import json
import tempfile
import shutil

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.conversation_service import ConversationService


class TestCharacterPersonaIndependence:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.conversation_service = ConversationService()
        self.test_user_id = "persona_test_user"

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_different_characters_should_have_different_personas(self):
        """
        Test 32.1: Different characters should maintain their own persona prompts
        
        RED PHASE: This test will fail if character personas are getting mixed up
        """
        # Given: Two different characters with distinct personas
        dr_python_prompt = """
        name: Dr. Python
        personality: Patient, friendly programming teacher
        speaking_style: Clear explanations in Korean
        role: Programming instructor
        """
        
        yoon_ahri_prompt = """
        name: 윤아리
        personality: Aggressive, grumpy forest creature
        speaking_style: Rough, uses "Krrr" sounds
        role: Forest guardian
        """
        
        # When: Get AI context for Dr. Python
        dr_session = self.conversation_service.create_session(
            self.test_user_id, "dr_python", None
        )
        dr_session_id = dr_session["session_id"]
        
        self.conversation_service.add_message_to_session(
            dr_session_id, "user", "안녕하세요", self.test_user_id
        )
        
        dr_context = self.conversation_service.get_enhanced_ai_context(
            dr_session_id, self.test_user_id
        )
        
        # When: Get AI context for Yoon Ahri  
        ahri_session = self.conversation_service.create_session(
            self.test_user_id, "yoon_ahri", None
        )
        ahri_session_id = ahri_session["session_id"]
        
        self.conversation_service.add_message_to_session(
            ahri_session_id, "user", "안녕하세요", self.test_user_id
        )
        
        ahri_context = self.conversation_service.get_enhanced_ai_context(
            ahri_session_id, self.test_user_id
        )
        
        # Then: Contexts should be independent
        # Note: The character prompt is passed separately in the API call
        # The context should only contain conversation history, not mixed personas
        assert dr_context != ahri_context  # Different contexts for different characters
        
        # Each should have their own recent messages
        assert len(dr_context["recent_messages"]) >= 1
        assert len(ahri_context["recent_messages"]) >= 1
        
        # Sessions should be different
        assert dr_session_id != ahri_session_id

    def test_character_context_should_not_contain_persona_data(self):
        """
        Test 32.2: Enhanced AI context should only contain conversation memory, not character persona
        
        RED PHASE: This test will fail if persona data is mixed into conversation context
        """
        # Given: A character session
        session_data = self.conversation_service.create_session(
            self.test_user_id, "dr_python", None
        )
        session_id = session_data["session_id"]
        
        self.conversation_service.add_message_to_session(
            session_id, "user", "Hello", self.test_user_id
        )
        
        # When: Get enhanced AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: Context should only contain conversation elements, not character persona
        expected_keys = {"recent_messages", "compressed_summary", "core_memories", "context_prompt"}
        actual_keys = set(ai_context.keys())
        
        assert actual_keys == expected_keys, f"Unexpected keys in context: {actual_keys - expected_keys}"
        
        # Context prompt should not contain character persona directly
        context_prompt = ai_context.get("context_prompt", "")
        
        # Should contain conversation context
        assert "Recent conversation history" in context_prompt or "messages" in context_prompt.lower()
        
        # Should NOT contain character-specific persona (that's passed separately)
        # Character name/personality should NOT be in the conversation context
        assert "Dr. Python" not in context_prompt
        assert "Patient, friendly" not in context_prompt

    def test_memory_context_should_be_session_specific(self):
        """
        Test 32.3: Memory context should be specific to each session, not shared
        
        RED PHASE: This test will fail if sessions are sharing memory context
        """
        # Given: Two separate sessions for the same character
        session1_data = self.conversation_service.create_session(
            self.test_user_id, "dr_python", None
        )
        session1_id = session1_data["session_id"]
        
        session2_data = self.conversation_service.create_session(
            self.test_user_id, "dr_python", None  
        )
        session2_id = session2_data["session_id"]
        
        # Add different messages to each session
        self.conversation_service.add_message_to_session(
            session1_id, "user", "I like cats", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session1_id, "assistant", "Cats are great pets!", self.test_user_id
        )
        
        self.conversation_service.add_message_to_session(
            session2_id, "user", "I like dogs", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session2_id, "assistant", "Dogs are wonderful companions!", self.test_user_id
        )
        
        # When: Get context for both sessions
        context1 = self.conversation_service.get_enhanced_ai_context(session1_id, self.test_user_id)
        context2 = self.conversation_service.get_enhanced_ai_context(session2_id, self.test_user_id)
        
        # Then: Contexts should be different and session-specific
        assert context1 != context2
        
        # Session 1 should contain "cats" but not "dogs"
        context1_prompt = context1.get("context_prompt", "")
        assert "cats" in context1_prompt.lower()
        assert "dogs" not in context1_prompt.lower()
        
        # Session 2 should contain "dogs" but not "cats"
        context2_prompt = context2.get("context_prompt", "")
        assert "dogs" in context2_prompt.lower()
        assert "cats" not in context2_prompt.lower()

    def test_conversation_memory_should_work_with_any_character_prompt(self):
        """
        Test 32.4: Memory system should work regardless of character persona
        
        RED PHASE: This test will fail if memory is tied to specific character types
        """
        # Given: A session with a custom character
        session_data = self.conversation_service.create_session(
            self.test_user_id, "custom_character", None
        )
        session_id = session_data["session_id"]
        
        # Add conversation with memory elements
        self.conversation_service.add_message_to_session(
            session_id, "user", "My name is Alice and I study physics", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "Nice to meet you Alice! Physics is fascinating.", self.test_user_id
        )
        
        self.conversation_service.add_message_to_session(
            session_id, "user", "Do you remember my name and field?", self.test_user_id
        )
        
        # When: Get enhanced AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: Memory should work independent of character
        context_prompt = ai_context.get("context_prompt", "")
        
        # Should contain the actual conversation
        assert "Alice" in context_prompt
        assert "physics" in context_prompt
        assert "Recent conversation history" in context_prompt
        
        # Recent messages should be preserved
        recent_messages = ai_context.get("recent_messages", [])
        assert len(recent_messages) >= 3
        
        # Should find the user's name in the messages
        has_name = any("Alice" in msg.get("content", "") for msg in recent_messages)
        assert has_name, "User name should be preserved in recent messages"

    def test_memory_context_should_not_leak_between_characters(self):
        """
        Test 32.5: Memory from one character should not leak to another
        
        RED PHASE: This test will fail if character memory is being shared incorrectly
        """
        # Given: Conversations with two different characters
        session1_data = self.conversation_service.create_session(
            self.test_user_id, "character_a", None
        )
        session1_id = session1_data["session_id"]
        
        session2_data = self.conversation_service.create_session(
            self.test_user_id, "character_b", None
        )
        session2_id = session2_data["session_id"]
        
        # Add specific conversation to character A
        self.conversation_service.add_message_to_session(
            session1_id, "user", "I told you about my secret hobby: collecting stamps", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session1_id, "assistant", "Yes, stamp collecting is a wonderful hobby!", self.test_user_id
        )
        
        # Add different conversation to character B  
        self.conversation_service.add_message_to_session(
            session2_id, "user", "Hello there", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session2_id, "assistant", "Hello! How can I help you?", self.test_user_id
        )
        
        # When: Get context for character B
        context_b = self.conversation_service.get_enhanced_ai_context(session2_id, self.test_user_id)
        
        # Then: Character B should not have access to character A's memory
        context_b_prompt = context_b.get("context_prompt", "")
        
        # Should NOT contain information from character A's conversation
        assert "stamps" not in context_b_prompt.lower()
        assert "collecting" not in context_b_prompt.lower()
        assert "secret hobby" not in context_b_prompt.lower()
        
        # Should only contain character B's own conversation
        assert "Hello there" in context_b_prompt or "Hello!" in context_b_prompt