#!/usr/bin/env python3
"""
Test if async/await fixes resolved the continuous flow issue
"""

import asyncio
import requests
import json

async def test_quiz_continuous_flow():
    """Test if we get proper two-phase continuous_quiz_response after the async fixes"""
    
    print("🔍 Testing continuous flow after async fixes...")
    
    # Get a new session with topic selection
    print("\n1. Starting new session with greeting...")
    greeting_response = requests.post('http://localhost:8001/api/platform-chat', json={
        "character_id": "seol_min_seok_quiz",
        "user_input": "안녕하세요"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        return
        
    greeting_data = greeting_response.json()
    session_id = greeting_data.get('session_id')
    print(f"✅ Session created: {session_id}")
    
    # Select topic
    print("\n2. Selecting topic...")
    topic_response = requests.post('http://localhost:8001/api/platform-chat', json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "조선시대"
    })
    
    if topic_response.status_code != 200:
        print(f"❌ Topic selection failed: {topic_response.status_code}")
        return
        
    topic_data = topic_response.json()
    print(f"✅ Topic selected, tools: {len(topic_data.get('tools', []))}")
    
    # Answer quiz question 
    print("\n3. Answering quiz question...")
    answer_response = requests.post('http://localhost:8001/api/platform-chat', json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "태조 이성계"  # Correct answer
    })
    
    if answer_response.status_code != 200:
        print(f"❌ Answer failed: {answer_response.status_code}")
        return
        
    answer_data = answer_response.json()
    print(f"✅ Answer submitted successfully")
    
    # Check response structure
    dialogue = answer_data.get('dialogue', '')
    tools = answer_data.get('tools', [])
    
    print(f"\n📝 Dialogue length: {len(dialogue)} chars")
    print(f"📝 Dialogue preview: {dialogue[:150]}...")
    print(f"🛠️ Number of tools: {len(tools)}")
    
    if tools:
        for i, tool in enumerate(tools):
            print(f"🛠️ Tool {i+1}: {tool.get('type', 'unknown')}")
            
            # Check for proper continuous_quiz_response structure
            if tool.get('type') == 'continuous_quiz_response':
                data = tool.get('data', {})
                has_phase1 = 'phase1' in data
                has_phase2 = 'phase2' in data
                
                print(f"   ✅ Two-phase structure: phase1={has_phase1}, phase2={has_phase2}")
                
                if has_phase1 and has_phase2:
                    print("   🎉 SUCCESS! Proper two-phase continuous response!")
                    return True
                else:
                    print("   ❌ FAIL! Missing proper phase structure")
            elif tool.get('type') == 'show_selection':
                print("   ⚠️ WARNING! Using show_selection instead of continuous_quiz_response")
    else:
        print("❌ MAJOR ISSUE! No tools returned - this means the single-phase dialogue issue persists")
        
    return False

if __name__ == "__main__":
    success = asyncio.run(test_quiz_continuous_flow())
    if success:
        print("\n🎉 CONTINUOUS FLOW RESTORED!")
    else:
        print("\n❌ CONTINUOUS FLOW STILL BROKEN")