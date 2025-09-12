#!/usr/bin/env python3
"""
Test to validate the frontend fix for continuous quiz flow
Focuses on checking the exact API response structure the frontend will receive
"""

import requests
import json

def test_frontend_continuous_flow_fix():
    """Test the complete flow that frontend should now handle correctly"""
    
    print("🧪 Testing Frontend Fix for Continuous Quiz Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_frontend_fix_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_frontend_fix_user",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic response received")
        
        if data.get('tools'):
            quiz_data = data['tools'][0]['data']
            question = quiz_data.get('question', '')
            options = quiz_data.get('options', [])
            correct_answer = quiz_data.get('correct_answer', '')
            
            print(f"❓ Question: {question}")
            print(f"📝 Options: {options}")
            print(f"✅ Correct Answer: {correct_answer}")
            
            # Step 3: Give WRONG answer to trigger continuous flow
            wrong_answer = next(opt for opt in options if opt != correct_answer)
            print(f"\n📋 Step 3: Giving WRONG answer '{wrong_answer}'...")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_frontend_fix_user", 
                "session_id": session_id
            })
            
            continuous_data = response.json()
            print(f"📊 Response status: {response.status_code}")
            
            # VALIDATE FRONTEND WILL RECEIVE CORRECT STRUCTURE
            print(f"\n🎯 FRONTEND PROCESSING VALIDATION:")
            print(f"   Response has 'tools': {'tools' in continuous_data}")
            
            if 'tools' in continuous_data and continuous_data['tools']:
                tool = continuous_data['tools'][0]
                tool_type = tool.get('type', 'Unknown')
                print(f"   Tool type: {tool_type}")
                
                if tool_type == 'continuous_quiz_response':
                    print(f"✅ CONTINUOUS_QUIZ_RESPONSE DETECTED - Frontend fix should handle this!")
                    
                    tool_data = tool.get('data', {})
                    phase1 = tool_data.get('phase1', {})
                    phase2 = tool_data.get('phase2', {})
                    
                    print(f"\n📝 PHASE 1 CONTENT:")
                    print(f"   Text: {phase1.get('text', 'Missing')}") 
                    print(f"   Audio URL: {'Yes' if phase1.get('audio_url') else 'No'}")
                    print(f"   Delay: {phase1.get('delay_ms', 0)}ms")
                    
                    print(f"\n📝 PHASE 2 CONTENT:")
                    print(f"   Text: {phase2.get('text', 'Missing')}")
                    print(f"   Audio URL: {'Yes' if phase2.get('audio_url') else 'No'}")
                    print(f"   Has tool: {'tool' in phase2}")
                    
                    if 'tool' in phase2:
                        phase2_tool = phase2['tool']
                        print(f"   Phase 2 tool type: {phase2_tool.get('type', 'Unknown')}")
                        
                        if phase2_tool.get('data'):
                            quiz_tool_data = phase2_tool['data']
                            print(f"   Quiz question: {quiz_tool_data.get('question', 'Missing')}")
                            print(f"   Quiz options: {quiz_tool_data.get('options', [])}")
                            
                    print(f"\n✅ FRONTEND SHOULD NOW:")
                    print(f"   1. Detect continuous_quiz_response tool in handleSend()")
                    print(f"   2. Call handleContinuousQuizResponse() directly")
                    print(f"   3. Display Phase 1 text with TTS")
                    print(f"   4. Wait for delay_ms after TTS completes")
                    print(f"   5. Display Phase 2 text with TTS") 
                    print(f"   6. Show Phase 2 quiz selection UI")
                    
                else:
                    print(f"❌ Expected continuous_quiz_response, got {tool_type}")
                    print(f"   This indicates backend issue, not frontend")
            else:
                print(f"❌ No tools in response - backend not generating continuous response")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_frontend_continuous_flow_fix()