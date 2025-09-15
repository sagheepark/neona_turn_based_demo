#!/usr/bin/env python3
"""
Dr. Genie Exact Error Test - Find the exact error for Dr. Genie character
"""

import requests
import json
import traceback

BASE_URL = "http://localhost:8001"

def test_dr_genie_exact_error():
    """Test Dr. Genie to find the exact error"""
    print("🔍 DR. GENIE EXACT ERROR TEST")
    print("=" * 60)
    
    # Test Dr. Genie Science Quiz - exact same sequence as frontend
    character_id = "dr_genie_science_quiz"
    
    try:
        # Step 1: Greeting (empty input)
        print("\n📋 STEP 1: Dr. Genie Greeting")
        
        greeting_payload = {
            "user_input": "",
            "character_id": character_id,
            "session_id": None,
            "user_id": "demo_user"
        }
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=greeting_payload, timeout=30)
        print(f"Greeting status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ GREETING FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response text: {response.text}")
            return
            
        data = response.json()
        session_id = data.get('session_id')
        audio_url = data.get('audio_url')
        dialogue = data.get('dialogue', 'NO DIALOGUE')
        tools = data.get('tools', [])
        
        print(f"Session ID: {session_id}")
        print(f"Dialogue: {dialogue[:100]}...")
        print(f"Audio URL present: {bool(audio_url)}")
        print(f"Tools count: {len(tools)}")
        
        if not audio_url:
            print("❌ NO TTS AUDIO GENERATED FOR GREETING")
        
        if not tools or len(tools) == 0:
            print("❌ NO TOOLS GENERATED FOR TOPIC SELECTION")
            return
            
        # Step 2: Topic Selection
        print("\n📋 STEP 2: Dr. Genie Topic Selection")
        
        first_tool = tools[0]
        tool_data = first_tool.get('data', {})
        options = tool_data.get('options', tool_data.get('items', []))
        
        if not options:
            print("❌ NO OPTIONS IN GREETING TOOL")
            return
            
        print(f"Available options: {options}")
        selected_topic = options[0]  # Select first option
        print(f"Selecting: {selected_topic}")
        
        topic_payload = {
            "user_input": selected_topic,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "demo_user"
        }
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=topic_payload, timeout=30)
        print(f"Topic selection status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ TOPIC SELECTION FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Response text: {response.text}")
            return
            
        data = response.json()
        dialogue = data.get('dialogue', 'NO DIALOGUE')
        audio_url = data.get('audio_url')
        tools = data.get('tools', [])
        
        print(f"Dialogue: {dialogue[:100]}...")
        print(f"Audio URL present: {bool(audio_url)}")
        print(f"Tools count: {len(tools)}")
        
        if not audio_url:
            print("❌ NO TTS AUDIO FOR TOPIC SELECTION")
            
        if not tools or len(tools) == 0:
            print("❌ NO QUIZ QUESTION GENERATED")
            return
            
        # Step 3: Quiz Answer (THIS IS WHERE ERROR HAPPENS)
        print("\n📋 STEP 3: Dr. Genie Quiz Answer - ERROR LOCATION")
        
        quiz_tool = tools[0]
        quiz_data = quiz_tool.get('data', {})
        quiz_options = quiz_data.get('options', quiz_data.get('items', []))
        correct_answer = quiz_data.get('correct_answer')
        
        print(f"Quiz question: {quiz_data.get('question', 'NO QUESTION')}")
        print(f"Quiz options: {quiz_options}")
        print(f"Correct answer: {correct_answer}")
        
        if not quiz_options:
            print("❌ NO QUIZ OPTIONS AVAILABLE")
            return
            
        # Try answering with WRONG answer first
        if len(quiz_options) > 1:
            wrong_answer = quiz_options[1] if quiz_options[1] != correct_answer else quiz_options[0]
        else:
            wrong_answer = quiz_options[0]
            
        print(f"Answering with: {wrong_answer}")
        
        answer_payload = {
            "user_input": wrong_answer,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "demo_user"
        }
        
        print(f"Answer payload: {json.dumps(answer_payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=answer_payload, timeout=30)
        print(f"Quiz answer status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ QUIZ ANSWER PROCESSING FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Error response: {response.text}")
            return
            
        data = response.json()
        dialogue = data.get('dialogue', 'NO DIALOGUE')
        audio_url = data.get('audio_url')
        tools = data.get('tools', [])
        emotion = data.get('emotion', 'NO EMOTION')
        
        print(f"✅ Quiz answer response received:")
        print(f"Dialogue: {dialogue}")
        print(f"Emotion: {emotion}")
        print(f"Audio URL present: {bool(audio_url)}")
        print(f"Tools count: {len(tools)}")
        
        # Check if this is the error message
        if "죄송합니다" in dialogue and "잠시 문제가 있었습니다" in dialogue:
            print("🚨 FOUND THE ERROR MESSAGE!")
            print("This confirms the backend is returning the error message during quiz processing")
        
        if not audio_url:
            print("❌ NO TTS AUDIO FOR QUIZ RESPONSE")
            
        print(f"✅ Dr. Genie flow completed successfully")
        return True
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dr_genie_exact_error()
    print(f"\n🏁 DR. GENIE TEST RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")