import pytest
import sys
from pathlib import Path
import os
import json
import tempfile
import shutil

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent.parent))

from services.knowledge_service import KnowledgeService
from services.conversation_service import ConversationService
from services.persona_service import PersonaService


class TestIntegration:
    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Setup test knowledge base for dr_python
        self._setup_test_knowledge()
    
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _setup_test_knowledge(self):
        """Create test knowledge base for integration tests"""
        knowledge_dir = Path("knowledge/characters/dr_python")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        test_knowledge = {
            "character_id": "dr_python",
            "knowledge_items": [
                {
                    "id": "k_variables",
                    "title": "Python 변수와 데이터 타입",
                    "content": "Python에서 변수는 데이터를 저장하는 공간입니다. name = '김파이썬' 처럼 사용합니다.",
                    "trigger_keywords": ["변수", "variable", "데이터타입"],
                    "tags": ["기초", "syntax"],
                    "priority": 8
                },
                {
                    "id": "k_functions",
                    "title": "Python 함수 정의와 사용",
                    "content": "함수는 def 키워드로 정의합니다. def greet(name): return f'안녕하세요 {name}님!'",
                    "trigger_keywords": ["함수", "function", "def"],
                    "tags": ["기초", "함수"],
                    "priority": 9
                }
            ]
        }
        
        with open(knowledge_dir / "knowledge.json", 'w', encoding='utf-8') as f:
            json.dump(test_knowledge, f, ensure_ascii=False, indent=2)
    
    def test_shouldHandleFullConversationWithKnowledgeAndPersona(self):
        """
        RED PHASE: Write failing test for complete conversation flow
        
        Test that all three systems (Knowledge + Conversation + Persona) work together
        in a realistic conversation scenario where a student asks Dr. Python about programming.
        """
        # Given: All three services initialized
        knowledge_service = KnowledgeService()
        conversation_service = ConversationService()
        persona_service = PersonaService()
        
        # Create student persona for context-aware responses
        student_persona = {
            "name": "프로그래밍 초보 학생",
            "description": "Python을 처음 배우는 컴퓨터공학과 1학년",
            "attributes": {
                "age": "19세",
                "occupation": "대학생 (컴퓨터공학과 1학년)",
                "personality": "호기심 많음, 차근차근 배우고 싶어함",
                "speaking_style": "존댓말, 예의바름",
                "background": "프로그래밍 첫 수업, Python 기초 학습 중",
                "current_mood": "배우고 싶어서 설렘"
            }
        }
        
        created_persona = persona_service.create_persona("student_001", student_persona)
        persona_service.set_active_persona("student_001", created_persona["id"])
        
        # Create conversation session
        session = conversation_service.create_session(
            user_id="student_001",
            character_id="dr_python", 
            persona_id=created_persona["id"]
        )
        session_id = session["session_id"]
        
        # When: Simulate complete conversation flow
        
        # Step 1: Student asks about variables
        user_question = "Python에서 변수가 뭔가요?"
        conversation_service.add_message_to_session(session_id, "user", user_question, "student_001")
        
        # System finds relevant knowledge
        relevant_knowledge = knowledge_service.search_relevant_knowledge(user_question, "dr_python", max_results=2)
        
        # System gets persona context
        persona_context = persona_service.generate_persona_context("student_001")
        
        # Simulate AI response generation (this would normally go through LLM)
        ai_response = self._generate_mock_ai_response(user_question, relevant_knowledge, persona_context)
        conversation_service.add_message_to_session(session_id, "assistant", ai_response, "student_001")
        
        # Step 2: Follow-up question about functions
        follow_up_question = "그럼 함수는 어떻게 만들어요?"
        conversation_service.add_message_to_session(session_id, "user", follow_up_question, "student_001")
        
        follow_up_knowledge = knowledge_service.search_relevant_knowledge(follow_up_question, "dr_python", max_results=2)
        follow_up_response = self._generate_mock_ai_response(follow_up_question, follow_up_knowledge, persona_context)
        conversation_service.add_message_to_session(session_id, "assistant", follow_up_response, "student_001")
        
        # Then: Verify integrated system behavior
        
        # 1. Knowledge retrieval should work correctly
        assert len(relevant_knowledge) > 0, "Should find relevant knowledge for variables"
        assert any("변수" in item.get("title", "") for item in relevant_knowledge), "Should find variable-related knowledge"
        
        assert len(follow_up_knowledge) > 0, "Should find relevant knowledge for functions"
        assert any("함수" in item.get("title", "") for item in follow_up_knowledge), "Should find function-related knowledge"
        
        # 2. Persona context should be generated
        assert len(persona_context) > 0, "Should generate persona context"
        assert "프로그래밍 초보" in persona_context, "Context should include persona name"
        assert "19세" in persona_context, "Context should include age"
        assert "컴퓨터공학과" in persona_context, "Context should include major"
        
        # 3. Conversation should be persisted correctly
        loaded_session = conversation_service.load_session_messages(session_id, "student_001")
        messages = loaded_session["messages"]
        assert len(messages) == 4, "Should have 4 messages (2 questions + 2 responses)"
        
        # Check message content and flow
        assert messages[0]["role"] == "user", "First message should be user"
        assert "변수" in messages[0]["content"], "First question should be about variables"
        
        assert messages[1]["role"] == "assistant", "Second message should be assistant"
        assert len(messages[1]["content"]) > 10, "AI response should be substantial"
        
        assert messages[2]["role"] == "user", "Third message should be user follow-up"
        assert "함수" in messages[2]["content"], "Follow-up should be about functions"
        
        assert messages[3]["role"] == "assistant", "Fourth message should be assistant response"
        
        # 4. Last Q&A should be properly extracted for resume feature
        last_qa = loaded_session["last_message_pair"]
        assert "함수" in last_qa["user_message"], "Last user message should be about functions"
        assert len(last_qa["assistant_message"]) > 0, "Last assistant message should exist"
        
        # 5. Session metadata should be updated
        assert loaded_session["message_count"] == 4, "Message count should be accurate"
        assert loaded_session["character_id"] == "dr_python", "Character should be Dr. Python"
        assert loaded_session["user_id"] == "student_001", "User should be student_001"
    
    def _generate_mock_ai_response(self, question: str, knowledge_items: list, persona_context: str) -> str:
        """
        Mock AI response generation that incorporates knowledge and persona context
        (In real implementation, this would be sent to LLM)
        """
        # Simulate how AI would use knowledge and persona context
        response_parts = []
        
        if knowledge_items:
            # Use knowledge content
            primary_knowledge = knowledge_items[0]
            knowledge_content = primary_knowledge.get("content", "")
            response_parts.append(knowledge_content)
        
        # Adapt response based on persona (beginner student)
        if "초보" in persona_context and "19세" in persona_context:
            response_parts.append("초보자분께 쉽게 설명드리면,")
            
        if "변수" in question:
            response_parts.append("예를 들어 age = 19 라고 하면 age라는 변수에 19라는 값이 저장됩니다.")
        elif "함수" in question:
            response_parts.append("예를 들어 인사하는 함수를 만들어보세요: def say_hello(): print('안녕하세요!')")
        
        return " ".join(response_parts)
    
    def test_shouldOfferSessionContinuationAtChatStart(self):
        """
        RED PHASE: Write failing test for session continuation flow
        
        Test that when a user starts a new chat, the system can offer to continue
        a previous session and show the last Q&A pair as requested.
        """
        # Given: Services and existing conversation history
        conversation_service = ConversationService()
        persona_service = PersonaService()
        
        # Create persona and previous session
        persona = persona_service.create_persona("returning_user", {
            "name": "복습하는 학생",
            "description": "이전 학습 내용을 복습하고 싶어하는 학생"
        })
        persona_service.set_active_persona("returning_user", persona["id"])
        
        # Create previous session with conversation history
        previous_session = conversation_service.create_session(
            user_id="returning_user",
            character_id="dr_python",
            persona_id=persona["id"]
        )
        prev_session_id = previous_session["session_id"]
        
        # Add conversation history to previous session
        conversation_service.add_message_to_session(prev_session_id, "user", "리스트와 딕셔너리의 차이점을 알려주세요", "returning_user")
        conversation_service.add_message_to_session(prev_session_id, "assistant", "리스트는 순서가 있는 데이터 모음이고, 딕셔너리는 키-값 쌍으로 저장하는 데이터 구조입니다.", "returning_user")
        conversation_service.add_message_to_session(prev_session_id, "user", "실제 예제를 보여주실 수 있나요?", "returning_user")
        conversation_service.add_message_to_session(prev_session_id, "assistant", "네! 리스트 예제: fruits = ['사과', '바나나', '오렌지'], 딕셔너리 예제: person = {'이름': '김파이썬', '나이': 25}", "returning_user")
        
        # When: User starts new chat session (chat start simulation)
        previous_sessions = conversation_service.get_previous_sessions("returning_user", "dr_python")
        
        # Then: System should offer session continuation with last Q&A context
        
        # 1. Should find previous sessions
        assert len(previous_sessions) > 0, "Should find previous sessions"
        assert len(previous_sessions) == 1, "Should find exactly 1 previous session"
        
        latest_session = previous_sessions[0]
        
        # 2. Should have session summary information
        assert latest_session["session_id"] == prev_session_id, "Should match the previous session"
        assert latest_session["user_id"] == "returning_user", "Should match user"
        assert latest_session["character_id"] == "dr_python", "Should match character"
        assert latest_session["message_count"] == 4, "Should show correct message count"
        
        # 3. Should include last Q&A pair for continuation context
        last_qa = latest_session["last_message_pair"]
        assert "예제" in last_qa["user_message"], "Should show last user question about examples"
        assert "리스트 예제" in last_qa["assistant_message"], "Should show last assistant response with examples"
        assert "김파이썬" in last_qa["assistant_message"], "Should include specific example content"
        
        # 4. When user chooses to continue, should load full conversation
        if len(previous_sessions) > 0:
            # User chooses to continue the session
            continued_session = conversation_service.load_session_messages(prev_session_id, "returning_user")
            
            # Should load complete conversation history
            assert len(continued_session["messages"]) == 4, "Should load all previous messages"
            
            # Messages should be in chronological order
            messages = continued_session["messages"]
            assert messages[0]["content"] == "리스트와 딕셔너리의 차이점을 알려주세요", "First message should match"
            assert messages[-1]["role"] == "assistant", "Last message should be assistant response"
            assert "김파이썬" in messages[-1]["content"], "Last message should contain example"
            
            # Should be ready for new messages to continue conversation
            new_user_message = "딕셔너리에서 값을 어떻게 가져오나요?"
            updated_session = conversation_service.add_message_to_session(
                prev_session_id, 
                "user", 
                new_user_message, 
                "returning_user"
            )
            
            assert updated_session["message_count"] == 5, "Should increment message count"
            assert updated_session["messages"][-1]["content"] == new_user_message, "Should add new message"
        
        # 5. Alternatively, user can start fresh session
        new_session = conversation_service.create_session(
            user_id="returning_user",
            character_id="dr_python", 
            persona_id=persona["id"]
        )
        
        assert new_session["session_id"] != prev_session_id, "New session should have different ID"
        assert new_session["message_count"] == 0, "New session should start empty"
        
        # After creating new session, should still be able to access previous sessions
        all_sessions = conversation_service.get_previous_sessions("returning_user", "dr_python")
        # Filter sessions with messages (non-empty sessions)
        sessions_with_messages = [s for s in all_sessions if s["message_count"] > 0]
        assert len(sessions_with_messages) == 1, "Should have 1 previous session with messages"
        assert len(all_sessions) == 2, "Should have 2 total sessions (1 with messages, 1 empty new session)"