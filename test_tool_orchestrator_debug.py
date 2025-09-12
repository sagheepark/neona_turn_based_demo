#!/usr/bin/env python3
"""
Debug script to test the ToolOrchestrator's conversation state analysis
and prompt building to understand why continuous_quiz_response isn't being used
"""

import requests
import json

def test_tool_orchestrator_quiz_flow():
    """Test the complete quiz flow through the platform-chat endpoint"""
    
    print("🧪 Testing ToolOrchestrator Quiz Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_orchestrator_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        print(f"📝 Greeting: {data.get('dialogue', '')[:100]}...")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_orchestrator_user",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic response: {data.get('dialogue', '')[:100]}...")
        
        if data.get('tools'):
            quiz_data = data['tools'][0]['data']
            question = quiz_data.get('question', '')
            options = quiz_data.get('options', [])
            correct_answer = quiz_data.get('correct_answer', '')
            
            print(f"❓ Question: {question}")
            print(f"📝 Options: {options}")
            print(f"✅ Correct Answer: {correct_answer}")
            
            # Step 3: Give WRONG answer - this should trigger continuous_quiz_response
            wrong_answer = next(opt for opt in options if opt != correct_answer)
            print(f"\n📋 Step 3: Giving WRONG answer '{wrong_answer}' to test continuous quiz response...")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": wrong_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_orchestrator_user", 
                "session_id": session_id
            })
            
            continuous_data = response.json()
            print(f"📊 Response status: {response.status_code}")
            
            # ANALYZE THE RESPONSE
            print(f"\n🔍 TOOLORCHESTRATOR RESPONSE ANALYSIS:")
            print(f"   Dialogue: {continuous_data.get('dialogue', 'No dialogue')[:100]}...")
            print(f"   Tools count: {len(continuous_data.get('tools', []))}")
            
            if continuous_data.get('tools'):
                tool = continuous_data['tools'][0]
                tool_type = tool.get('type', 'Unknown')
                print(f"   First tool type: {tool_type}")
                
                if tool_type == 'continuous_quiz_response':
                    print(f"✅ SUCCESS: ToolOrchestrator generated continuous_quiz_response!")
                    
                    tool_data = tool.get('data', {})
                    print(f"   Phase 1 text: {tool_data.get('phase1', {}).get('text', 'Missing')[:80]}...")
                    print(f"   Phase 2 text: {tool_data.get('phase2', {}).get('text', 'Missing')[:80]}...")
                    print(f"   Phase 2 has tool: {'tool' in tool_data.get('phase2', {})}")
                    
                elif tool_type == 'show_selection':
                    print(f"❌ PROBLEM: ToolOrchestrator generated regular show_selection instead of continuous_quiz_response")
                    print(f"   This means either:")
                    print(f"   1. Conversation state analysis failed to detect quiz answer")
                    print(f"   2. LLM ignored the continuous_quiz_response instruction") 
                    print(f"   3. Context-aware prompt building failed")
                    
                else:
                    print(f"❌ UNEXPECTED: ToolOrchestrator generated unexpected tool: {tool_type}")
                    
            else:
                print(f"❌ NO TOOLS: ToolOrchestrator didn't generate any tools")
                
            # Step 4: Try correct answer too
            print(f"\n📋 Step 4: Now testing CORRECT answer '{correct_answer}'...")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": correct_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_orchestrator_user", 
                "session_id": session_id
            })
            
            correct_data = response.json()
            print(f"📊 Correct answer response status: {response.status_code}")
            
            if correct_data.get('tools'):
                correct_tool = correct_data['tools'][0]
                correct_tool_type = correct_tool.get('type', 'Unknown')
                print(f"   Correct answer tool type: {correct_tool_type}")
                
                if correct_tool_type == 'continuous_quiz_response':
                    print(f"✅ SUCCESS: Correct answer also generated continuous_quiz_response!")
                else:
                    print(f"❌ PROBLEM: Correct answer generated {correct_tool_type} instead of continuous_quiz_response")
            else:
                print(f"❌ NO TOOLS: Correct answer didn't generate tools")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_orchestrator_quiz_flow()