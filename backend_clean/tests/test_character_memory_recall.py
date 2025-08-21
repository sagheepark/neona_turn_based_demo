"""
TDD Test for Character Memory Recall in Real Conversation Scenarios
Following TDD: Red → Green → Refactor
Testing that characters actually remember previous conversations - Test Group 31
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


class TestCharacterMemoryRecall:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.conversation_service = ConversationService()
        self.test_user_id = "memory_test_user"
        self.test_character_id = "dr_python"

    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_character_should_remember_user_name_when_asked(self):
        """
        Test 31.1: Character should remember user's name from earlier in conversation
        
        RED PHASE: This test will fail if memory recall isn't working properly
        """
        # Given: A conversation where user introduces themselves
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # User introduces themselves
        self.conversation_service.add_message_to_session(
            session_id, "user", "안녕하세요! 제 이름은 김철수입니다.", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "안녕하세요 김철수님! 만나서 반갑습니다.", self.test_user_id
        )
        
        # Some general conversation
        self.conversation_service.add_message_to_session(
            session_id, "user", "파이썬을 배우고 싶어요", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "좋은 선택이에요! 파이썬은 배우기 쉬운 언어입니다.", self.test_user_id
        )
        
        # When: User asks if character remembers their name
        self.conversation_service.add_message_to_session(
            session_id, "user", "제 이름을 기억하고 계시나요?", self.test_user_id
        )
        
        # Get enhanced AI context (this should include the name mention)
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        
        # Then: The context should contain the user's name in conversation history
        context_prompt = ai_context["context_prompt"]
        recent_messages = ai_context["recent_messages"]
        
        # Verify name appears in recent message history
        has_name_in_history = False
        for msg in recent_messages:
            if "김철수" in msg.get("content", ""):
                has_name_in_history = True
                break
        
        assert has_name_in_history, "User's name should be preserved in conversation history"
        assert "김철수" in context_prompt, "User's name should appear in AI context prompt"

    def test_character_should_remember_specific_conversation_details(self):
        """
        Test 31.2: Character should remember specific details mentioned earlier
        
        RED PHASE: This test will fail if detailed conversation memory isn't working
        """
        # Given: A conversation with specific details
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # User shares specific details
        conversation_history = [
            ("user", "저는 서울에 살고 있고, 대학교에서 컴퓨터과학을 전공하고 있어요"),
            ("assistant", "서울 대학생이시군요! 컴퓨터과학 전공이라면 파이썬이 많이 도움될 거예요."),
            ("user", "네, 특히 데이터 분석에 관심이 많아요"),
            ("assistant", "데이터 분석은 파이썬의 강점 중 하나예요! pandas와 numpy를 배우시면 좋을 것 같아요."),
            ("user", "그런데 저는 시각적으로 배우는 걸 선호해요"),
            ("assistant", "그렇다면 matplotlib으로 그래프를 그려보는 것부터 시작하시면 어떨까요?")
        ]
        
        for user_msg, assistant_msg in conversation_history:
            self.conversation_service.add_message_to_session(
                session_id, "user", user_msg, self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", assistant_msg, self.test_user_id
            )
        
        # When: User asks about what they discussed
        self.conversation_service.add_message_to_session(
            session_id, "user", "우리가 이전에 뭘 이야기했는지 기억하세요?", self.test_user_id
        )
        
        # Get enhanced AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Context should contain the specific details
        assert "서울" in context_prompt, "Should remember user lives in Seoul"
        assert "컴퓨터과학" in context_prompt or "컴퓨터" in context_prompt, "Should remember user's major"
        assert "데이터 분석" in context_prompt or "데이터" in context_prompt, "Should remember user's interest"
        assert "시각적" in context_prompt, "Should remember user's learning preference"

    def test_character_should_remember_across_multiple_messages(self):
        """
        Test 31.3: Character should maintain context across many messages
        
        RED PHASE: This test will fail if context isn't maintained properly
        """
        # Given: A longer conversation
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Initial context establishment
        self.conversation_service.add_message_to_session(
            session_id, "user", "저는 웹 개발자가 되고 싶어요", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "웹 개발자는 멋진 목표네요! 어떤 부분에 관심이 있으세요?", self.test_user_id
        )
        
        # Add many intervening messages
        for i in range(10):
            self.conversation_service.add_message_to_session(
                session_id, "user", f"질문 {i+1}: 파이썬 기본 문법에 대해 알려주세요", self.test_user_id
            )
            self.conversation_service.add_message_to_session(
                session_id, "assistant", f"답변 {i+1}: 파이썬의 기본 문법을 설명해드릴게요.", self.test_user_id
            )
        
        # When: Ask about original goal
        self.conversation_service.add_message_to_session(
            session_id, "user", "제가 처음에 말했던 목표를 기억하세요?", self.test_user_id
        )
        
        # Get enhanced AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        recent_messages = ai_context["recent_messages"]
        
        # Then: Should still contain reference to web development goal
        # Either in recent messages or in conversation summary if compressed
        has_web_dev_context = (
            "웹 개발" in context_prompt or 
            any("웹 개발" in msg.get("content", "") for msg in recent_messages)
        )
        
        assert has_web_dev_context, "Should remember user's web development goal"

    def test_context_prompt_format_includes_actual_messages(self):
        """
        Test 31.4: Verify context prompt actually includes message content
        
        RED PHASE: This test will fail if context prompt doesn't include actual conversation
        """
        # Given: A simple conversation
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        test_user_message = "안녕하세요, 파이썬을 배우고 싶습니다"
        test_assistant_message = "안녕하세요! 파이썬 학습을 도와드리겠습니다"
        
        self.conversation_service.add_message_to_session(
            session_id, "user", test_user_message, self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", test_assistant_message, self.test_user_id
        )
        
        # When: Get AI context
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Context prompt should include the actual message content
        assert "Recent conversation history" in context_prompt, "Should have conversation history section"
        assert test_user_message in context_prompt, "Should include actual user message"
        assert test_assistant_message in context_prompt, "Should include actual assistant message"
        assert "User:" in context_prompt, "Should format with User: prefix"
        assert "Assistant:" in context_prompt, "Should format with Assistant: prefix"

    def test_memory_works_with_session_continuation(self):
        """
        Test 31.5: Memory should work when continuing existing sessions
        
        RED PHASE: This test will fail if session continuation doesn't preserve memory
        """
        # Given: An existing conversation session
        session_data = self.conversation_service.create_session(
            self.test_user_id,
            self.test_character_id,
            None
        )
        session_id = session_data["session_id"]
        
        # Initial conversation
        self.conversation_service.add_message_to_session(
            session_id, "user", "제 이름은 박영희이고, 머신러닝을 공부하고 있어요", self.test_user_id
        )
        self.conversation_service.add_message_to_session(
            session_id, "assistant", "박영희님, 머신러닝 공부를 응원합니다!", self.test_user_id
        )
        
        # Simulate session continuation (like user coming back later)
        continued_session = self.conversation_service.load_session_messages(session_id, self.test_user_id)
        assert continued_session["session_id"] == session_id
        
        # Add new message to continued session
        self.conversation_service.add_message_to_session(
            session_id, "user", "제가 전에 말했던 공부 주제를 기억하세요?", self.test_user_id
        )
        
        # When: Get enhanced AI context for continued session
        ai_context = self.conversation_service.get_enhanced_ai_context(session_id, self.test_user_id)
        context_prompt = ai_context["context_prompt"]
        
        # Then: Should remember both name and study topic
        assert "박영희" in context_prompt, "Should remember user's name from previous session"
        assert "머신러닝" in context_prompt, "Should remember user's study topic from previous session"