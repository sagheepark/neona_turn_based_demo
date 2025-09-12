#!/usr/bin/env python3
"""
Test null safety fixes for NoneType errors in chat sessions
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_normal_chat_null_safety():
    """Test that normal chat doesn't crash with NoneType errors"""
    print("\n🧪 TEST: Normal Chat → No NoneType Errors")
    print("="*50)
    
    base_url = "http://localhost:8001/api"
    
    # Test data with various null scenarios
    test_cases = [
        {
            "name": "Nonexistent character ID",
            "data": {
                "message": "Hello, how are you?",
                "character_id": "nonexistent_character_123",
                "character_prompt": "",
                "user_id": "test_user",
                "session_id": "test_session_null_1"
            }
        },
        {
            "name": "Empty character ID", 
            "data": {
                "message": "What's the weather like?",
                "character_id": "",
                "character_prompt": "",
                "user_id": "test_user",
                "session_id": "test_session_null_2"
            }
        },
        {
            "name": "Regular character with normal chat",
            "data": {
                "message": "Tell me a joke",
                "character_id": "yoon_ari",
                "character_prompt": "",
                "user_id": "test_user", 
                "session_id": "test_session_null_3"
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nSubtest {i}: {test_case['name']}")
            
            try:
                # Make API call
                async with session.post(
                    f"{base_url}/chat-with-session",
                    json=test_case["data"],
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Success: Got response with dialogue")
                        print(f"   Character: {result.get('character', 'N/A')}")
                        print(f"   Dialogue: {result.get('dialogue', 'N/A')[:50]}...")
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP {response.status}: {error_text}")
                        if "NoneType" in error_text:
                            print("🚨 NoneType error detected!")
                            return False
                            
            except Exception as e:
                print(f"❌ Exception: {e}")
                if "NoneType" in str(e):
                    print("🚨 NoneType error in exception!")
                    return False
                    
    print("\n✅ All null safety tests passed!")
    return True

async def main():
    """Main test runner"""
    print("\n🔧 NULL SAFETY TEST SUITE")
    print("="*60)
    
    success = await test_normal_chat_null_safety()
    
    if success:
        print("\n🎉 All tests passed! No NoneType errors detected.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! NoneType errors still present.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())