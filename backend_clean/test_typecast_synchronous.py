#!/usr/bin/env python3
"""
Test script for Typecast Synchronous API with 설민석 specific credentials
Testing the new approach with dedicated API key and actor_id
"""

import requests
import json
import os
from pathlib import Path

def test_typecast_synchronous_api():
    """Test the Typecast synchronous API with 설민석 specific credentials"""
    
    # Test both new and existing API keys for comparison
    new_api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    existing_api_key = "__pltGFCASijaw6JxcHMDpKRDcc7PcKRU58AyvHsVnSPW"
    
    actor_id = "66f691e9b38df0481f09bf5e" 
    endpoint = "https://typecast.ai/api/text-to-speech"
    
    # Test configurations
    test_configs = [
        ("NEW API KEY (설민석 specific)", new_api_key, actor_id),
        ("EXISTING API KEY (for comparison)", existing_api_key, actor_id),
        ("EXISTING API KEY + Duke voice", existing_api_key, "tc_6073b2f6817dccf658bb159f"),
    ]
    
    for config_name, api_key, test_actor_id in test_configs:
        print(f"\n🧪 TESTING: {config_name}")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   Actor/Voice ID: {test_actor_id}")
        
        success = _test_single_config(endpoint, api_key, test_actor_id, config_name)
        if success:
            return True  # Return on first success
    
    return False

def _test_single_config(endpoint, api_key, actor_id, config_name):
    """Test a single API configuration"""
    
    # Test payload following the documentation format
    test_payload = {
        "text": "안녕하세요, 역사 여행 가이드 설민석입니다! 오늘은 3·1 운동 이야기로 함께 떠나볼까요?",
        "lang": "auto",
        "actor_id": actor_id,
        "xapi_hd": True,
        "model_version": "latest"
    }
    
    # Authentication using Bearer token as per documentation
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Sending request to Typecast Synchronous API...")
        response = requests.post(endpoint, headers=headers, json=test_payload, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: TTS request successful!")
            
            # Check response content
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print(f"🎵 Content-Type: {content_type}")
            print(f"🎵 Audio Size: {content_length} bytes")
            
            if content_length > 1000:  # Reasonable audio file size
                # Save the audio file
                output_file = Path("seolminseok_typecast_test.wav")
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"💾 Audio saved to: {output_file}")
                print(f"🎉 설민석 voice successfully generated!")
                return True
            else:
                print("⚠️  Warning: Response size too small for audio file")
                print(f"📄 Response content: {response.text[:200]}...")
                return False
                
        elif response.status_code == 401:
            print("❌ FAILED: Authentication error")
            try:
                error_data = response.json()
                print(f"📄 Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
        elif response.status_code == 404:
            print("❌ FAILED: Actor ID not found")
            print("   This suggests the actor_id doesn't exist in the system")
            try:
                error_data = response.json()
                print(f"📄 Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
        elif response.status_code == 422:
            print("❌ FAILED: Validation error")
            try:
                error_data = response.json()
                print(f"📄 Validation details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout (60s)")
        print("   Synchronous API might take longer for complex requests")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAILED: Request error - {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {e}")
        return False

def test_actor_availability():
    """Test if the actor_id is available by querying the actor endpoint"""
    
    api_key = "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG"
    actor_endpoint = "https://typecast.ai/api/actor"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*60)
    print("🔍 Testing Actor Availability")
    print("="*60)
    print(f"🌐 Endpoint: {actor_endpoint}")
    
    try:
        response = requests.get(actor_endpoint, headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            actors = response.json()
            print(f"✅ Actor API accessible - found {len(actors)} actors")
            
            # Look for our specific actor
            target_actor = "66f691e9b38df0481f09bf5e"
            found_actor = None
            
            for actor in actors:
                if actor.get('actor_id') == target_actor:
                    found_actor = actor
                    break
            
            if found_actor:
                print(f"✅ Target actor FOUND!")
                print(f"   Actor ID: {found_actor.get('actor_id')}")
                print(f"   Name: {found_actor.get('name', 'N/A')}")
                print(f"   Language: {found_actor.get('language', 'N/A')}")
                return True
            else:
                print(f"❌ Target actor NOT FOUND in {len(actors)} available actors")
                print("📋 Available actors:")
                for i, actor in enumerate(actors[:5]):  # Show first 5
                    print(f"   {i+1}. {actor.get('actor_id')} - {actor.get('name', 'N/A')}")
                if len(actors) > 5:
                    print(f"   ... and {len(actors)-5} more")
                return False
        else:
            print(f"❌ Actor API failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Actor API error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Typecast Synchronous API Test for 설민석 Character")
    print("="*70)
    
    # Test 1: Check if actor is available
    actor_available = test_actor_availability()
    
    # Test 2: Try TTS generation
    tts_success = test_typecast_synchronous_api()
    
    print("\n" + "="*70)
    print("📋 TEST RESULTS SUMMARY")
    print("="*70)
    print(f"🎭 Actor Available: {'✅ YES' if actor_available else '❌ NO'}")
    print(f"🎵 TTS Generation: {'✅ SUCCESS' if tts_success else '❌ FAILED'}")
    
    if tts_success:
        print("\n🎉 EXCELLENT! 설민석 specific voice is working!")
        print("✅ Ready to implement character-specific TTS service")
    elif actor_available:
        print("\n⚠️  Actor exists but TTS failed - check implementation")
    else:
        print("\n❌ Actor not available with provided credentials")
        print("   Recommendation: Verify actor_id and API access")
    
    print("="*70)