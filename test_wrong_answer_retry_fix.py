#!/usr/bin/env python3
"""
Test that wrong answers now retry the same question with the LLM fix
"""

import requests
import json
import time

def test_wrong_answer_retry_fix():
    """Test that wrong answers retry same question"""
    
    print("🧪 Wrong Answer Retry Fix Test")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Use timestamp to ensure unique user
    timestamp = int(time.time())
    user_id = f"retry_test_{timestamp}"
    
    try:
        # Step 1: Create fresh session
        print(f"\n📋 Step 1: Creating fresh session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": user_id
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": user_id,
            "session_id": session_id
        })
        
        data = response.json()
        quiz1_data = data['tools'][0]['data']
        quiz1_question = quiz1_data.get('question', '')
        quiz1_options = quiz1_data.get('options', [])
        quiz1_correct = quiz1_data.get('correct_answer', '')
        
        print(f"❓ FIRST QUIZ: {quiz1_question}")
        print(f"📝 Options: {quiz1_options}")
        print(f"✅ Correct: {quiz1_correct}")
        
        # Step 3: Answer FIRST quiz INCORRECTLY - this is the critical test
        wrong_answer = next((opt for opt in quiz1_options if opt != quiz1_correct), quiz1_options[0])
        print(f"\n📋 Step 3: Answering FIRST quiz INCORRECTLY with '{wrong_answer}'...")
        print(f"   EXPECTED: Should retry the SAME question")
        print(f"   ORIGINAL QUESTION: {quiz1_question}")
        
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": wrong_answer,
            "character_id": "seol_min_seok_quiz",
            "user_id": user_id,
            "session_id": session_id
        })
        
        wrong_data = response.json()
        
        if wrong_data.get('tools') and wrong_data['tools'][0].get('type') == 'continuous_quiz_response':
            retry_tool = wrong_data['tools'][0]['data']['phase2']['tool']['data']
            retry_question = retry_tool.get('question', '')
            retry_options = retry_tool.get('options', [])
            
            print(f"\n🔍 RETRY QUESTION CHECK:")
            print(f"   ORIGINAL: {quiz1_question}")
            print(f"   RETRY: {retry_question}")
            
            if retry_question == quiz1_question:
                print(f"✅ SUCCESS: Retry shows SAME question (fix working!)")
                
                # Check options too
                if retry_options == quiz1_options:
                    print(f"✅ SUCCESS: Options are identical")
                else:
                    print(f"⚠️  WARNING: Options are different")
                    print(f"   ORIGINAL: {quiz1_options}")
                    print(f"   RETRY: {retry_options}")
                    
            else:
                print(f"❌ BUG PERSISTS: Retry shows DIFFERENT question")
                print(f"   This means the LLM fix didn't work")
                
        else:
            print(f"❌ No continuous quiz response for wrong answer")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wrong_answer_retry_fix()