#!/usr/bin/env python3
"""
Test with completely fresh session to verify the bug exists
"""

import requests
import json
import time

def test_fresh_session_bug():
    """Test with fresh session and different user ID"""
    
    print("🧪 Fresh Session Bug Test")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Use timestamp to ensure unique user
    timestamp = int(time.time())
    user_id = f"fresh_test_{timestamp}"
    
    try:
        # Step 1: Create completely fresh session
        print(f"\n📋 Step 1: Creating fresh session for user {user_id}...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": user_id
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Fresh Session: {session_id}")
        
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
        quiz1_correct = quiz1_data.get('correct_answer', '')
        
        print(f"❓ QUIZ 1: {quiz1_question}")
        print(f"✅ Correct: {quiz1_correct}")
        
        # Step 3: Answer FIRST quiz CORRECTLY
        print(f"\n📋 Step 3: Answering QUIZ 1 CORRECTLY...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": quiz1_correct,
            "character_id": "seol_min_seok_quiz",
            "user_id": user_id,
            "session_id": session_id
        })
        
        correct_data = response.json()
        
        if correct_data.get('tools') and correct_data['tools'][0].get('type') == 'continuous_quiz_response':
            phase2_tool = correct_data['tools'][0]['data']['phase2']['tool']['data']
            quiz2_question = phase2_tool.get('question', '')
            quiz2_options = phase2_tool.get('options', [])
            quiz2_correct = phase2_tool.get('correct_answer', '')
            
            print(f"❓ QUIZ 2: {quiz2_question}")
            print(f"✅ Correct: {quiz2_correct}")
            
            # Step 4: Answer SECOND quiz CORRECTLY to get THIRD quiz
            print(f"\n📋 Step 4: Answering QUIZ 2 CORRECTLY to get QUIZ 3...")
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": quiz2_correct,
                "character_id": "seol_min_seok_quiz",
                "user_id": user_id,
                "session_id": session_id
            })
            
            quiz2_correct_data = response.json()
            
            if quiz2_correct_data.get('tools') and quiz2_correct_data['tools'][0].get('type') == 'continuous_quiz_response':
                phase2_tool = quiz2_correct_data['tools'][0]['data']['phase2']['tool']['data']
                quiz3_question = phase2_tool.get('question', '')
                quiz3_options = phase2_tool.get('options', [])
                quiz3_correct = phase2_tool.get('correct_answer', '')
                
                print(f"❓ QUIZ 3: {quiz3_question}")
                print(f"✅ Correct: {quiz3_correct}")
                
                # Step 5: Answer THIRD quiz INCORRECTLY - this is where bug might appear
                wrong_answer = next((opt for opt in quiz3_options if opt != quiz3_correct), quiz3_options[0])
                print(f"\n📋 Step 5: Answering QUIZ 3 INCORRECTLY with '{wrong_answer}'...")
                print(f"   (CRITICAL: Should retry QUIZ 3, NOT revert to QUIZ 1 or QUIZ 2)")
                
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
                    
                    print(f"\n🔍 FINAL CRITICAL ANALYSIS:")
                    print(f"   QUIZ 1 was: {quiz1_question[:50]}...")
                    print(f"   QUIZ 2 was: {quiz2_question[:50]}...")  
                    print(f"   QUIZ 3 was: {quiz3_question[:50]}...")
                    print(f"   RETRY shows: {retry_question[:50]}...")
                    
                    if retry_question == quiz3_question:
                        print(f"✅ CORRECT: Retrying QUIZ 3 (as expected)")
                    elif retry_question == quiz2_question:
                        print(f"❌ BUG: Reverted to QUIZ 2!")
                    elif retry_question == quiz1_question:
                        print(f"❌ BUG: Reverted to QUIZ 1!")
                    else:
                        print(f"⚠️  UNEXPECTED: Shows different question entirely")
                        
                else:
                    print(f"❌ No continuous quiz response for wrong answer")
            else:
                print(f"❌ Quiz 2 correct didn't generate Quiz 3")
        else:
            print(f"❌ Quiz 1 correct didn't generate Quiz 2")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fresh_session_bug()