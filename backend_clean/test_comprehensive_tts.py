#!/usr/bin/env python3
"""
Comprehensive TTS Test for 설민석 Character
Testing multiple endpoints, authentication methods, and payload formats
"""

import requests
import json
from pathlib import Path

def test_comprehensive_tts():
    """Test all possible combinations for 설민석 TTS"""
    
    # Credentials
    new_api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    existing_api_key = "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW"
    actor_id = "66f691e9b38df0481f09bf5e"
    
    print("🎭 Comprehensive TTS Testing for 설민석 Character")
    print("="*70)
    print(f"🎯 Target Actor ID: {actor_id}")
    print(f"🔑 New API Key: {new_api_key[:12]}...{new_api_key[-4:]}")
    print(f"🔑 Existing Key: {existing_api_key[:12]}...{existing_api_key[-4:]}")
    print()
    
    # Test configurations: (endpoint, auth_method, payload_format, api_key, description)
    test_configs = [
        # New API key with Typecast synchronous format
        ("https://typecast.ai/api/text-to-speech", "Bearer", "typecast_sync", new_api_key, "NEW KEY + Typecast Sync API"),
        ("https://api.typecast.ai/text-to-speech", "Bearer", "typecast_sync", new_api_key, "NEW KEY + Alt Typecast URL"),
        ("https://api.icepeak.ai/v1/text-to-speech", "X-API-KEY", "icepeak_format", new_api_key, "NEW KEY + Icepeak Format"),
        
        # Test if existing key works with new actor
        ("https://api.icepeak.ai/v1/text-to-speech", "X-API-KEY", "icepeak_format", existing_api_key, "EXISTING KEY + New Actor"),
        ("https://typecast.ai/api/text-to-speech", "Bearer", "typecast_sync", existing_api_key, "EXISTING KEY + Typecast Sync"),
        
        # Test new API key with icepeak endpoint
        ("https://api.icepeak.ai/v1/text-to-speech", "Bearer", "icepeak_format", new_api_key, "NEW KEY + Bearer + Icepeak"),
    ]
    
    for endpoint, auth_method, payload_format, api_key, description in test_configs:
        print(f"\n🧪 TESTING: {description}")
        print(f"   🌐 Endpoint: {endpoint}")
        print(f"   🔐 Auth: {auth_method}")
        print(f"   📋 Format: {payload_format}")
        
        success = _test_single_config(endpoint, auth_method, payload_format, api_key, actor_id)
        if success:
            print(f"   ✅ SUCCESS!")
            return True
        else:
            print(f"   ❌ Failed")
    
    print("\n❌ All configurations failed")
    return False

def _test_single_config(endpoint, auth_method, payload_format, api_key, actor_id):
    """Test a single configuration"""
    
    # Prepare headers based on auth method
    if auth_method == "Bearer":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    else:  # X-API-KEY
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    # Prepare payload based on format
    if payload_format == "typecast_sync":
        payload = {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
            "lang": "auto",
            "actor_id": actor_id,
            "xapi_hd": True,
            "model_version": "latest"
        }
    else:  # icepeak_format
        payload = {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
            "model": "ssfm-v21",
            "voice_id": actor_id,
            "prompt": {
                "preset": "normal",
                "preset_intensity": 1.0
            }
        }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        status = response.status_code
        
        print(f"      📊 Status: {status}")
        
        if status == 200:
            # Success! Save audio
            output_file = Path(f"seolminseok_success_{auth_method}_{payload_format}.wav")
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"      🎵 Audio saved: {output_file}")
            print(f"      💾 Size: {len(response.content):,} bytes")
            return True
            
        elif status == 401:
            print(f"      🔐 Auth failed")
            
        elif status == 404:
            print(f"      🔍 Actor/endpoint not found")
            
        elif status == 422:
            try:
                error = response.json()
                if "detail" in error:
                    for detail in error["detail"][:2]:  # Show first 2 errors
                        print(f"      📋 Validation: {detail.get('msg', 'Unknown')}")
            except:
                print(f"      📋 Validation error")
                
        else:
            print(f"      ❓ Other error: {status}")
            
    except requests.Timeout:
        print(f"      ⏰ Timeout")
        
    except Exception as e:
        print(f"      ❌ Exception: {e}")
    
    return False

def test_actor_availability():
    """Test if we can list actors with the new API key"""
    
    print("\n" + "="*70)
    print("🔍 Testing Actor Availability")
    print("="*70)
    
    api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    
    # Try different actor endpoints
    actor_endpoints = [
        "https://typecast.ai/api/actor",
        "https://api.typecast.ai/actor", 
        "https://api.icepeak.ai/v1/voices",
    ]
    
    for endpoint in actor_endpoints:
        print(f"\n🧪 Testing: {endpoint}")
        
        for auth_method in ["Bearer", "X-API-KEY"]:
            headers = (
                {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                if auth_method == "Bearer" else
                {"X-API-KEY": api_key, "Content-Type": "application/json"}
            )
            
            try:
                response = requests.get(endpoint, headers=headers, timeout=15)
                print(f"   {auth_method}: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"      ✅ Success - found {len(data)} items")
                        
                        # Look for our actor
                        target = "66f691e9b38df0481f09bf5e"
                        found = False
                        for item in data:
                            if (item.get("actor_id") == target or 
                                item.get("voice_id") == target):
                                print(f"      🎯 Found target actor!")
                                found = True
                                break
                        
                        if not found:
                            print(f"      📋 Target actor not in list")
                            
                    except Exception as e:
                        print(f"      📄 JSON parse error: {e}")
                        
            except Exception as e:
                print(f"   {auth_method}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Comprehensive 설민석 TTS Testing")
    print("🎯 Testing all possible API configurations")
    print()
    
    # Test TTS generation
    success = test_comprehensive_tts()
    
    # Test actor availability
    test_actor_availability()
    
    print("\n" + "="*70)
    print("📋 FINAL SUMMARY")
    print("="*70)
    
    if success:
        print("🎉 SUCCESS: Found working configuration for 설민석 voice!")
        print("✅ Ready to implement character-specific TTS")
    else:
        print("❌ No working configuration found")
        print("💡 Recommendations:")
        print("   • Verify API key is active and has correct permissions")
        print("   • Confirm actor_id exists in the target system")
        print("   • Check if actor requires special access permissions")
    
    print("="*70)