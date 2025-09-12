#!/usr/bin/env python3
"""
Test the JSON parsing fix for markdown code blocks
This addresses the root cause of missing text/audio in continuous flow
"""

import requests
import json
import time

def test_json_parsing_fix():
    """Test that the JSON parsing fix resolves the continuous flow issue"""
    
    backend_url = "http://localhost:8001"
    character_id = "seol_min_seok_quiz"
    
    print("🔧 TESTING JSON PARSING FIX FOR CONTINUOUS FLOW")
    print("=" * 60)
    
    try:
        # Step 1: Start session with the FE integrated flow
        print("1️⃣ Starting FE integrated session...")
        
        session_response = requests.post(f"{backend_url}/api/sessions/start", json={
            "character_id": character_id
        }, timeout=10)
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            print(f"✅ Session created: {session_id}")
            
            # Step 2: Trigger quiz to get tools
            print("\n2️⃣ Triggering quiz flow...")
            
            chat_response = requests.post(f"{backend_url}/api/chat-with-session", json={
                "session_id": session_id,
                "message": "조선시대 퀴즈 시작해주세요!"
            }, timeout=15)
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                dialogue = chat_data.get("text", "")
                tools = chat_data.get("tools", [])
                
                print(f"📝 Quiz dialogue length: {len(dialogue)} chars")
                print(f"🔧 Quiz tools count: {len(tools)}")
                
                if tools and len(tools) > 0:
                    # Step 3: Trigger continuous flow (this should now work)
                    print("\n3️⃣ Triggering continuous flow...")
                    
                    tool_data = tools[0].get('data', {})
                    correct_answer = tool_data.get('correct_answer', '')
                    question = tool_data.get('question', '')
                    options = tool_data.get('options', [])
                    
                    print(f"📝 Question: '{question}'")
                    print(f"✅ Correct answer: '{correct_answer}'")
                    
                    # Use the continuous flow trigger endpoint
                    flow_response = requests.post(f"{backend_url}/api/continuous-flow/trigger", json={
                        "session_id": session_id,
                        "character_id": character_id,
                        "tool_type": "continuous_answer",  # Change to match the flow config
                        "trigger_data": {
                            "selection": correct_answer,
                            "correct_answer": correct_answer,
                            "question": question,
                            "items": options
                        }
                    }, timeout=30)
                    
                    print(f"🌐 Flow trigger status: {flow_response.status_code}")
                    
                    if flow_response.status_code == 200:
                        flow_data = flow_response.json()
                        flow_dialogue = flow_data.get("text", "")
                        flow_audio = flow_data.get("audio_url", "")
                        flow_tools = flow_data.get("tools", [])
                        
                        print(f"\n🎯 CONTINUOUS FLOW RESULTS (AFTER JSON FIX):")
                        print(f"📝 Dialogue length: {len(flow_dialogue)} characters")
                        print(f"📝 Dialogue content: '{flow_dialogue}'")
                        print(f"🔊 Audio URL present: {'✅' if flow_audio else '❌'}")
                        print(f"🔧 New tools count: {len(flow_tools)}")
                        
                        # Check for meaningful content
                        has_meaningful_dialogue = len(flow_dialogue) > 30 and any(word in flow_dialogue for word in ["문제", "다음", "정답", "축하", "퀴즈"])
                        has_audio = bool(flow_audio and len(flow_audio) > 20)
                        has_tools = len(flow_tools) > 0
                        
                        print(f"\n📊 ANALYSIS:")
                        print(f"Meaningful dialogue: {'✅' if has_meaningful_dialogue else '❌'}")
                        print(f"Audio generation: {'✅' if has_audio else '❌'}")
                        print(f"Next quiz tools: {'✅' if has_tools else '❌'}")
                        
                        if has_tools:
                            next_tool = flow_tools[0]
                            if next_tool.get('type') == 'show_selection':
                                next_question = next_tool.get('data', {}).get('question', '')
                                print(f"🔧 Next question: '{next_question[:80]}...'")
                        
                        # Final verdict
                        if has_meaningful_dialogue and has_audio and has_tools:
                            print(f"\n🏆 SUCCESS: JSON parsing fix resolved the continuous flow issue!")
                            print("   ✅ Second phase now generates meaningful dialogue")
                            print("   ✅ Audio is properly generated")
                            print("   ✅ Next quiz tools are provided")
                            return True
                        else:
                            print(f"\n⚠️ PARTIAL SUCCESS: JSON parsing may be fixed but other issues remain")
                            return False
                        
                    else:
                        print(f"❌ Continuous flow failed: {flow_response.status_code}")
                        print(f"   Response: {flow_response.text}")
                        return False
                        
                else:
                    print("❌ No tools received from initial quiz")
                    return False
                    
            else:
                print(f"❌ Chat failed: {chat_response.status_code}")
                return False
                
        else:
            print(f"❌ Session creation failed: {session_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_json_parsing_fix()
    print(f"\n🎯 FINAL RESULT: {'JSON parsing fix successful!' if success else 'Issue persists - needs further investigation'}")