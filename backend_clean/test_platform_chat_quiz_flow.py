#!/usr/bin/env python3
"""
Test Platform Chat Quiz Flow Step by Step

Tests the complete quiz flow to understand when continuous_quiz_response triggers:
1. Initial greeting 
2. Get quiz tool
3. Answer quiz question 
4. Verify continuous_quiz_response triggered
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_platform_chat_quiz_flow():
    """Test complete quiz flow with proper conversation history"""
    print("🧪 TESTING PLATFORM CHAT QUIZ FLOW - STEP BY STEP")
    print("=" * 70)
    
    session_id = None
    
    # Step 1: Initial greeting to establish session
    print("\n📝 STEP 1: Initial Greeting")
    print("-" * 30)
    
    greeting_payload = {
        "user_input": "안녕하세요! 한국사 퀴즈를 풀고 싶어요",
        "character_id": "seol_min_seok_quiz",
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json=greeting_payload)
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"✅ Session created: {session_id}")
        print(f"✅ Greeting dialogue: {data['dialogue'][:100]}...")
        
        if data.get("tools"):
            print(f"✅ Tools received: {len(data['tools'])} tools")
            quiz_tool = data["tools"][0]
            if quiz_tool.get("type") == "show_selection":
                question = quiz_tool["data"]["question"]
                options = quiz_tool["data"]["options"]
                correct_answer = quiz_tool["data"].get("correct_answer", "")
                
                print(f"✅ Quiz question: {question}")
                print(f"✅ Options: {options}")
                print(f"✅ Correct answer: {correct_answer}")
                
                # Step 2: Answer the quiz INCORRECTLY
                print(f"\n📝 STEP 2: Answer Quiz INCORRECTLY")
                print("-" * 40)
                
                # Pick wrong answer
                wrong_answer = options[1] if options[1] != correct_answer else options[0]
                print(f"🚀 Answering with WRONG answer: '{wrong_answer}'")
                
                wrong_payload = {
                    "user_input": wrong_answer,
                    "character_id": "seol_min_seok_quiz",
                    "session_id": session_id,
                    "user_id": "test_user"
                }
                
                wrong_response = requests.post(f"{BASE_URL}/api/platform-chat", json=wrong_payload)
                if wrong_response.status_code == 200:
                    wrong_data = wrong_response.json()
                    print(f"✅ Wrong answer response received")
                    
                    # Check if we got continuous_quiz_response
                    wrong_tools = wrong_data.get("tools", [])
                    if wrong_tools and wrong_tools[0].get("type") == "continuous_quiz_response":
                        print(f"🎯 SUCCESS: Got continuous_quiz_response tool!")
                        
                        tool_data = wrong_tools[0]["data"]
                        print(f"   Phase 1 Text: {tool_data.get('phase1', {}).get('text', '')}")
                        print(f"   Phase 2 Text: {tool_data.get('phase2', {}).get('text', '')}")
                        
                        phase2_tool = tool_data.get('phase2', {}).get('tool', {})
                        if phase2_tool:
                            retry_question = phase2_tool.get('data', {}).get('question', '')
                            same_question = retry_question == question
                            print(f"   Same question for retry: {'✅ Yes' if same_question else '❌ No'}")
                            
                    else:
                        print(f"❌ Expected continuous_quiz_response, got: {[t['type'] for t in wrong_tools]}")
                        print(f"📋 Full response dialogue: {wrong_data.get('dialogue', '')}")
                        print(f"📋 Full tools: {json.dumps(wrong_tools, indent=2, ensure_ascii=False)}")
                        
                        # Debug: Let's check what the conversation state detection thinks
                        print(f"\n🔍 DEBUGGING INFO:")
                        print(f"   User input length: {len(wrong_answer.split())} words")
                        print(f"   User input: '{wrong_answer}'")
                        print(f"   Previous dialogue contains quiz keywords: {'퀴즈' in data['dialogue'] or '문제' in data['dialogue']}")
                        
                else:
                    print(f"❌ Wrong answer API call failed: {wrong_response.status_code}")
                    
                # Step 3: Answer CORRECTLY (if we got retry)
                if session_id:
                    print(f"\n📝 STEP 3: Answer Quiz CORRECTLY")
                    print("-" * 40)
                    
                    print(f"🚀 Answering with CORRECT answer: '{correct_answer}'")
                    
                    correct_payload = {
                        "user_input": correct_answer,
                        "character_id": "seol_min_seok_quiz",
                        "session_id": session_id,
                        "user_id": "test_user"
                    }
                    
                    correct_response = requests.post(f"{BASE_URL}/api/platform-chat", json=correct_payload)
                    if correct_response.status_code == 200:
                        correct_data = correct_response.json()
                        correct_tools = correct_data.get("tools", [])
                        
                        if correct_tools and correct_tools[0].get("type") == "continuous_quiz_response":
                            print(f"🎯 SUCCESS: Got continuous_quiz_response for correct answer!")
                            
                            correct_tool_data = correct_tools[0]["data"]
                            phase1_text = correct_tool_data.get('phase1', {}).get('text', '')
                            celebrates = any(word in phase1_text for word in ["정답", "맞", "훌륭", "좋"])
                            print(f"   Celebrates: {'✅ Yes' if celebrates else '❌ No'}")
                            
                            phase2_correct_tool = correct_tool_data.get('phase2', {}).get('tool', {})
                            if phase2_correct_tool:
                                new_question = phase2_correct_tool.get('data', {}).get('question', '')
                                different = new_question != question
                                print(f"   Different question: {'✅ Yes' if different else '❌ No'}")
                                print(f"   New question: {new_question[:60]}...")
                            
                        else:
                            print(f"❌ Expected continuous_quiz_response for correct answer, got: {[t['type'] for t in correct_tools]}")
                    else:
                        print(f"❌ Correct answer API call failed: {correct_response.status_code}")
                        
            else:
                print(f"❌ Expected show_selection tool in greeting, got: {quiz_tool.get('type')}")
        else:
            print(f"❌ No tools in greeting response")
    else:
        print(f"❌ Greeting API call failed: {response.status_code}")
    
    print(f"\n{'='*70}")
    print("🎉 PLATFORM CHAT QUIZ FLOW TESTING COMPLETE")

if __name__ == "__main__":
    test_platform_chat_quiz_flow()