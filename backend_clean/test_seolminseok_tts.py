#!/usr/bin/env python3
"""
Test script for 설민석 character specific TTS endpoint
Testing the dev.icepeak.ai endpoint with actor_id: 66f691e9b38df0481f09bf5e
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_seolminseok_tts():
    """Test the specific TTS endpoint for 설민석 character"""
    
    # Configuration from environment and Character.md
    base_url = os.getenv("TYPECAST_API_URL", "https://api.icepeak.ai/v1")
    endpoint = f"{base_url}/text-to-speech"
    actor_id = "66f691e9b38df0481f09bf5e"
    
    print(f"🌐 Using base URL from env: {base_url}")
    print(f"🌐 Full endpoint: {endpoint}")
    
    # Get API key from environment
    api_key = os.getenv("TYPECAST_API_KEY")
    if not api_key:
        print("❌ TYPECAST_API_KEY not found in environment variables")
        return False
    
    # Test parameters from Character.md - try both actor_id and voice_id
    test_payload_actor = {
        "actor_id": actor_id,
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "adjust_lastword": 0,
        "bp_c_l": True,
        "emotion_scale": 1,
        "lang": "auto",
        "mode": "one-vocoder",
        "pitch": 0,
        "retake": True,
        "style_label": "normal-1",
        "style_label_version": "v1",
        "tempo": 1
    }
    
    # Test with ssfm-20 model instead of ssfm-v21
    test_payload_ssfm20 = {
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "model": "ssfm-20",  # Try ssfm-20 instead of ssfm-v21
        "voice_id": actor_id,  # Use the actor_id as voice_id
        "prompt": {
            "preset": "normal",
            "preset_intensity": 1.0
        }
    }
    
    # Also keep the v21 version for comparison
    test_payload_ssfm21 = {
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "model": "ssfm-v21",  # Original version
        "voice_id": actor_id,  # Use the actor_id as voice_id
        "prompt": {
            "preset": "normal",
            "preset_intensity": 1.0
        }
    }
    
    # Use the same authentication method as the current TTS service
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"🎵 Testing 설민석 TTS endpoint:")
    print(f"   Actor ID: {actor_id}")
    print(f"   Text: {test_payload_actor['text'][:50]}...")
    print()
    
    # Try other potential model names based on the error message pattern
    additional_models = ["ssfm-v20", "ssfm-20", "ssfm", "ssfm-v22"]
    
    test_combinations = [
        (endpoint, test_payload_ssfm21, "✅ WORKING: actor_id + ssfm-v21 (baseline)"),
    ]
    
    # Add tests for additional model variations
    for model_name in additional_models:
        test_payload_variant = {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
            "model": model_name,
            "voice_id": actor_id,
            "prompt": {"preset": "normal", "preset_intensity": 1.0}
        }
        test_combinations.append((endpoint, test_payload_variant, f"🧪 TESTING: actor_id + {model_name}"))
    
    for test_endpoint, test_payload, description in test_combinations:
        print(f"📡 Trying: {description}")
        print(f"   Endpoint: {test_endpoint}")
        try:
            response = requests.post(test_endpoint, headers=headers, json=test_payload, timeout=15)
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS with {test_endpoint}!")
                
                # Check if response contains audio data
                content_type = response.headers.get('content-type', '')
                if 'audio' in content_type or len(response.content) > 1000:
                    print(f"   🎵 Audio data: {len(response.content)} bytes")
                    
                    # Save test audio file
                    test_file = "test_seolminseok_voice.wav"
                    with open(test_file, 'wb') as f:
                        f.write(response.content)
                    print(f"   💾 Audio saved to: {test_file}")
                    return True
                else:
                    try:
                        response_data = response.json()
                        print(f"   📄 JSON Response: {json.dumps(response_data, indent=4, ensure_ascii=False)[:200]}...")
                    except:
                        print(f"   📄 Text Response: {response.text[:200]}...")
                        
            elif response.status_code in [401, 403]:
                print(f"   🔐 Authentication issue")
                try:
                    error_data = response.json()
                    print(f"   📄 Auth error: {error_data}")
                except:
                    print(f"   📄 Auth error text: {response.text[:100]}...")
                    
            elif response.status_code == 405:
                print(f"   ❌ Method not allowed - wrong HTTP method or endpoint")
                
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
                
            else:
                print(f"   ❌ Other error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error: {json.dumps(error_data, indent=2, ensure_ascii=False)[:150]}...")
                except:
                    print(f"   📄 Error text: {response.text[:100]}...")
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout (15s)")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {e}")
        
        print()  # Add spacing between attempts
    
    print("❌ All endpoints failed")
    return False

def compare_with_current_endpoint():
    """Compare with current endpoint for reference"""
    print("\n" + "="*60)
    print("🔍 COMPARISON: Testing current endpoint")
    print("="*60)
    
    # Current endpoint configuration
    current_endpoint = "https://typecast.ai/api/speak"
    current_voice_id = "tc_6073b2f6817dccf658bb159f"  # Duke voice we just set
    
    api_key = os.getenv("TYPECAST_API_KEY")
    if not api_key:
        print("❌ TYPECAST_API_KEY not found")
        return False
    
    test_payload = {
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "voice_id": current_voice_id,
        "speed": 1.0,
        "pitch": 0,
        "emotion": "default"
    }
    
    # Use the same authentication method as the current TTS service
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"🎵 Testing current TTS endpoint:")
    print(f"   Endpoint: {current_endpoint}")
    print(f"   Voice ID: {current_voice_id}")
    print()
    
    try:
        response = requests.post(current_endpoint, headers=headers, json=test_payload, timeout=30)
        print(f"📊 Current endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Current endpoint working")
            return True
        else:
            print(f"❌ Current endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Current endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Testing 설민석 Character Specific TTS Configuration")
    print("="*60)
    
    # Test new endpoint
    success = test_seolminseok_tts()
    
    # Compare with current endpoint
    compare_with_current_endpoint()
    
    print("\n" + "="*60)
    if success:
        print("🎉 RESULT: New endpoint test SUCCESSFUL!")
        print("✅ Ready to implement in the actual service")
    else:
        print("⚠️  RESULT: New endpoint test FAILED")
        print("❌ Need to investigate before implementing")
    print("="*60)