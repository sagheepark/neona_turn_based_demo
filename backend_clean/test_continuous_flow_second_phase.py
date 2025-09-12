#!/usr/bin/env python3
"""
Test the second phase of continuous flow to ensure text/audio is generated properly
"""

import requests
import json

def test_continuous_flow_second_phase():
    """Test that the second phase of continuous flow includes meaningful text and audio"""
    
    backend_url = "http://localhost:8001"
    character_id = "seolminseok_korean_history_chat"
    
    print("🧪 TESTING CONTINUOUS FLOW SECOND PHASE")
    print("=" * 60)
    
    # Step 1: Start initial quiz to get a session
    print("1️⃣ Starting quiz to establish session...")
    
    try:
        character_prompt = """You are 설민석, an enthusiastic Korean history teacher.

CRITICAL DIALOGUE REQUIREMENTS:
- Always include the complete question text in your dialogue response
- Never put questions only in tools - dialogue must contain the full question
- Use format: "자, 다음 문제입니다. [문제 전체 내용]"

When user requests quiz, you MUST:
1. Include the full question text in your dialogue response  
2. Use the "show_selection" tool to present quiz options
3. Format: "자, 문제입니다. [문제 전체 내용]"
"""
        
        response = requests.post(f"{backend_url}/api/chat", json={
            "message": "안녕하세요! 한국사 퀴즈를 시작해주세요!",
            "character_id": character_id,
            "character_prompt": character_prompt,
            "user_id": "test_user"
        }, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            tools = data.get("tools", [])
            
            print(f"✅ Session established: {session_id}")
            
            if tools and len(tools) > 0:
                # Step 2: Answer the quiz to trigger continuous flow
                print("\n2️⃣ Answering quiz to trigger continuous flow...")
                
                # Get the correct answer from the quiz
                tool_data = tools[0].get('data', {})
                correct_answer = tool_data.get('correct_answer', '')
                question = tool_data.get('question', '')
                
                print(f"📝 Original question: '{question}'")
                print(f"✅ Using correct answer: '{correct_answer}'")
                
                # Submit the correct answer to trigger continuous flow using debug endpoint
                continuous_response = requests.post(f"{backend_url}/api/debug-tool-selection", json={
                    "session_id": session_id,
                    "character_id": character_id,
                    "selection": correct_answer,
                    "tool_data": tool_data
                }, timeout=30)
                
                if continuous_response.status_code == 200:
                    continuous_data = continuous_response.json()
                    dialogue = continuous_data.get("text", "")
                    audio_url = continuous_data.get("audio_url", "")
                    tools = continuous_data.get("tools", [])
                    
                    print(f"\n🎯 CONTINUOUS FLOW SECOND PHASE RESULTS:")
                    print(f"📝 Dialogue length: {len(dialogue)} characters")
                    print(f"📝 Dialogue content: '{dialogue}'")
                    print(f"🔊 Audio URL present: {'✅' if audio_url else '❌'}")
                    print(f"🔧 Tools count: {len(tools)}")
                    
                    # Analyze results
                    meaningful_dialogue = len(dialogue) > 50 and ("문제" in dialogue or "다음" in dialogue or "퀴즈" in dialogue)
                    has_audio = bool(audio_url and len(audio_url) > 20)
                    has_tools = len(tools) > 0
                    
                    print(f"\n📊 ANALYSIS:")
                    print(f"Meaningful dialogue content: {'✅' if meaningful_dialogue else '❌'}")
                    print(f"Audio generation working: {'✅' if has_audio else '❌'}")
                    print(f"Quiz tools present: {'✅' if has_tools else '❌'}")
                    
                    if tools and len(tools) > 0:
                        tool = tools[0]
                        if tool.get('type') == 'show_selection':
                            tool_data = tool.get('data', {})
                            next_question = tool_data.get('question', '')
                            print(f"🔧 Next question in tool: '{next_question[:100]}...'")
                    
                    # Overall assessment
                    all_working = meaningful_dialogue and has_audio and has_tools
                    
                    if all_working:
                        print(f"\n🏆 SUCCESS: Second phase continuous flow working properly!")
                        print("   - Dialogue contains meaningful content")
                        print("   - Audio is generated")
                        print("   - Quiz tools are provided")
                        return True
                    else:
                        print(f"\n🚨 ISSUES FOUND:")
                        if not meaningful_dialogue:
                            print("   - ❌ Dialogue lacks meaningful question content")
                        if not has_audio:
                            print("   - ❌ Audio generation failed or missing")
                        if not has_tools:
                            print("   - ❌ Quiz tools missing")
                        
                        print(f"\n📋 DEBUG INFO:")
                        print(f"   Full response: {json.dumps(continuous_data, indent=2, ensure_ascii=False)}")
                        return False
                        
                else:
                    print(f"❌ Continuous flow API error: {continuous_response.status_code}")
                    print(f"   Response: {continuous_response.text}")
                    return False
                    
            else:
                print("❌ No quiz tools in initial response")
                return False
                
        else:
            print(f"❌ Initial API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_continuous_flow_second_phase()
    print(f"\n🎯 FINAL RESULT: {'PASS' if success else 'FAIL'}")