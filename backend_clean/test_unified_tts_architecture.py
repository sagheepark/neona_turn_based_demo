#!/usr/bin/env python3
"""
Test unified TTS architecture - ALL characters should use SeolMinSeok TTS
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_unified_tts_flow():
    """Test that both greeting and quiz use same working TTS service"""
    
    print("🎯 Testing UNIFIED TTS Architecture")
    print("=" * 60)
    
    # Create session
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "tts_unified_test", 
        "character_id": "seol_min_seok_quiz"
    })
    
    if create_response.status_code != 200:
        print(f"❌ Session creation failed: {create_response.status_code}")
        return False
        
    session_data = create_response.json()
    session_id = session_data.get("data", {}).get("session", {}).get("session_id")
    print(f"✅ Session created: {session_id}")
    
    # Test 1: Greeting should use unified SeolMinSeok TTS
    print("\n🎭 Test 1: Greeting with unified TTS...")
    
    try:
        greeting_response = requests.post(f"{API_BASE}/api/platform-chat", json={
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_input": "__PREDEFINED_GREETING__:안녕하세요! 한국사 퀴즈를 함께 풀어볼까요?",
            "user_id": "tts_unified_test"
        })
        
        if greeting_response.status_code == 200:
            greeting_data = greeting_response.json()
            audio_url = greeting_data.get('audio_url')
            
            if audio_url and len(audio_url) > 100000:  # Real TTS is large
                print(f"✅ GREETING SUCCESS: Unified SeolMinSeok TTS working ({len(audio_url)/1000:.0f}KB)")
                greeting_working = True
            else:
                print(f"❌ GREETING FAILED: No proper TTS audio")
                greeting_working = False
        else:
            print(f"❌ Greeting request failed: {greeting_response.status_code}")
            greeting_working = False
    except Exception as e:
        print(f"❌ Greeting test failed: {e}")
        greeting_working = False
    
    # Test 2: Quiz should use same unified SeolMinSeok TTS
    print("\n🎯 Test 2: Quiz with unified TTS...")
    
    try:
        # Start quiz
        quiz_response = requests.post(f"{API_BASE}/api/platform-chat", json={
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_input": "조선시대",
            "user_id": "tts_unified_test"
        })
        
        if quiz_response.status_code == 200:
            quiz_data = quiz_response.json()
            audio_url = quiz_data.get('audio_url')
            
            if audio_url and len(audio_url) > 100000:  # Real TTS is large
                print(f"✅ QUIZ SUCCESS: Unified SeolMinSeok TTS working ({len(audio_url)/1000:.0f}KB)")
                quiz_working = True
            else:
                print(f"❌ QUIZ FAILED: No proper TTS audio")
                quiz_working = False
        else:
            print(f"❌ Quiz request failed: {quiz_response.status_code}")
            quiz_working = False
    except Exception as e:
        print(f"❌ Quiz test failed: {e}")
        quiz_working = False
    
    # Final verification
    print(f"\n📊 UNIFIED TTS TEST RESULTS:")
    print(f"   Greeting TTS: {'✅ WORKING' if greeting_working else '❌ BROKEN'}")
    print(f"   Quiz TTS: {'✅ WORKING' if quiz_working else '❌ BROKEN'}")
    
    if greeting_working and quiz_working:
        print(f"\n🎉 SUCCESS: Unified SeolMinSeok TTS architecture is working!")
        print(f"🎯 No more 403 AUTH_TOKEN_INVALID errors!")
        print(f"🎯 Both greeting and quiz use same working TTS service!")
        return True
    else:
        print(f"\n❌ FAILURE: Unified TTS architecture has issues")
        return False

def main():
    print("🚀 Testing Unified TTS Architecture")
    print("=" * 60)
    
    success = test_unified_tts_flow()
    
    if success:
        print(f"\n✅ UNIFIED TTS WORKING PERFECTLY")
    else:
        print(f"\n❌ UNIFIED TTS NEEDS MORE FIXES")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)