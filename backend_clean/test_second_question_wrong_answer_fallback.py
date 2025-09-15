#!/usr/bin/env python3
"""
TDD Test: Second Question Wrong Answer Fallback Issue
Testing specific user-reported issue:
"when I got wrong answer at second question, it fallbacks to first question"

Test flow:
1. Get first question -> Answer CORRECTLY -> Get second question
2. Answer second question WRONG -> Should retry SECOND question, not fallback to first
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_second_question_wrong_answer_no_fallback():
    """
    Test the specific progression fallback issue reported by user
    """
    print("🔴 TDD RED: Testing second question wrong answer fallback issue")
    
    character_id = "dr_genie_science_quiz"
    
    # Step 1: Start session and get topic selection
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "test_fallback"
    })
    
    data = response.json()
    session_id = data.get('session_id')
    tools = data.get('tools', [])
    
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Select topic to get first question
    topic = tools[0]['data']['options'][0]
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": topic,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_fallback"
    })
    
    data = response.json()
    tools = data.get('tools', [])
    
    # Extract first question details
    first_question = tools[0]['data']['question']
    first_options = tools[0]['data']['options']
    first_correct = tools[0]['data']['correct_answer']
    
    print(f"📋 FIRST QUESTION:")
    print(f"   Question: {first_question}")
    print(f"   Correct: {first_correct}")
    
    # Step 3: Answer first question CORRECTLY
    print(f"✅ Answering first question CORRECTLY with: {first_correct}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": first_correct,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_fallback"
    })
    
    data = response.json()
    dialogue1 = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"   Response: {dialogue1[:100]}...")
    
    # Verify we got a celebration and new question
    assert any(word in dialogue1.lower() for word in ['정답', '맞', '훌륭', '좋아']), \
        f"Should celebrate correct first answer: {dialogue1}"
    
    # Extract second question details
    if tools[0].get('type') == 'continuous_quiz_response':
        second_question = tools[0]['data']['phase2']['tool']['data']['question']
        second_options = tools[0]['data']['phase2']['tool']['data']['options']
        second_correct = tools[0]['data']['phase2']['tool']['data']['correct_answer']
    else:
        second_question = tools[0]['data']['question']
        second_options = tools[0]['data']['options']
        second_correct = tools[0]['data']['correct_answer']
    
    print(f"📋 SECOND QUESTION:")
    print(f"   Question: {second_question}")
    print(f"   Correct: {second_correct}")
    
    # Verify second question is different from first
    assert second_question != first_question, \
        f"Second question should be different from first. Got: {second_question}"
    
    # Step 4: Answer second question WRONG (this is the critical test)
    wrong_answer = None
    for option in second_options:
        if option != second_correct:
            wrong_answer = option
            break
    
    print(f"❌ Answering second question WRONG with: {wrong_answer}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": wrong_answer,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_fallback"
    })
    
    data = response.json()
    dialogue2 = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"   Response: {dialogue2[:100]}...")
    
    # Verify response indicates wrong answer
    assert any(word in dialogue2.lower() for word in ['틀', '아니', '다시', '생각']), \
        f"Should indicate wrong answer: {dialogue2}"
    
    # CRITICAL TEST: Extract retry question details
    if tools:
        if tools[0].get('type') == 'continuous_quiz_response':
            retry_question = tools[0]['data']['phase2']['tool']['data']['question']
            retry_options = tools[0]['data']['phase2']['tool']['data']['options']
        else:
            retry_question = tools[0]['data']['question']
            retry_options = tools[0]['data']['options']
        
        print(f"📋 RETRY QUESTION:")
        print(f"   Question: {retry_question}")
        
        # THE KEY TEST: Should retry with SECOND question, not fallback to FIRST
        assert retry_question == second_question, \
            f"❌ BUG DETECTED: Wrong answer on second question should retry second question, not fallback to first.\\n" \
            f"   First question:  {first_question}\\n" \
            f"   Second question: {second_question}\\n" \
            f"   Retry question:  {retry_question}"
        
        assert retry_question != first_question, \
            f"❌ BUG DETECTED: Should NOT fallback to first question when second question is wrong.\\n" \
            f"   Retry question should be: {second_question}\\n" \
            f"   But got fallback to:     {retry_question}"
        
        print("✅ CORRECT: Wrong answer on second question retries second question (no fallback)")
        
    else:
        assert False, "Should provide retry tool after wrong answer"
    
    print("✅ Second question wrong answer fallback test PASSED")

if __name__ == "__main__":
    test_second_question_wrong_answer_no_fallback()
    print("🔴 RED: Second question fallback test completed")