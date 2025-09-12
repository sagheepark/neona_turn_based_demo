#!/usr/bin/env python3
"""
Frontend Simulation Test - Test that mimics actual browser behavior
Tests the exact same API calls and logic flow that the frontend uses
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def simulate_frontend_greeting_selection():
    """
    Simulate the exact frontend behavior when selecting a greeting option
    """
    print("🖥️  SIMULATING FRONTEND: Greeting Selection")
    print("=" * 60)
    
    # Step 1: Get greeting with tools (like frontend page load)
    print("\n1️⃣ Frontend: Initial greeting request")
    greeting_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "frontend_sim"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        return False
        
    greeting_data = greeting_response.json()
    session_id = greeting_data["session_id"]
    tools = greeting_data.get('tools', [])
    
    print(f"   Session ID: {session_id}")
    print(f"   Tools received: {len(tools)}")
    
    if not tools:
        print("   ❌ No tools received - frontend would show no selection UI")
        return False
    
    # Step 2: Analyze tool structure (like frontend handleToolSelection does)
    tool = tools[0]
    tool_data = tool['data']
    
    has_correct_answer = 'correct_answer' in tool_data and tool_data['correct_answer'] != ''
    has_selection_mode = 'selection_mode' in tool_data
    selection_mode = tool_data.get('selection_mode')
    
    print(f"\n2️⃣ Frontend: Tool analysis")
    print(f"   Tool type: {tool['type']}")
    print(f"   Has correct_answer: {has_correct_answer}")
    print(f"   Correct answer: {tool_data.get('correct_answer', 'None')}")
    print(f"   Selection mode: {selection_mode}")
    print(f"   Items: {tool_data.get('items', [])}")
    
    # Step 3: Determine frontend behavior
    is_quiz_answer = has_correct_answer and selection_mode == 'quiz_question'
    should_use_continuous_flow = is_quiz_answer
    
    print(f"\n3️⃣ Frontend: Logic determination")
    print(f"   Is quiz answer: {is_quiz_answer}")
    print(f"   Should use continuous flow: {should_use_continuous_flow}")
    print(f"   Will use: {'Continuous Flow' if should_use_continuous_flow else 'Regular Message'}")
    
    # Step 4: Simulate user clicking first option
    selected_option = tool_data['items'][0]  # "조선시대 퀴즈"
    print(f"\n4️⃣ Frontend: User clicks '{selected_option}'")
    
    if should_use_continuous_flow:
        print("   → Triggering continuous flow (WRONG for greeting!)")
        
        # This is what frontend does when it triggers continuous flow
        continuous_response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "show_selection",
            "data": {
                "selection": selected_option,
                "correct_answer": tool_data.get('correct_answer', ''),
                "question": tool_data.get('question', ''),
                "items": tool_data.get('items', [])
            }
        })
        
        if continuous_response.status_code == 200:
            result = continuous_response.json()
            print(f"   ✅ Continuous flow result: {result.get('status')}")
            return True
        else:
            print(f"   ❌ Continuous flow failed: {continuous_response.status_code}")
            return False
            
    else:
        print("   → Sending regular message (CORRECT for greeting!)")
        
        # This is what frontend does when it sends regular message
        message_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
            "message": selected_option,
            "character_prompt": "당신은 설민석 선생님입니다.",
            "character_id": "seol_min_seok_quiz",
            "user_id": "frontend_sim",
            "session_id": session_id
        })
        
        if message_response.status_code == 200:
            result = message_response.json()
            print(f"   ✅ Message response received")
            print(f"   Dialogue: {result['dialogue'][:100]}...")
            
            # Check if quiz question was generated
            new_tools = result.get('tools', [])
            if new_tools:
                quiz_tool = new_tools[0]
                quiz_data = quiz_tool['data']
                has_quiz_correct_answer = 'correct_answer' in quiz_data
                
                print(f"   📝 Quiz generated: {has_quiz_correct_answer}")
                print(f"   Question: {quiz_data.get('question', 'None')[:50]}...")
                return True
            else:
                print(f"   ❌ No quiz question generated")
                return False
        else:
            print(f"   ❌ Message failed: {message_response.status_code}")
            return False

def test_both_scenarios():
    """
    Test both greeting selection and quiz answer scenarios
    """
    print("🧪 COMPREHENSIVE FRONTEND SIMULATION")
    print("=" * 80)
    
    # Test 1: Greeting selection (should use regular message)
    greeting_success = simulate_frontend_greeting_selection()
    
    time.sleep(2)
    
    # Test 2: Quiz answer simulation
    print(f"\n" + "="*80)
    quiz_success = simulate_frontend_quiz_answer()
    
    print(f"\n" + "="*80)
    print("📊 SIMULATION RESULTS")
    print(f"Greeting Selection: {'✅ SUCCESS' if greeting_success else '❌ FAILED'}")
    print(f"Quiz Answer: {'✅ SUCCESS' if quiz_success else '❌ FAILED'}")
    
    return greeting_success and quiz_success

def simulate_frontend_quiz_answer():
    """
    Simulate frontend behavior when answering a quiz question
    """
    print("🖥️  SIMULATING FRONTEND: Quiz Answer")
    print("=" * 60)
    
    # First, get a quiz question
    session_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "quiz_sim"
    })
    
    if session_response.status_code != 200:
        return False
        
    session_data = session_response.json()
    session_id = session_data["session_id"]
    
    # Get quiz question
    quiz_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "조선시대 퀴즈",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "quiz_sim",
        "session_id": session_id
    })
    
    if quiz_response.status_code != 200:
        return False
        
    quiz_data = quiz_response.json()
    tools = quiz_data.get('tools', [])
    
    if not tools:
        print("   ❌ No quiz tools received")
        return False
    
    # Analyze quiz tool (should have correct_answer)
    tool = tools[0]
    tool_data = tool['data']
    
    has_correct_answer = 'correct_answer' in tool_data and tool_data['correct_answer'] != ''
    selection_mode = tool_data.get('selection_mode')
    
    print(f"   Tool analysis:")
    print(f"   Has correct_answer: {has_correct_answer}")
    print(f"   Selection mode: {selection_mode}")
    print(f"   Correct answer: {tool_data.get('correct_answer')}")
    
    # This should be a quiz question, so continuous flow should be used
    is_quiz_answer = has_correct_answer and selection_mode == 'quiz_question'
    
    if not is_quiz_answer:
        print("   ❌ Tool doesn't look like quiz question")
        return False
    
    print(f"   ✅ Detected as quiz answer - will use continuous flow")
    
    # Simulate answering
    selected_answer = tool_data['items'][0]
    print(f"   User selects: {selected_answer}")
    
    continuous_response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
        "session_id": session_id,
        "character_id": "seol_min_seok_quiz",
        "tool_type": "show_selection",
        "data": {
            "selection": selected_answer,
            "correct_answer": tool_data['correct_answer'],
            "question": tool_data['question'],
            "items": tool_data['items']
        }
    })
    
    if continuous_response.status_code == 200:
        result = continuous_response.json()
        print(f"   ✅ Continuous flow triggered: {result.get('status')}")
        
        # Check for educational feedback
        if 'step_result' in result:
            step_result = result['step_result']
            if 'response' in step_result:
                dialogue = step_result['response'].get('dialogue', '')
                has_feedback = any(word in dialogue for word in ['정답', '틀렸', '훌륭', '맞습니다'])
                print(f"   📚 Educational feedback: {'✅' if has_feedback else '❌'}")
                return has_feedback
        
        return True
    else:
        print(f"   ❌ Continuous flow failed: {continuous_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_both_scenarios()
    
    print(f"\n🎯 FRONTEND SIMULATION: {'SUCCESS' if success else 'FAILED'}")
    
    if not success:
        print("\n🔧 LIKELY ISSUES:")
        print("1. Frontend code not updated (need hard refresh)")
        print("2. Logic still treating greeting as quiz answer")
        print("3. Default correct_answer still being added")
        print("4. handleFlowStepResult not processing results correctly")
        
        print("\n📋 DEBUGGING STEPS:")
        print("1. Hard refresh browser (Ctrl+Shift+R)")
        print("2. Check for '🆕 UPDATED CODE VERSION' in console")
        print("3. Verify tool analysis logs show correct values")
        print("4. Test each scenario individually")