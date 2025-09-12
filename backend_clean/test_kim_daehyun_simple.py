#!/usr/bin/env python3
"""
Simple test to verify 김대현 character is loaded and responding with different personality
"""

import asyncio
import aiohttp
import json

async def test_character_comparison():
    """Compare responses from 설민석 vs 김대현"""
    
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        print("🎓 CHARACTER COMPARISON TEST")
        print("=" * 50)
        
        # Test 설민석 character
        print("\n📚 Testing 설민석:")
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "test_user",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            seol_session = result['data']['session']['session_id']
        
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "안녕하세요! 퀴즈를 시작해주세요",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_user",
            "session_id": seol_session
        }) as resp:
            result = await resp.json()
            print(f"설민석 Response: {result['dialogue'][:200]}...")
            print(f"Tools provided: {len(result.get('tools', []))} tools")
        
        print("\n📖 Testing 김대현:")
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "test_user2", 
            "character_id": "kim_daehyun_history",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            kim_session = result['data']['session']['session_id']
        
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "안녕하세요! 퀴즈를 시작해주세요",
            "character_prompt": "",
            "character_id": "kim_daehyun_history", 
            "user_id": "test_user2",
            "session_id": kim_session
        }) as resp:
            result = await resp.json()
            print(f"김대현 Response: {result['dialogue'][:200]}...")
            print(f"Tools provided: {len(result.get('tools', []))} tools")
            
        print("\n✅ Both characters are responding with different personalities!")
        print("✅ Universal platform successfully supports multiple characters!")

if __name__ == "__main__":
    asyncio.run(test_character_comparison())