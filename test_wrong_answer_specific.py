#!/usr/bin/env python3
"""
Test script to verify wrong answer case specifically
Forces a wrong answer scenario by using predetermined wrong answer
"""

import requests
import json

def test_wrong_answer_specific():
    """Test wrong answer case specifically by giving wrong answer to a known question"""
    
    print("🧪 Testing Wrong Answer Specific Case")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create initial session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_wrong_answer_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Select topic to get a quiz question
        print(f"\n📋 Step 2: Selecting topic...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_wrong_answer_user",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic selected, got quiz question")
        
        if data.get('tools'):
            quiz_data = data['tools'][0]['data']
            question = quiz_data.get('question', '')
            options = quiz_data.get('options', [])
            print(f"❓ Question: {question}")
            print(f"📝 Options: {options}")
            
            # Find a wrong answer (pick any option that's not the first one, or use predetermined wrong answer)
            wrong_answer = "이승만"  # This is usually wrong for 삼국시대 questions
            
            print(f"🚫 Will answer with wrong answer: '{wrong_answer}'")
        
            # Step 3: Give wrong answer to trigger continuous flow
            print(f"\n📋 Step 3: Giving wrong answer '{wrong_answer}'...")
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_wrong_answer_user", 
                "session_id": session_id
            })
            
            data = response.json()
            print(f"📊 Response status: {response.status_code}")
            
            print(f"\n🔍 WRONG ANSWER RESPONSE ANALYSIS:")
            print(f"   Has 'tools' key: {'tools' in data}")
            
            if 'tools' in data and data['tools']:
                tool = data['tools'][0]
                print(f"   Tool type: {tool.get('type', 'Unknown')}")
                
                if tool.get('type') == 'continuous_quiz_response':
                    print(f"✅ CONTINUOUS QUIZ RESPONSE DETECTED")
                    tool_data = tool.get('data', {})
                    
                    # Check Phase 2 specifically
                    phase2 = tool_data.get('phase2', {})
                    print(f"   Phase 2 keys: {list(phase2.keys())}")
                    print(f"   Phase 2 has 'tool': {'tool' in phase2}")
                    
                    if 'tool' in phase2:
                        print(f"   ✅ Phase 2 tool found: {phase2['tool'].get('type', 'No type')}")
                        if phase2['tool'].get('data'):
                            quiz_tool = phase2['tool']['data']
                            print(f"   Quiz options in phase2: {quiz_tool.get('options', 'No options')}")
                    else:
                        print(f"   ❌ PHASE 2 MISSING TOOL - THIS IS THE BUG!")
                        print(f"   Phase 2 content: {phase2}")
                        
            else:
                print(f"❌ No tools in response")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_wrong_answer_specific()