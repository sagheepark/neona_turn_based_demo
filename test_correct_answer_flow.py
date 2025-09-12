#!/usr/bin/env python3
"""
Test correct answer flow to verify continuous quiz response works for progression
"""

import requests
import json

def test_correct_answer_flow():
    """Test correct answer triggers new question generation"""
    
    print("🧪 Testing Correct Answer Continuous Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    session_id = None
    
    try:
        # Step 1: Create session
        print("\n📋 Step 1: Creating session...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "test_correct_answer_user"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Select topic
        print(f"\n📋 Step 2: Selecting topic '삼국시대'...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "삼국시대",
            "character_id": "seol_min_seok_quiz",
            "user_id": "test_correct_answer_user",
            "session_id": session_id
        })
        
        data = response.json()
        
        if data.get('tools'):
            quiz_data = data['tools'][0]['data']
            question = quiz_data.get('question', '')
            options = quiz_data.get('options', [])
            correct_answer = quiz_data.get('correct_answer', '')
            
            print(f"❓ First Question: {question}")
            print(f"📝 Options: {options}")
            print(f"✅ Will answer correctly: {correct_answer}")
            
            # Step 3: Give CORRECT answer to trigger progression flow
            print(f"\n📋 Step 3: Giving CORRECT answer '{correct_answer}'...")
            
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": correct_answer,
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_correct_answer_user", 
                "session_id": session_id
            })
            
            continuous_data = response.json()
            print(f"📊 Response status: {response.status_code}")
            
            # VALIDATE CORRECT ANSWER PROGRESSION
            print(f"\n🎯 CORRECT ANSWER PROGRESSION VALIDATION:")
            
            if 'tools' in continuous_data and continuous_data['tools']:
                tool = continuous_data['tools'][0]
                tool_type = tool.get('type', 'Unknown')
                print(f"   Tool type: {tool_type}")
                
                if tool_type == 'continuous_quiz_response':
                    print(f"✅ CONTINUOUS_QUIZ_RESPONSE FOR CORRECT ANSWER!")
                    
                    tool_data = tool.get('data', {})
                    phase1 = tool_data.get('phase1', {})
                    phase2 = tool_data.get('phase2', {})
                    
                    print(f"\n📝 PHASE 1 (CELEBRATION):")
                    print(f"   Text: {phase1.get('text', 'Missing')}")
                    print(f"   Contains celebration: {'정답' in phase1.get('text', '') or '맞습니다' in phase1.get('text', '')}")
                    
                    print(f"\n📝 PHASE 2 (NEW QUESTION):")
                    print(f"   Text: {phase2.get('text', 'Missing')}")
                    
                    if 'tool' in phase2:
                        new_quiz = phase2['tool']['data']
                        new_question = new_quiz.get('question', '')
                        print(f"   New Question: {new_question}")
                        print(f"   New Options: {new_quiz.get('options', [])}")
                        
                        # Check if it's a NEW question (different from original)
                        is_new_question = new_question != question
                        print(f"   Is NEW question: {is_new_question}")
                        
                        if is_new_question:
                            print(f"✅ PROGRESSION FLOW WORKS: Correct answer → New question")
                        else:
                            print(f"❌ SAME QUESTION REPEATED: Should be new for correct answers")
                    
                else:
                    print(f"❌ Expected continuous_quiz_response, got {tool_type}")
            else:
                print(f"❌ No tools in response")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_correct_answer_flow()