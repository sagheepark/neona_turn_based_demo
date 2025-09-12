#!/usr/bin/env python3
"""
Simple test to verify audio generation in continuous_answer flow
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_audio_generation():
    """Test if audio is generated for continuous_answer flow outputs"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        print("🎵 TESTING AUDIO GENERATION IN CONTINUOUS FLOW")
        print("=" * 50)
        
        # Create session
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "audio_test_user",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
            print(f"✅ Session created: {session_id}")
        
        # Start quiz to get first question
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "조선시대 퀴즈 시작해주세요",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "audio_test_user",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            first_question = result['tools'][0]['data']
            print(f"✅ Got first question: {first_question['question']}")
        
        # Submit correct answer and check audio
        print("\n🔍 Testing audio generation for correct answer...")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": first_question['correct_answer'],
                "correct_answer": first_question['correct_answer'],
                "question": first_question['question'],
                "items": first_question['options']
            }
        }) as resp:
            result = await resp.json()
            print(f"Response keys: {list(result.keys())}")
            
            # Check if step_result contains audio
            step_result = result.get('step_result')
            if step_result:
                print(f"Step result keys: {list(step_result.keys())}")
                
                # Check for audio at step_result level (this is where it should be)
                audio_data = step_result.get('audio')
                if audio_data:
                    print(f"✅ Audio data found in step_result: {len(audio_data)} bytes")
                    print(f"   Audio type: {type(audio_data)}")
                else:
                    print("❌ No audio found in step_result")
                
                # Check response data
                response_data = step_result.get('response', {})
                print(f"Response data keys: {list(response_data.keys())}")
                    
                # Check dialogue
                dialogue = response_data.get('dialogue', '')
                print(f"Dialogue length: {len(dialogue)} chars")
                print(f"Dialogue preview: {dialogue[:100]}...")
                
                # Check metadata for TTS info
                metadata = step_result.get('metadata', {})
                audio_generated = metadata.get('audio_generated', False)
                print(f"Audio generated (metadata): {audio_generated}")
                
            else:
                print("❌ No step_result in response")
                
        return True

if __name__ == "__main__":
    asyncio.run(test_audio_generation())