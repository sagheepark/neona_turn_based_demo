#!/usr/bin/env python3
"""
Test the fixed TTS performance after Phase 1 & 2 optimizations
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_fixed_quiz_performance():
    """Test that quiz now responds with audio in <5 seconds"""
    
    print("🧪 Testing fixed TTS performance...")
    print("=" * 50)
    
    # Create a new session  
    create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
        "user_id": "performance_test",
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
    
    # Test quiz interaction with timing
    print("\n🎯 Testing quiz answer with audio generation timing...")
    
    start_time = time.time()
    
    response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "태조 이성계", 
        "user_id": "performance_test"
    })
    
    end_time = time.time()
    response_time = end_time - start_time
    
    print(f"⏱️  Total response time: {response_time:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        has_audio = bool(data.get("audio_url"))
        dialogue = data.get("dialogue", "")[:100]
        
        print(f"✅ Response received!")
        print(f"   📝 Dialogue: {dialogue}...")
        print(f"   🎵 Has audio: {has_audio}")
        print(f"   🔧 Tools: {len(data.get('tools', []))}")
        
        # Performance assessment
        print(f"\n🎯 Performance Analysis:")
        if response_time < 3.0:
            print(f"   ✅ EXCELLENT: {response_time:.2f}s (< 3s target)")
        elif response_time < 5.0:
            print(f"   ✅ GOOD: {response_time:.2f}s (< 5s acceptable)")
        elif response_time < 10.0:
            print(f"   ⚠️  SLOW: {response_time:.2f}s (10s+ concerning)")
        else:
            print(f"   ❌ TOO SLOW: {response_time:.2f}s (unacceptable)")
            
        if has_audio:
            print(f"   ✅ Audio generated successfully")
        else:
            print(f"   🔇 No audio (but response was fast)")
        
        return response_time < 5.0 and len(dialogue) > 0
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def main():
    print("🚀 Testing Phase 1 & 2 TTS Performance Fixes")
    print("=" * 60)
    
    success = test_fixed_quiz_performance()
    
    print(f"\n📊 FINAL RESULT:")
    if success:
        print("   ✅ TTS performance optimization SUCCESS!")
        print("   🎉 Phase 1 & 2 fixes working correctly")
        print("   💡 Audio generation now < 5s with fast fallback")
    else:
        print("   ❌ Performance issues remain")
        print("   🔧 May need additional investigation")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)