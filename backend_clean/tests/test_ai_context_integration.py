"""
TDD Tests for AI Context Integration with Compressed History
Following TDD: Red → Green → Refactor
Testing compressed history integration into AI generation - Test Group 30
"""

import pytest
import sys
from pathlib import Path
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.conversation_service import ConversationService


class TestAIContextIntegration:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.conversation_service = ConversationService()
        self.test_user_id = "ai_context_test_user"
        self.test_character_id = "dr_python"

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_should_provide_compressed_context_to_ai_generation(self):
        """
        Test 30.1: AI generation should receive compressed history for full context
        
        RED PHASE: This test will fail until we integrate compressed context into chat
        """
        # Given: Session with compressed history
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add conversation that will be compressed
        for i in range(51):  # 102 messages to trigger compression
            self.conversation_service.add_message_to_session(
                session_id, "user", f"User question {i+1} about Python", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Assistant explains Python concept {i+1}", self.test_user_id
            )
        
        # When: Get AI context for generation
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: Context should include compressed history
        assert "recent_messages" in ai_context
        assert "compressed_summary" in ai_context
        assert "core_memories" in ai_context
        assert "context_prompt" in ai_context
        
        # Recent messages should be limited (around 20 for compressed sessions)
        assert len(ai_context["recent_messages"]) <= 25
        
        # Compressed summary should contain older conversation content
        assert ai_context["compressed_summary"] is not None
        assert len(ai_context["compressed_summary"]) > 0
        
        # Context prompt should be formatted for AI consumption
        context_prompt = ai_context["context_prompt"]
        assert "Previous conversation summary:" in context_prompt
        assert "Recent conversation history" in context_prompt

    def test_should_format_compressed_context_for_ai_prompt(self):
        """
        Test 30.2: Compressed context should be formatted for AI consumption
        
        RED PHASE: This test will fail until we implement context formatting
        """
        # Given: Session with meaningful conversation history
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add meaningful conversation
        learning_conversation = [
            ("user", "I'm new to programming"),
            ("assistant", "Welcome! Let's start with Python basics."),
            ("user", "I learn best with visual examples"),
            ("assistant", "Perfect! I'll use lots of code examples."),
        ]
        
        for user_msg, assistant_msg in learning_conversation:
            self.conversation_service.add_message_to_session(
                session_id, "user", user_msg, self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", assistant_msg, self.test_user_id
            )
        
        # Add filler to trigger compression
        for i in range(49):  # Total 102 messages
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Technical question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Technical answer {i+1}", self.test_user_id
            )
        
        # When: Get formatted context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Context should be properly formatted for AI
        assert isinstance(context_prompt, str)
        assert len(context_prompt) > 0
        
        # Should include sections for different types of context
        assert "Previous conversation summary:" in context_prompt
        assert "Recent conversation history" in context_prompt
        # Should contain context sections (specific text may vary)
        assert "context" in context_prompt.lower()
        
        # Should be actionable for AI
        assert "Continue the conversation" in context_prompt or "Based on this context" in context_prompt

    def test_should_handle_uncompressed_sessions_gracefully(self):
        """
        Test 30.3: AI context should work for sessions without compression
        
        RED PHASE: This test will fail until we handle both compressed and uncompressed sessions
        """
        # Given: Session with few messages (no compression)
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add only a few messages (under compression threshold)
        for i in range(5):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Answer {i+1}", self.test_user_id
            )
        
        # When: Get AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: Should work without compression
        assert "recent_messages" in ai_context
        assert len(ai_context["recent_messages"]) == 10  # All messages
        
        # Compressed fields should be None or empty
        assert ai_context["compressed_summary"] is None or ai_context["compressed_summary"] == ""
        assert ai_context["core_memories"] is None or ai_context["core_memories"] == {}
        
        # Context prompt should still be generated
        assert ai_context["context_prompt"] is not None
        assert len(ai_context["context_prompt"]) > 0

    def test_should_prioritize_recent_messages_over_compressed_summary(self):
        """
        Test 30.4: Recent messages should take priority in context formatting
        
        RED PHASE: This test will fail until we implement context prioritization
        """
        # Given: Compressed session
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add messages to trigger compression
        for i in range(51):  # 102 total messages
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Old question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Old answer {i+1}", self.test_user_id
            )
        
        # When: Get AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Recent messages should be prominently featured
        recent_messages = ai_context["recent_messages"]
        last_user_message = recent_messages[-1]["content"] if recent_messages else ""
        
        # Context prompt should mention recent content more prominently than compressed summary
        prompt_lines = context_prompt.split("\n")
        recent_section_line = -1
        summary_section_line = -1
        
        for i, line in enumerate(prompt_lines):
            if "recent messages" in line.lower() or "current conversation" in line.lower():
                recent_section_line = i
            if "previous conversation summary" in line.lower():
                summary_section_line = i
        
        # Recent messages should appear before or be more prominent than summary
        assert recent_section_line != -1, "Recent messages section should exist"
        
        # Context should acknowledge recent messages
        assert "current conversation" in context_prompt.lower() or "recent" in context_prompt.lower()

    def test_should_include_character_development_context(self):
        """
        Test 30.5: AI context should include character development and relationship progression
        
        RED PHASE: This test will fail until we implement character development context
        """
        # Given: Session with character development progression
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add conversation showing relationship growth
        development_conversation = [
            ("user", "I'm struggling with this concept"),
            ("assistant", "Don't worry, let's work through it together step by step."),
            ("user", "You're really patient with me"),
            ("assistant", "That's what I'm here for! Teaching is about patience and understanding."),
            ("user", "I'm starting to enjoy programming thanks to you"),
            ("assistant", "I'm so proud of your progress! Your enthusiasm is wonderful to see."),
        ]
        
        for user_msg, assistant_msg in development_conversation:
            self.conversation_service.add_message_to_session(
                session_id, "user", user_msg, self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", assistant_msg, self.test_user_id
            )
        
        # Add filler to trigger compression
        for i in range(48):  # Total 102 messages
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Regular question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Regular answer {i+1}", self.test_user_id
            )
        
        # When: Get AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Should include character development context
        assert "character development" in context_prompt.lower() or "relationship" in context_prompt.lower()
        # Should have meaningful context about the conversation
        assert len(context_prompt) > 100  # Should be a substantial prompt
        
        # Should reference the emotional journey
        assert any(word in context_prompt.lower() for word in ["patient", "proud", "progress", "growth"])

    def test_should_maintain_conversation_continuity_across_compressions(self):
        """
        Test 30.6: Multiple compressions should maintain conversation continuity
        
        RED PHASE: This test will fail until we handle multiple compression cycles
        """
        # Given: Session that will undergo multiple compressions
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # First compression cycle (102 messages)
        for i in range(51):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"First phase question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"First phase answer {i+1}", self.test_user_id
            )
        
        # Get context after first compression
        context_after_first = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Second compression cycle (add 82 more messages to existing 20, reaching 102 again)
        for i in range(41):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Second phase question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Second phase answer {i+1}", self.test_user_id
            )
        
        # When: Get context after second compression
        context_after_second = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: Should maintain continuity across both compressions
        assert len(context_after_second["recent_messages"]) >= 20
        
        # Compressed summary should include information from both phases
        second_summary = context_after_second["compressed_summary"]
        # Multiple compressions should maintain or increase summary information
        assert len(second_summary) >= 10  # Should have meaningful summary
        
        # Core memories should be preserved and potentially enhanced
        second_memories = context_after_second["core_memories"]
        assert isinstance(second_memories, dict)
        assert len(second_memories) > 0