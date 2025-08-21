"""
TDD Tests for Conversation Memory Compression (Phase 2)
Following TDD: Red → Green → Refactor
Testing basic compression at 100 messages threshold - Test Group 28
"""

import pytest
import sys
from pathlib import Path
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.conversation_service import ConversationService

class TestConversationCompression:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.conversation_service = ConversationService()
        self.test_user_id = "compression_test_user"
        self.test_character_id = "dr_python"

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_should_not_compress_sessions_under_100_messages(self):
        """
        Test 28.1: Sessions with <100 messages should not trigger compression
        
        RED PHASE: This test will fail until we implement compression logic
        """
        # Given: Session with 50 messages (under threshold)
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 50 messages
        for i in range(25):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"User message {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Assistant response {i+1}", self.test_user_id
            )
        
        # When: Check if session needs compression
        needs_compression = self.conversation_service.should_compress_session(session_id, self.test_user_id)
        
        # Then: Should not need compression
        assert needs_compression == False
        
        # And: Session should have no compression metadata
        session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        assert "compressed_history" not in session
        assert "compression_metadata" not in session

    def test_should_compress_sessions_over_100_messages(self):
        """
        Test 28.2: Sessions with 100+ messages should trigger compression
        
        RED PHASE: This test will fail until we implement compression logic
        """
        # Given: Session with 120 messages (over threshold)
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 120 messages (60 exchanges)
        for i in range(60):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"User message {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Assistant response {i+1}", self.test_user_id
            )
        
        # When: Check if session needs compression
        needs_compression = self.conversation_service.should_compress_session(session_id, self.test_user_id)
        
        # Then: Should need compression
        assert needs_compression == True

    def test_should_keep_last_20_messages_raw_after_compression(self):
        """
        Test 28.3: Compression should preserve last 20 messages as raw
        
        RED PHASE: This test will fail until we implement compression
        """
        # Given: Session with 120 messages
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 120 messages with identifiable content
        for i in range(60):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"User message {i+1} about Python topic", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Assistant explains Python concept {i+1}", self.test_user_id
            )
        
        # When: Apply compression
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Session should have exactly 20 raw messages
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        assert len(compressed_session["messages"]) == 20
        
        # And: Last messages should be the most recent ones
        last_message = compressed_session["messages"][-1]
        assert "concept 60" in last_message["content"]  # Should be the last assistant message
        
        first_retained_message = compressed_session["messages"][0]
        assert "51" in first_retained_message["content"]  # Should be message from 51st exchange

    def test_should_create_conversation_summary_for_compressed_messages(self):
        """
        Test 28.4: Compression should create summary of older messages
        
        RED PHASE: This test will fail until we implement compression
        """
        # Given: Session with 120 messages with story progression
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add messages with story elements
        story_messages = [
            ("user", "I'm new to Python, can you help me?"),
            ("assistant", "Of course! I'm Dr. Python, your programming mentor. Let's start with basics."),
            ("user", "What are variables?"),
            ("assistant", "Variables are containers for storing data. Like boxes with labels!"),
            ("user", "I'm getting confused with syntax errors"),
            ("assistant", "Don't worry, everyone makes syntax errors. Let me show you common ones."),
        ]
        
        # Add these story messages plus filler to reach 120 total
        for user_msg, assistant_msg in story_messages:
            self.conversation_service.add_message_to_session(session_id, "user", user_msg, self.test_user_id)
            self.conversation_service.add_message_to_session(session_id, "assistant", assistant_msg, self.test_user_id)
        
        # Add filler messages to reach 120 total
        for i in range(54):  # 6 story messages + 114 filler = 120 total
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Filler user message {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Filler assistant response {i+1}", self.test_user_id
            )
        
        # When: Apply compression
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Should have compressed history with summary
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        assert "compressed_history" in compressed_session
        
        compressed_history = compressed_session["compressed_history"]
        assert "conversation_summary" in compressed_history
        assert isinstance(compressed_history["conversation_summary"], str)
        assert len(compressed_history["conversation_summary"]) > 0

    def test_should_extract_core_memories_during_compression(self):
        """
        Test 28.5: Compression should extract core memories about relationships
        
        RED PHASE: This test will fail until we implement core memory extraction
        """
        # Given: Session with relationship-building messages
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add messages with relationship elements
        relationship_messages = [
            ("user", "I'm a complete beginner and feel overwhelmed"),
            ("assistant", "That's completely normal! I was once a beginner too. We'll take it slow."),
            ("user", "You're really patient with me, thank you"),
            ("assistant", "That's what I'm here for! I remember my first programming struggles."),
            ("user", "I prefer learning with visual examples"),
            ("assistant", "Perfect! I'll make sure to use lots of diagrams and code examples."),
        ]
        
        for user_msg, assistant_msg in relationship_messages:
            self.conversation_service.add_message_to_session(session_id, "user", user_msg, self.test_user_id)
            self.conversation_service.add_message_to_session(session_id, "assistant", assistant_msg, self.test_user_id)
        
        # Add filler to reach compression threshold
        for i in range(54):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Technical question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Technical answer {i+1}", self.test_user_id
            )
        
        # When: Apply compression
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Should have core memories extracted
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        compressed_history = compressed_session["compressed_history"]
        
        assert "core_memories" in compressed_history
        core_memories = compressed_history["core_memories"]
        
        # Should contain relationship insights
        assert isinstance(core_memories, dict)
        assert "user_learning_style" in core_memories
        assert "relationship_dynamic" in core_memories

    def test_should_preserve_story_continuity_elements(self):
        """
        Test 28.6: Compression should preserve story and character development
        
        RED PHASE: This test will fail until we implement story preservation
        """
        # Given: Session with character development progression
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add messages showing character evolution
        story_progression = [
            ("user", "I failed my first program"),
            ("assistant", "Failure is the first step to success! Let me help you debug."),
            ("user", "Wow, that actually worked! You're amazing at explaining"),
            ("assistant", "You did the hard work! I'm proud of your persistence."),
            ("user", "I'm starting to really enjoy programming now"),
            ("assistant", "That's wonderful! Your confidence has grown so much since we started."),
        ]
        
        for user_msg, assistant_msg in story_progression:
            self.conversation_service.add_message_to_session(session_id, "user", user_msg, self.test_user_id)
            self.conversation_service.add_message_to_session(session_id, "assistant", assistant_msg, self.test_user_id)
        
        # Add filler to reach compression threshold
        for i in range(54):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Regular question {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Regular answer {i+1}", self.test_user_id
            )
        
        # When: Apply compression
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Should preserve story elements
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        compressed_history = compressed_session["compressed_history"]
        
        assert "story_continuity" in compressed_history
        story_continuity = compressed_history["story_continuity"]
        
        assert isinstance(story_continuity, dict)
        assert "character_development" in story_continuity
        assert "user_progression" in story_continuity
        assert "emotional_journey" in story_continuity

    def test_should_create_compression_metadata(self):
        """
        Test 28.7: Compression should create metadata for tracking
        
        RED PHASE: This test will fail until we implement compression metadata
        """
        # Given: Session that needs compression
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 120 messages
        for i in range(60):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Message {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Response {i+1}", self.test_user_id
            )
        
        # When: Apply compression
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Should have compression metadata
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        assert "compression_metadata" in compressed_session
        metadata = compressed_session["compression_metadata"]
        
        assert "original_message_count" in metadata
        assert "compression_date" in metadata
        assert "compression_ratio" in metadata
        
        # Verify metadata values
        assert metadata["original_message_count"] == 100  # 120 total - 20 kept = 100 compressed
        assert "100:1" in metadata["compression_ratio"]
        
        # Verify compression date is recent
        compression_date = datetime.fromisoformat(metadata["compression_date"])
        assert compression_date > datetime.now() - timedelta(minutes=1)

    def test_should_handle_multiple_compressions_gracefully(self):
        """
        Test 28.8: Multiple compressions should work correctly
        
        RED PHASE: This test will fail until we implement compression logic
        """
        # Given: Session that has been compressed once
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Add 120 messages and compress
        for i in range(60):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"First batch {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"First response {i+1}", self.test_user_id
            )
        
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Add 120 more messages (40 more, for 160 total)
        for i in range(40):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"Second batch {i+1}", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"Second response {i+1}", self.test_user_id
            )
        
        # When: Apply compression again
        self.conversation_service.compress_session_if_needed(session_id, self.test_user_id)
        
        # Then: Should handle second compression
        compressed_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        
        # Should still have 20 raw messages (most recent)
        assert len(compressed_session["messages"]) == 20
        
        # Should have updated compression metadata
        metadata = compressed_session["compression_metadata"]
        assert metadata["original_message_count"] > 100  # Should account for multiple compressions
        
        # Should preserve both compression histories
        compressed_history = compressed_session["compressed_history"]
        assert "conversation_summary" in compressed_history
        assert len(compressed_history["conversation_summary"]) > 0