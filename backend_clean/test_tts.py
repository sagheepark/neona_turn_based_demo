#!/usr/bin/env python3
"""
Test script for Typecast TTS API
Usage: python test_tts.py
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voices_endpoint(base_url, api_key):
    """Test the voices endpoint"""
    url = f"{base_url}/voices"
    headers = {"X-API-KEY": api_key}
    
    print(f"\n🔍 Testing Voices Endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                voices = response.json()
                print(f"   ✅ Success! Found {len(voices)} voices")
                
                # Show first 3 voices
                for i, voice in enumerate(voices[:3]):
                    print(f"   Voice {i+1}: {voice.get('voice_name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
                
                # Look for Korean voices
                korean_voices = [v for v in voices if any(
                    k in v.get('voice_name', '').lower() or k in v.get('voice_id', '').lower() 
                    for k in ['korean', 'korea', 'kr', '한국']
                )]
                
                if korean_voices:
                    print(f"   🇰🇷 Found {len(korean_voices)} Korean voices:")
                    for v in korean_voices[:3]:
                        print(f"      - {v.get('voice_name')} (ID: {v.get('voice_id')})")
                
                return True
                
            except json.JSONDecodeError:
                print(f"   ❌ Response is not JSON: {response.text[:100]}...")
                return False
        else:
            print(f"   ❌ Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def test_tts_endpoint(base_url, api_key, voice_id=None):
    """Test the text-to-speech endpoint"""
    url = f"{base_url}/text-to-speech"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": "안녕하세요! 테스트 메시지입니다.",
        "model": "ssfm-v21",
        "voice_id": voice_id or "tc_62a8975e695ad26f7fb514d1",
        "prompt": {
            "preset": "happy",
            "preset_intensity": 2.0
        },
        "speed": 1.0
    }
    
    print(f"\n🎤 Testing TTS Endpoint: {url}")
    print(f"   Text: {payload['text']}")
    print(f"   Voice ID: {payload['voice_id']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            
            if 'audio' in content_type or 'wav' in content_type or 'mp3' in content_type:
                audio_size = len(response.content)
                print(f"   ✅ Success! Audio received: {audio_size} bytes")
                
                # Save audio to file
                filename = "test_output.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"   💾 Audio saved to: {filename}")
                
                return True
            else:
                print(f"   ❌ Unexpected content type: {content_type}")
                print(f"   Response: {response.text[:200]}...")
                return False
        else:
            print(f"   ❌ Error: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🎵 Typecast TTS API Test Script")
    print("=" * 60)
    
    # Get configuration
    api_key = os.getenv("TYPECAST_API_KEY", "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW")
    base_url = os.getenv("TYPECAST_API_URL", "https://api.typecast.ai/v1")
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Base URL: {base_url}")
    
    # Test different endpoints if main one fails
    test_urls = [
        base_url,
        "https://api.icepeak.ai/v1",  # Alpha test development server
        "https://api.typecast.ai/v1",  # Production server
        "https://dev.icepeak.ai/v1",
        "https://dev.icepeak.ai/api/v1"
    ]
    
    voices_success = False
    tts_success = False
    working_url = None
    
    for url in test_urls:
        if url != base_url:
            print(f"\n🔄 Trying alternative endpoint: {url}")
        
        # Test voices endpoint
        voices_result = test_voices_endpoint(url, api_key)
        if voices_result:
            voices_success = True
            working_url = url
        
        # Always test TTS endpoint regardless of voices result
        tts_result = test_tts_endpoint(url, api_key)
        if tts_result:
            tts_success = True
            working_url = url
        
        # If both work, we're done
        if voices_success and tts_success:
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    if voices_success and tts_success:
        print("✅ All tests passed!")
        print(f"   Working endpoint: {working_url}")
        print("\n💡 To use this endpoint, update your .env file:")
        print(f"   TYPECAST_API_URL={working_url}")
    elif voices_success:
        print("⚠️  Voices endpoint works but TTS failed")
        print(f"   Working endpoint: {working_url}")
    else:
        print("❌ No working endpoints found")
        print("\n💡 Possible issues:")
        print("   1. Invalid API key")
        print("   2. Incorrect endpoint URL")
        print("   3. API service is down")
        print("\n📝 Next steps:")
        print("   1. Verify your API key is correct")
        print("   2. Check the Typecast documentation for the correct endpoint")
        print("   3. Contact Typecast support if issues persist")

if __name__ == "__main__":
    main()