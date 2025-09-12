#!/usr/bin/env python3
"""
Real frontend integrated test to reproduce the continuous flow issue
This simulates exactly what happens when user clicks quiz options in the frontend
"""

import requests
import json
import time

def test_real_fe_continuous_flow():
    """Test the real frontend continuous flow integration"""
    
    backend_url = "http://localhost:8001"
    character_id = "seol_min_seok_quiz"
    
    print("🔍 REAL FE INTEGRATED CONTINUOUS FLOW TEST")
    print("=" * 60)
    
    try:
        # Step 1: Initial chat to start quiz (mimicking frontend behavior)
        print("1️⃣ Starting quiz conversation...")
        
        chat_response = requests.post(f"{backend_url}/api/chat", json={
            "message": "안녕하세요! 퀴즈를 시작해주세요!",
            "character_id": character_id,
            "character_prompt": """You are 설민석, an enthusiastic Korean history teacher.

When user requests quiz, you MUST:
1. Include the full question text in your dialogue response  
2. Use the "show_selection" tool to present quiz options
3. Format: "자, 문제입니다. [문제 전체 내용]"

CRITICAL DIALOGUE REQUIREMENTS:
- Always include the complete question text in your dialogue response
- Never put questions only in tools - dialogue must contain the full question""",
            "user_id": "test_user"
        }, timeout=15)
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            session_id = chat_data.get("session_id")
            initial_dialogue = chat_data.get("text", "")
            initial_tools = chat_data.get("tools", [])
            
            print(f"✅ Session created: {session_id}")
            print(f"📝 Initial dialogue: '{initial_dialogue[:100]}...'")
            print(f"🔧 Initial tools count: {len(initial_tools)}")
            
            if initial_tools and len(initial_tools) > 0:
                # Step 2: Simulate user clicking on a quiz option (this should trigger continuous flow)
                print(f"\n2️⃣ Simulating user quiz selection...")
                
                # Get the quiz tool data
                quiz_tool = initial_tools[0]
                tool_data = quiz_tool.get('data', {})
                options = tool_data.get('options', [])
                correct_answer = tool_data.get('correct_answer', '')
                question = tool_data.get('question', '')
                
                print(f"📝 Question: '{question}'")
                print(f"📝 Options: {options}")
                print(f"✅ Correct answer: '{correct_answer}'")
                
                # Simulate the frontend's tool selection call
                # This is what happens when user clicks an option in the frontend
                print(f"\n3️⃣ Triggering continuous flow via tool selection...")
                
                # Use the continuous flow trigger endpoint (this is what frontend should call)
                trigger_response = requests.post(f"{backend_url}/api/continuous-flow/trigger", json={
                    "session_id": session_id,
                    "character_id": character_id,
                    "tool_type": "show_selection",
                    "trigger_data": {
                        "selection": correct_answer,  # User's selection
                        "question": question,
                        "options": options,
                        "correct_answer": correct_answer,
                        "items": options
                    }
                }, timeout=30)
                
                print(f"🌐 Continuous flow trigger status: {trigger_response.status_code}")
                
                if trigger_response.status_code == 200:
                    trigger_data = trigger_response.json()
                    print(f"✅ Continuous flow triggered successfully")
                    print(f"📋 Trigger response: {json.dumps(trigger_data, indent=2, ensure_ascii=False)}")
                    
                    # The response should contain the second phase results
                    dialogue = trigger_data.get("text", "")
                    audio_url = trigger_data.get("audio_url", "")
                    tools = trigger_data.get("tools", [])
                    
                    print(f"\n🎯 SECOND PHASE CONTINUOUS FLOW RESULTS:")
                    print(f"📝 Dialogue length: {len(dialogue)} characters")
                    print(f"📝 Dialogue content: '{dialogue}'")
                    print(f"🔊 Audio URL present: {'✅' if audio_url else '❌'}")
                    print(f"🔧 Tools count: {len(tools)}")
                    
                    # Analysis
                    has_meaningful_dialogue = len(dialogue) > 30 and ("문제" in dialogue or "다음" in dialogue or "정답" in dialogue)
                    has_audio = bool(audio_url and len(audio_url) > 20) 
                    has_new_tools = len(tools) > 0
                    
                    print(f"\n📊 ANALYSIS:")
                    print(f"Meaningful dialogue: {'✅' if has_meaningful_dialogue else '❌'}")
                    print(f"Audio generation: {'✅' if has_audio else '❌'}")
                    print(f"New quiz tools: {'✅' if has_new_tools else '❌'}")
                    
                    if has_new_tools and tools:
                        next_tool = tools[0]
                        if next_tool.get('type') == 'show_selection':
                            next_question = next_tool.get('data', {}).get('question', '')
                            print(f"🔧 Next question: '{next_question[:100]}...'")
                    
                    # Final assessment
                    if has_meaningful_dialogue and has_audio and has_new_tools:
                        print(f"\n🏆 SUCCESS: Continuous flow working correctly!")
                        return True
                    else:
                        print(f"\n🚨 PROBLEM IDENTIFIED:")
                        if not has_meaningful_dialogue:
                            print("   ❌ Second phase dialogue lacks meaningful content")
                        if not has_audio:
                            print("   ❌ Second phase audio generation missing")
                        if not has_new_tools:
                            print("   ❌ Second phase quiz tools missing")
                        
                        print(f"\n🔍 DEBUG: This explains why user sees 'just the quiz selection(1~4)' without text/audio")
                        return False
                        
                else:
                    print(f"❌ Continuous flow trigger failed: {trigger_response.status_code}")
                    print(f"   Response: {trigger_response.text}")
                    
                    # Try alternative endpoint that might work
                    print(f"\n4️⃣ Trying alternative debug endpoint...")
                    debug_response = requests.post(f"{backend_url}/api/debug-tool-selection", json={
                        "session_id": session_id,
                        "character_id": character_id,
                        "selection": correct_answer,
                        "tool_data": tool_data
                    }, timeout=15)
                    
                    print(f"Debug endpoint status: {debug_response.status_code}")
                    if debug_response.status_code == 200:
                        print(f"Debug response: {debug_response.json()}")
                    
                    return False
                    
            else:
                print("❌ No initial quiz tools received")
                return False
        else:
            print(f"❌ Initial chat failed: {chat_response.status_code}")
            print(f"   Response: {chat_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_real_fe_continuous_flow()
    print(f"\n🎯 FINAL RESULT: {'PASS - Issue resolved' if success else 'FAIL - Issue persists, needs investigation'}")