#!/usr/bin/env python3
"""
Exact simulation of what the browser frontend does
Test the exact API calls and responses that the frontend makes
"""

import requests
import json

def simulate_exact_browser_flow():
    """Simulate the exact API calls that the browser frontend makes"""
    
    print("🧪 Simulating Exact Browser Frontend Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # EXACT Step 1: Initial session creation (empty user_input)
        print("\n📋 Step 1: Initial session creation (empty user_input)...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "demo_user"  # Same as frontend uses
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        print(f"📝 Greeting dialogue: {data.get('dialogue', '')[:100]}...")
        print(f"🔧 Tools: {len(data.get('tools', []))} tools")
        if data.get('tools'):
            print(f"   First tool type: {data['tools'][0].get('type', 'Unknown')}")
        
        # EXACT Step 2: User selects topic (topic selection)
        print(f"\n📋 Step 2: User selects topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",  # User clicks this topic option
            "character_id": "seol_min_seok_quiz",
            "user_id": "demo_user",  # Same as frontend
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic selection response")
        print(f"📝 Dialogue: {data.get('dialogue', '')[:100]}...")
        print(f"🔧 Tools: {len(data.get('tools', []))} tools")
        
        # Extract quiz question details
        if data.get('tools'):
            quiz_tool = data['tools'][0]
            quiz_data = quiz_tool['data']
            question = quiz_data.get('question', '')
            options = quiz_data.get('options', [])
            correct_answer = quiz_data.get('correct_answer', '')
            
            print(f"❓ Quiz Question: {question}")
            print(f"📝 Options: {options}")
            print(f"✅ Correct Answer: {correct_answer}")
            
            # EXACT Step 3: User answers quiz question WRONG
            # This is the critical step that should return continuous_quiz_response
            wrong_answer = next(opt for opt in options if opt != correct_answer)
            print(f"\n📋 Step 3: User selects WRONG answer '{wrong_answer}'...")
            print(f"   This should trigger continuous_quiz_response from backend")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,  # User clicks wrong option
                "character_id": "seol_min_seok_quiz",
                "user_id": "demo_user",
                "session_id": session_id
            })
            
            result = response.json()
            print(f"📊 Response status: {response.status_code}")
            
            print(f"\n🎯 CRITICAL ANALYSIS - WHAT FRONTEND RECEIVES:")
            print(f"   response.dialogue: '{result.get('dialogue', 'MISSING')[:100]}...'")
            print(f"   response.audio: {'Present' if result.get('audio_url') else 'MISSING'}")
            print(f"   response.tools: {len(result.get('tools', []))} tools")
            
            if result.get('tools'):
                first_tool = result['tools'][0]
                tool_type = first_tool.get('type', 'MISSING')
                print(f"   response.tools[0].type: '{tool_type}'")
                
                # This is the exact check the frontend does
                continuousQuizTool = None
                for tool in result['tools']:
                    if tool.get('type') == 'continuous_quiz_response':
                        continuousQuizTool = tool
                        break
                
                if continuousQuizTool:
                    print(f"✅ FRONTEND CHECK: continuous_quiz_response tool found!")
                    print(f"   Frontend SHOULD call handleContinuousQuizResponse()")
                    
                    # Show what the continuous response contains
                    tool_data = continuousQuizTool.get('data', {})
                    phase1 = tool_data.get('phase1', {})
                    phase2 = tool_data.get('phase2', {})
                    
                    print(f"\n📋 CONTINUOUS QUIZ RESPONSE CONTENT:")
                    print(f"   Phase 1 text: '{phase1.get('text', 'MISSING')[:80]}...'")
                    print(f"   Phase 1 audio: {'Present' if phase1.get('audio_url') else 'MISSING'}")
                    print(f"   Phase 1 delay: {phase1.get('delay_ms', 'MISSING')}ms")
                    
                    print(f"   Phase 2 text: '{phase2.get('text', 'MISSING')[:80]}...'")
                    print(f"   Phase 2 audio: {'Present' if phase2.get('audio_url') else 'MISSING'}")
                    print(f"   Phase 2 has quiz tool: {'tool' in phase2}")
                    
                    if 'tool' in phase2:
                        phase2_tool = phase2['tool']
                        print(f"   Phase 2 quiz question: '{phase2_tool['data'].get('question', 'MISSING')[:60]}...'")
                        print(f"   Phase 2 quiz options: {phase2_tool['data'].get('options', 'MISSING')}")
                        
                        print(f"\n✅ EXPECTED FRONTEND BEHAVIOR:")
                        print(f"   1. Display phase1.text with typewriter effect")
                        print(f"   2. Play phase1.audio_url TTS")
                        print(f"   3. Wait phase1.delay_ms after audio")
                        print(f"   4. Display phase2.text")
                        print(f"   5. Play phase2.audio_url TTS")
                        print(f"   6. Show phase2.tool quiz selection UI")
                        
                else:
                    print(f"❌ FRONTEND CHECK: continuous_quiz_response tool NOT found!")
                    print(f"   Frontend will NOT call handleContinuousQuizResponse()")
                    print(f"   This explains why the user sees no Phase 2!")
                    
                    # Show what was received instead
                    print(f"\n🔍 RECEIVED TOOLS INSTEAD:")
                    for i, tool in enumerate(result.get('tools', [])):
                        print(f"   Tool {i}: type='{tool.get('type', 'Unknown')}', data keys={list(tool.get('data', {}).keys())}")
                    
            else:
                print(f"❌ NO TOOLS: Backend returned no tools at all")
                
        else:
            print(f"❌ NO QUIZ: Topic selection didn't return quiz question")
                
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_exact_browser_flow()