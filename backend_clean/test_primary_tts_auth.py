#!/usr/bin/env python3
"""
Test PRIMARY TTS authentication - NO FALLBACKS ALLOWED
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_primary_tts_auth():
    """Test PRIMARY TTS with proper authentication"""
    
    print("🚀 Testing PRIMARY TTS Authentication (NO FALLBACKS)")
    print("=" * 60)
    
    # Create session
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "primary_tts_test", 
        "character_id": "seol_min_seok_quiz"
    })
    
    if create_response.status_code != 200:
        print(f"❌ Session creation failed: {create_response.status_code}")
        return False
        
    session_data = create_response.json()
    session_id = session_data.get("data", {}).get("session", {}).get("session_id")
    print(f"✅ Session created: {session_id}")
    
    # Test platform-chat - this should use PRIMARY TTS or FAIL
    print("\n🎯 Testing PRIMARY TTS (should succeed or fail loudly)...")
    
    try:
        greeting_response = requests.post(f"{API_BASE}/api/platform-chat", json={
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_input": "안녕하세요 선생님",
            "user_id": "primary_tts_test"
        })
        
        if greeting_response.status_code == 200:
            greeting_data = greeting_response.json()
            audio_url = greeting_data.get('audio_url')
            
            if audio_url:
                audio_size = len(audio_url)
                print(f"✅ PRIMARY TTS SUCCESS: {audio_size} chars")
                
                # Check if it's real TTS (large) or fallback (small)
                if audio_size > 500000:  # >500KB indicates real TTS
                    print(f"✅ CONFIRMED: Real PRIMARY TTS working ({audio_size/1000:.0f}KB)")
                    return True
                else:
                    print(f"❌ FALLBACK DETECTED: Audio too small ({audio_size} chars)")
                    return False
            else:
                print(f"❌ NO AUDIO: Primary TTS failed completely")
                return False
        else:
            print(f"❌ Request failed: {greeting_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ PRIMARY TTS FAILED: {e}")
        return False

def main():
    print("🚀 Testing PRIMARY TTS Authentication")
    print("=" * 60)
    
    success = test_primary_tts_auth()
    
    if success:
        print(f"\n✅ PRIMARY TTS WORKING CORRECTLY")
    else:
        print(f"\n❌ PRIMARY TTS BROKEN - NEED TO FIX AUTH")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)