#!/usr/bin/env python3
"""
Test Frontend Quiz Flow - Simulate actual frontend conversation
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user"
CHARACTER_ID = "seol_min_seok_quiz"

def test_frontend_quiz_flow():
    """Test the complete quiz flow as frontend would use it"""
    
    print("🧪 TESTING FRONTEND QUIZ FLOW")
    print("=" * 60)
    
    # Step 1: Start a session
    print("1️⃣ Starting new session...")
    session_response = requests.post(f"{BASE_URL}/api/sessions/start", json={
        "user_id": TEST_USER_ID,
        "character_id": CHARACTER_ID
    })
    
    if session_response.status_code != 200:
        print(f"❌ Failed to start session: {session_response.status_code}")
        return
        
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session started: {session_id}")
    
    # Step 2: Request a quiz
    print("\n2️⃣ Requesting quiz...")
    quiz_request = {
        "message": "조선시대 퀴즈 시작해주세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": CHARACTER_ID,
        "user_id": TEST_USER_ID,
        "session_id": session_id
    }
    
    quiz_response = requests.post(f"{BASE_URL}/api/chat-with-session", json=quiz_request)
    
    if quiz_response.status_code != 200:
        print(f"❌ Failed to get quiz: {quiz_response.status_code}")
        print(f"Response: {quiz_response.text}")
        return
        
    quiz_data = quiz_response.json()
    print(f"✅ Quiz response received")
    print(f"📝 Dialogue: {quiz_data['dialogue'][:200]}...")
    
    # Check if tools (quiz UI) were generated
    tools = quiz_data.get('tools', [])
    if tools:
        print(f"🎯 Tools detected: {len(tools)} tool(s)")
        for tool in tools:
            if tool.get('type') == 'show_selection':
                print(f"   Quiz options: {tool.get('data', {}).get('items', [])}")
    else:
        print("❌ No quiz tools detected in response")
    
    time.sleep(1)  # Give backend time to process
    
    # Step 3: Answer the quiz (simulate user clicking option 2)
    print("\n3️⃣ Answering quiz question...")
    answer_request = {
        "message": "2) 1443년",  # This should trigger our fixed educational logic
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": CHARACTER_ID,
        "user_id": TEST_USER_ID,
        "session_id": session_id
    }
    
    answer_response = requests.post(f"{BASE_URL}/api/chat-with-session", json=answer_request)
    
    if answer_response.status_code != 200:
        print(f"❌ Failed to submit answer: {answer_response.status_code}")
        print(f"Response: {answer_response.text}")
        return
        
    answer_data = answer_response.json()
    print(f"✅ Answer response received")
    print(f"📝 Dialogue: {answer_data['dialogue'][:300]}...")
    
    # Check if educational feedback was provided
    dialogue = answer_data['dialogue']
    educational_indicators = ['정답', '틀렸', '훌륭', '맞습니다', '아쉽', '다음 문제', '다시']
    
    has_educational_content = any(indicator in dialogue for indicator in educational_indicators)
    
    if has_educational_content:
        print("✅ Educational feedback detected!")
    else:
        print("❌ No educational feedback detected")
        
    # Check if next question or retry was provided
    has_continuation = any(word in dialogue for word in ['다음 문제', '다시 한번', '다시 도전'])
    
    if has_continuation:
        print("✅ Quiz continuation detected!")
    else:
        print("❌ No quiz continuation detected")
        
    print(f"\n📋 FINAL ASSESSMENT:")
    print(f"   Session Management: ✅")
    print(f"   Quiz Generation: {'✅' if tools else '❌'}")
    print(f"   Answer Processing: ✅")
    print(f"   Educational Feedback: {'✅' if has_educational_content else '❌'}")
    print(f"   Quiz Continuation: {'✅' if has_continuation else '❌'}")
    
    return has_educational_content and (tools or has_continuation)

if __name__ == "__main__":
    success = test_frontend_quiz_flow()
    
    if success:
        print("\n🎉 FRONTEND QUIZ FLOW: SUCCESS!")
        print("The educational quiz system is working correctly with the frontend.")
    else:
        print("\n❌ FRONTEND QUIZ FLOW: ISSUES FOUND")
        print("The fix may not be working properly in the actual frontend flow.")