#!/usr/bin/env python3
"""
Test to reproduce the quiz regression issue
Focus on identifying content filter and LLM processing issues
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_quiz_progression():
    """Test the complete quiz flow to identify where it breaks"""
    
    print("🧪 Testing Quiz Regression Issues...")
    print("=" * 60)
    
    # Step 1: Create session and get greeting
    print("\n🎯 Step 1: Testing session creation and greeting...")
    
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "regression_test",
        "character_id": "seol_min_seok_quiz"
    })
    
    if create_response.status_code != 200:
        print(f"❌ Session creation failed: {create_response.status_code}")
        return False
        
    session_data = create_response.json()
    session_id = session_data.get("data", {}).get("session", {}).get("session_id")
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Test platform chat for greeting
    print("\n🎯 Step 2: Testing greeting response...")
    
    greeting_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "안녕하세요 선생님",
        "user_id": "regression_test"
    })
    
    if greeting_response.status_code == 200:
        greeting_data = greeting_response.json()
        print(f"✅ Greeting dialogue: {greeting_data.get('dialogue', '')[:100]}...")
        print(f"✅ Tools count: {len(greeting_data.get('tools', []))}")
        
        if greeting_data.get('tools') and len(greeting_data.get('tools', [])) > 0:
            first_tool = greeting_data['tools'][0]
            print(f"✅ First tool type: {first_tool.get('type')}")
            if first_tool.get('data'):
                print(f"✅ Tool question: {first_tool['data'].get('question', 'N/A')[:50]}...")
                print(f"✅ Tool options count: {len(first_tool['data'].get('options', []))}")
        else:
            print("❌ No tools in greeting response")
            return False
    else:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        return False
    
    # Step 3: Test answering first quiz question (this is where it breaks)
    print("\n🎯 Step 3: Testing quiz answer (where regression occurs)...")
    
    # Try a safe answer that shouldn't trigger content filter
    safe_answer = "조선시대"
    
    answer_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz", 
        "session_id": session_id,
        "user_input": safe_answer,
        "user_id": "regression_test"
    })
    
    if answer_response.status_code == 200:
        answer_data = answer_response.json()
        dialogue = answer_data.get('dialogue', '')
        print(f"📝 Answer response dialogue: {dialogue[:100]}...")
        
        # Check if it's the generic error message
        if "죄송합니다" in dialogue:
            print("❌ REGRESSION CONFIRMED: Generic error message returned")
            print(f"   Full dialogue: {dialogue}")
        else:
            print("✅ Proper response received (not generic error)")
            
        print(f"📊 Tools count: {len(answer_data.get('tools', []))}")
        if answer_data.get('tools'):
            print(f"📊 Tool types: {[tool.get('type') for tool in answer_data.get('tools', [])]}")
            
    else:
        print(f"❌ Quiz answer failed: {answer_response.status_code}")
        try:
            error_data = answer_response.json()
            print(f"   Error details: {error_data}")
        except:
            print(f"   Error text: {answer_response.text}")
        return False
    
    return True

def main():
    print("🚀 Testing Quiz Regression Issues")
    print("=" * 60)
    
    success = test_quiz_progression()
    
    print(f"\n📊 FINAL RESULT:")
    if success:
        print("   ✅ Test completed - check logs for specific issues")
    else:
        print("   ❌ Test failed - critical system issues found")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)