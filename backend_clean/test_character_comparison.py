#!/usr/bin/env python3
"""
Character Comparison Test - Test both seol_min_seok_quiz and dr_genie_science_quiz
to see exactly where dr_genie fails compared to seol
"""

import requests
import json
import traceback

BASE_URL = "http://localhost:8001"

def test_character_flow(character_id, character_name):
    """Test the complete character flow"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {character_name} ({character_id})")
    print(f"{'='*80}")
    
    try:
        # Step 1: Greeting
        print(f"\n📋 STEP 1: {character_name} Greeting")
        
        greeting_payload = {
            "user_input": "",
            "character_id": character_id,
            "session_id": None,
            "user_id": "demo_user"
        }
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=greeting_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ GREETING FAILED! {response.status_code}: {response.text}")
            return False
            
        data = response.json()
        session_id = data.get('session_id')
        dialogue = data.get('dialogue', '')
        audio_url = data.get('audio_url')
        tools = data.get('tools', [])
        
        print(f"Session ID: {session_id}")
        print(f"Dialogue: {dialogue[:80]}...")
        print(f"Audio: {'✅' if audio_url else '❌'}")
        print(f"Tools: {len(tools)}")
        
        if not tools:
            print("❌ NO TOOLS FOR TOPIC SELECTION")
            return False
            
        # Step 2: Topic Selection
        print(f"\n📋 STEP 2: {character_name} Topic Selection")
        
        first_tool = tools[0]
        tool_data = first_tool.get('data', {})
        options = tool_data.get('options', tool_data.get('items', []))
        
        if not options:
            print("❌ NO OPTIONS IN GREETING TOOL")
            return False
            
        selected_topic = options[0]
        print(f"Selecting: {selected_topic}")
        
        topic_payload = {
            "user_input": selected_topic,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "demo_user"
        }
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=topic_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ TOPIC SELECTION FAILED! {response.status_code}: {response.text}")
            return False
            
        data = response.json()
        dialogue = data.get('dialogue', '')
        audio_url = data.get('audio_url')
        tools = data.get('tools', [])
        
        print(f"Dialogue: {dialogue[:80]}...")
        print(f"Audio: {'✅' if audio_url else '❌'}")
        print(f"Tools: {len(tools)}")
        
        # Check for error message
        if "죄송합니다" in dialogue and "잠시 문제가 있었습니다" in dialogue:
            print("🚨 ERROR MESSAGE DETECTED!")
            return False
            
        if not tools:
            print("❌ NO QUIZ QUESTION GENERATED")
            return False
            
        # Step 3: Quiz Answer
        print(f"\n📋 STEP 3: {character_name} Quiz Answer")
        
        quiz_tool = tools[0]
        quiz_data = quiz_tool.get('data', {})
        quiz_options = quiz_data.get('options', quiz_data.get('items', []))
        
        if not quiz_options:
            print("❌ NO QUIZ OPTIONS")
            return False
            
        # Answer with first option
        selected_answer = quiz_options[0]
        print(f"Answering: {selected_answer}")
        
        answer_payload = {
            "user_input": selected_answer,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "demo_user"
        }
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=answer_payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ QUIZ ANSWER FAILED! {response.status_code}: {response.text}")
            return False
            
        data = response.json()
        dialogue = data.get('dialogue', '')
        audio_url = data.get('audio_url')
        tools = data.get('tools', [])
        
        print(f"Dialogue: {dialogue[:80]}...")
        print(f"Audio: {'✅' if audio_url else '❌'}")
        print(f"Tools: {len(tools)}")
        
        # Check for error message
        if "죄송합니다" in dialogue and "잠시 문제가 있었습니다" in dialogue:
            print("🚨 ERROR MESSAGE DETECTED!")
            return False
            
        print(f"✅ {character_name} COMPLETE FLOW SUCCESS")
        return True
        
    except Exception as e:
        print(f"❌ Exception in {character_name}: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comparison test"""
    print("🔍 CHARACTER COMPARISON TEST")
    print("Testing seol_min_seok_quiz vs dr_genie_science_quiz")
    
    # Test both characters
    seol_success = test_character_flow("seol_min_seok_quiz", "설민석 Korean History Quiz")
    genie_success = test_character_flow("dr_genie_science_quiz", "Dr. Genie Science Quiz")
    
    # Results
    print(f"\n🏁 COMPARISON RESULTS")
    print(f"=" * 80)
    print(f"설민석 Korean History Quiz: {'✅ SUCCESS' if seol_success else '❌ FAILED'}")
    print(f"Dr. Genie Science Quiz:     {'✅ SUCCESS' if genie_success else '❌ FAILED'}")
    
    if seol_success and not genie_success:
        print(f"\n🔍 CONCLUSION: Dr. Genie has implementation gaps that seol_min_seok_quiz doesn't have")
    elif genie_success and not seol_success:
        print(f"\n🔍 CONCLUSION: seol_min_seok_quiz has issues that Dr. Genie doesn't have")
    elif seol_success and genie_success:
        print(f"\n🔍 CONCLUSION: Both characters work - issue might be elsewhere")
    else:
        print(f"\n🔍 CONCLUSION: Both characters have issues - systematic problem")

if __name__ == "__main__":
    main()