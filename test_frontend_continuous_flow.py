#!/usr/bin/env python3
"""
Test script to verify exact response format when selecting answer "이승만"
This tests the scenario the user reported where flow stops after answer selection
"""

import requests
import json

def test_frontend_continuous_flow():
    """Test the specific scenario user reported with 이승만 answer"""
    
    print("🧪 Testing Frontend Continuous Flow - User's Specific Case")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create initial session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_frontend_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Select topic to get a quiz question
        print(f"\n📋 Step 2: Selecting topic...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "현대 한국사",  # Select modern Korean history
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_frontend_user",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic selected, got quiz question")
        
        if data.get('tools'):
            quiz_data = data['tools'][0]['data']
            print(f"❓ Question: {quiz_data.get('question', '')}")
            print(f"📝 Options: {quiz_data.get('options', [])}")
        
        # Step 3: Answer with "이승만" to trigger continuous flow
        print(f"\n📋 Step 3: Answering with '이승만'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "이승만",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_frontend_user", 
            "session_id": session_id
        })
        
        data = response.json()
        print(f"📊 Response status: {response.status_code}")
        print(f"📨 FULL RESPONSE STRUCTURE:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Analyze the exact response structure for frontend
        print(f"\n🔍 FRONTEND RESPONSE ANALYSIS:")
        print(f"   Has 'tools' key: {'tools' in data}")
        print(f"   Has 'step_result' key: {'step_result' in data}")
        
        if 'tools' in data:
            print(f"   Direct tools count: {len(data['tools'])}")
            if data['tools'] and len(data['tools']) > 0:
                print(f"   First tool type: {data['tools'][0].get('type', 'No type')}")
        
        if 'step_result' in data:
            step_result = data['step_result']
            print(f"   Step result has 'tools': {'tools' in step_result}")
            if 'tools' in step_result:
                print(f"   Step result tools count: {len(step_result['tools'])}")
                if step_result['tools'] and len(step_result['tools']) > 0:
                    print(f"   Step result first tool type: {step_result['tools'][0].get('type', 'No type')}")
                    
                    # Check if it's continuous_quiz_response
                    if step_result['tools'][0].get('type') == 'continuous_quiz_response':
                        print(f"\n✅ FOUND continuous_quiz_response in step_result.tools!")
                        tool_data = step_result['tools'][0]['data']
                        print(f"   Phase1 text: {tool_data.get('phase1', {}).get('text', 'No phase1 text')}")
                        print(f"   Phase2 text: {tool_data.get('phase2', {}).get('text', 'No phase2 text')}")
        
        # Check other possible locations
        print(f"\n🔍 OTHER KEYS IN RESPONSE:")
        for key in data.keys():
            if key not in ['tools', 'step_result', 'session_id', 'dialogue', 'audio_url']:
                print(f"   {key}: {type(data[key])}")
        
        print(f"\n🏁 Test completed - Frontend should use this structure!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_frontend_continuous_flow()