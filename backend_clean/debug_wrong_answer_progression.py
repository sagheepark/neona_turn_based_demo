#!/usr/bin/env python3
"""
Debug Wrong Answer Progression Issue
Test what happens when user gets first question right, second question wrong
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_wrong_answer_progression():
    """Test the progression issue when getting wrong answer on second question"""
    print("🔍 DEBUGGING WRONG ANSWER PROGRESSION ISSUE")
    
    character_id = "dr_genie_science_quiz"
    
    # Step 1: Get greeting
    print("\n📋 STEP 1: Get Greeting")
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "debug_user"
    })
    
    data = response.json()
    session_id = data.get('session_id')
    tools = data.get('tools', [])
    print(f"✅ Session: {session_id}")
    
    # Step 2: Select topic
    print("\n📋 STEP 2: Select Topic")
    topic = tools[0]['data']['options'][0]
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": topic,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "debug_user"
    })
    
    data = response.json()
    tools = data.get('tools', [])
    print(f"✅ Topic selected: {topic}")
    
    # Step 3: Answer first question CORRECTLY
    print("\n📋 STEP 3: Answer First Question CORRECTLY")
    first_question = tools[0]['data']['question']
    first_options = tools[0]['data']['options']
    first_correct = tools[0]['data']['correct_answer']
    
    print(f"Question 1: {first_question}")
    print(f"Options 1: {first_options}")
    print(f"Correct Answer 1: {first_correct}")
    print(f"Selecting CORRECT answer: {first_correct}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": first_correct,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "debug_user"
    })
    
    data = response.json()
    dialogue = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"Response: {dialogue[:80]}...")
    print(f"Tools: {len(tools)}")
    
    if not tools:
        print("❌ No second question generated!")
        return
    
    # DEBUG: Check what's in the tools
    print(f"🔍 TOOL DEBUG TYPE: {tools[0].get('type')}")
    
    # Handle continuous_quiz_response vs show_selection
    if tools[0].get('type') == 'continuous_quiz_response':
        print("🔍 This is a continuous_quiz_response (two-phase) tool")
        phase2_data = tools[0]['data']['phase2']
        if 'tool' in phase2_data:
            actual_tool = phase2_data['tool']['data']
            print(f"Phase2 tool data: {actual_tool}")
            second_question = actual_tool['question']
            second_options = actual_tool['options'] 
            second_correct = actual_tool['correct_answer']
        else:
            print("❌ No tool in phase2!")
            return
    else:
        # Regular show_selection tool
        tool_data = tools[0]['data']
        if 'question' not in tool_data:
            print("❌ Tool missing question field!")
            print(f"Available fields: {list(tool_data.keys())}")
            return
        second_question = tool_data['question']
        second_options = tool_data['options']
        second_correct = tool_data['correct_answer']
        
    # Step 4: Handle the next question
    print("\n📋 STEP 4: Analyze Next Question")
    
    print(f"Question 2: {second_question}")
    print(f"Options 2: {second_options}")
    print(f"Correct Answer 2: {second_correct}")
    
    # Select a WRONG answer (not the correct one)
    wrong_answer = None
    for option in second_options:
        if option != second_correct:
            wrong_answer = option
            break
    
    print(f"Selecting WRONG answer: {wrong_answer}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": wrong_answer,
        "character_id": character_id,
        "session_id": session_id,
        "user_id": "debug_user"
    })
    
    data = response.json()
    dialogue = data.get('dialogue', '')
    tools = data.get('tools', [])
    
    print(f"Response: {dialogue[:80]}...")
    print(f"Tools: {len(tools)}")
    
    if tools:
        # Handle continuous_quiz_response vs show_selection for retry
        if tools[0].get('type') == 'continuous_quiz_response':
            print("🔍 Retry tool is continuous_quiz_response (two-phase)")
            phase2_data = tools[0]['data']['phase2']
            if 'tool' in phase2_data:
                actual_tool = phase2_data['tool']['data']
                retry_question = actual_tool['question']
                retry_options = actual_tool['options'] 
                retry_correct = actual_tool['correct_answer']
            else:
                print("❌ No tool in phase2 for retry!")
                return
        else:
            # Regular show_selection tool
            retry_question = tools[0]['data']['question']
            retry_options = tools[0]['data']['options']
            retry_correct = tools[0]['data']['correct_answer']
        
        print(f"\n🔍 RETRY ANALYSIS:")
        print(f"Retry Question: {retry_question}")
        print(f"Retry Options: {retry_options}")
        print(f"Retry Correct: {retry_correct}")
        
        # Check if it's the same question (correct behavior) or first question (bug)
        if retry_question == second_question:
            print("✅ CORRECT: Shows same second question for retry")
        elif retry_question == first_question:
            print("❌ BUG DETECTED: Fallback to first question instead of retry on second!")
        else:
            print("❓ UNEXPECTED: Shows completely different question")
            
        print(f"\n🔍 COMPARISON:")
        print(f"First Question:  {first_question}")
        print(f"Second Question: {second_question}")
        print(f"Retry Question:  {retry_question}")

if __name__ == "__main__":
    test_wrong_answer_progression()