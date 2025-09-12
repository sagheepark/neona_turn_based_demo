#!/usr/bin/env python3
"""
ACTUAL JSON EXTRACTOR - Get raw JSON responses from both phases
"""

import requests
import json
import time

def extract_actual_json():
    """Extract the actual JSON responses"""
    
    backend_url = "http://localhost:8001"
    
    print("🔍 EXTRACTING ACTUAL JSON FROM WRONG ANSWER FLOW")
    print("=" * 60)
    
    try:
        # STEP 1: Initial chat
        chat_response = requests.post(f"{backend_url}/api/chat", json={
            "message": "한국사 퀴즈 시작해주세요!",
            "character_id": "seolminseok_korean_history_chat",
            "character_prompt": "You are 설민석, a Korean history teacher.",
            "user_id": "json_extractor"
        }, timeout=30)
        
        if chat_response.status_code != 200:
            print(f"❌ Chat failed: {chat_response.status_code}")
            return
            
        chat_data = chat_response.json()
        session_id = chat_data.get("session_id")
        tools = chat_data.get("tools", [])
        
        print(f"📋 INITIAL CHAT JSON:")
        print(json.dumps(chat_data, indent=2, ensure_ascii=False))
        print()
        
        if not tools:
            print("❌ No tools returned")
            return
            
        # Extract quiz data
        quiz_tool = tools[0]
        question = quiz_tool.get('data', {}).get('question', '')
        options = quiz_tool.get('data', {}).get('options', [])
        correct_answer = quiz_tool.get('data', {}).get('correct_answer', '')
        
        # Find wrong answer
        wrong_answer = None
        for option in options:
            if option != correct_answer:
                wrong_answer = option
                break
        
        if not wrong_answer:
            print("❌ Could not find wrong answer")
            return
        
        print(f"🎯 Using wrong answer: '{wrong_answer}' (correct: '{correct_answer}')")
        print()
        
        # STEP 2: Submit wrong answer - get first phase JSON
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
            print(f"❌ Flow failed: {flow_response.status_code}")
            return
            
        flow_data = flow_response.json()
        print(f"📋 FIRST PHASE JSON:")
        print(json.dumps(flow_data, indent=2, ensure_ascii=False))
        print()
        
        # STEP 3: Get second phase JSON
        print("⏳ Waiting 3 seconds for second phase...")
        time.sleep(3)
        
        second_phase_response = requests.get(
            f"{backend_url}/api/continuous-flow/second-phase/{session_id}",
            params={"wait_timeout": 15, "poll_interval": 0.5},
            timeout=20
        )
        
        if second_phase_response.status_code != 200:
            print(f"❌ Second phase failed: {second_phase_response.status_code}")
            print(f"Response: {second_phase_response.text}")
            return
            
        second_phase_data = second_phase_response.json()
        print(f"📋 SECOND PHASE JSON:")
        print(json.dumps(second_phase_data, indent=2, ensure_ascii=False))
        print()
        
        # Extract specific fields for analysis
        if second_phase_data.get('available', False):
            tools = second_phase_data.get('tools', [])
            if tools:
                retry_tool = tools[0]
                retry_data = retry_tool.get('data', {})
                
                print("🔍 RETRY TOOL ANALYSIS:")
                print(f"   Question: '{retry_data.get('question', 'N/A')}'")
                print(f"   Options: {retry_data.get('options', 'N/A')}")
                print(f"   Correct Answer: '{retry_data.get('correct_answer', 'N/A')}'")
                print(f"   Retry Mode: {retry_data.get('retry_mode', 'N/A')}")
                print()
                
                # Check if it matches original
                same_question = retry_data.get('question', '') == question
                same_correct = retry_data.get('correct_answer', '') == correct_answer
                retry_mode = retry_data.get('retry_mode', False)
                
                print("✅ VALIDATION:")
                print(f"   Same question: {same_question}")
                print(f"   Same correct answer: {same_correct}")
                print(f"   Retry mode enabled: {retry_mode}")
            else:
                print("❌ No tools in second phase")
        else:
            print("❌ Second phase not available")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_actual_json()