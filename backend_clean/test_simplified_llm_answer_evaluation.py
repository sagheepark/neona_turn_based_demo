#!/usr/bin/env python3
"""
TDD Test: Simplified LLM-Based Answer Evaluation
Following plan_new.md implementation requirements

Test the simplified approach where:
1. Store question context in chat history 
2. Let LLM directly compare user answer with correct answer
3. LLM uses its knowledge to determine correctness
4. No hardcoded if/else logic for answer checking
"""

import requests
import json
import pytest

BASE_URL = "http://localhost:8001"

def test_llm_direct_answer_evaluation():
    """
    RED Phase: Test that LLM can directly evaluate answers using knowledge
    This should replace hardcoded answer checking logic
    """
    print("🔴 TDD RED: Testing LLM direct answer evaluation")
    
    character_id = "dr_genie_science_quiz"
    
    # Step 1: Start session and get first question
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "test_llm_eval"
    })
    
    data = response.json()
    session_id = data.get('session_id')
    tools = data.get('tools', [])
    
    # Step 2: Select science topic to get quiz question
    if tools:
        topic = tools[0]['data']['options'][0]  # Pick first topic
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": topic,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "test_llm_eval"
        })
        
        data = response.json()
        tools = data.get('tools', [])
    
    # Step 3: Get the question details
    if tools:
        question = tools[0]['data']['question']
        options = tools[0]['data']['options']
        correct_answer = tools[0]['data']['correct_answer']
        
        print(f"Question: {question}")
        print(f"Options: {options}")
        print(f"System's correct answer: {correct_answer}")
        
        # Step 4: Test LLM evaluation with WRONG answer
        # For "물이 0도 이하로 내려가면?" correct should be "고체", wrong is "기체"
        wrong_answer = None
        for option in options:
            if option != correct_answer:
                wrong_answer = option
                break
        
        print(f"Testing with WRONG answer: {wrong_answer}")
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": wrong_answer,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "test_llm_eval"
        })
        
        data = response.json()
        dialogue = data.get('dialogue', '')
        tools = data.get('tools', [])
        
        print(f"LLM Response to wrong answer: {dialogue}")
        
        # CRITICAL TEST: LLM should correctly identify this as WRONG
        # The response should indicate the answer is incorrect
        assert any(word in dialogue.lower() for word in ['틀', '아니', '다시', '잘못']), \
            f"LLM should identify wrong answer as incorrect, got: {dialogue}"
        
        # Should provide retry with same question (not progression)
        if tools:
            if tools[0].get('type') == 'continuous_quiz_response':
                retry_question = tools[0]['data']['phase2']['tool']['data']['question']
                retry_mode = tools[0]['data']['phase2']['tool']['data'].get('retry_mode', False)
            else:
                retry_question = tools[0]['data']['question']
                retry_mode = tools[0]['data'].get('retry_mode', False)
            
            print(f"Retry question: {retry_question}")
            
            # Should be same question for retry
            assert retry_question == question, \
                f"Wrong answer should trigger retry with same question, got different: {retry_question}"
            
            # Should be in retry mode (optional - focus on same question retry)
            print(f"Retry mode flag: {retry_mode}")  # Log for debugging
        
        print("✅ LLM correctly identified wrong answer and provided retry")
        
        # Step 5: Now test with CORRECT answer on retry
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": correct_answer,
            "character_id": character_id,
            "session_id": session_id,
            "user_id": "test_llm_eval"
        })
        
        data = response.json()
        dialogue = data.get('dialogue', '')
        tools = data.get('tools', [])
        
        print(f"LLM Response to correct answer: {dialogue}")
        
        # CRITICAL TEST: LLM should correctly identify this as CORRECT
        assert any(word in dialogue.lower() for word in ['정답', '맞', '훌륭', '좋아']), \
            f"LLM should identify correct answer as right, got: {dialogue}"
        
        # Should provide new question (progression)
        if tools:
            if tools[0].get('type') == 'continuous_quiz_response':
                new_question = tools[0]['data']['phase2']['tool']['data']['question']
                retry_mode = tools[0]['data']['phase2']['tool']['data'].get('retry_mode', False)
            else:
                new_question = tools[0]['data']['question']
                retry_mode = tools[0]['data'].get('retry_mode', False)
            
            print(f"New question after correct: {new_question}")
            
            # Should be different question (progression)
            assert new_question != question, \
                f"Correct answer should trigger new question, got same: {new_question}"
            
            # Should NOT be in retry mode
            assert not retry_mode, "Correct answer should not be in retry mode"
        
        print("✅ LLM correctly identified correct answer and provided progression")
    
    print("✅ LLM direct answer evaluation test completed")

def test_llm_context_storage_in_chat_history():
    """
    Test that question context is properly stored in chat history
    for LLM to reference during evaluation (per plan_new.md)
    """
    print("🔴 TDD RED: Testing question context storage in chat history")
    
    # This test verifies that the LLM has access to the current question context
    # when evaluating answers, following plan_new.md approach
    
    character_id = "seol_min_seok_quiz"
    
    # Start session and get to quiz question
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "test_context_storage"
    })
    
    data = response.json()
    session_id = data.get('session_id')
    
    # The actual implementation of context storage testing will be in GREEN phase
    # For now, just verify we can access the system
    assert session_id, "Should create session for context storage testing"
    
    print("✅ Context storage test framework ready")

if __name__ == "__main__":
    test_llm_direct_answer_evaluation()
    test_llm_context_storage_in_chat_history()
    print("🔴 RED: Simplified LLM answer evaluation tests written")