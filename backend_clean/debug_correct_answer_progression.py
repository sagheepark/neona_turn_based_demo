#!/usr/bin/env python3
"""
Debug Correct Answer Progression
Test what happens when user gets first question right, then second question right
Should show progression to new questions
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_correct_answer_progression():
    """Test the progression when getting correct answers"""
    print("🔍 DEBUGGING CORRECT ANSWER PROGRESSION")
    
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
    
    # Handle continuous_quiz_response vs show_selection
    if tools[0].get('type') == 'continuous_quiz_response':
        print("🔍 This is a continuous_quiz_response (two-phase) tool")
        phase2_data = tools[0]['data']['phase2']
        if 'tool' in phase2_data:
            actual_tool = phase2_data['tool']['data']
            second_question = actual_tool['question']
            second_options = actual_tool['options'] 
            second_correct = actual_tool['correct_answer']
        else:
            print("❌ No tool in phase2!")
            return
    else:
        tool_data = tools[0]['data']
        second_question = tool_data['question']
        second_options = tool_data['options']
        second_correct = tool_data['correct_answer']
        
    # Step 4: Analyze second question
    print("\n📋 STEP 4: Analyze Second Question")
    
    print(f"Question 2: {second_question}")
    print(f"Options 2: {second_options}")
    print(f"Correct Answer 2: {second_correct}")
    
    # Step 5: Answer second question CORRECTLY
    print("\n📋 STEP 5: Answer Second Question CORRECTLY")
    print(f"Selecting CORRECT answer: {second_correct}")
    
    response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": second_correct,
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
        # Handle continuous_quiz_response vs show_selection for third question
        if tools[0].get('type') == 'continuous_quiz_response':
            print("🔍 Third question tool is continuous_quiz_response (two-phase)")
            phase2_data = tools[0]['data']['phase2']
            if 'tool' in phase2_data:
                actual_tool = phase2_data['tool']['data']
                third_question = actual_tool['question']
                third_options = actual_tool['options'] 
                third_correct = actual_tool['correct_answer']
            else:
                print("❌ No tool in phase2 for third question!")
                return
        else:
            third_question = tools[0]['data']['question']
            third_options = tools[0]['data']['options']
            third_correct = tools[0]['data']['correct_answer']
        
        print(f"\n🔍 PROGRESSION ANALYSIS:")
        print(f"Third Question: {third_question}")
        print(f"Third Options: {third_options}")
        print(f"Third Correct: {third_correct}")
        
        # Check if questions are actually progressing
        if third_question == second_question:
            print("❌ BUG: Third question is same as second question!")
        elif third_question == first_question:
            print("❌ BUG: Third question fallback to first question!")
        else:
            print("✅ CORRECT: Third question is different (progression working)")
            
        print(f"\n🔍 COMPARISON:")
        print(f"First Question:  {first_question}")
        print(f"Second Question: {second_question}")
        print(f"Third Question:  {third_question}")

if __name__ == "__main__":
    test_correct_answer_progression()