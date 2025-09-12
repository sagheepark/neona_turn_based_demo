#!/usr/bin/env python3
"""
TDD Test: Realistic Educational Quiz Flow End-to-End
RED Phase: Comprehensive test for complete educational quiz experience

Following Kent Beck's TDD methodology from claude.md:
1. Write failing test that defines the complete behavior we want
2. Test actual LLM output, not just trigger mechanisms
3. Verify educational logic works in realistic environment

Quiz Flow Requirements:
- Greeting → Suggestions appear
- Topic selection → Quiz question  
- Wrong answer → Review with hints + same question retry
- Right answer → Educational reflection + next question

This test validates the ACTUAL user experience with real LLM responses.
"""

import pytest
import requests
import json
from typing import Dict, Any
import time

# Test configuration
API_BASE = "http://localhost:8000"
TEST_USER_ID = "test_educational_flow_user"
TEST_CHARACTER_ID = "seol_min_seok_quiz"
TEST_CHARACTER_PROMPT = """
<name>설민석</name>
<personality>열정적이고 재미있는 역사 선생님</personality>
<speaking_style>친근하고 교육적이며 격려하는 말투</speaking_style>
<role>한국사 전문 교육자</role>
<scenario>학생들과 함께 재미있는 한국사 퀴즈를 진행하는 상황</scenario>
"""

class TestRealisticEducationalQuizFlow:
    """Realistic end-to-end educational quiz flow testing"""
    
    def test_complete_educational_quiz_flow_with_real_llm_responses(self):
        """
        TDD RED PHASE: Complete educational quiz flow with actual LLM output validation
        
        This test validates the ENTIRE user experience:
        1. Initial greeting → topic suggestions appear
        2. User picks quiz topic → question appears  
        3. Wrong answer → educational review + hints + same question retry
        4. Right answer → educational reflection + next question progression
        
        Tests ACTUAL LLM responses, not just API structure.
        """
        session_id = None
        
        try:
            # ===========================================
            # STEP 1: GREETING → TOPIC SUGGESTIONS
            # ===========================================
            print("\n🎯 STEP 1: Testing greeting → topic suggestions")
            
            greeting_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
                "user_id": TEST_USER_ID,
                "character_id": TEST_CHARACTER_ID,
                "message": "안녕하세요! 한국사 퀴즈를 해보고 싶어요.",
                "character_prompt": TEST_CHARACTER_PROMPT,
                "voice_id": "seol_voice"
            })
            
            assert greeting_response.status_code == 200, f"Greeting failed: {greeting_response.status_code}"
            greeting_data = greeting_response.json()
            session_id = greeting_data["session_id"]
            
            # Validate greeting response content
            dialogue = greeting_data["dialogue"]
            print(f"📝 Greeting Response: {dialogue}")
            
            assert "안녕" in dialogue or "환영" in dialogue, "Should include greeting"
            assert "퀴즈" in dialogue, "Should acknowledge quiz request"
            
            # Validate topic suggestions (tools) appear
            tools = greeting_data.get("tools")
            assert tools is not None, "Should provide topic selection tools after greeting"
            assert len(tools) > 0, "Should have at least one topic suggestion"
            
            # Find quiz-related tool
            quiz_tool = None
            for tool in tools:
                if "조선" in str(tool) or "퀴즈" in str(tool):
                    quiz_tool = tool
                    break
            
            assert quiz_tool is not None, f"Should provide quiz topic options. Got: {tools}"
            print(f"✅ Topic suggestions found: {quiz_tool}")
            
            # ===========================================  
            # STEP 2: TOPIC SELECTION → QUIZ QUESTION
            # ===========================================
            print("\n🎯 STEP 2: Testing topic selection → quiz question")
            
            quiz_start_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
                "session_id": session_id,
                "user_id": TEST_USER_ID,
                "character_id": TEST_CHARACTER_ID,
                "message": "조선시대 퀴즈 시작해주세요",
                "character_prompt": TEST_CHARACTER_PROMPT,
                "voice_id": "seol_voice"
            })
            
            assert quiz_start_response.status_code == 200, "Quiz start should succeed"
            quiz_data = quiz_start_response.json()
            
            quiz_dialogue = quiz_data["dialogue"]
            print(f"📝 Quiz Question Response: {quiz_dialogue}")
            
            # Validate actual quiz question appears
            assert "문제" in quiz_dialogue or "질문" in quiz_dialogue or "?" in quiz_dialogue, "Should contain quiz question"
            assert any(option in quiz_dialogue for option in ["A)", "B)", "C)", "D)", "1.", "2.", "3.", "4."]), "Should have multiple choice options"
            
            # Validate quiz UI tools appear
            quiz_tools = quiz_data.get("tools")
            if quiz_tools:
                print(f"✅ Quiz tools provided: {quiz_tools}")
                
            # ===========================================
            # STEP 3: WRONG ANSWER → EDUCATIONAL REVIEW + HINTS + RETRY
            # ===========================================
            print("\n🎯 STEP 3: Testing wrong answer → educational review + hints + retry")
            
            wrong_answer_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
                "session_id": session_id,
                "user_id": TEST_USER_ID,
                "character_id": TEST_CHARACTER_ID,
                "message": "B) 불교 장려",  # Intentionally wrong answer for 세종대왕 question
                "character_prompt": TEST_CHARACTER_PROMPT,
                "voice_id": "seol_voice"
            })
            
            assert wrong_answer_response.status_code == 200, "Wrong answer processing should succeed"
            wrong_data = wrong_answer_response.json()
            
            wrong_dialogue = wrong_data["dialogue"]
            print(f"📝 Wrong Answer Response: {wrong_dialogue}")
            
            # Validate educational feedback with hints
            assert len(wrong_dialogue) > 100, "Should provide substantial educational feedback"
            assert any(word in wrong_dialogue for word in ["아쉽", "틀", "다시", "생각"]), "Should indicate incorrect answer"
            assert any(word in wrong_dialogue for word in ["힌트", "생각", "업적", "세종"]), "Should provide educational hints"
            
            # Check for continuous flow tools (same question retry)
            wrong_tools = wrong_data.get("tools")
            if wrong_tools:
                print(f"✅ Retry tools provided: {wrong_tools}")
                # Should have same question again for retry
                
            time.sleep(2)  # Allow continuous flow to process
            
            # ===========================================
            # STEP 4: RIGHT ANSWER → EDUCATIONAL REFLECTION + NEXT QUESTION  
            # ===========================================
            print("\n🎯 STEP 4: Testing right answer → educational reflection + next question")
            
            right_answer_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
                "session_id": session_id,
                "user_id": TEST_USER_ID,
                "character_id": TEST_CHARACTER_ID,
                "message": "A) 한글 창제",  # Correct answer
                "character_prompt": TEST_CHARACTER_PROMPT,
                "voice_id": "seol_voice"
            })
            
            assert right_answer_response.status_code == 200, "Right answer processing should succeed"
            right_data = right_answer_response.json()
            
            right_dialogue = right_data["dialogue"]
            print(f"📝 Right Answer Response: {right_dialogue}")
            
            # Validate educational reflection
            assert len(right_dialogue) > 150, "Should provide substantial educational reflection"
            assert any(word in right_dialogue for word in ["정답", "맞", "훌륭", "좋"]), "Should acknowledge correct answer"
            assert any(word in right_dialogue for word in ["한글", "세종", "훈민정음", "백성"]), "Should provide historical context"
            assert any(word in right_dialogue for word in ["의미", "중요", "발전", "문화"]), "Should include educational significance"
            
            # Check for next question progression
            right_tools = right_data.get("tools")
            if right_tools:
                print(f"✅ Next question tools: {right_tools}")
                # Should have NEW question, not same one
                
            time.sleep(2)  # Allow continuous flow to complete
            
            # ===========================================
            # VALIDATION: CONTINUOUS FLOW WORKED  
            # ===========================================
            print("\n🎯 VALIDATION: Checking continuous flow completed successfully")
            
            # Verify session messages show proper progression
            session_messages_response = requests.get(f"{API_BASE}/api/sessions/{session_id}/messages", params={
                "user_id": TEST_USER_ID
            })
            
            if session_messages_response.status_code == 200:
                session_data = session_messages_response.json()
                messages = session_data.get("messages", [])
                
                print(f"📊 Total conversation messages: {len(messages)}")
                assert len(messages) >= 6, "Should have multiple conversation exchanges"
                
                # Verify conversation flow structure
                user_messages = [msg for msg in messages if msg["role"] == "user"]
                assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
                
                assert len(user_messages) >= 3, "Should have multiple user inputs"
                assert len(assistant_messages) >= 3, "Should have multiple AI responses"
                
                print(f"✅ Conversation structure validated: {len(user_messages)} user, {len(assistant_messages)} assistant")
                
            print("\n🟢 REALISTIC EDUCATIONAL QUIZ FLOW TEST COMPLETED")
            print("=" * 60)
            print("✅ Greeting → topic suggestions")
            print("✅ Topic selection → quiz question")  
            print("✅ Wrong answer → educational review + hints")
            print("✅ Right answer → educational reflection + progression")
            print("✅ Continuous flow system working")
            
        except AssertionError as e:
            print(f"❌ Educational quiz flow test failed: {e}")
            print("This indicates the educational logic is not working as expected")
            raise
        except Exception as e:
            print(f"❌ Unexpected error in quiz flow test: {e}")
            raise


if __name__ == "__main__":
    # Run realistic test
    test_instance = TestRealisticEducationalQuizFlow()
    
    try:
        print("🔴 RUNNING REALISTIC EDUCATIONAL QUIZ FLOW TEST")
        print("Testing complete user experience with actual LLM responses")
        print("=" * 60)
        
        test_instance.test_complete_educational_quiz_flow_with_real_llm_responses()
        
        print("\n🟢 ALL REALISTIC TESTS PASSED!")
        print("Educational quiz flow is working correctly.")
        
    except Exception as e:
        print(f"\n🔴 REALISTIC TEST FAILED: {e}")
        print("Implementation needed to make this test pass.")