#!/usr/bin/env python3
"""
Test Typecast Synchronous API with 설민석 specific credentials
Following the documentation at: https://docs.typecast.ai/guide/synchronous.html
"""

import requests
import json
from pathlib import Path

def test_new_credentials():
    """Test the new 설민석 specific API credentials with multiple endpoint variations"""
    
    # New credentials provided by user
    api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    actor_id = "66f691e9b38df0481f09bf5e"
    
    # Try multiple endpoint variations
    endpoints_to_test = [
        "https://typecast.ai/api/text-to-speech",       # From documentation
        "https://api.typecast.ai/text-to-speech",       # Alternative structure
        "https://api.typecast.ai/v1/text-to-speech",    # With version
        "https://api.icepeak.ai/v1/text-to-speech",     # Our working endpoint
        "https://typecast.ai/api/speak",                 # Alternative speak endpoint
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🧪 TESTING ENDPOINT: {endpoint}")
        success = _test_single_endpoint(endpoint, api_key, actor_id)
        if success:
            return True
    
    return False

def _test_single_endpoint(endpoint, api_key, actor_id):
    """Test a single endpoint configuration with different auth methods"""
    
    # Test both Bearer and X-API-KEY authentication
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}),
        ("X-API-KEY", {"X-API-KEY": api_key, "Content-Type": "application/json"}),
    ]
    
    # Payload according to Typecast synchronous documentation
    payload = {
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "lang": "auto",
        "actor_id": actor_id,
        "xapi_hd": True,
        "model_version": "latest"
    }
    
    # Bearer token authentication as per documentation
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("📋 Request Details:")
    print(f"   Text: {payload['text'][:60]}...")
    print(f"   Language: {payload['lang']}")
    print(f"   HD Mode: {payload['xapi_hd']}")
    print(f"   Model: {payload['model_version']}")
    print()
    
    try:
        print("📡 Sending TTS request...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📊 Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! TTS generation successful")
            
            # Save audio file
            output_file = Path("seolminseok_voice_test.wav")
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"💾 Audio saved: {output_file}")
            print(f"🎵 File size: {output_file.stat().st_size:,} bytes")
            print("\n🎉 설민석 specific voice is working!")
            return True
            
        elif response.status_code == 401:
            print("\n❌ Authentication Failed")
            print("   • Check if API key is correct")
            print("   • Verify API key has access to synchronous endpoint")
            try:
                error = response.json()
                print(f"   • Error details: {error}")
            except:
                print(f"   • Raw error: {response.text}")
            
        elif response.status_code == 404:
            print("\n❌ Actor Not Found")
            print(f"   • Actor ID '{actor_id}' may not exist")
            print("   • Or may not be accessible with this API key")
            
        elif response.status_code == 422:
            print("\n❌ Validation Error")
            print("   • Check request payload format")
            try:
                error = response.json()
                print(f"   • Validation details: {json.dumps(error, indent=2, ensure_ascii=False)}")
            except:
                print(f"   • Raw error: {response.text}")
                
        else:
            print(f"\n❌ Unexpected Error: HTTP {response.status_code}")
            try:
                error = response.json()
                print(f"   Error details: {json.dumps(error, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Raw response: {response.text}")
        
        return False
        
    except requests.Timeout:
        print("\n⏰ Request timed out (60s)")
        print("   Synchronous API may be slower for first requests")
        return False
        
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

def compare_with_existing_api():
    """Compare with existing API for reference"""
    
    print("\n" + "="*70)
    print("🔍 COMPARISON: Testing with existing API key")
    print("="*70)
    
    # Existing API key for comparison
    existing_key = "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW"
    actor_id = "66f691e9b38df0481f09bf5e"  # Same actor ID
    endpoint = "https://typecast.ai/api/text-to-speech"
    
    payload = {
        "text": "Test with existing key",
        "lang": "auto", 
        "actor_id": actor_id,
        "xapi_hd": True,
        "model_version": "latest"
    }
    
    headers = {
        "Authorization": f"Bearer {existing_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        print(f"📊 Existing key result: HTTP {response.status_code}")
        
        if response.status_code != 200:
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Raw: {response.text}")
                
    except Exception as e:
        print(f"❌ Existing key test failed: {e}")

if __name__ == "__main__":
    print("🚀 설민석 Typecast Synchronous API Test")
    print("🎯 Testing new dedicated credentials for 설민석 character")
    print()
    
    # Main test with new credentials
    success = test_new_credentials()
    
    # Comparison test
    compare_with_existing_api()
    
    print("\n" + "="*70)
    print("📋 FINAL RESULT")
    print("="*70)
    if success:
        print("🎉 SUCCESS: 설민석 specific voice is working!")
        print("✅ Ready to implement character-specific TTS service")
        print("📁 Audio file saved for verification")
    else:
        print("❌ FAILED: Issues with 설민석 specific credentials")
        print("🔍 Check API key validity and actor accessibility")
    print("="*70)