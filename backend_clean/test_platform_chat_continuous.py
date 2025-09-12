#!/usr/bin/env python3
"""
Test Platform Chat Endpoint with Continuous Quiz Response

Tests if the /api/platform-chat endpoint can properly trigger continuous_quiz_response
tool when a user answers quiz questions, connecting V2 backend to frontend.
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_platform_chat_continuous():
    """Test platform chat endpoint with quiz answer inputs"""
    print("🧪 TESTING PLATFORM CHAT CONTINUOUS QUIZ RESPONSE")
    print("=" * 60)
    
    # Test 1: Start with initial greeting to get session and quiz
    print("\n📝 TEST 1: Initial Chat to Get Quiz")
    print("-" * 30)
    
    initial_payload = {
        "user_input": "안녕하세요",
        "character_id": "seol_min_seok_quiz",
        "user_id": "test_user"
    }
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json=initial_payload)
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Session created: {session_id}")
        
        if session_data.get("tools"):
            print(f"✅ Initial tools received: {len(session_data['tools'])} tools")
            
            # Check if initial tool is quiz
            initial_tool = session_data["tools"][0]
            if initial_tool.get("type") == "show_selection":
                print(f"✅ Initial quiz tool: {initial_tool['data']['question']}")
                options = initial_tool["data"].get("options", [])
                correct_answer = initial_tool["data"].get("correct_answer", "")
                
                # Test 2: Answer quiz incorrectly via platform-chat
                print("\n📝 TEST 2: Wrong Answer via Platform Chat")
                print("-" * 40)
                
                wrong_answer = "왕건"  # Wrong answer
                
                chat_payload = {
                    "user_input": wrong_answer,
                    "character_id": "seol_min_seok_quiz", 
                    "session_id": session_id,
                    "user_id": "test_user"
                }
                
                chat_response = requests.post(f"{BASE_URL}/api/platform-chat", json=chat_payload)
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    print(f"✅ Chat response received")
                    
                    # Check if we got continuous_quiz_response tool
                    tools = chat_data.get("tools", [])
                    if tools and tools[0].get("type") == "continuous_quiz_response":
                        print(f"✅ Got continuous_quiz_response tool!")
                        
                        tool_data = tools[0]["data"]
                        
                        # Analyze structure
                        print(f"📋 TOOL STRUCTURE:")
                        print(f"   Phase 1 Text: {tool_data.get('phase1', {}).get('text', 'N/A')[:60]}...")
                        print(f"   Phase 1 Audio: {'✅ Yes' if tool_data.get('phase1', {}).get('audio_url') else '❌ No'}")
                        print(f"   Phase 2 Text: {tool_data.get('phase2', {}).get('text', 'N/A')}")
                        print(f"   Phase 2 Audio: {'✅ Yes' if tool_data.get('phase2', {}).get('audio_url') else '❌ No'}")
                        
                        phase2_tool = tool_data.get('phase2', {}).get('tool', {})
                        if phase2_tool:
                            print(f"   Phase 2 Tool: {phase2_tool.get('type', 'N/A')}")
                            print(f"   Retry Question: {phase2_tool.get('data', {}).get('question', 'N/A')}")
                            
                            same_question = phase2_tool.get('data', {}).get('question') == initial_tool['data']['question']
                            print(f"   Same Question for Retry: {'✅ Yes' if same_question else '❌ No'}")
                        
                        print(f"\n🎯 PLATFORM CHAT → CONTINUOUS FLOW: ✅ SUCCESS")
                        
                        # Test 3: Answer correctly 
                        print("\n📝 TEST 3: Correct Answer via Platform Chat")
                        print("-" * 40)
                        
                        correct_answer_payload = {
                            "user_input": correct_answer,
                            "character_id": "seol_min_seok_quiz",
                            "session_id": session_id,
                            "user_id": "test_user"
                        }
                        
                        correct_response = requests.post(f"{BASE_URL}/api/platform-chat", json=correct_answer_payload)
                        
                        if correct_response.status_code == 200:
                            correct_data = correct_response.json()
                            correct_tools = correct_data.get("tools", [])
                            
                            if correct_tools and correct_tools[0].get("type") == "continuous_quiz_response":
                                correct_tool_data = correct_tools[0]["data"]
                                phase1_text = correct_tool_data.get('phase1', {}).get('text', '')
                                
                                celebrates = any(word in phase1_text for word in ["정답", "맞", "훌륭", "축하"])
                                print(f"   Celebrates Correct Answer: {'✅ Yes' if celebrates else '❌ No'}")
                                
                                phase2_correct_tool = correct_tool_data.get('phase2', {}).get('tool', {})
                                if phase2_correct_tool:
                                    new_question = phase2_correct_tool.get('data', {}).get('question', '')
                                    different_question = new_question != initial_tool['data']['question']
                                    print(f"   Different Question: {'✅ Yes' if different_question else '❌ No'}")
                                    print(f"   New Question: {new_question[:50]}...")
                                
                                print(f"\n🎯 CORRECT ANSWER FLOW: ✅ SUCCESS")
                            else:
                                print(f"❌ Expected continuous_quiz_response, got: {correct_tools}")
                        else:
                            print(f"❌ Correct answer chat failed: {correct_response.status_code}")
                            
                    else:
                        print(f"❌ Expected continuous_quiz_response tool, got: {tools}")
                        print(f"Full response: {json.dumps(chat_data, indent=2, ensure_ascii=False)}")
                        
                else:
                    print(f"❌ Chat API failed: {chat_response.status_code} - {chat_response.text}")
            else:
                print(f"❌ Expected show_selection tool, got: {initial_tool.get('type')}")
        else:
            print(f"❌ No initial tools in session")
    else:
        print(f"❌ Session creation failed: {response.status_code} - {response.text}")
    
    print(f"\n{'='*60}")
    print("🎉 PLATFORM CHAT CONTINUOUS TESTING COMPLETE")
    print("✅ Testing if /api/platform-chat can trigger continuous_quiz_response")

if __name__ == "__main__":
    test_platform_chat_continuous()