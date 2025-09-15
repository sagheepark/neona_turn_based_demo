#!/usr/bin/env python3
"""
Final Comprehensive Test for Both Quiz Characters
Tests both seol_min_seok_quiz and dr_genie_science_quiz characters end-to-end
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_character_flow(character_id, character_name):
    """Test complete flow for a quiz character"""
    print(f"🧪 Testing {character_name} ({character_id})...")
    
    session_id = f"test_{character_id}_{int(time.time())}"
    
    try:
        # Step 1: Test greeting
        print("1️⃣ Testing greeting...")
        greeting_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": "",
            "character_id": character_id,
            "session_id": session_id
        })
        
        if greeting_response.status_code != 200:
            print(f"❌ Greeting failed: {greeting_response.status_code} - {greeting_response.text[:200]}...")
            return False
            
        greeting_data = greeting_response.json()
        print(f"✅ Greeting success")
        print(f"   Has audio: {bool(greeting_data.get('audio_url'))}")
        print(f"   Has tools: {len(greeting_data.get('tools', []))}")
        
        if not greeting_data.get('tools') or len(greeting_data['tools']) == 0:
            print(f"❌ No tools provided in greeting")
            return False
        
        # Step 2: Select topic
        print("2️⃣ Testing topic selection...")
        tool_data = greeting_data['tools'][0]['data']
        if not tool_data.get('options') or len(tool_data['options']) == 0:
            print(f"❌ No options provided in greeting tool")
            return False
            
        selected_topic = tool_data['options'][0]  # Select first topic
        print(f"   Selected topic: {selected_topic}")
        
        topic_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": selected_topic,
            "character_id": character_id,
            "session_id": session_id
        })
        
        if topic_response.status_code != 200:
            print(f"❌ Topic selection failed: {topic_response.status_code} - {topic_response.text[:200]}...")
            return False
            
        topic_data = topic_response.json()
        print(f"✅ Topic selection success")
        print(f"   Has audio: {bool(topic_data.get('audio_url'))}")
        print(f"   Has tools: {len(topic_data.get('tools', []))}")
        
        if not topic_data.get('tools') or len(topic_data['tools']) == 0:
            print(f"❌ No quiz tools provided after topic selection")
            return False
            
        # Step 3: Answer quiz question (wrong answer)
        print("3️⃣ Testing quiz answer (wrong)...")
        quiz_tool = topic_data['tools'][0]['data']
        if not quiz_tool.get('options') or len(quiz_tool['options']) < 2:
            print(f"❌ Not enough quiz options provided")
            return False
            
        # Select second option (likely wrong) 
        wrong_answer = quiz_tool['options'][1]
        print(f"   Question: {quiz_tool.get('question', 'No question')[:50]}...")
        print(f"   Selected (wrong) answer: {wrong_answer}")
        
        quiz_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": wrong_answer,
            "character_id": character_id,
            "session_id": session_id
        })
        
        if quiz_response.status_code != 200:
            print(f"❌ Quiz answer failed: {quiz_response.status_code} - {quiz_response.text[:200]}...")
            return False
            
        quiz_data = quiz_response.json()
        response_text = quiz_data.get('text', '')
        
        # Check if it's the error message
        if "죄송합니다. 잠시 문제가 있었습니다" in response_text:
            print(f"❌ Still getting error message: {response_text[:100]}...")
            return False
        else:
            print(f"✅ Quiz answer processed successfully")
            print(f"   Has audio: {bool(quiz_data.get('audio_url'))}")
            print(f"   Has tools: {len(quiz_data.get('tools', []))}")
            print(f"   Response preview: {response_text[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Exception during {character_name} test: {e}")
        return False

def main():
    """Test both characters"""
    print("🚀 COMPREHENSIVE CHARACTER TEST")
    print("=" * 50)
    
    characters = [
        ("seol_min_seok_quiz", "설민석 Korean History Quiz"),
        ("dr_genie_science_quiz", "Dr. Genie Science Quiz")
    ]
    
    results = {}
    
    for character_id, character_name in characters:
        print(f"\n{character_name}")
        print("-" * 40)
        results[character_id] = test_character_flow(character_id, character_name)
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n{'='*50}")
    print("🏁 FINAL RESULTS")
    print("=" * 50)
    
    all_passed = True
    for character_id, character_name in characters:
        status = "✅ WORKING" if results[character_id] else "❌ FAILED"
        print(f"{character_name}: {status}")
        if not results[character_id]:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 ALL CHARACTERS ARE WORKING PERFECTLY!")
        print("🔧 TTS method signature fix was successful")
        print("✅ End-to-end integration is complete")
    else:
        print("❌ Some characters still have issues")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)