#!/usr/bin/env python3
"""
Test the caching issue where second wrong answer reviews first wrong option instead of current selection
"""

import requests
import json

def test_consecutive_wrong_answers():
    """Test that consecutive wrong answers review the CURRENT selection, not cached previous selection"""
    
    print("🧪 Testing Consecutive Wrong Answers Caching Fix")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "cache_test_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "cache_test_user",
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
        
        # Get two different wrong answers
        wrong_options = [opt for opt in options if opt != correct_answer]
        if len(wrong_options) < 2:
            print("❌ Not enough wrong options to test consecutive failures")
            return False
            
        first_wrong = wrong_options[0]
        second_wrong = wrong_options[1]
        
        # Step 3: First wrong answer
        print(f"\n📋 Step 3: Answering INCORRECTLY (1st time) with '{first_wrong}'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": first_wrong,
            "character_id": "seol_min_seok_quiz",
            "user_id": "cache_test_user",
            "session_id": session_id
        })
        
        result1 = response.json()
        if result1.get('tools') and result1['tools'][0].get('type') == 'continuous_quiz_response':
            phase1_text_1 = result1['tools'][0]['data']['phase1']['text']
            print(f"🔍 First wrong answer feedback: '{phase1_text_1}'")
            
            # Verify it mentions the first wrong answer
            mentions_first_wrong = first_wrong in phase1_text_1
            print(f"   Mentions first wrong answer '{first_wrong}': {mentions_first_wrong}")
        
        # Step 4: Second wrong answer (DIFFERENT from first)
        print(f"\n📋 Step 4: Answering INCORRECTLY (2nd time) with '{second_wrong}'...")
        print(f"   CRITICAL: This should review '{second_wrong}', NOT '{first_wrong}'")
        
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": second_wrong,
            "character_id": "seol_min_seok_quiz",
            "user_id": "cache_test_user",
            "session_id": session_id
        })
        
        result2 = response.json()
        
        if result2.get('tools') and result2['tools'][0].get('type') == 'continuous_quiz_response':
            phase1_text_2 = result2['tools'][0]['data']['phase1']['text']
            print(f"🔍 Second wrong answer feedback: '{phase1_text_2}'")
            
            # Critical test: Should mention second wrong answer, not first
            mentions_second_wrong = second_wrong in phase1_text_2
            mentions_first_wrong = first_wrong in phase1_text_2
            
            print(f"\n🎯 CACHING VALIDATION:")
            print(f"   Mentions current selection '{second_wrong}': {mentions_second_wrong}")
            print(f"   Mentions previous selection '{first_wrong}': {mentions_first_wrong}")
            
            if mentions_second_wrong and not mentions_first_wrong:
                print(f"\n✅ CACHING FIX SUCCESSFUL!")
                print(f"✅ System correctly reviews current selection, not cached previous")
                return True
            elif mentions_first_wrong and not mentions_second_wrong:
                print(f"\n❌ CACHING BUG CONFIRMED!")
                print(f"❌ System reviews PREVIOUS selection '{first_wrong}' instead of CURRENT '{second_wrong}'")
                print(f"   This is the exact bug the user reported")
                return False
            elif mentions_second_wrong and mentions_first_wrong:
                print(f"\n⚠️ PARTIAL ISSUE:")
                print(f"⚠️ System mentions both selections - may be using cached context")
                return False
            else:
                print(f"\n❓ UNCLEAR RESULT:")
                print(f"❓ System doesn't mention either selection specifically")
                return False
                
        else:
            print(f"❌ No continuous_quiz_response tool found in second response")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_consecutive_wrong_answers()
    if success:
        print(f"\n🎯 RESULT: Caching issue is FIXED!")
    else:
        print(f"\n⚠️ RESULT: Caching issue needs to be addressed.")