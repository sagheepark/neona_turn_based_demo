#!/usr/bin/env python3
"""
Test tool orchestrator audio URL generation
Check if SeolMinSeok TTS audio is being properly generated and passed
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_tool_orchestrator_audio():
    """Test that tool orchestrator generates and passes audio URLs correctly"""
    
    print("🧪 Testing Tool Orchestrator Audio Generation...")
    print("=" * 60)
    
    # Create a new session  
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "audio_test",
        "character_id": "seol_min_seok_quiz"
    })
    
    if create_response.status_code != 200:
        print(f"❌ Session creation failed: {create_response.status_code}")
        return False
        
    session_data = create_response.json()
    session_id = session_data.get("data", {}).get("session", {}).get("session_id")
    
    if not session_id:
        print(f"❌ No session_id returned: {session_data}")
        return False
    
    print(f"✅ Session created: {session_id}")
    
    # Test platform-chat endpoint (regular chat, not quiz)
    print("\n🎯 Testing platform-chat endpoint audio generation...")
    
    start_time = time.time()
    
    response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "안녕하세요", 
        "user_id": "audio_test"
    })
    
    end_time = time.time()
    response_time = end_time - start_time
    
    print(f"⏱️  Response time: {response_time:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        
        # Detailed audio analysis
        audio_url = data.get("audio_url")
        dialogue = data.get("dialogue", "")
        tools = data.get("tools", [])
        
        print(f"\n📋 RESPONSE ANALYSIS:")
        print(f"   📝 Dialogue: '{dialogue[:100]}...' ({len(dialogue)} chars)")
        print(f"   🔧 Tools count: {len(tools)}")
        print(f"   🎵 Has audio_url field: {audio_url is not None}")
        
        if audio_url:
            print(f"   📊 Audio URL type: {type(audio_url)}")
            if isinstance(audio_url, str):
                print(f"   📏 Audio URL length: {len(audio_url)}")
                if audio_url.startswith("data:audio/"):
                    print(f"   ✅ Audio format: Data URI (base64)")
                    print(f"   🎯 Audio prefix: {audio_url[:50]}...")
                else:
                    print(f"   ⚠️  Audio format: {audio_url[:50]}...")
            else:
                print(f"   ❌ Audio URL not string: {audio_url}")
        else:
            print(f"   🔇 No audio_url in response")
        
        # Full response inspection for debugging
        print(f"\n🔍 FULL RESPONSE KEYS:")
        for key, value in data.items():
            if key == "audio_url":
                if value:
                    print(f"   {key}: [PRESENT - {len(str(value))} chars]")
                else:
                    print(f"   {key}: [NULL/EMPTY]")
            else:
                print(f"   {key}: {str(value)[:100]}...")
        
        # Test result assessment
        print(f"\n🎯 DIAGNOSIS:")
        if audio_url and len(str(audio_url)) > 100:
            print(f"   ✅ Tool Orchestrator generating audio successfully")
            print(f"   🎉 Audio URL present and substantial length")
            if audio_url.startswith("data:audio/"):
                print(f"   ✅ Correct data URI format for frontend")
            else:
                print(f"   ⚠️  Unexpected audio format - may cause frontend issues")
        elif audio_url:
            print(f"   ⚠️  Audio URL present but very short - possible error")
            print(f"   🔍 Audio content: '{audio_url}'")
        else:
            print(f"   ❌ Tool Orchestrator NOT generating audio")
            print(f"   🚨 SeolMinSeok TTS service not being called or failing")
        
        return audio_url is not None and len(str(audio_url)) > 100
        
    else:
        print(f"❌ Platform-chat request failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error text: {response.text}")
        return False

def main():
    print("🚀 Testing Tool Orchestrator Audio URL Generation")
    print("=" * 60)
    
    success = test_tool_orchestrator_audio()
    
    print(f"\n📊 FINAL RESULT:")
    if success:
        print("   ✅ Tool Orchestrator audio generation WORKING!")
        print("   🎉 Audio URLs being generated and passed correctly")
        print("   💡 Issue may be on frontend side")
    else:
        print("   ❌ Tool Orchestrator audio generation FAILING")
        print("   🔧 SeolMinSeok TTS not being called properly")
        print("   🚨 Need to fix orchestrator audio generation")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)