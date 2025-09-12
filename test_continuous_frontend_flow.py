#!/usr/bin/env python3
"""
Test script to verify complete continuous flow from frontend perspective
Tests both Phase 1 (feedback) and Phase 2 (quiz tools) display properly
"""

import asyncio
import aiohttp
import json

async def test_complete_frontend_continuous_flow():
    """Test complete continuous quiz flow that frontend should handle"""
    
    print("🧪 Testing Complete Frontend Continuous Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Create platform session for Korean history character
        print("\n📋 Step 1: Creating platform session...")
        session_response = await session.post(f"{base_url}/api/platform/sessions", 
            json={
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_continuous_flow_user"
            })
        
        session_data = await session_response.json()
        print(f"✅ Session created: {session_data.get('session_id')}")
        print(f"📝 Greeting: {session_data.get('dialogue', 'No greeting')[:100]}...")
        
        if session_data.get('tools'):
            print(f"🔧 Initial tools: {len(session_data['tools'])} tools")
        
        # Step 2: Select a topic (simulate user selecting a topic first)  
        print("\n📋 Step 2: Selecting topic...")
        topic_response = await session.post(f"{base_url}/api/platform/chat",
            json={
                "session_id": session_data['session_id'],
                "character_id": "seol_min_seok_quiz", 
                "user_id": "test_continuous_flow_user",
                "user_input": "삼국시대"
            })
        
        topic_data = await topic_response.json()
        print(f"✅ Topic response: {topic_data.get('dialogue', '')[:100]}...")
        
        if topic_data.get('tools'):
            first_question = topic_data['tools'][0]['data'] if topic_data['tools'] else None
            if first_question:
                print(f"❓ First question: {first_question.get('question', '')}")
                print(f"📝 Options: {first_question.get('options', [])}")
        
        # Step 3: Answer question incorrectly to trigger continuous flow
        print("\n📋 Step 3: Answering question incorrectly...")
        wrong_answer_response = await session.post(f"{base_url}/api/platform/chat",
            json={
                "session_id": session_data['session_id'],
                "character_id": "seol_min_seok_quiz", 
                "user_id": "test_continuous_flow_user",
                "user_input": first_question['options'][1] if first_question else "고국천왕"  # Wrong answer
            })
        
        continuous_data = await wrong_answer_response.json()
        print(f"📊 Response status: {wrong_answer_response.status}")
        print(f"📨 Response type: {type(continuous_data)}")
        
        # Analyze the continuous response
        print(f"\n🔍 CONTINUOUS RESPONSE ANALYSIS:")
        print(f"   Dialogue: {continuous_data.get('dialogue', 'No dialogue')}")
        print(f"   Audio: {'Yes' if continuous_data.get('audio_url') else 'No'}")
        print(f"   Tools: {len(continuous_data.get('tools', []))} tools")
        
        if continuous_data.get('tools'):
            tool = continuous_data['tools'][0]
            print(f"   Tool type: {tool.get('type', 'Unknown')}")
            
            # Check if it's continuous_quiz_response format
            if tool.get('type') == 'continuous_quiz_response':
                print(f"\n✅ CONTINUOUS QUIZ RESPONSE FORMAT DETECTED")
                tool_data = tool.get('data', {})
                
                # Phase 1 Analysis
                phase1 = tool_data.get('phase1', {})
                print(f"   Phase 1:")
                print(f"     Text: {phase1.get('text', 'No text')}")
                print(f"     Audio: {'Yes' if phase1.get('audio_url') else 'No'}")
                print(f"     Delay: {phase1.get('delay_ms', 'No delay')}ms")
                
                # Phase 2 Analysis
                phase2 = tool_data.get('phase2', {})
                print(f"   Phase 2:")
                print(f"     Text: {phase2.get('text', 'No text')}")
                print(f"     Audio: {'Yes' if phase2.get('audio_url') else 'No'}")
                print(f"     Tool: {phase2.get('tool', {}).get('type', 'No tool')}")
                
                if phase2.get('tool'):
                    quiz_tool = phase2['tool']['data']
                    print(f"     Quiz Question: {quiz_tool.get('question', 'No question')}")
                    print(f"     Quiz Options: {quiz_tool.get('options', [])}")
                    print(f"     Correct Answer: {quiz_tool.get('correct_answer', 'No answer')}")
                
                print(f"\n🎯 FRONTEND HANDLING EXPECTATIONS:")
                print(f"   1. Display Phase 1 text immediately with typewriter effect")
                print(f"   2. Play Phase 1 audio if available") 
                print(f"   3. Wait for audio completion")
                print(f"   4. After delay, show Phase 2 text")
                print(f"   5. Display Phase 2 quiz tools for user selection")
                print(f"   6. Handle user's next answer with same flow")
                
            else:
                print(f"❌ Expected continuous_quiz_response, got: {tool.get('type')}")
        else:
            print(f"❌ No tools in response - continuous flow may have failed")
    
    print(f"\n🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_frontend_continuous_flow())