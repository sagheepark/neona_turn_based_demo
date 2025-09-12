#!/usr/bin/env python3
"""
Step-by-step test to track exactly what happens with wrong answers
"""

import requests
import json

def test_step_by_step_wrong_answer():
    """Test wrong answer flow step by step to see the reversion issue"""
    
    print("🧪 Step-by-Step Wrong Answer Test")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "step_by_step_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "step_by_step_user",
            "session_id": session_id
        })
        
        data = response.json()
        quiz1_data = data['tools'][0]['data']
        quiz1_question = quiz1_data.get('question', '')
        quiz1_options = quiz1_data.get('options', [])
        quiz1_correct = quiz1_data.get('correct_answer', '')
        
        print(f"❓ QUIZ 1: {quiz1_question}")
        print(f"📝 Options: {quiz1_options}")
        print(f"✅ Correct Answer: {quiz1_correct}")
        
        # Step 3: Answer FIRST quiz CORRECTLY to get second quiz
        print(f"\n📋 Step 3: Answering QUIZ 1 CORRECTLY with '{quiz1_correct}'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": quiz1_correct,
            "character_id": "seol_min_seok_quiz",
            "user_id": "step_by_step_user",
            "session_id": session_id
        })
        
        correct_data = response.json()
        print(f"✅ Quiz 1 correct response received")
        print(f"📊 Response has tools: {len(correct_data.get('tools', []))} tools")
        
        if correct_data.get('tools') and correct_data['tools'][0].get('type') == 'continuous_quiz_response':
            phase2_tool = correct_data['tools'][0]['data']['phase2']['tool']['data']
            quiz2_question = phase2_tool.get('question', '')
            quiz2_options = phase2_tool.get('options', [])
            quiz2_correct = phase2_tool.get('correct_answer', '')
            
            print(f"❓ QUIZ 2: {quiz2_question}")
            print(f"📝 Options: {quiz2_options}")
            print(f"✅ Correct Answer: {quiz2_correct}")
            
            # Step 4: Answer SECOND quiz INCORRECTLY
            wrong_answer = next((opt for opt in quiz2_options if opt != quiz2_correct), quiz2_options[0])
            print(f"\n📋 Step 4: Answering QUIZ 2 INCORRECTLY with '{wrong_answer}'...")
            print(f"   (Expected behavior: Should retry QUIZ 2, NOT revert to QUIZ 1)")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "step_by_step_user",
                "session_id": session_id
            })
            
            wrong_data = response.json()
            print(f"📊 Quiz 2 wrong answer response received")
            print(f"📊 Response has tools: {len(wrong_data.get('tools', []))} tools")
            
            if wrong_data.get('tools') and wrong_data['tools'][0].get('type') == 'continuous_quiz_response':
                retry_tool = wrong_data['tools'][0]['data']['phase2']['tool']['data']
                retry_question = retry_tool.get('question', '')
                retry_options = retry_tool.get('options', [])
                
                print(f"\n🔍 CRITICAL ANALYSIS:")
                print(f"   QUIZ 1 was: {quiz1_question[:50]}...")
                print(f"   QUIZ 2 was: {quiz2_question[:50]}...")  
                print(f"   RETRY shows: {retry_question[:50]}...")
                
                if retry_question == quiz2_question:
                    print(f"✅ CORRECT: Retrying QUIZ 2 (same question)")
                elif retry_question == quiz1_question:
                    print(f"❌ BUG CONFIRMED: Reverted to QUIZ 1!")
                    print(f"   This is the bug user reported!")
                else:
                    print(f"⚠️  DIFFERENT: Shows completely different question")
                    print(f"   This might be progression to QUIZ 3 (wrong behavior for wrong answer)")
                
                print(f"\n📝 Full retry question: {retry_question}")
                print(f"📝 Retry options: {retry_options}")
                    
        else:
            print(f"❌ Quiz 1 correct answer didn't generate continuous quiz response")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_step_by_step_wrong_answer()