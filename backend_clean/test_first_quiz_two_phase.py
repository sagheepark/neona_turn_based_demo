#!/usr/bin/env python3
"""
Test Two-Phase Flow for First Quiz Answer
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_first_quiz_two_phase_flow():
    """Test that first correct quiz answer triggers proper two-phase continuous_quiz_response"""
    
    print("🔴 TDD: Testing first quiz two-phase flow issue")
    
    # Step 1: Create session and get greeting
    print("✅ Step 1: Creating session...")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": "seol_min_seok_quiz",
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        return
        
    data = response.json()
    session_id = data["session_id"]
    print(f"   Session ID: {session_id}")
    
    # Step 2: Select topic
    print("✅ Step 2: Selecting topic...")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "현대사",
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to select topic: {response.status_code}")
        return
        
    data = response.json()
    
    # Extract first question
    tools = data.get("tools", [])
    if not tools or tools[0].get('type') != 'show_selection':
        print(f"❌ Expected show_selection tool, got: {tools}")
        return
        
    first_question = tools[0]['data']['question']
    first_options = tools[0]['data']['options']
    
    print(f"📋 FIRST QUESTION:")
    print(f"   Question: {first_question}")
    print(f"   Options: {first_options}")
    
    # Step 3: Answer first question CORRECTLY
    # Look for "이승만" in options since that's usually the correct answer for first president
    correct_answer = None
    for option in first_options:
        if "이승만" in option:
            correct_answer = option
            break
    
    if not correct_answer:
        # Default to first option
        correct_answer = first_options[0]
    
    print(f"✅ Step 3: Answering first question CORRECTLY with: {correct_answer}")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": correct_answer,
        "character_id": "seol_min_seok_quiz", 
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to answer question: {response.status_code}")
        return
        
    data = response.json()
    print(f"   Response: {data['dialogue'][:100]}...")
    
    # CRITICAL TEST: Check if response is two-phase continuous_quiz_response
    tools = data.get("tools", [])
    
    if not tools:
        print("❌ BUG DETECTED: No tools returned - expected continuous_quiz_response")
        print(f"   Full response: {json.dumps(data, indent=2)}")
        return
        
    primary_tool = tools[0]
    
    if primary_tool.get('type') == 'continuous_quiz_response':
        print("✅ CORRECT: Got continuous_quiz_response tool")
        
        # Check phase structure
        phase1 = primary_tool['data'].get('phase1', {})
        phase2 = primary_tool['data'].get('phase2', {})
        
        print(f"   Phase1 text: {phase1.get('text', 'MISSING')[:60]}...")
        print(f"   Phase2 text: {phase2.get('text', 'MISSING')[:60]}...")
        
        if phase2.get('tool', {}).get('type') == 'show_selection':
            second_question = phase2['tool']['data']['question']
            print(f"   Phase2 question: {second_question[:60]}...")
            print("✅ Two-phase flow working correctly")
        else:
            print("❌ BUG: Phase2 missing show_selection tool")
            
    elif primary_tool.get('type') == 'show_selection':
        print("❌ BUG DETECTED: Got show_selection instead of continuous_quiz_response")
        print("   This means the two-phase flow is not working")
        print(f"   Question in response: {primary_tool['data']['question'][:60]}...")
        
        # Check if the dialogue contains both feedback AND next question
        dialogue = data['dialogue']
        if "다음 문제" in dialogue or "다음 질문" in dialogue:
            print("❌ CONFIRMED BUG: Dialogue contains merged phase1+phase2 content")
            print(f"   Merged content: {dialogue}")
        
    else:
        print(f"❌ UNEXPECTED: Got tool type: {primary_tool.get('type')}")
        print(f"   Tool data: {json.dumps(primary_tool, indent=2)}")

if __name__ == "__main__":
    test_first_quiz_two_phase_flow()