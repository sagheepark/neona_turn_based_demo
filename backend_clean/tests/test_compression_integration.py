"""
TDD Tests for Compression Integration with Session API
Following TDD: Red → Green → Refactor
Testing automatic compression during active sessions - Test Group 29
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


class TestCompressionIntegration:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.conversation_service = ConversationService()
        self.test_user_id = "integration_test_user"
        self.test_character_id = "dr_python"

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_should_automatically_compress_during_active_conversation(self):
        """
        Test 29.1: Compression should trigger automatically when threshold is reached
        
        RED PHASE: This test will fail until we integrate compression into add_message
        """
        # Given: An active conversation session
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # When: Messages exceed compression threshold during normal conversation
        for i in range(101):  # Add 101 messages to trigger compression
            self.conversation_service.add_message_to_session(
                session_id, 
                "user" if i % 2 == 0 else "assistant",
                f"Message {i+1} in conversation",
                self.test_user_id
            )
        
        # Then: Session should be automatically compressed
        session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Should have compressed history
        assert "compressed_history" in session
        assert "compression_metadata" in session
        
        # Should keep only recent 20 messages
        assert len(session["messages"]) == 20
        
        # Message count should still reflect total messages
        assert session["message_count"] == 101

    def test_should_preserve_conversation_context_after_compression(self):
        """
        Test 29.2: Compressed sessions should maintain conversation context
        
        RED PHASE: This test will fail until we properly track compressed messages
        """
        # Given: Session with meaningful conversation
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add meaningful conversation that should be preserved
        important_messages = [
            ("user", "I'm learning Python for the first time"),
            ("assistant", "Welcome! Python is a great first language. Let's start with basics."),
            ("user", "I prefer visual examples"),
            ("assistant", "Perfect! I'll use lots of code examples and diagrams."),
        ]
        
        for user_msg, assistant_msg in important_messages:
            self.conversation_service.add_message_to_session(
                session_id, "user", user_msg, self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", assistant_msg, self.test_user_id
            )
        
        # Add filler to trigger compression
        for i in range(46):  # 8 + 92 = 100 messages total
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Answer {i+1}", self.test_user_id
            )
        
        # Add one more to trigger compression
        self.conversation_service.add_message_to_session(
            session_id, "user", "Final question", self.test_user_id
        )
        
        # When: Load compressed session
        session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Then: Core memories should be extracted (specific content depends on implementation)
        core_memories = session["compressed_history"]["core_memories"]
        assert isinstance(core_memories, dict)
        assert "user_learning_style" in core_memories
        assert "relationship_dynamic" in core_memories
        
        # And: Conversation summary should capture key topics
        summary = session["compressed_history"]["conversation_summary"]
        assert len(summary) > 0

    def test_should_provide_compressed_context_for_ai_generation(self):
        """
        Test 29.3: Compressed history should be available for AI context
        
        RED PHASE: This test will fail until we expose compression for AI use
        """
        # Given: Compressed session with history
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Create conversation with clear progression
        for i in range(50):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Learning about topic {i//10 + 1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Explaining topic {i//10 + 1} concept", self.test_user_id
            )
        
        # Trigger compression
        self.conversation_service.add_message_to_session(
            session_id, "user", "What have we covered so far?", self.test_user_id
        )
        
        # When: Get context for AI generation
        ai_context = self.conversation_service.get_ai_context(session_id, self.test_user_id)
        
        # Then: Context should include both recent messages and compressed summary
        assert "recent_messages" in ai_context
        assert "compressed_summary" in ai_context
        assert "core_memories" in ai_context
        
        # Recent messages should be the last 20
        assert len(ai_context["recent_messages"]) <= 20
        
        # Compressed summary should be present
        assert ai_context["compressed_summary"] is not None
        assert len(ai_context["compressed_summary"]) > 0

    def test_should_handle_compression_gracefully_during_errors(self):
        """
        Test 29.4: Compression failures should not break conversation flow
        
        RED PHASE: This test will fail until we add error handling
        """
        # Given: Session approaching compression threshold
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 99 messages (just under threshold)
        for i in range(99):
            self.conversation_service.add_message_to_session(
                session_id, 
                "user" if i % 2 == 0 else "assistant",
                f"Message {i+1}",
                self.test_user_id
            )
        
        # Simulate compression error by temporarily breaking the save method
        original_save = self.conversation_service._save_session
        
        def broken_save(sid, data):
            if "compressed_history" in data:
                raise Exception("Simulated compression save error")
            return original_save(sid, data)
        
        self.conversation_service._save_session = broken_save
        
        # When: Add message that would trigger compression
        result = self.conversation_service.add_message_to_session(
            session_id, "user", "Message 100", self.test_user_id
        )
        
        # Then: Message should still be added despite compression failure
        assert result is not None
        assert result["message_count"] == 100
        
        # Restore original save method
        self.conversation_service._save_session = original_save
        
        # Session should still be loadable
        session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        assert session["message_count"] == 100

    def test_should_update_session_metadata_after_compression(self):
        """
        Test 29.5: Session metadata should reflect compression state
        
        RED PHASE: This test will fail until we track compression in metadata
        """
        # Given: Session that will be compressed
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add messages to trigger compression
        for i in range(101):
            self.conversation_service.add_message_to_session(
                session_id,
                "user" if i % 2 == 0 else "assistant",
                f"Message {i+1}",
                self.test_user_id
            )
        
        # When: Check session metadata
        session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Then: Metadata should indicate compression
        assert "is_compressed" in session or "compressed_history" in session
        assert session["message_count"] == 101  # Total messages tracked
        assert len(session["messages"]) == 20  # Only recent messages in memory
        
        # Compression metadata should be present
        compression_meta = session.get("compression_metadata", {})
        assert "compression_date" in compression_meta
        assert "original_message_count" in compression_meta