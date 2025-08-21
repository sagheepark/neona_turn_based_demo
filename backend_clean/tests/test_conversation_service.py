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


class TestConversationService:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_shouldCreateNewConversationSession(self):
        """
        RED PHASE: Write failing test for conversation session creation
        
        Test that conversation service can create new sessions with unique IDs
        and proper metadata for user-character pairs.
        """
        # Given: Conversation service
        service = ConversationService()
        
        # When: Create new session
        session = service.create_session(
            user_id="user_123",
            character_id="dr_python", 
            persona_id="persona_student"
        )
        
        # Then: Returns session with unique ID and metadata
        assert session is not None, "Should return a session object"
        assert isinstance(session, dict), "Session should be a dictionary"
        
        # Check required fields
        assert "session_id" in session, "Session should have session_id"
        assert "user_id" in session, "Session should have user_id"
        assert "character_id" in session, "Session should have character_id"
        assert "persona_id" in session, "Session should have persona_id"
        assert "created_at" in session, "Session should have created_at timestamp"
        assert "status" in session, "Session should have status"
        assert "messages" in session, "Session should have messages array"
        assert "message_count" in session, "Session should have message_count"
        
        # Verify field values
        assert session["session_id"] is not None, "Session ID should not be None"
        assert len(session["session_id"]) > 0, "Session ID should not be empty"
        assert session["user_id"] == "user_123", "User ID should match input"
        assert session["character_id"] == "dr_python", "Character ID should match input"
        assert session["persona_id"] == "persona_student", "Persona ID should match input"
        assert session["status"] == "active", "New session should be active"
        assert isinstance(session["messages"], list), "Messages should be a list"
        assert len(session["messages"]) == 0, "New session should have no messages"
        assert session["message_count"] == 0, "New session should have zero message count"
        
        # Verify session ID format (should contain timestamp and unique identifier)
        session_id = session["session_id"]
        assert session_id.startswith("sess_"), "Session ID should start with 'sess_'"
        assert len(session_id) > 10, "Session ID should be reasonably long for uniqueness"
    
    def test_shouldCreateUniqueSessionIds(self):
        """
        Test that multiple session creations produce unique session IDs
        """
        # Given: Conversation service
        service = ConversationService()
        
        # When: Create multiple sessions
        session1 = service.create_session("user_123", "dr_python", "persona_student")
        session2 = service.create_session("user_123", "dr_python", "persona_student")
        session3 = service.create_session("user_456", "yoon_ahri", "persona_worker")
        
        # Then: All sessions should have unique IDs
        session_ids = [session1["session_id"], session2["session_id"], session3["session_id"]]
        unique_ids = set(session_ids)
        
        assert len(unique_ids) == 3, "All session IDs should be unique"
        assert session1["session_id"] != session2["session_id"], "Sessions should have different IDs even with same parameters"
    
    def test_shouldPersistSessionToFile(self):
        """
        Test that created sessions are persisted to the file system
        """
        # Given: Conversation service
        service = ConversationService()
        
        # When: Create new session
        session = service.create_session("user_789", "dr_python", "persona_beginner")
        
        # Then: Session file should exist
        session_id = session["session_id"]
        expected_path = Path("conversations/user_789/dr_python") / f"{session_id}.json"
        
        assert expected_path.exists(), f"Session file should exist at {expected_path}"
        
        # Verify file contents
        with open(expected_path, 'r', encoding='utf-8') as f:
            saved_session = json.load(f)
        
        assert saved_session["session_id"] == session["session_id"], "Saved session should match created session"
        assert saved_session["user_id"] == "user_789", "Saved session should have correct user_id"
        assert saved_session["character_id"] == "dr_python", "Saved session should have correct character_id"
    
    def test_shouldRetrievePreviousSessionsForUserAndCharacter(self):
        """
        RED PHASE: Write failing test for session retrieval
        
        Test that conversation service can retrieve previous sessions for a user-character pair,
        with the last Q&A context needed for resuming conversations.
        """
        # Given: Conversation service with multiple sessions
        service = ConversationService()
        
        # Create some test sessions with different combinations
        session1 = service.create_session("user_123", "dr_python", "persona_student")
        session2 = service.create_session("user_123", "dr_python", "persona_worker") 
        session3 = service.create_session("user_123", "yoon_ahri", "persona_student")
        session4 = service.create_session("user_456", "dr_python", "persona_student")
        
        # Add some messages to sessions to test last Q&A retrieval
        # Simulate adding messages (we'll need add_message method)
        session1_with_messages = service.add_message_to_session(
            session1["session_id"], 
            "user", 
            "Python 변수가 뭔가요?",
            "user_123"
        )
        
        session1_with_messages = service.add_message_to_session(
            session1["session_id"],
            "assistant", 
            "Python에서 변수는 데이터를 저장하는 공간입니다. name = '김파이썬' 이런 식으로 사용합니다.",
            "user_123"
        )
        
        # When: Retrieve sessions for user_123 and dr_python
        sessions = service.get_previous_sessions("user_123", "dr_python")
        
        # Then: Returns list of sessions with summaries and last Q&A context
        assert isinstance(sessions, list), "Should return a list of sessions"
        assert len(sessions) == 2, "Should return 2 sessions for user_123 + dr_python"
        
        # Check that sessions contain required fields for resuming
        for session in sessions:
            assert "session_id" in session, "Session should have session_id"
            assert "created_at" in session, "Session should have created_at"
            assert "last_updated" in session, "Session should have last_updated"
            assert "message_count" in session, "Session should have message_count"
            assert "session_summary" in session, "Session should have session_summary"
            assert "last_message_pair" in session, "Session should have last Q&A pair for resuming"
            
            # Verify user and character match
            assert session["user_id"] == "user_123", "Should match requested user"
            assert session["character_id"] == "dr_python", "Should match requested character"
        
        # Find the session with messages and verify last Q&A
        session_with_messages = next((s for s in sessions if s["message_count"] > 0), None)
        assert session_with_messages is not None, "Should find session with messages"
        
        last_qa = session_with_messages["last_message_pair"]
        assert "user_message" in last_qa, "Should have last user message"
        assert "assistant_message" in last_qa, "Should have last assistant message"
        assert "Python 변수가 뭔가요?" in last_qa["user_message"], "Should contain actual user question"
        assert "변수는 데이터를 저장" in last_qa["assistant_message"], "Should contain actual assistant answer"
        
        # Sessions should be ordered by last_updated (most recent first)
        if len(sessions) > 1:
            for i in range(len(sessions) - 1):
                curr_time = sessions[i]["last_updated"]
                next_time = sessions[i + 1]["last_updated"]
                assert curr_time >= next_time, "Sessions should be ordered by last_updated (newest first)"
    
    def test_shouldReturnEmptyListWhenNoSessionsExist(self):
        """
        Test that retrieval returns empty list when no sessions exist for user-character pair
        """
        # Given: Conversation service with no sessions
        service = ConversationService()
        
        # When: Try to retrieve sessions for non-existent combination
        sessions = service.get_previous_sessions("nonexistent_user", "nonexistent_character")
        
        # Then: Should return empty list
        assert isinstance(sessions, list), "Should return a list"
        assert len(sessions) == 0, "Should return empty list when no sessions exist"
    
    def test_shouldLoadPreviousMessagesWhenContinuingSession(self):
        """
        RED PHASE: Write failing test for loading session messages
        
        Test that conversation service can load previous messages when continuing 
        an existing session, supporting the requirement that "when user chooses to 
        resume the last question and answer should be shown".
        """
        # Given: Conversation service with an existing session containing messages
        service = ConversationService()
        
        # Create session and add multiple messages to simulate conversation history
        session = service.create_session("user_456", "dr_python", "persona_advanced")
        session_id = session["session_id"]
        
        # Add a conversation with multiple exchanges
        service.add_message_to_session(session_id, "user", "Python에서 리스트와 튜플의 차이점이 뭔가요?", "user_456")
        service.add_message_to_session(session_id, "assistant", "리스트는 변경 가능하고 튜플은 변경 불가능합니다.", "user_456")
        service.add_message_to_session(session_id, "user", "그럼 언제 튜플을 사용하나요?", "user_456") 
        service.add_message_to_session(session_id, "assistant", "딕셔너리의 키로 사용하거나 데이터가 변경되지 않아야 할 때 사용합니다.", "user_456")
        service.add_message_to_session(session_id, "user", "예시를 보여주세요", "user_456")
        
        # When: Load previous messages for session continuation
        loaded_session = service.load_session_messages(session_id, "user_456")
        
        # Then: Returns complete session with all messages in chronological order
        assert loaded_session is not None, "Should return session data"
        assert isinstance(loaded_session, dict), "Session should be a dictionary"
        
        # Verify session metadata
        assert loaded_session["session_id"] == session_id, "Should match requested session ID"
        assert loaded_session["user_id"] == "user_456", "Should match session user"
        assert loaded_session["character_id"] == "dr_python", "Should match session character"
        
        # Verify message loading
        messages = loaded_session.get("messages", [])
        assert len(messages) == 5, "Should load all 5 messages from the conversation"
        
        # Check message chronological order and content integrity
        assert messages[0]["role"] == "user", "First message should be from user"
        assert messages[0]["content"] == "Python에서 리스트와 튜플의 차이점이 뭔가요?", "First message content should match"
        
        assert messages[1]["role"] == "assistant", "Second message should be from assistant"
        assert "리스트는 변경 가능" in messages[1]["content"], "Assistant response should match"
        
        assert messages[4]["role"] == "user", "Last message should be from user"
        assert messages[4]["content"] == "예시를 보여주세요", "Last message content should match"
        
        # Verify message metadata
        for i, message in enumerate(messages):
            assert "id" in message, f"Message {i} should have an ID"
            assert "role" in message, f"Message {i} should have a role"
            assert "content" in message, f"Message {i} should have content"
            assert "timestamp" in message, f"Message {i} should have timestamp"
            
            # Messages should be in chronological order
            if i > 0:
                prev_time = messages[i-1]["timestamp"]
                curr_time = message["timestamp"]
                assert curr_time >= prev_time, f"Message {i} should be chronologically after message {i-1}"
        
        # Verify the last Q&A pair is easily accessible (supporting resume requirement)
        assert "last_message_pair" in loaded_session, "Should include last Q&A pair for resuming"
        last_qa = loaded_session["last_message_pair"]
        assert last_qa["user_message"] == "예시를 보여주세요", "Should capture the last user question"
        assert "딕셔너리의 키로 사용" in last_qa["assistant_message"], "Should capture the last assistant answer"
    
    def test_shouldSaveMessageToExistingSession(self):
        """
        RED PHASE: Write failing test for message saving to existing sessions
        
        Test that conversation service can append new messages to existing sessions
        and properly update session metadata. This is critical for ongoing conversations.
        """
        # Given: Conversation service with an existing session
        service = ConversationService()
        
        # Create initial session
        session = service.create_session("user_789", "dr_python", "persona_beginner")
        session_id = session["session_id"]
        initial_message_count = session["message_count"]
        initial_updated_time = session["last_updated"]
        
        # Add an initial message
        service.add_message_to_session(session_id, "user", "Python은 어떤 언어인가요?", "user_789")
        
        # When: Add another message to the same session
        import time
        time.sleep(0.01)  # Ensure timestamp difference
        
        updated_session = service.add_message_to_session(
            session_id, 
            "assistant", 
            "Python은 간단하고 배우기 쉬운 프로그래밍 언어입니다.", 
            "user_789"
        )
        
        # Then: Message should be appended and metadata updated
        assert updated_session is not None, "Should return updated session"
        assert isinstance(updated_session, dict), "Updated session should be a dictionary"
        
        # Verify session metadata updates
        assert updated_session["session_id"] == session_id, "Session ID should remain the same"
        assert updated_session["user_id"] == "user_789", "User ID should remain the same"
        assert updated_session["message_count"] == 2, "Message count should be updated to 2"
        assert updated_session["last_updated"] > initial_updated_time, "Last updated time should be newer"
        
        # Verify message was properly added
        messages = updated_session["messages"]
        assert len(messages) == 2, "Should have 2 messages total"
        
        # Check first message
        first_msg = messages[0]
        assert first_msg["role"] == "user", "First message should be from user"
        assert first_msg["content"] == "Python은 어떤 언어인가요?", "First message content should match"
        assert "id" in first_msg, "First message should have ID"
        assert "timestamp" in first_msg, "First message should have timestamp"
        
        # Check second message (the newly added one)
        second_msg = messages[1]
        assert second_msg["role"] == "assistant", "Second message should be from assistant"
        assert second_msg["content"] == "Python은 간단하고 배우기 쉬운 프로그래밍 언어입니다.", "Second message content should match"
        assert "id" in second_msg, "Second message should have ID"
        assert "timestamp" in second_msg, "Second message should have timestamp"
        
        # Verify message ordering (chronological)
        assert second_msg["timestamp"] >= first_msg["timestamp"], "Messages should be in chronological order"
        
        # Verify message IDs are sequential
        assert first_msg["id"] == "msg_001", "First message should have ID msg_001"
        assert second_msg["id"] == "msg_002", "Second message should have ID msg_002"
        
        # Verify persistence: Load session from file and check it matches
        loaded_session = service.load_session_messages(session_id, "user_789")
        assert len(loaded_session["messages"]) == 2, "Persisted session should have 2 messages"
        assert loaded_session["message_count"] == 2, "Persisted session should have correct count"
        assert loaded_session["messages"][1]["content"] == "Python은 간단하고 배우기 쉬운 프로그래밍 언어입니다.", "Persisted message should match"
        
        # Verify security: Wrong user should not be able to add messages
        try:
            service.add_message_to_session(session_id, "user", "Unauthorized message", "wrong_user")
            assert False, "Should have raised ValueError for unauthorized user"
        except ValueError as e:
            assert "does not have access" in str(e), "Should prevent unauthorized access"