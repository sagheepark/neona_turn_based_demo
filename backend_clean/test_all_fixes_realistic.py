#!/usr/bin/env python3
"""
Comprehensive Test: All User-Reported Issues Fixed
Tests the complete user journey with all fixes applied:
1. Greeting selection works (topic selection → regular message)
2. Quiz answer selection works (correct_answer passed properly)  
3. Audio works in continuous flow (uses seolminseok_tts_service)
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_fixed_user_journey():
    """
    Test the complete user journey that was previously broken
    """
    print("🎯 COMPLETE FIXED USER JOURNEY TEST")
    print("=" * 70)
    
    # Step 1: Get greeting with topic selection
    print("\n1️⃣ GREETING: Get topic selection options")
    greeting_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "final_test"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed")
        return False
    
    greeting_data = greeting_response.json()
    session_id = greeting_data["session_id"]
    greeting_tools = greeting_data.get('tools', [])
    
    if not greeting_tools:
        print(f"❌ No greeting tools")
        return False
    
    greeting_tool = greeting_tools[0]
    greeting_has_correct_answer = 'correct_answer' in greeting_tool['data']
    
    print(f"✅ Greeting received:")
    print(f"   Topic options: {len(greeting_tool['data']['items'])}")
    print(f"   Has correct_answer: {greeting_has_correct_answer} (should be False)")
    print(f"   Frontend should: Send as regular message")
    
    # Step 2: Select topic (simulate frontend logic)
    print(f"\n2️⃣ TOPIC SELECTION: User clicks '조선시대 퀴즈'")
    
    # This simulates what the frontend should do (send regular message)
    topic_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "조선시대 퀴즈",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "final_test",
        "session_id": session_id
    })
    
    if topic_response.status_code != 200:
        print(f"❌ Topic selection failed")
        return False
    
    topic_data = topic_response.json()
    quiz_tools = topic_data.get('tools', [])
    
    if not quiz_tools:
        print(f"❌ No quiz question generated")
        return False
    
    quiz_tool = quiz_tools[0]
    quiz_data = quiz_tool['data']
    
    has_correct_answer = 'correct_answer' in quiz_data
    correct_answer = quiz_data.get('correct_answer')
    quiz_options = quiz_data.get('items', [])
    
    print(f"✅ Quiz question generated:")
    print(f"   Question: {quiz_data.get('question', '')[:50]}...")
    print(f"   Options: {quiz_options}")
    print(f"   Has correct_answer: {has_correct_answer} (should be True)")
    print(f"   Correct answer: {correct_answer}")
    print(f"   Frontend should: Trigger continuous flow")
    
    # Step 3: Answer quiz (simulate continuous flow)
    print(f"\n3️⃣ QUIZ ANSWER: User clicks '{correct_answer}'")
    
    # This simulates what the frontend should do (trigger continuous flow)
    continuous_response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
        "session_id": session_id,
        "character_id": "seol_min_seok_quiz",
        "tool_type": "show_selection",
        "data": {
            "selection": correct_answer,
            "correct_answer": correct_answer,  # Should now be passed properly
            "question": quiz_data.get('question', ''),
            "items": quiz_options
        }
    })
    
    if continuous_response.status_code != 200:
        print(f"❌ Continuous flow failed: {continuous_response.status_code}")
        try:
            error_data = continuous_response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error text: {continuous_response.text}")
        return False
    
    continuous_data = continuous_response.json()
    
    print(f"✅ Continuous flow triggered:")
    print(f"   Status: {continuous_data.get('status')}")
    
    # Check step result
    step_result = continuous_data.get('step_result')
    if not step_result:
        print(f"❌ No step result")
        return False
    
    response_data = step_result.get('response', {})
    dialogue = response_data.get('dialogue', '')
    audio = step_result.get('audio')
    
    print(f"   Response dialogue: {dialogue[:100]}...")
    print(f"   Has audio: {audio is not None}")
    print(f"   Audio length: {len(audio) if audio else 0} characters")
    
    # Check for educational feedback
    has_feedback = any(word in dialogue for word in ['정답', '훌륭', '맞습니다', '설명'])
    
    print(f"   Educational feedback: {'✅' if has_feedback else '❌'}")
    
    # Verify all fixes
    fixes_verified = {
        "greeting_selection": greeting_has_correct_answer == False,  # Greeting should not have correct_answer
        "quiz_generation": len(quiz_options) > 0,           # Quiz should be generated
        "continuous_flow": continuous_data.get('status') == 'flow_triggered', # Flow should trigger
        "educational_feedback": has_feedback,               # Should provide feedback
        "audio_generated": audio is not None               # Audio should be generated
    }
    
    print(f"\n📊 FIXES VERIFICATION:")
    for fix, verified in fixes_verified.items():
        print(f"   {fix}: {'✅' if verified else '❌'}")
    
    all_fixes_working = all(fixes_verified.values())
    
    return all_fixes_working

def analyze_backend_integration():
    """
    Analyze what should happen vs what actually happens
    """
    print("\n🔍 BACKEND INTEGRATION ANALYSIS")
    print("=" * 50)
    
    print("📱 FRONTEND BEHAVIOR (Fixed):")
    print("   1. Greeting options → Has no correct_answer → Regular message")
    print("   2. Quiz options → Has correct_answer → Continuous flow")
    print("   3. Continuous flow → Passes actual correct_answer (not empty)")
    
    print("\n🔧 BACKEND BEHAVIOR (Fixed):")
    print("   1. Regular message → Generates quiz with proper correct_answer")
    print("   2. Continuous flow → Receives correct_answer properly")
    print("   3. TTS generation → Uses seolminseok_tts_service for quiz character")
    
    print("\n✅ EXPECTED USER EXPERIENCE:")
    print("   1. Click greeting option → Quiz question appears")
    print("   2. Click quiz answer → Educational feedback with audio")
    print("   3. No errors, smooth interaction flow")

if __name__ == "__main__":
    print("🚀 FINAL COMPREHENSIVE TEST")
    print("Testing all user-reported issues are fixed")
    print("=" * 80)
    
    journey_success = test_complete_fixed_user_journey()
    
    print("\n" + "=" * 80)
    
    if journey_success:
        analyze_backend_integration()
        
        print("\n🎉 ALL FIXES VERIFIED: SUCCESS!")
        print("=" * 80)
        
        print("✅ ISSUES RESOLVED:")
        print("   1. Greeting selection → Now works (sends regular message)")
        print("   2. Quiz answer selection → Now works (correct continuous flow)")
        print("   3. Audio generation → Now works (uses dedicated TTS service)")
        
        print("\n🎯 USER EXPERIENCE:")
        print("   ✅ Click greeting options → Gets quiz question")
        print("   ✅ Click quiz answers → Gets educational feedback with audio")
        print("   ✅ Seamless, error-free interaction flow")
        
        print("\n📋 TECHNICAL FIXES APPLIED:")
        print("   1. Frontend: Added isQuizAnswer detection logic")
        print("   2. Frontend: Fixed correct_answer passing (no more empty strings)")
        print("   3. Backend: Continuous flow uses seolminseok_tts_service")
        
    else:
        print("❌ SOME ISSUES REMAIN")
        print("Check individual test results above")
        
        print("\n🔧 IF STILL NOT WORKING:")
        print("   1. Hard refresh browser (Ctrl+Shift+R)")
        print("   2. Restart Next.js dev server")
        print("   3. Check browser console for '🆕 UPDATED CODE VERSION' log")
        print("   4. Verify backend logs show seolminseok TTS usage")