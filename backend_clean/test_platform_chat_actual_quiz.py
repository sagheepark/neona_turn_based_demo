#!/usr/bin/env python3
"""
Test Platform Chat with Actual Quiz Answer

Now we test answering the ACTUAL quiz question that was returned
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_actual_quiz_answer():
    """Test answering the actual quiz question from the response"""
    print("🧪 TESTING PLATFORM CHAT - ACTUAL QUIZ ANSWER")
    print("=" * 60)
    
    session_id = None
    
    # Step 1: Get to the quiz question first
    print("\n📝 STEP 1: Get Quiz Question")
    print("-" * 30)
    
    greeting_payload = {
        "user_input": "안녕하세요! 한국사 퀴즈를 풀고 싶어요",
        "character_id": "seol_min_seok_quiz",
        "user_id": "test_user"
    }
    
    response1 = requests.post(f"{BASE_URL}/api/platform-chat", json=greeting_payload)
    if response1.status_code == 200:
        data1 = response1.json()
        session_id = data1["session_id"]
        
        # Select topic to get actual quiz
        topic_payload = {
            "user_input": "고려시대",
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_id": "test_user"
        }
        
        response2 = requests.post(f"{BASE_URL}/api/platform-chat", json=topic_payload)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Topic selected, got quiz")
            
            if data2.get("tools") and data2["tools"][0]["type"] == "show_selection":
                quiz_tool = data2["tools"][0]
                question = quiz_tool["data"]["question"]
                options = quiz_tool["data"]["options"]
                correct_answer = quiz_tool["data"]["correct_answer"]
                
                print(f"✅ Quiz Question: {question}")
                print(f"✅ Options: {options}")
                print(f"✅ Correct Answer: {correct_answer}")
                
                # Step 2: Answer the quiz question WRONG
                print(f"\n📝 STEP 2: Answer Quiz Question WRONG")
                print("-" * 40)
                
                # Pick wrong answer
                wrong_answer = None
                for option in options:
                    if option != correct_answer:
                        wrong_answer = option
                        break
                
                print(f"🚀 Answering with WRONG answer: '{wrong_answer}'")
                
                wrong_payload = {
                    "user_input": wrong_answer,
                    "character_id": "seol_min_seok_quiz",
                    "session_id": session_id,
                    "user_id": "test_user"
                }
                
                response3 = requests.post(f"{BASE_URL}/api/platform-chat", json=wrong_payload)
                if response3.status_code == 200:
                    data3 = response3.json()
                    print(f"✅ Wrong answer response received")
                    print(f"✅ Dialogue: {data3.get('dialogue', '')[:100]}...")
                    
                    # Check tools
                    tools = data3.get("tools", [])
                    if tools:
                        tool_type = tools[0].get("type", "")
                        print(f"✅ Tool Type: {tool_type}")
                        
                        if tool_type == "continuous_quiz_response":
                            print(f"🎯 SUCCESS: Got continuous_quiz_response!")
                            
                            tool_data = tools[0]["data"]
                            phase1 = tool_data.get("phase1", {})
                            phase2 = tool_data.get("phase2", {})
                            
                            print(f"   Phase 1: {phase1.get('text', '')[:60]}...")
                            print(f"   Phase 2: {phase2.get('text', '')}")
                            print(f"   Phase 2 has tool: {'✅ Yes' if phase2.get('tool') else '❌ No'}")
                            
                        else:
                            print(f"❌ Got {tool_type} instead of continuous_quiz_response")
                            print(f"📋 Full tool: {json.dumps(tools[0], indent=2, ensure_ascii=False)}")
                            
                            # Debug conversation state detection
                            print(f"\n🔍 DEBUGGING:")
                            print(f"   Previous dialogue: {data2.get('dialogue', '')[:100]}...")
                            print(f"   Contains quiz keywords: {'퀴즈' in data2.get('dialogue', '') or '문제' in data2.get('dialogue', '')}")
                            print(f"   User input short: {len(wrong_answer.split()) <= 3}")
                    else:
                        print(f"❌ No tools in response")
                        
                else:
                    print(f"❌ Wrong answer API failed: {response3.status_code}")
                    
            else:
                print(f"❌ No quiz tool after topic selection")
        else:
            print(f"❌ Topic selection failed: {response2.status_code}")
    else:
        print(f"❌ Initial greeting failed: {response1.status_code}")
    
    print(f"\n{'='*60}")
    print("🎉 ACTUAL QUIZ ANSWER TEST COMPLETE")

if __name__ == "__main__":
    test_actual_quiz_answer()