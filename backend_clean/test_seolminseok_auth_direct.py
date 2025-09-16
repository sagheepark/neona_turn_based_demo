#!/usr/bin/env python3
"""
Direct test of SeolMinSeok TTS service authentication
"""

import requests
import os
import base64

def test_seolminseok_direct():
    """Test SeolMinSeok TTS service directly"""
    
    print("🎯 Testing SeolMinSeok TTS Direct Authentication")
    print("=" * 60)
    
    # Use exact same configuration as seolminseok_tts_service.py
    api_key = os.getenv("SEOLMINSEOK_API_KEY", "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG")
    actor_id = os.getenv("SEOLMINSEOK_ACTOR_ID", "66f691e9b38df0481f09bf5e")
    endpoint = os.getenv("SEOLMINSEOK_ENDPOINT", "https://dev.icepeak.ai/api/text-to-speech")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": "안녕하세요",
        "lang": "auto",
        "actor_id": actor_id,
        "xapi_hd": True,
        "model_version": "latest"
    }
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🎭 Actor ID: {actor_id}")
    print(f"🌐 Endpoint: {endpoint}")
    print(f"📋 Headers: {headers}")
    print(f"📦 Payload: {payload}")
    
    try:
        print(f"\n⏳ Calling SeolMinSeok TTS with 10s timeout...")
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Success - check audio size
            audio_data = response.content
            audio_size = len(audio_data)
            
            print(f"✅ SUCCESS: SeolMinSeok TTS working!")
            print(f"🎵 Audio size: {audio_size} bytes ({audio_size/1000:.0f}KB)")
            
            if audio_size > 10000:  # Real TTS should be large
                print(f"✅ CONFIRMED: Real TTS audio generated")
                return True
            else:
                print(f"❌ SUSPICIOUS: Audio too small for TTS")
                return False
                
        elif response.status_code == 403:
            # Authentication failure
            print(f"❌ AUTHENTICATION FAILED: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error details: {error_data}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
        else:
            print(f"❌ REQUEST FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error details: {error_data}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
    except requests.Timeout:
        print(f"❌ TIMEOUT: SeolMinSeok TTS took too long")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    success = test_seolminseok_direct()
    
    if success:
        print(f"\n🎉 SeolMinSeok TTS is working correctly!")
        print(f"✅ Authentication is valid")
        print(f"✅ Audio generation successful")
    else:
        print(f"\n❌ SeolMinSeok TTS has authentication issues")
        print(f"🔧 Need to fix API key or endpoint configuration")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)