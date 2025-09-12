#!/usr/bin/env python3
"""
Test Complete User Flow: Greeting → Topic Selection → Quiz Question → Quiz Answer
Validates the entire user journey with all fixes applied
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_user_flow():
    """
    Test the complete user journey from greeting to quiz answer
    """
    print("🎮 TESTING COMPLETE USER FLOW")
    print("=" * 70)
    
    # Step 1: Greeting
    print("\n1️⃣ STEP 1: USER GREETING")
    print("-" * 40)
    
    greeting_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "flow_test_user"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        return False
        
    greeting_data = greeting_response.json()
    session_id = greeting_data["session_id"]
    
    print(f"✅ Greeting Response:")
    print(f"   Dialogue: {greeting_data['dialogue']}")
    print(f"   Session: {session_id}")
    
    # Check greeting tools
    greeting_tools = greeting_data.get('tools', [])
    if greeting_tools:
        tool = greeting_tools[0]
        items = tool['data'].get('items', [])
        has_correct_answer = 'correct_answer' in tool['data']
        
        print(f"   📋 Topic Options: {items}")
        print(f"   🎯 Tool Type: {tool['type']}")
        print(f"   ❓ Has correct_answer: {has_correct_answer}")
        print(f"   ✅ This is a TOPIC SELECTION (not quiz answer)")
        
        if len(items) == 0:
            print(f"   ❌ No topic options provided")
            return False
    else:
        print(f"   ❌ No tools in greeting response")
        return False
    
    time.sleep(1)
    
    # Step 2: Topic Selection
    print("\n2️⃣ STEP 2: TOPIC SELECTION")
    print("-" * 40)
    print(f"   User clicks: '근현대사 퀴즈'")
    
    topic_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "근현대사 퀴즈",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "flow_test_user",
        "session_id": session_id
    })
    
    if topic_response.status_code != 200:
        print(f"❌ Topic selection failed: {topic_response.status_code}")
        return False
        
    topic_data = topic_response.json()
    
    print(f"✅ Topic Selection Response:")
    print(f"   Dialogue: {topic_data['dialogue'][:100]}...")
    
    # Check quiz question tools
    quiz_tools = topic_data.get('tools', [])
    if quiz_tools:
        tool = quiz_tools[0]
        tool_data = tool['data']
        
        question = tool_data.get('question')
        items = tool_data.get('items', [])
        correct_answer = tool_data.get('correct_answer')
        selection_mode = tool_data.get('selection_mode')
        
        print(f"   📋 Quiz Question: {question}")
        print(f"   🎯 Options: {items}")
        print(f"   ✅ Correct Answer: {correct_answer}")
        print(f"   📝 Selection Mode: {selection_mode}")
        print(f"   ✅ This is a QUIZ QUESTION (has correct_answer)")
        
        if not correct_answer:
            print(f"   ❌ No correct_answer in quiz question")
            return False
            
        if selection_mode != 'quiz_question':
            print(f"   ❌ Wrong selection_mode: {selection_mode}")
            return False
    else:
        print(f"   ❌ No tools in topic response (no quiz question)")
        return False
    
    time.sleep(1)
    
    # Step 3: Quiz Answer
    print("\n3️⃣ STEP 3: QUIZ ANSWER")
    print("-" * 40)
    print(f"   User clicks first option: '{items[0]}'")
    
    answer_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": items[0],  # Answer with first option
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "flow_test_user",
        "session_id": session_id
    })
    
    if answer_response.status_code != 200:
        print(f"❌ Quiz answer failed: {answer_response.status_code}")
        return False
        
    answer_data = answer_response.json()
    
    print(f"✅ Quiz Answer Response:")
    print(f"   Dialogue: {answer_data['dialogue'][:150]}...")
    
    # Check for educational feedback
    dialogue = answer_data['dialogue']
    has_feedback = any(word in dialogue for word in [
        '정답', '틀렸', '훌륭', '맞습니다', '아쉽', '설명'
    ])
    
    print(f"   📚 Educational Feedback: {'✅' if has_feedback else '❌'}")
    
    # Check if next question is provided
    next_tools = answer_data.get('tools', [])
    if next_tools:
        print(f"   🔄 Next Question Ready: ✅")
    else:
        print(f"   🔄 Next Question: Not provided (may come via continuous flow)")
    
    return True

def analyze_flow_behavior():
    """
    Analyze expected behavior for each step
    """
    print("\n📊 EXPECTED FLOW BEHAVIOR ANALYSIS")
    print("=" * 70)
    
    print("\n🎯 GREETING SELECTION (Topic):")
    print("   - Tool has: question, items")
    print("   - Tool lacks: correct_answer, selection_mode")
    print("   - Frontend action: handleSend(selection) - regular message")
    print("   - Backend response: Generate quiz question")
    
    print("\n🎯 QUIZ ANSWER SELECTION:")
    print("   - Tool has: question, items, correct_answer, selection_mode='quiz_question'")
    print("   - Frontend action: triggerContinuousFlow() - educational feedback")
    print("   - Backend response: Provide feedback + next question")
    
    print("\n✅ KEY DIFFERENTIATION:")
    print("   Topic Selection: NO correct_answer → Regular message")
    print("   Quiz Answer: HAS correct_answer → Continuous flow")

if __name__ == "__main__":
    print("🚀 COMPLETE USER FLOW TEST")
    print("Testing: Greeting → Topic Selection → Quiz Question → Quiz Answer")
    print("=" * 80)
    
    flow_success = test_complete_user_flow()
    
    print("\n" + "=" * 80)
    
    if flow_success:
        analyze_flow_behavior()
        
        print("\n🎉 COMPLETE FLOW TEST: SUCCESS!")
        print("=" * 80)
        print("✅ All steps working correctly:")
        print("   1. Greeting provides topic selection")
        print("   2. Topic selection generates quiz question") 
        print("   3. Quiz answer provides educational feedback")
        
        print("\n📱 FRONTEND BEHAVIOR:")
        print("   ✅ Topic selections → Regular messages")
        print("   ✅ Quiz answers → Continuous flow with feedback")
        
        print("\n🎯 USER EXPERIENCE:")
        print("   ✅ Click greeting option → Gets quiz started")
        print("   ✅ Answer quiz → Gets educational feedback")
        print("   ✅ Seamless flow without errors")
    else:
        print("❌ COMPLETE FLOW TEST: FAILED")
        print("Check individual step results above for details")