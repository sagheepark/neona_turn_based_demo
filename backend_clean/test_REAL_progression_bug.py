#!/usr/bin/env python3
"""
REAL TEST: Reproduce the exact user scenario where wrong answer at second question falls back to first
This will test the ACTUAL running system, not mock data
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_real_progression_fallback():
    """Test the EXACT scenario user reported: wrong answer at second question falls back to first"""
    
    print("🚨 REAL PROGRESSION FALLBACK TEST")
    print("="*80)
    
    character_id = "seol_min_seok_quiz"
    session_id = None
    
    # Step 1: Get initial greeting and first topic selection
    print("\n📋 STEP 1: Get initial greeting")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Step 1 failed: {response.status_code}")
        return False
        
    data = response.json()
    session_id = data.get('session_id')
    print(f"✅ Got greeting, session: {session_id}")
    
    # Look for topic selection tool
    tools = data.get('tools', [])
    if not tools or tools[0].get('type') != 'show_selection':
        print(f"❌ No topic selection tool found")
        return False
        
    topic_options = tools[0].get('data', {}).get('options', [])
    print(f"📋 Topic options: {topic_options}")
    
    # Step 2: Select a topic (e.g., 조선시대)
    print("\n📋 STEP 2: Select topic")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "조선시대",
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Step 2 failed: {response.status_code}")
        return False
        
    data = response.json()
    print(f"✅ Selected topic")
    
    # Extract FIRST question
    tools = data.get('tools', [])
    if not tools:
        print(f"❌ No tools after topic selection")
        return False
        
    first_question = tools[0].get('data', {}).get('question', '')
    first_options = tools[0].get('data', {}).get('options', [])
    first_correct = tools[0].get('data', {}).get('correct_answer', '')
    
    print(f"📝 FIRST QUESTION: {first_question}")
    print(f"📝 FIRST CORRECT: {first_correct}")
    
    # Step 3: Answer FIRST question CORRECTLY to progress to second
    print(f"\n📋 STEP 3: Answer first question CORRECTLY")
    print(f"   Answering: {first_correct}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": first_correct,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Step 3 failed: {response.status_code}")
        return False
        
    data = response.json()
    print(f"✅ Answered first question correctly")
    
    # Wait for second phase with new question
    import time
    time.sleep(2)  # Wait for two-phase flow
    
    # Get the second phase
    response = requests.get(f"{BASE_URL}/api/continuous-flow/get-second-phase/{session_id}")
    if response.status_code == 200:
        data = response.json()
        tools = data.get('tools', [])
    else:
        # Fallback - the response might already contain the second question
        tools = data.get('tools', [])
    
    if not tools:
        print(f"❌ No second question found")
        return False
        
    second_question = tools[0].get('data', {}).get('question', '')
    second_options = tools[0].get('data', {}).get('options', [])
    second_correct = tools[0].get('data', {}).get('correct_answer', '')
    
    print(f"📝 SECOND QUESTION: {second_question}")
    print(f"📝 SECOND CORRECT: {second_correct}")
    
    if second_question == first_question:
        print(f"❌ ALREADY BROKEN: Second question is same as first!")
        return False
    
    # Step 4: Answer SECOND question INCORRECTLY (this is where bug occurs)
    print(f"\n📋 STEP 4: Answer second question INCORRECTLY")
    wrong_answers = [opt for opt in second_options if opt != second_correct]
    wrong_answer = wrong_answers[0] if wrong_answers else "wrong answer"
    print(f"   Answering: {wrong_answer} (should be: {second_correct})")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": wrong_answer,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_user"
    })
    
    if response.status_code != 200:
        print(f"❌ Step 4 failed: {response.status_code}")
        return False
        
    data = response.json()
    print(f"✅ Answered second question incorrectly")
    
    # Wait for retry phase
    time.sleep(2)
    
    # Get retry question
    response = requests.get(f"{BASE_URL}/api/continuous-flow/get-second-phase/{session_id}")
    if response.status_code == 200:
        data = response.json()
        tools = data.get('tools', [])
    else:
        tools = data.get('tools', [])
    
    if not tools:
        print(f"❌ No retry question found")
        return False
        
    retry_question = tools[0].get('data', {}).get('question', '')
    retry_correct = tools[0].get('data', {}).get('correct_answer', '')
    
    print(f"\n🔍 CRITICAL TEST:")
    print(f"   First question:  {first_question}")
    print(f"   Second question: {second_question}")
    print(f"   Retry question:  {retry_question}")
    
    # THE CRITICAL TEST: Does retry question match second question or first?
    if retry_question == first_question:
        print(f"\n❌ BUG CONFIRMED: Wrong answer at second question caused fallback to FIRST question!")
        print(f"   Expected: {second_question}")
        print(f"   Actual:   {retry_question}")
        return False
    elif retry_question == second_question:
        print(f"\n✅ FIX CONFIRMED: Wrong answer at second question correctly retries SECOND question!")
        return True
    else:
        print(f"\n❓ UNCLEAR: Retry question is neither first nor second question")
        print(f"   This might be a different issue")
        return False

if __name__ == "__main__":
    success = test_real_progression_fallback()
    if success:
        print(f"\n🎉 PROGRESSION FALLBACK BUG IS ACTUALLY FIXED")
    else:
        print(f"\n🚨 PROGRESSION FALLBACK BUG STILL EXISTS - NEEDS REAL FIX")
    exit(0 if success else 1)