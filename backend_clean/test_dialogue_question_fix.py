#!/usr/bin/env python3
"""
Test the fix for including question text in dialogue responses
"""

import requests
import json

def test_dialogue_question_inclusion():
    """Test that quiz questions are included in dialogue for TTS and display"""
    
    backend_url = "http://localhost:8001"
    character_id = "seolminseok_korean_history_chat"
    
    print("🧪 TESTING DIALOGUE QUESTION INCLUSION FIX")
    print("=" * 60)
    
    # Step 1: Start initial quiz
    print("1️⃣ Starting initial quiz...")
    character_prompt = """You are 설민석, an enthusiastic Korean history teacher.

CRITICAL DIALOGUE REQUIREMENTS:
- Always include the complete question text in your dialogue response
- Never put questions only in tools - dialogue must contain the full question
- Use format: "자, 다음 문제입니다. [문제 전체 내용]"

When user requests quiz or asks for questions, you MUST:
1. Include the full question text in your dialogue response  
2. Use the "show_selection" tool to present quiz options
3. Format: "자, 문제입니다. [문제 전체 내용]"
"""
    
    try:
        response = requests.post(f"{backend_url}/api/chat", json={
            "message": "안녕하세요! 한국사 퀴즈를 시작해주세요!",
            "character_id": character_id,
            "character_prompt": character_prompt,
            "user_id": "test_user"
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            dialogue = data.get("text", data.get("dialogue", ""))
            tools = data.get("tools", [])
            
            print(f"✅ Initial quiz response received")
            print(f"📝 Dialogue: '{dialogue}'")
            print(f"🔧 Tools count: {len(tools)}")
            
            # Check if dialogue contains question text
            if len(dialogue) > 50 and ("문제" in dialogue or "다음" in dialogue):
                print("✅ PASS: Dialogue contains meaningful question content")
                question_in_dialogue = True
            else:
                print("❌ FAIL: Dialogue does not contain question text")
                question_in_dialogue = False
            
            if tools and len(tools) > 0:
                tool = tools[0]
                if tool.get('type') == 'show_selection':
                    tool_data = tool.get('data', {})
                    question = tool_data.get('question', '')
                    print(f"🔧 Tool question: '{question}'")
                    print("✅ PASS: Tools contain quiz selection")
                else:
                    print("❌ FAIL: Wrong tool type or missing tools")
                    return False
            else:
                print("❌ FAIL: No tools returned")
                return False
            
            # Step 2: Test wrong answer flow
            if session_id and tools:
                print("\n2️⃣ Testing wrong answer flow...")
                
                # Submit wrong answer
                wrong_response = requests.post(f"{backend_url}/api/continuous-answer-tool", json={
                    "session_id": session_id,
                    "selection": "틀린답변"  # Intentionally wrong
                }, timeout=30)
                
                if wrong_response.status_code == 200:
                    wrong_data = wrong_response.json()
                    wrong_dialogue = wrong_data.get("text", "")
                    wrong_tools = wrong_data.get("tools", [])
                    
                    print(f"📝 Wrong answer dialogue: '{wrong_dialogue}'")
                    print(f"🔧 Wrong answer tools: {len(wrong_tools)}")
                    
                    # Check if wrong answer dialogue contains question for retry
                    if len(wrong_dialogue) > 50 and ("문제" in wrong_dialogue or "다시" in wrong_dialogue):
                        print("✅ PASS: Wrong answer dialogue contains question text")
                        retry_question_in_dialogue = True
                    else:
                        print("❌ FAIL: Wrong answer dialogue missing question text") 
                        retry_question_in_dialogue = False
                    
                    # Step 3: Test correct answer flow
                    print("\n3️⃣ Testing correct answer flow...")
                    
                    if wrong_tools and len(wrong_tools) > 0:
                        # Get the correct answer from tools
                        correct_answer = wrong_tools[0].get('data', {}).get('correct_answer', '')
                        if correct_answer:
                            correct_response = requests.post(f"{backend_url}/api/continuous-answer-tool", json={
                                "session_id": session_id,
                                "selection": correct_answer
                            }, timeout=30)
                            
                            if correct_response.status_code == 200:
                                correct_data = correct_response.json()
                                correct_dialogue = correct_data.get("text", "")
                                correct_tools = correct_data.get("tools", [])
                                
                                print(f"📝 Correct answer dialogue: '{correct_dialogue}'")
                                print(f"🔧 Correct answer tools: {len(correct_tools)}")
                                
                                # Check if correct answer dialogue contains next question
                                if len(correct_dialogue) > 50 and ("문제" in correct_dialogue or "다음" in correct_dialogue):
                                    print("✅ PASS: Correct answer dialogue contains next question text")
                                    next_question_in_dialogue = True
                                else:
                                    print("❌ FAIL: Correct answer dialogue missing next question text")
                                    next_question_in_dialogue = False
                                
                                # Overall result
                                print(f"\n🎯 RESULTS SUMMARY:")
                                print(f"Initial question in dialogue: {'✅' if question_in_dialogue else '❌'}")
                                print(f"Retry question in dialogue: {'✅' if retry_question_in_dialogue else '❌'}")
                                print(f"Next question in dialogue: {'✅' if next_question_in_dialogue else '❌'}")
                                
                                if question_in_dialogue and retry_question_in_dialogue and next_question_in_dialogue:
                                    print("🏆 ALL TESTS PASSED: Question text properly included in dialogue")
                                    return True
                                else:
                                    print("🚨 SOME TESTS FAILED: Question text missing from dialogue")
                                    return False
                    
        else:
            print(f"❌ Initial API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_dialogue_question_inclusion()