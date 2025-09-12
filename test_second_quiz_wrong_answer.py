#!/usr/bin/env python3
"""
Test the exact issue: Second quiz wrong answer going back to first quiz
Also check if duplication is really fixed
"""

import requests
import json

def test_second_quiz_wrong_answer_issue():
    """Test the complete flow: correct first quiz → wrong second quiz"""
    
    print("🧪 Testing Second Quiz Wrong Answer Issue")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_second_quiz_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_second_quiz_user",
            "session_id": session_id
        })
        
        data = response.json()
        quiz1_data = data['tools'][0]['data']
        quiz1_question = quiz1_data.get('question', '')
        quiz1_correct = quiz1_data.get('correct_answer', '')
        
        print(f"❓ First Quiz: {quiz1_question}")
        print(f"✅ Correct Answer: {quiz1_correct}")
        
        # Step 3: Answer FIRST quiz CORRECTLY → should get second quiz
        print(f"\n📋 Step 3: Answering FIRST quiz CORRECTLY with '{quiz1_correct}'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": quiz1_correct,
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_second_quiz_user",
            "session_id": session_id
        })
        
        correct_data = response.json()
        print(f"✅ First quiz correct response received")
        
        # Check if we got a continuous quiz response with new question
        if correct_data.get('tools') and correct_data['tools'][0].get('type') == 'continuous_quiz_response':
            phase2_tool = correct_data['tools'][0]['data']['phase2']['tool']['data']
            quiz2_question = phase2_tool.get('question', '')
            quiz2_options = phase2_tool.get('options', [])
            quiz2_correct = phase2_tool.get('correct_answer', '')
            
            print(f"❓ Second Quiz: {quiz2_question}")
            print(f"📝 Options: {quiz2_options}")
            print(f"✅ Correct Answer: {quiz2_correct}")
            
            # CRITICAL: Verify this is a DIFFERENT question from first quiz
            is_new_question = quiz2_question != quiz1_question
            print(f"🔍 Is second quiz different from first: {is_new_question}")
            
            if not is_new_question:
                print(f"❌ ERROR: Second quiz is same as first quiz!")
                return
            
            # Step 4: Answer SECOND quiz INCORRECTLY → should retry second quiz, NOT go back to first
            wrong_answer = next(opt for opt in quiz2_options if opt != quiz2_correct)
            print(f"\n📋 Step 4: Answering SECOND quiz INCORRECTLY with '{wrong_answer}'...")
            print(f"   This should retry the SECOND quiz, NOT go back to first quiz")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_second_quiz_user",
                "session_id": session_id
            })
            
            wrong_data = response.json()
            print(f"📊 Second quiz wrong answer response:")
            
            # Check for duplication in the dialogue
            dialogue = wrong_data.get('dialogue', '')
            print(f"📝 Dialogue: {dialogue}")
            
            # Check for question duplication
            question_count = dialogue.count(quiz2_question) if quiz2_question in dialogue else 0
            print(f"🔍 Question appears {question_count} times in dialogue")
            if question_count > 1:
                print(f"❌ DUPLICATION ISSUE: Question appears {question_count} times!")
            else:
                print(f"✅ No duplication in dialogue")
            
            # Check the continuous quiz response
            if wrong_data.get('tools') and wrong_data['tools'][0].get('type') == 'continuous_quiz_response':
                retry_tool = wrong_data['tools'][0]['data']['phase2']['tool']['data']
                retry_question = retry_tool.get('question', '')
                
                print(f"❓ Retry Question: {retry_question}")
                
                # CRITICAL TEST: Should retry SECOND quiz, not revert to first
                if retry_question == quiz2_question:
                    print(f"✅ CORRECT: Retrying second quiz question")
                elif retry_question == quiz1_question:
                    print(f"❌ BUG CONFIRMED: Reverted to first quiz question!")
                    print(f"   Expected: {quiz2_question}")
                    print(f"   Got: {retry_question}")
                else:
                    print(f"❌ UNEXPECTED: Got completely different question: {retry_question}")
                
                # Check for duplication in phase2 text
                phase2_text = wrong_data['tools'][0]['data']['phase2'].get('text', '')
                print(f"📝 Phase 2 text: {phase2_text}")
                phase2_question_count = phase2_text.count(retry_question) if retry_question in phase2_text else 0
                print(f"🔍 Question appears {phase2_question_count} times in Phase 2 text")
                if phase2_question_count > 1:
                    print(f"❌ PHASE 2 DUPLICATION: Question appears {phase2_question_count} times!")
                else:
                    print(f"✅ No duplication in Phase 2 text")
                    
            else:
                print(f"❌ Expected continuous_quiz_response for wrong answer retry")
        else:
            print(f"❌ First correct answer didn't generate continuous quiz response")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_second_quiz_wrong_answer_issue()