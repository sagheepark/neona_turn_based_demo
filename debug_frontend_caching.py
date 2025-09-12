#!/usr/bin/env python3
"""
Debug frontend caching issues by testing with different sessions and browsers
"""

import requests
import json
import time

def test_frontend_caching_scenarios():
    """Test multiple scenarios that could cause frontend caching issues"""
    
    print("🔍 Debugging Frontend Caching Issues")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Same session, rapid consecutive wrong answers
    print("\n🧪 Test 1: Rapid consecutive wrong answers in same session")
    try:
        session_id_1 = create_session(base_url, "rapid_test_user")
        quiz_data_1 = get_quiz(base_url, session_id_1, "rapid_test_user", "삼국시대")
        
        wrong_options = [opt for opt in quiz_data_1['options'] if opt != quiz_data_1['correct_answer']]
        
        # First wrong answer
        response1 = submit_answer(base_url, session_id_1, "rapid_test_user", wrong_options[0])
        feedback1 = extract_feedback(response1)
        print(f"   First wrong '{wrong_options[0]}' → feedback mentions: {get_mentioned_option(feedback1, quiz_data_1['options'])}")
        
        # Second wrong answer immediately
        response2 = submit_answer(base_url, session_id_1, "rapid_test_user", wrong_options[1])
        feedback2 = extract_feedback(response2)
        print(f"   Second wrong '{wrong_options[1]}' → feedback mentions: {get_mentioned_option(feedback2, quiz_data_1['options'])}")
        
        if wrong_options[1] in feedback2 and wrong_options[0] not in feedback2:
            print("   ✅ Rapid test PASSED - correct feedback")
        else:
            print("   ❌ Rapid test FAILED - caching issue detected")
    
    except Exception as e:
        print(f"   ❌ Rapid test failed: {e}")
    
    print("\n" + "="*40)
    
    # Test 2: Different user, same scenario
    print("\n🧪 Test 2: Different user, same caching test")
    try:
        session_id_2 = create_session(base_url, "different_user")
        quiz_data_2 = get_quiz(base_url, session_id_2, "different_user", "삼국시대")
        
        wrong_options = [opt for opt in quiz_data_2['options'] if opt != quiz_data_2['correct_answer']]
        
        # First wrong answer
        response1 = submit_answer(base_url, session_id_2, "different_user", wrong_options[0])
        feedback1 = extract_feedback(response1)
        print(f"   First wrong '{wrong_options[0]}' → feedback: {feedback1[:50]}...")
        
        # Delay to ensure no timing issues
        time.sleep(1)
        
        # Second wrong answer
        response2 = submit_answer(base_url, session_id_2, "different_user", wrong_options[1])
        feedback2 = extract_feedback(response2)
        print(f"   Second wrong '{wrong_options[1]}' → feedback: {feedback2[:50]}...")
        
        if wrong_options[1] in feedback2:
            print("   ✅ Different user test PASSED")
        else:
            print("   ❌ Different user test FAILED")
    
    except Exception as e:
        print(f"   ❌ Different user test failed: {e}")
    
    print("\n" + "="*40)
    
    # Test 3: Check for any response caching in tool_orchestrator
    print("\n🧪 Test 3: Check tool orchestrator response consistency")
    try:
        session_id_3 = create_session(base_url, "consistency_user")
        quiz_data_3 = get_quiz(base_url, session_id_3, "consistency_user", "삼국시대")
        
        wrong_option = [opt for opt in quiz_data_3['options'] if opt != quiz_data_3['correct_answer']][0]
        
        # Submit same wrong answer multiple times to see if response changes
        for i in range(3):
            response = submit_answer(base_url, session_id_3, "consistency_user", wrong_option)
            feedback = extract_feedback(response)
            print(f"   Attempt {i+1} with '{wrong_option}' → mentions option: {wrong_option in feedback}")
        
    except Exception as e:
        print(f"   ❌ Consistency test failed: {e}")

def create_session(base_url, user_id):
    """Create a new session and return session_id"""
    response = requests.post(f"{base_url}/api/platform-chat", json={
        "user_input": "",
        "character_id": "seol_min_seok_quiz", 
        "user_id": user_id
    })
    return response.json().get('session_id')

def get_quiz(base_url, session_id, user_id, topic):
    """Get quiz data for a topic"""
    response = requests.post(f"{base_url}/api/platform-chat", json={
        "user_input": topic,
        "character_id": "seol_min_seok_quiz",
        "user_id": user_id,
        "session_id": session_id
    })
    return response.json()['tools'][0]['data']

def submit_answer(base_url, session_id, user_id, answer):
    """Submit an answer and return the response"""
    response = requests.post(f"{base_url}/api/platform-chat", json={
        "user_input": answer,
        "character_id": "seol_min_seok_quiz",
        "user_id": user_id,
        "session_id": session_id
    })
    return response.json()

def extract_feedback(response):
    """Extract phase1 feedback text from response"""
    if response.get('tools') and response['tools'][0].get('type') == 'continuous_quiz_response':
        return response['tools'][0]['data']['phase1']['text']
    return response.get('dialogue', '')

def get_mentioned_option(feedback, options):
    """Find which option is mentioned in the feedback"""
    for option in options:
        if option in feedback:
            return option
    return "None"

if __name__ == "__main__":
    test_frontend_caching_scenarios()