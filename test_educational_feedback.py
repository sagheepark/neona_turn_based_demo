#!/usr/bin/env python3
"""
Test that wrong answer feedback provides educational hints without revealing the correct answer
"""

import requests
import json
import re

def test_educational_feedback():
    """Test that wrong answers get educational hints, not answer revelations"""
    
    print("🧪 Testing Educational Feedback (No Answer Revelation)")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "educational_test_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "educational_test_user",
            "session_id": session_id
        })
        
        data = response.json()
        quiz_data = data['tools'][0]['data']
        question = quiz_data.get('question', '')
        options = quiz_data.get('options', [])
        correct_answer = quiz_data.get('correct_answer', '')
        
        print(f"❓ Quiz Question: {question}")
        print(f"📝 Options: {options}")
        print(f"✅ Correct Answer: {correct_answer}")
        
        # Step 3: Answer INCORRECTLY - this is the critical test
        wrong_answer = next((opt for opt in options if opt != correct_answer), options[0])
        print(f"\n📋 Step 3: Answering INCORRECTLY with '{wrong_answer}'...")
        print(f"   Expected: Educational hints WITHOUT revealing '{correct_answer}'")
        
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": wrong_answer,
            "character_id": "seol_min_seok_quiz",
            "user_id": "educational_test_user",
            "session_id": session_id
        })
        
        result = response.json()
        
        if result.get('tools') and result['tools'][0].get('type') == 'continuous_quiz_response':
            phase1_text = result['tools'][0]['data']['phase1']['text']
            
            print(f"\n🔍 EDUCATIONAL FEEDBACK ANALYSIS:")
            print(f"   Phase 1 text: '{phase1_text}'")
            
            # Test 1: Check if correct answer is revealed
            contains_correct_answer = correct_answer in phase1_text
            print(f"   Contains correct answer '{correct_answer}': {contains_correct_answer}")
            
            if contains_correct_answer:
                print(f"❌ EDUCATIONAL FAILURE: Correct answer revealed in feedback!")
                print(f"   This breaks the learning process - students should discover the answer")
                return False
            else:
                print(f"✅ EDUCATIONAL SUCCESS: No answer revelation detected")
            
            # Test 2: Check for educational content
            has_educational_content = len(phase1_text) > 20  # Should have substantial content
            print(f"   Has substantial educational content: {has_educational_content}")
            
            # Test 3: Check for encouraging language
            encouraging_words = ['다시', '생각', '한번', '힌트', '중요', '역할', '시대', '건국', '인물']
            has_encouraging_language = any(word in phase1_text for word in encouraging_words)
            print(f"   Contains encouraging/guiding language: {has_encouraging_language}")
            
            # Test 4: Check that it doesn't just say "wrong"
            is_just_wrong = phase1_text in ['틀렸습니다', '잘못되었습니다', '아닙니다']
            print(f"   Is just a simple 'wrong' response: {is_just_wrong}")
            
            # Final assessment
            if (not contains_correct_answer and 
                has_educational_content and 
                has_encouraging_language and 
                not is_just_wrong):
                print(f"\n🎉 EDUCATIONAL FEEDBACK TEST PASSED!")
                print(f"✅ Provides hints without revealing answer")
                print(f"✅ Contains educational content")
                print(f"✅ Uses encouraging language") 
                print(f"✅ More than just 'wrong' response")
                return True
            else:
                print(f"\n❌ EDUCATIONAL FEEDBACK NEEDS IMPROVEMENT:")
                if contains_correct_answer:
                    print(f"   - Reveals correct answer (major issue)")
                if not has_educational_content:
                    print(f"   - Lacks substantial educational content")
                if not has_encouraging_language:
                    print(f"   - Missing encouraging/guiding language")
                if is_just_wrong:
                    print(f"   - Too simple, just says 'wrong'")
                return False
                
        else:
            print(f"❌ No continuous_quiz_response tool found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_educational_feedback()
    if success:
        print(f"\n🎯 RESULT: Educational feedback system is working correctly!")
    else:
        print(f"\n⚠️  RESULT: Educational feedback needs improvement.")