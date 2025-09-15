#!/usr/bin/env python3
"""
Debug Quiz Answer Validation Issue
Test the specific problem with answer checking logic
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_quiz_answer_validation():
    """Test actual quiz validation flow"""
    print("🔍 DEBUGGING QUIZ ANSWER VALIDATION")
    
    character_id = "dr_genie_science_quiz"
    
    # Step 1: Get greeting and tools
    print("\n📋 STEP 1: Get Greeting")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "debug_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Greeting failed: {response.status_code}")
        return
    
    data = response.json()
    session_id = data.get('session_id')
    tools = data.get('tools', [])
    
    if not tools:
        print("❌ No tools in greeting")
        return
        
    print(f"✅ Greeting success, session: {session_id}")
    
    # Step 2: Select topic
    print("\n📋 STEP 2: Select Topic")
    topic_options = tools[0]['data']['options']
    selected_topic = topic_options[0]  # Select first topic
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": selected_topic,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "debug_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Topic selection failed: {response.status_code}")
        return
    
    data = response.json()
    tools = data.get('tools', [])
    
    if not tools:
        print("❌ No quiz question generated")
        return
        
    print(f"✅ Topic selected: {selected_topic}")
    
    # Step 3: Examine quiz question structure
    print("\n📋 STEP 3: Analyze Quiz Question Structure")
    quiz_tool = tools[0]
    quiz_data = quiz_tool['data']
    
    print(f"Question: {quiz_data.get('question', 'NO_QUESTION')}")
    print(f"Options: {quiz_data.get('options', [])}")
    print(f"Correct Answer: {quiz_data.get('correct_answer', 'NO_CORRECT_ANSWER')}")
    print(f"Selection Mode: {quiz_data.get('selection_mode', 'NO_MODE')}")
    
    # Check if correct answer is in options
    correct_answer = quiz_data.get('correct_answer', '')
    options = quiz_data.get('options', [])
    
    print(f"\n🔍 VALIDATION ANALYSIS:")
    print(f"Correct answer: '{correct_answer}'")
    print(f"Options: {options}")
    print(f"Is correct answer in options? {correct_answer in options}")
    
    # Test answer selection
    print("\n📋 STEP 4: Test Answer Selection")
    
    # Try selecting the correct answer
    if correct_answer in options:
        test_answer = correct_answer
        print(f"Testing with CORRECT answer: '{test_answer}'")
    else:
        test_answer = options[0] if options else "No options available"
        print(f"Testing with FIRST option: '{test_answer}'")
        print(f"⚠️  WARNING: Correct answer not in options!")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": test_answer,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "debug_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Answer submission failed: {response.status_code}")
        print(f"Response text: {response.text}")
        return
    
    data = response.json()
    dialogue = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"Response dialogue: {dialogue}")
    print(f"Response tools: {len(tools)}")
    
    # Analyze response
    if "정답" in dialogue or "맞아요" in dialogue or "좋은 선택" in dialogue or "맞았어요" in dialogue:
        print("✅ Response indicates correct answer")
    elif "틀렸" in dialogue or "아쉽" in dialogue or "다시" in dialogue:
        print("❌ Response indicates wrong answer")  
    elif "죄송합니다" in dialogue:
        print("🚨 ERROR MESSAGE DETECTED - System failure!")
    else:
        print("❓ Unclear response type")
        
    print(f"\n🔍 SUMMARY:")
    print(f"Question had options: {len(options) > 0}")
    print(f"Correct answer in options: {correct_answer in options}")
    is_working = "✅ Response indicates correct answer" in locals() or any(x in dialogue for x in ["정답", "맞아요", "맞았어요", "좋은 선택"])
    print(f"Answer validation appears: {'✅ WORKING' if is_working else '❌ BROKEN'}")

if __name__ == "__main__":
    test_quiz_answer_validation()