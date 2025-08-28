#!/usr/bin/env python3
"""
Test dev.icepeak.ai endpoint with 설민석 specific credentials
The API key is for the DEV server, not production!
"""

import requests
import json
from pathlib import Path
import base64

def test_dev_server():
    """Test the dev.icepeak.ai endpoint with 설민석 credentials"""
    
    # Dev server credentials
    api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    actor_id = "66f691e9b38df0481f09bf5e"
    
    print("🎭 Testing dev.icepeak.ai Server for 설민석 Character")
    print("="*70)
    print("🔑 Dev API Key: " + api_key[:15] + "..." + api_key[-6:])
    print("🎭 Actor ID: " + actor_id)
    print()
    
    # Test different endpoint variations on dev server
    endpoints = [
        "https://dev.icepeak.ai/api/text-to-speech",  # Most likely endpoint
        "https://dev.icepeak.ai/text-to-speech",      # Without /api
        "https://dev.icepeak.ai/v1/text-to-speech",   # With version
        "https://dev.icepeak.ai/api/speak",           # Alternative name
        "https://dev.icepeak.ai/api/tts",             # Short name
    ]
    
    # Test multiple payload formats
    payloads = {
        "Typecast Sync Format": {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
            "lang": "auto",
            "actor_id": actor_id,
            "xapi_hd": True,
            "model_version": "latest"
        },
        "Simple Format": {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다!",
            "actor_id": actor_id,
        },
        "With voice_id instead": {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다!",
            "voice_id": actor_id,
            "lang": "auto",
        },
        "Character.md format": {
            "text": "안녕하세요, 역사 여행 가이드 설민석입니다!",
            "actor_id": actor_id,
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
    }
    
    # Test authentication methods
    auth_methods = {
        "Bearer": lambda key: {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        "X-API-KEY": lambda key: {"X-API-KEY": key, "Content-Type": "application/json"},
        "API-Key": lambda key: {"API-Key": key, "Content-Type": "application/json"},
        "x-api-key": lambda key: {"x-api-key": key, "Content-Type": "application/json"},
    }
    
    success_count = 0
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        print("-" * 60)
        
        for auth_name, auth_func in auth_methods.items():
            headers = auth_func(api_key)
            
            for payload_name, payload in payloads.items():
                print(f"\n  🧪 Auth: {auth_name} | Payload: {payload_name}")
                
                try:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    status = response.status_code
                    print(f"     📊 Status: {status}")
                    
                    if status == 200:
                        print(f"     ✅ SUCCESS!")
                        content_length = len(response.content)
                        print(f"     🎵 Response size: {content_length:,} bytes")
                        
                        # Check content type
                        content_type = response.headers.get('content-type', '')
                        print(f"     📄 Content-Type: {content_type}")
                        
                        # Save successful audio
                        if content_length > 1000:  # Reasonable audio size
                            filename = f"seolminseok_dev_{auth_name}_{payload_name.replace(' ', '_')}.wav"
                            with open(filename, 'wb') as f:
                                f.write(response.content)
                            print(f"     💾 Audio saved: {filename}")
                            
                            success_count += 1
                            
                            # Print the working configuration
                            print("\n" + "🎉" * 20)
                            print("🎯 WORKING CONFIGURATION FOUND!")
                            print(f"   Endpoint: {endpoint}")
                            print(f"   Auth Method: {auth_name}")
                            print(f"   Payload Format: {payload_name}")
                            print("🎉" * 20)
                            
                            return {
                                "success": True,
                                "endpoint": endpoint,
                                "auth_method": auth_name,
                                "payload_format": payload_name,
                                "headers": headers,
                                "payload": payload
                            }
                    
                    elif status == 401:
                        print(f"     🔐 Unauthorized")
                        
                    elif status == 404:
                        print(f"     🔍 Not found")
                        
                    elif status == 405:
                        print(f"     ⚠️  Method not allowed")
                        
                    elif status == 422:
                        print(f"     📋 Validation error")
                        try:
                            error = response.json()
                            if "detail" in error and error["detail"]:
                                first_error = error["detail"][0] if isinstance(error["detail"], list) else error["detail"]
                                print(f"        → {first_error.get('msg', 'Unknown error')}")
                        except:
                            pass
                    
                    else:
                        print(f"     ❓ Other: {status}")
                        
                except requests.Timeout:
                    print(f"     ⏰ Timeout")
                    
                except Exception as e:
                    print(f"     ❌ Error: {str(e)[:50]}")
    
    return {"success": False, "message": "No working configuration found"}

def test_actor_list():
    """Try to list available actors on dev server"""
    
    api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    
    print("\n" + "="*70)
    print("🔍 Testing Actor List on Dev Server")
    print("="*70)
    
    actor_endpoints = [
        "https://dev.icepeak.ai/api/actors",
        "https://dev.icepeak.ai/api/actor",
        "https://dev.icepeak.ai/actors",
        "https://dev.icepeak.ai/api/voices",
    ]
    
    for endpoint in actor_endpoints:
        print(f"\n📡 Testing: {endpoint}")
        
        # Try different auth methods
        headers_options = [
            {"Authorization": f"Bearer {api_key}"},
            {"X-API-KEY": api_key},
            {"API-Key": api_key},
        ]
        
        for headers in headers_options:
            auth_type = list(headers.keys())[0]
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"   {auth_type}: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"      ✅ Found {len(data)} actors/voices")
                        
                        # Look for our target actor
                        target = "66f691e9b38df0481f09bf5e"
                        for item in data:
                            if target in str(item):
                                print(f"      🎯 Found target actor!")
                                print(f"         {item}")
                                break
                    except:
                        print(f"      📄 Non-JSON response")
                        
            except Exception as e:
                print(f"   {auth_type}: Error - {str(e)[:30]}")

if __name__ == "__main__":
    print("🚀 Dev Server (dev.icepeak.ai) TTS Test for 설민석")
    print("🎯 Testing with dev server credentials")
    print()
    
    # Main test
    result = test_dev_server()
    
    # Test actor list
    test_actor_list()
    
    print("\n" + "="*70)
    print("📋 FINAL RESULT")
    print("="*70)
    
    if result["success"]:
        print("🎉 SUCCESS: Dev server TTS is working!")
        print(f"✅ Endpoint: {result['endpoint']}")
        print(f"✅ Auth Method: {result['auth_method']}")
        print(f"✅ Payload Format: {result['payload_format']}")
        print("\n📝 Ready to implement character-specific TTS service")
    else:
        print("❌ Dev server test failed")
        print("💡 Check if dev server is accessible and API key is valid")
    
    print("="*70)