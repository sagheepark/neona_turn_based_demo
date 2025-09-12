#!/usr/bin/env python3
"""
FINAL DIALOGUE VALIDATION: Prove dialogue duplication is fixed
Extract exact JSON from both phases to demonstrate fix
"""

import requests
import json
import time
import asyncio

async def final_dialogue_validation():
    """Final validation showing dialogue duplication is fixed"""
    
    backend_url = "http://localhost:8001"
    
    print("🎯 FINAL DIALOGUE VALIDATION")
    print("=" * 50)
    print("Testing: '아쉽지만 정답이 아니에요' should ONLY appear in first phase")
    print()
    
    try:
        # STEP 1: Start quiz with wrong answer
        print("1️⃣ Creating quiz session and submitting wrong answer...")
        
        chat_response = requests.post(f"{backend_url}/api/chat", json={
            "message": "한국사 퀴즈 시작해주세요!",
            "character_id": "seolminseok_korean_history_chat",
            "character_prompt": "You are 설민석, a Korean history teacher.",
            "user_id": "final_test"
        }, timeout=30)
        
        if chat_response.status_code != 200:
            print(f"❌ Chat creation failed: {chat_response.status_code}")
            return False
            
        chat_data = chat_response.json()
        session_id = chat_data.get("session_id")
        tools = chat_data.get("tools", [])
        
        if not tools:
            print("❌ No quiz tools generated")
            return False
            
        quiz_tool = tools[0]
        tool_data = quiz_tool.get('data', {})
        question = tool_data.get('question', '')
        options = tool_data.get('options', [])
        correct_answer = tool_data.get('correct_answer', '')
        
        # Find a wrong answer
        wrong_answer = None
        for option in options:
            if option != correct_answer:
                wrong_answer = option
                break
        
        if not wrong_answer:
            wrong_answer = "틀린답"
            
        print(f"✅ Session: {session_id}")
        print(f"✅ Question: '{question}'")
        print(f"✅ Correct: '{correct_answer}' | Wrong: '{wrong_answer}'")
        
        # STEP 2: Trigger continuous flow with wrong answer
        print(f"\n2️⃣ Triggering continuous flow with wrong answer...")
        
        flow_response = requests.post(f"{backend_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seolminseok_korean_history_chat",
            "tool_type": "continuous_answer",
            "data": {
                "selection": wrong_answer,
                "correct_answer": correct_answer,
                "question": question,
                "items": options
            }
        }, timeout=30)
        
        if flow_response.status_code != 200:
            print(f"❌ Flow trigger failed: {flow_response.status_code}")
            return False
            
        flow_data = flow_response.json()
        
        # Extract first phase data
        first_phase_dialogue = ""
        if "step_result" in flow_data and "response" in flow_data["step_result"]:
            first_phase_dialogue = flow_data["step_result"]["response"].get("dialogue", "")
        else:
            first_phase_dialogue = flow_data.get("dialogue", "") or flow_data.get("text", "")
        
        print(f"✅ First phase captured")
        
        # STEP 3: Wait and get second phase with background processing
        print(f"\n3️⃣ Waiting for second phase background processing...")
        
        # Wait a bit for background processing
        await asyncio.sleep(3)
        
        second_phase_response = requests.get(f"{backend_url}/api/continuous-flow/second-phase/{session_id}", 
                                           params={"wait_timeout": 10, "poll_interval": 0.5}, 
                                           timeout=15)
        
        second_phase_dialogue = ""
        second_phase_available = False
        
        if second_phase_response.status_code == 200:
            second_phase_data = second_phase_response.json()
            second_phase_available = second_phase_data.get('available', False)
            
            if second_phase_available:
                second_phase_dialogue = second_phase_data.get("dialogue", "")
                print(f"✅ Second phase captured")
            else:
                print(f"⚠️  Second phase not yet available")
        else:
            print(f"❌ Second phase retrieval failed: {second_phase_response.status_code}")
        
        # STEP 4: JSON Analysis 
        print(f"\n📋 COMPLETE JSON ANALYSIS:")
        print("=" * 70)
        
        print(f"🔍 FIRST PHASE JSON:")
        first_phase_json = {
            "dialogue": first_phase_dialogue,
            "contains_retry_feedback": "아쉽지만 정답이 아니에요" in first_phase_dialogue
        }
        print(json.dumps(first_phase_json, ensure_ascii=False, indent=2))
        
        print(f"\n🔍 SECOND PHASE JSON:")
        if second_phase_available:
            second_phase_json = {
                "dialogue": second_phase_dialogue,
                "contains_retry_feedback": "아쉽지만 정답이 아니에요" in second_phase_dialogue,
                "available": True
            }
        else:
            second_phase_json = {
                "dialogue": "",
                "contains_retry_feedback": False,
                "available": False,
                "note": "Background processing failed or incomplete"
            }
        print(json.dumps(second_phase_json, ensure_ascii=False, indent=2))
        
        # STEP 5: VALIDATION RESULTS
        print(f"\n🎯 VALIDATION RESULTS:")
        print("=" * 50)
        
        first_has_feedback = "아쉽지만 정답이 아니에요" in first_phase_dialogue
        second_has_feedback = second_phase_available and "아쉽지만 정답이 아니에요" in second_phase_dialogue
        
        print(f"First phase has '아쉽지만 정답이 아니에요': {first_has_feedback}")
        print(f"Second phase has '아쉽지만 정답이 아니에요': {second_has_feedback}")
        print(f"Second phase available: {second_phase_available}")
        
        if first_has_feedback and not second_has_feedback and second_phase_available:
            print(f"\n✅ SUCCESS: Dialogue duplication FIXED!")
            print(f"   ✅ First phase correctly shows retry feedback")
            print(f"   ✅ Second phase correctly excludes retry feedback") 
            return True
        elif first_has_feedback and second_has_feedback:
            print(f"\n❌ FAILURE: Dialogue duplication STILL EXISTS")
            print(f"   ❌ Both phases contain retry feedback")
            return False
        elif not second_phase_available:
            print(f"\n⚠️  INCOMPLETE: Cannot validate - second phase not generated")
            print(f"   ⚠️  Background processing issue prevents full validation")
            return False
        else:
            print(f"\n❓ UNEXPECTED: Unusual feedback pattern")
            return False
        
    except Exception as e:
        print(f"❌ Validation failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(final_dialogue_validation())
    if result:
        print(f"\n🏆 FINAL RESULT: DIALOGUE DUPLICATION FIXED ✅")
    else:
        print(f"\n🚨 FINAL RESULT: DIALOGUE DUPLICATION NOT FIXED ❌")