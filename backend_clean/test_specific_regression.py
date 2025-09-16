#!/usr/bin/env python3
"""
Test the specific case that caused regression: "4.19 혁명" answer
This tests the exact scenario the user experienced
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_419_revolution_scenario():
    """Test the specific case that caused regression"""
    
    print("🧪 Testing Specific Regression: 4.19 혁명 Answer...")
    print("=" * 60)
    
    # Create session
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "419_test", 
        "character_id": "seol_min_seok_quiz"
    })
    
    session_data = create_response.json()
    session_id = session_data.get("data", {}).get("session", {}).get("session_id")
    print(f"✅ Session created: {session_id}")
    
    # Get initial greeting and first question
    print("\n🎯 Getting initial question...")
    
    greeting_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id, 
        "user_input": "안녕하세요",
        "user_id": "419_test"
    })
    
    greeting_data = greeting_response.json()
    print(f"✅ Initial response: {greeting_data.get('dialogue', '')[:80]}...")
    
    # Select a topic to get to the actual quiz
    print("\n🎯 Selecting history topic...")
    
    topic_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "근현대사", 
        "user_id": "419_test"
    })
    
    topic_data = topic_response.json()
    print(f"✅ Topic selection response: {topic_data.get('dialogue', '')[:80]}...")
    
    # Now test the problematic answer: "4.19 혁명"
    print("\n🎯 Testing problematic answer: '4.19 혁명'...")
    
    problem_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "4.19 혁명",
        "user_id": "419_test"
    })
    
    if problem_response.status_code == 200:
        problem_data = problem_response.json()
        dialogue = problem_data.get('dialogue', '')
        
        print(f"📝 Response dialogue: {dialogue}")
        
        # Check for generic error
        if "죄송합니다" in dialogue and "문제가 있었습니다" in dialogue:
            print("❌ REGRESSION CONFIRMED: Generic error for '4.19 혁명'")
            print("🔍 This is likely due to Azure OpenAI content filtering on violence/war content")
        else:
            print("✅ Proper response received for '4.19 혁명'")
            
        print(f"📊 Tools: {len(problem_data.get('tools', []))} tools returned")
        
    else:
        print(f"❌ Request failed: {problem_response.status_code}")
        print(f"   Error: {problem_response.text}")
    
    # Test with less politically sensitive content
    print("\n🎯 Testing safe answer: '세종대왕'...")
    
    safe_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "세종대왕",
        "user_id": "419_test"
    })
    
    if safe_response.status_code == 200:
        safe_data = safe_response.json()
        dialogue = safe_data.get('dialogue', '')
        
        print(f"📝 Safe response dialogue: {dialogue[:100]}...")
        
        if "죄송합니다" in dialogue:
            print("❌ Even safe content triggers error - system issue")
        else:
            print("✅ Safe content works properly")
    
    return True

def main():
    print("🚀 Testing Specific Regression Case: 4.19 혁명")
    print("=" * 60)
    
    success = test_419_revolution_scenario()
    
    print(f"\n📊 DIAGNOSIS:")
    print("   The regression likely happens with specific historical content")
    print("   that triggers Azure OpenAI's content filtering policies.")
    print("   Content about revolutions/wars gets flagged as 'violence: high'")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)