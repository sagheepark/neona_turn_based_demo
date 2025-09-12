#!/usr/bin/env python3
"""
Test sequential continuous quiz flow with proper session context
"""

import requests
import json

def test_sequential_continuous_flow():
    """Test the complete flow from session creation to continuous quiz response"""
    
    print("🧪 Testing Sequential Continuous Quiz Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create initial session with empty input (triggers greeting)
        print("\n📋 Step 1: Creating session with greeting...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_continuous_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        print(f"📝 Greeting: {data.get('dialogue', '')[:100]}...")
        
        if data.get('tools'):
            print(f"🔧 Greeting tools: {len(data['tools'])} tools")
            first_tool = data['tools'][0]
            if first_tool.get('type') == 'show_selection':
                print(f"   Topics: {first_tool['data'].get('options', [])}")
        
        # Step 2: Select "삼국시대" topic to get quiz question
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_continuous_user",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic response: {data.get('dialogue', '')[:100]}...")
        
        quiz_question = None
        quiz_options = []
        correct_answer = None
        
        if data.get('tools'):
            quiz_tool = data['tools'][0]
            if quiz_tool.get('type') == 'show_selection':
                quiz_question = quiz_tool['data'].get('question')
                quiz_options = quiz_tool['data'].get('options', [])
                correct_answer = quiz_tool['data'].get('correct_answer')
                
                print(f"❓ Quiz Question: {quiz_question}")
                print(f"📝 Options: {quiz_options}")
                print(f"✅ Correct Answer: {correct_answer}")
        
        if not quiz_question:
            print("❌ No quiz question found!")
            return
        
        # Step 3: Answer WRONG to trigger continuous quiz response
        wrong_answer = None
        for option in quiz_options:
            if option != correct_answer:
                wrong_answer = option
                break
        
        print(f"\n📋 Step 3: Answering WRONG with '{wrong_answer}'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": wrong_answer,
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_continuous_user", 
            "session_id": session_id
        })
        
        data = response.json()
        print(f"📊 Response status: {response.status_code}")
        print(f"📨 Response dialogue: {data.get('dialogue', 'No dialogue')}")
        print(f"🔧 Tools count: {len(data.get('tools', []))}")
        
        # Analyze the response
        if data.get('tools'):
            tool = data['tools'][0]
            tool_type = tool.get('type', 'Unknown')
            print(f"🔍 Tool type: {tool_type}")
            
            if tool_type == 'continuous_quiz_response':
                print(f"\n🎯 CONTINUOUS QUIZ RESPONSE DETECTED!")
                analyze_continuous_response(tool)
            else:
                print(f"❌ Expected continuous_quiz_response, got: {tool_type}")
                print(f"🔍 Tool data: {json.dumps(tool, indent=2, ensure_ascii=False)}")
        else:
            print("❌ No tools in response")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def analyze_continuous_response(tool):
    """Analyze the continuous_quiz_response tool data"""
    
    tool_data = tool.get('data', {})
    
    # Phase 1 Analysis
    phase1 = tool_data.get('phase1', {})
    print(f"   📋 Phase 1:")
    print(f"     Text: {phase1.get('text', 'No text')}")
    print(f"     Audio: {'Yes' if phase1.get('audio_url') else 'No'}")
    print(f"     Delay: {phase1.get('delay_ms', 'No delay')}ms")
    
    # Phase 2 Analysis  
    phase2 = tool_data.get('phase2', {})
    print(f"   📋 Phase 2:")
    print(f"     Text: {phase2.get('text', 'No text')}")
    print(f"     Audio: {'Yes' if phase2.get('audio_url') else 'No'}")
    print(f"     Tool: {phase2.get('tool', {}).get('type', 'No tool')}")
    
    if phase2.get('tool'):
        quiz_tool = phase2['tool']['data']
        print(f"     Quiz Question: {quiz_tool.get('question', 'No question')}")
        print(f"     Quiz Options: {quiz_tool.get('options', [])}")
        print(f"     Correct Answer: {quiz_tool.get('correct_answer', 'No answer')}")
    
    print(f"\n🎯 FRONTEND EXPECTATIONS:")
    print(f"   1. Display Phase 1 text with typewriter effect")
    print(f"   2. Play Phase 1 audio if available") 
    print(f"   3. Wait {phase1.get('delay_ms', 3000)}ms after audio completion")
    print(f"   4. Display Phase 2 text")
    print(f"   5. Show Phase 2 quiz tools for user selection")

if __name__ == "__main__":
    test_sequential_continuous_flow()