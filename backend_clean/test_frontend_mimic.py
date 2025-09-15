#!/usr/bin/env python3
"""
Frontend Mimic Test - Replicate EXACT frontend API calls
Test the exact same sequence the frontend makes
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_exact_frontend_sequence():
    """Test the exact sequence the frontend makes"""
    print("🔍 FRONTEND MIMIC TEST")
    print("=" * 60)
    
    # Step 1: Frontend first checks for sessions 
    print("\n📋 STEP 1: Sessions Start (like frontend does)")
    
    sessions_payload = {
        "user_id": "demo_user",
        "character_id": "dr_genie_science_quiz"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/sessions/start", json=sessions_payload, timeout=30)
        print(f"Sessions start: {response.status_code}")
        if response.status_code != 200:
            print(f"Sessions start failed: {response.text}")
    except Exception as e:
        print(f"Sessions start exception: {e}")
    
    # Step 2: Frontend calls chatWithSession which converts to platform-chat
    print("\n📋 STEP 2: Platform Chat - Greeting (empty input)")
    
    platform_payload = {
        "user_input": "",
        "character_id": "dr_genie_science_quiz",
        "session_id": None,
        "user_id": "demo_user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=platform_payload, timeout=30)
        print(f"Platform chat greeting: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"Session ID: {session_id}")
            print(f"Tools: {len(data.get('tools', []))}")
            
            if data.get('tools'):
                print(f"First tool: {data['tools'][0].get('type')}")
                tool_data = data['tools'][0].get('data', {})
                options = tool_data.get('options', tool_data.get('items', []))
                print(f"Options: {options}")
                
                # Step 3: User selects first topic (like frontend does)
                print("\n📋 STEP 3: Platform Chat - Topic Selection")
                
                if options and len(options) > 0:
                    selected_topic = options[0]  # Select first option
                    print(f"Selecting: {selected_topic}")
                    
                    topic_payload = {
                        "user_input": selected_topic,
                        "character_id": "dr_genie_science_quiz", 
                        "session_id": session_id,
                        "user_id": "demo_user"
                    }
                    
                    response = requests.post(f"{BASE_URL}/api/platform-chat", json=topic_payload, timeout=30)
                    print(f"Topic selection: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Tools: {len(data.get('tools', []))}")
                        
                        if data.get('tools'):
                            quiz_tool = data['tools'][0]
                            quiz_data = quiz_tool.get('data', {})
                            quiz_options = quiz_data.get('options', quiz_data.get('items', []))
                            correct_answer = quiz_data.get('correct_answer')
                            
                            print(f"Quiz question: {quiz_data.get('question', 'NO QUESTION')[:50]}...")
                            print(f"Quiz options: {quiz_options}")
                            print(f"Correct answer: {correct_answer}")
                            
                            # Step 4: Answer the quiz (THIS IS WHERE THE ERROR MIGHT HAPPEN)
                            print("\n📋 STEP 4: Platform Chat - Quiz Answer")
                            
                            if quiz_options and len(quiz_options) > 1:
                                # Try wrong answer first (like user might do)
                                wrong_answer = quiz_options[1] if quiz_options[1] != correct_answer else quiz_options[0]
                                print(f"Answering with WRONG answer: {wrong_answer}")
                                
                                answer_payload = {
                                    "user_input": wrong_answer,
                                    "character_id": "dr_genie_science_quiz",
                                    "session_id": session_id, 
                                    "user_id": "demo_user"
                                }
                                
                                print(f"Answer payload: {json.dumps(answer_payload, indent=2, ensure_ascii=False)}")
                                
                                response = requests.post(f"{BASE_URL}/api/platform-chat", json=answer_payload, timeout=30)
                                print(f"Quiz answer: {response.status_code}")
                                print(f"Response headers: {dict(response.headers)}")
                                
                                if response.status_code != 200:
                                    print(f"❌ QUIZ ANSWER FAILED!")
                                    print(f"Status: {response.status_code}")
                                    print(f"Response text: {response.text}")
                                    print(f"This is likely the source of the frontend error!")
                                    return False
                                else:
                                    data = response.json()
                                    print(f"✅ Quiz answer SUCCESS")
                                    print(f"Dialogue: {data.get('dialogue', 'NO DIALOGUE')[:100]}...")
                                    print(f"Audio URL: {bool(data.get('audio_url'))}")
                                    return True
                    else:
                        print(f"Topic selection failed: {response.status_code} - {response.text}")
                        return False
        else:
            print(f"Greeting failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in frontend mimic: {e}")
        return False
    
    return False

if __name__ == "__main__":
    success = test_exact_frontend_sequence()
    print(f"\n🏁 FRONTEND MIMIC RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print("This test replicates the exact frontend behavior to isolate the real issue.")