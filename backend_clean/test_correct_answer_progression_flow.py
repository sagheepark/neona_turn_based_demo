#!/usr/bin/env python3
"""
TDD Test: Verify Correct Answer Progression Flow
Following plan_new.md Phase 1 requirements

Test Case: When user answers question correctly, system should:
1. Provide positive feedback celebrating the correct answer
2. Generate NEW question on different topic (progression)
3. Store question context in chat history for future evaluation
"""

import requests
import json
import pytest

BASE_URL = "http://localhost:8001"

def test_correct_answer_progression_flow():
    """
    RED Phase: Write failing test for correct answer progression
    This test verifies that correct answers lead to NEW questions (progression)
    """
    print("🔴 TDD RED: Testing correct answer progression flow")
    
    character_id = "seol_min_seok_quiz"
    
    # Step 1: Get greeting and select topic
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "test_progression"
    })
    
    data = response.json()
    session_id = data.get('session_id')
    tools = data.get('tools', [])
    
    assert session_id, "Should create valid session"
    assert tools, "Should provide topic selection tools"
    
    # Step 2: Select first topic
    topic = tools[0]['data']['options'][0]
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": topic,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_progression"
    })
    
    data = response.json()
    tools = data.get('tools', [])
    
    # Extract first question details
    first_question = tools[0]['data']['question']
    first_options = tools[0]['data']['options']
    first_correct = tools[0]['data']['correct_answer']
    
    print(f"First Question: {first_question}")
    print(f"Correct Answer: {first_correct}")
    
    # Step 3: Answer CORRECTLY (this is the key test)
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": first_correct,  # Provide correct answer
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "test_progression"
    })
    
    data = response.json()
    dialogue = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"Response to correct answer: {dialogue}")
    
    # ASSERTIONS for correct answer progression flow:
    
    # 1. Should celebrate correct answer in dialogue
    assert any(word in dialogue.lower() for word in ['정답', '맞습니다', '맞았습니다', '축하', '잘했어요']), \
        f"Dialogue should celebrate correct answer, got: {dialogue}"
    
    # 2. Should provide NEW question (different from first)
    assert tools, "Should provide new question tool after correct answer"
    
    if tools[0].get('type') == 'continuous_quiz_response':
        second_question = tools[0]['data']['phase2']['tool']['data']['question']
    else:
        second_question = tools[0]['data']['question']
    
    print(f"Second Question: {second_question}")
    
    # CRITICAL: New question should be different (progression, not retry)
    assert second_question != first_question, \
        f"After correct answer, should get NEW question, not retry. Got same question: {first_question}"
    
    # 3. Should not be in retry mode
    if tools[0].get('type') == 'continuous_quiz_response':
        retry_mode = tools[0]['data']['phase2']['tool']['data'].get('retry_mode', False)
    else:
        retry_mode = tools[0]['data'].get('retry_mode', False)
    
    assert not retry_mode, "After correct answer, should not be in retry mode"
    
    print("✅ Correct answer progression flow test assertions passed")

def test_answer_evaluation_with_llm_context():
    """
    Test that answer evaluation uses explicit question context as per plan_new.md
    This verifies the LLM gets proper context for evaluation
    """
    print("🔴 TDD RED: Testing LLM context-aware answer evaluation")
    
    # This test will verify that the system provides explicit question context
    # to the LLM for evaluation, following plan_new.md requirements
    
    # Test scenarios from plan_new.md
    scenarios = [
        {
            "question": "세종대왕의 업적은?", 
            "correct": "한글", 
            "user": "한글 창제", 
            "should_pass": True,
            "description": "Should accept variations of correct answer"
        },
        {
            "question": "물의 화학식은?", 
            "correct": "H2O", 
            "user": "h2o", 
            "should_pass": True,
            "description": "Should handle case insensitive matches"
        }
    ]
    
    # For now, just verify the framework is ready
    # Actual implementation will follow in GREEN phase
    character_id = "dr_genie_science_quiz"
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "test_llm_eval"
    })
    
    # Basic connectivity test
    assert response.status_code == 200, "Should connect to backend"
    
    print("✅ LLM evaluation test framework ready")

if __name__ == "__main__":
    test_correct_answer_progression_flow()
    test_answer_evaluation_with_llm_context()
    print("🔴 All RED tests written - ready for GREEN implementation")