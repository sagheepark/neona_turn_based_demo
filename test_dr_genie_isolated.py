#!/usr/bin/env python3
"""
Isolated test for Dr. Genie Science Quiz Character
Test each phase individually to isolate the exact problem
"""

import asyncio
import json
import sys
import requests
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8001"
CHARACTER_ID = "dr_genie_science_quiz"
TOPIC = "물리"

def test_greeting():
    """Test greeting phase"""
    print("🧪 Testing Dr. Genie Greeting Phase...")
    
    # Start session
    session_response = requests.post(f"{BASE_URL}/api/sessions/start", json={
        "character_id": CHARACTER_ID,
        "user_id": "test_user"
    })
    
    if session_response.status_code != 200:
        print(f"❌ Session start failed: {session_response.status_code}")
        print(f"Response: {session_response.text}")
        return None
    
    session_data = session_response.json()
    print(f"Session data keys: {list(session_data.keys())}")
    
    # Check for different possible session id keys
    session_id = session_data.get("session_id") or session_data.get("sessionId") or session_data.get("id")
    if not session_id:
        print(f"❌ No session ID found in response: {session_data}")
        return None
    
    print(f"✅ Session started: {session_id}")
    
    # Test greeting
    greeting_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "message": "",  # Empty message for greeting
        "session_id": session_id,
        "character_id": CHARACTER_ID
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        print(f"Response: {greeting_response.text}")
        return None
    
    greeting_data = greeting_response.json()
    print(f"✅ Greeting Response:")
    print(f"   - Dialogue: {bool(greeting_data.get('dialogue'))}")
    print(f"   - Audio: {bool(greeting_data.get('audio_url'))}")
    print(f"   - Tools: {len(greeting_data.get('tools', []))}")
    
    if greeting_data.get('tools'):
        tool = greeting_data['tools'][0]
        print(f"   - Tool Type: {tool.get('type', 'N/A')}")
        if tool.get('type') == 'show_selection':
            print(f"   - Question: {tool.get('data', {}).get('question', 'N/A')[:50]}...")
            print(f"   - Options: {len(tool.get('data', {}).get('options', []))}")
    
    return session_id, greeting_data

def test_topic_selection(session_id):
    """Test topic selection phase"""
    print(f"\n🧪 Testing Dr. Genie Topic Selection Phase...")
    
    # Select topic
    topic_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "message": TOPIC,
        "session_id": session_id,
        "character_id": CHARACTER_ID
    })
    
    if topic_response.status_code != 200:
        print(f"❌ Topic selection failed: {topic_response.status_code}")
        print(f"Response: {topic_response.text}")
        return None
    
    topic_data = topic_response.json()
    print(f"✅ Topic Selection Response:")
    print(f"   - Dialogue: {bool(topic_data.get('dialogue'))}")
    print(f"   - Audio: {bool(topic_data.get('audio_url'))}")
    print(f"   - Tools: {len(topic_data.get('tools', []))}")
    
    # Check for error message
    dialogue = topic_data.get('dialogue', '')
    if "죄송합니다" in dialogue or "문제가 있었습니다" in dialogue:
        print(f"❌ ERROR MESSAGE DETECTED: {dialogue[:100]}...")
        return None
    
    if topic_data.get('tools'):
        tool = topic_data['tools'][0]
        print(f"   - Tool Type: {tool.get('type', 'N/A')}")
        if tool.get('type') == 'show_selection':
            print(f"   - Question: {tool.get('data', {}).get('question', 'N/A')[:50]}...")
            print(f"   - Options: {len(tool.get('data', {}).get('options', []))}")
            return tool.get('data', {}).get('options', [])
    
    return topic_data

def test_quiz_answer(session_id, quiz_options):
    """Test quiz answer phase"""
    print(f"\n🧪 Testing Dr. Genie Quiz Answer Phase...")
    
    if not quiz_options:
        print("❌ No quiz options available")
        return None
    
    # Select first option
    selected_option = quiz_options[0]
    print(f"📝 Selecting option: {selected_option}")
    
    # Trigger continuous flow (this is where the problem likely occurs)
    quiz_response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
        "session_id": session_id,
        "character_id": CHARACTER_ID,
        "tool_type": "continuous_answer",
        "tool_data": {
            "selection": selected_option,
            "correct_answer": selected_option,  # Assume first is correct for testing
            "question": "Test question",
            "items": quiz_options
        }
    })
    
    if quiz_response.status_code != 200:
        print(f"❌ Quiz answer failed: {quiz_response.status_code}")
        print(f"Response: {quiz_response.text}")
        return None
    
    quiz_data = quiz_response.json()
    print(f"✅ Quiz Answer Response:")
    print(f"   - Has Response: {bool(quiz_data)}")
    print(f"   - Keys: {list(quiz_data.keys()) if quiz_data else 'None'}")
    
    if quiz_data and 'phase_1' in quiz_data:
        print(f"   - Phase 1: {quiz_data['phase_1']}")
    if quiz_data and 'phase_2' in quiz_data:
        print(f"   - Phase 2: {quiz_data['phase_2']}")
    
    return quiz_data

def main():
    """Run isolated tests"""
    print("🚀 DR. GENIE SCIENCE QUIZ - ISOLATED TEST")
    print("=" * 60)
    
    # Test 1: Greeting
    result = test_greeting()
    if not result:
        print("❌ Greeting phase failed")
        return False
    
    session_id, greeting_data = result
    
    # Test 2: Topic Selection
    topic_result = test_topic_selection(session_id)
    if not topic_result or isinstance(topic_result, dict) and not topic_result.get('tools'):
        print("❌ Topic selection phase failed")
        return False
    
    if isinstance(topic_result, list):
        quiz_options = topic_result
    else:
        quiz_options = topic_result.get('tools', [{}])[0].get('data', {}).get('options', [])
    
    # Test 3: Quiz Answer
    quiz_result = test_quiz_answer(session_id, quiz_options)
    if not quiz_result:
        print("❌ Quiz answer phase failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL PHASES COMPLETED")
    print("✅ Greeting: Working")
    print("✅ Topic Selection: Working")
    print("✅ Quiz Answer: Working")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)