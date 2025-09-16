#!/usr/bin/env python3
"""
Quick test to diagnose TTS authentication issues
"""

import requests
import os
import asyncio
from services.seolminseok_tts_service import SeolMinSeokTTSService

async def test_seolminseok_auth():
    """Test SeolMinSeok TTS authentication"""
    
    print("🔍 Testing SeolMinSeok TTS Authentication...")
    
    service = SeolMinSeokTTSService()
    
    print(f"API Key: {service.api_key[:10]}...{service.api_key[-10:] if len(service.api_key) > 20 else service.api_key}")
    print(f"Actor ID: {service.actor_id}")
    print(f"Endpoint: {service.endpoint}")
    
    # Test connection
    is_working = service.test_connection()
    print(f"Connection Test: {'✅ Working' if is_working else '❌ Failed'}")
    
    if not is_working:
        print("🚨 DIAGNOSIS: SeolMinSeok TTS API key is invalid or expired")
        
        # Try manual request to get more details
        payload = {
            "text": "테스트",
            "lang": "auto",
            "actor_id": service.actor_id,
            "xapi_hd": False,
            "model_version": "latest"
        }
        
        try:
            response = requests.post(
                service.endpoint,
                headers=service.headers,
                json=payload,
                timeout=5
            )
            
            print(f"Manual test response: {response.status_code}")
            print(f"Response body: {response.text}")
            
        except Exception as e:
            print(f"Manual test error: {e}")
    
    return is_working

async def test_typecast_auth():
    """Test TypeCast TTS authentication"""
    
    print("\n🔍 Testing TypeCast TTS Authentication...")
    
    # Import and test TypeCast service
    from services.tts_service import TypecastTTSService
    
    tts_service = TypecastTTSService()
    
    # Try a simple TTS generation
    try:
        result = await tts_service.generate_speech(
            text="테스트",
            voice_id="tc_61c97b56f1b7877a74df625b",  # SeolMinSeok voice 
            timeout_seconds=5
        )
        
        if result and result != "data:audio/wav;base64,":
            print("✅ TypeCast TTS working")
            return True
        else:
            print("❌ TypeCast TTS failed - no audio returned")
            return False
            
    except Exception as e:
        print(f"❌ TypeCast TTS error: {e}")
        return False

async def main():
    print("🔍 TTS AUTHENTICATION DIAGNOSTIC")
    print("="*50)
    
    # Test both TTS services
    seol_working = await test_seolminseok_auth()
    typecast_working = await test_typecast_auth()
    
    print("\n📊 SUMMARY:")
    print("="*50)
    print(f"SeolMinSeok TTS:  {'✅ Working' if seol_working else '❌ Failed (AUTH_TOKEN_INVALID)'}")
    print(f"TypeCast TTS:     {'✅ Working' if typecast_working else '❌ Failed'}")
    
    if not seol_working and not typecast_working:
        print("\n🚨 CONCLUSION: Both TTS services have authentication issues")
        print("   This explains why no audio is being generated")
        print("   Need to update API keys or fix authentication")
    elif not seol_working:
        print("\n⚠️  CONCLUSION: SeolMinSeok TTS auth failed, but TypeCast works")
        print("   Should fallback to TypeCast for SeolMinSeok character")
    elif not typecast_working:
        print("\n⚠️  CONCLUSION: TypeCast TTS auth failed, but SeolMinSeok works")
        print("   Should use SeolMinSeok TTS for all characters")
    else:
        print("\n✅ CONCLUSION: Both TTS services working - issue is elsewhere")

if __name__ == "__main__":
    asyncio.run(main())