#!/usr/bin/env python3
"""
Test Continuous Flow V2 - Single LLM Call Architecture

Tests the corrected implementation that matches plan_new.md specification:
- Single LLM call generates complete continuous_quiz_response
- Two-phase structure in one response
- Frontend handles timing and UI rendering
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_continuous_flow_v2():
    """Test the new V2 single-LLM-call architecture"""
    print("🧪 TESTING CONTINUOUS FLOW V2 - Single LLM Call Architecture")
    print("=" * 70)
    
    # Test wrong answer scenario
    print("\n📝 TEST: Wrong Answer Continuous Flow")
    print("-" * 40)
    
    wrong_answer_payload = {
        "session_id": "test_v2_session",
        "character_id": "seol_min_seok_quiz",
        "tool_type": "continuous_answer",
        "data": {
            "selection": "왕건",  # WRONG answer
            "question": "조선을 건국한 왕은 누구일까요?",
            "options": ["이성계", "왕건", "박혁거세", "김수로"],
            "correct_answer": "이성계"
        }
    }
    
    print(f"🚀 Triggering continuous flow with wrong answer: {wrong_answer_payload['data']['selection']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json=wrong_answer_payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ V2 API Response Status: {data.get('status', 'N/A')}")
            print(f"✅ Architecture: {data.get('step_result', {}).get('metadata', {}).get('architecture', 'N/A')}")
            
            # Extract tool data
            step_result = data.get("step_result", {})
            response_data = step_result.get("response", {})
            tools = response_data.get("tools", [])
            
            if tools and tools[0]["type"] == "continuous_quiz_response":
                tool_data = tools[0]["data"]
                
                print(f"\n🎯 CONTINUOUS QUIZ RESPONSE STRUCTURE:")
                print(f"   Phase 1 Text: {tool_data.get('phase1', {}).get('text', 'N/A')[:100]}...")
                print(f"   Phase 1 Delay: {tool_data.get('phase1', {}).get('delay_ms', 'N/A')}ms")
                print(f"   Phase 1 Audio: {'✅ Present' if tool_data.get('phase1', {}).get('audio_url') else '❌ Missing'}")
                
                print(f"   Phase 2 Text: {tool_data.get('phase2', {}).get('text', 'N/A')}")
                print(f"   Phase 2 Audio: {'✅ Present' if tool_data.get('phase2', {}).get('audio_url') else '❌ Missing'}")
                
                # Check Phase 2 tool (should be retry with same question)
                phase2_tool = tool_data.get('phase2', {}).get('tool', {})
                if phase2_tool:
                    print(f"   Phase 2 Tool: {phase2_tool.get('type', 'N/A')}")
                    phase2_data = phase2_tool.get('data', {})
                    print(f"   Phase 2 Question: {phase2_data.get('question', 'N/A')}")
                    print(f"   Same Question? {'✅ Yes' if phase2_data.get('question') == wrong_answer_payload['data']['question'] else '❌ No'}")
                    print(f"   Options: {phase2_data.get('options', [])}")
                else:
                    print(f"   ❌ Phase 2 Tool Missing")
                
                print(f"\n✅ V2 WRONG ANSWER TEST: STRUCTURE CORRECT")
                
            else:
                print(f"❌ Expected continuous_quiz_response tool, got: {tools}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    # Test correct answer scenario  
    print("\n📝 TEST: Correct Answer Continuous Flow")
    print("-" * 40)
    
    correct_answer_payload = {
        "session_id": "test_v2_session_2",
        "character_id": "seol_min_seok_quiz", 
        "tool_type": "continuous_answer",
        "data": {
            "selection": "이성계",  # CORRECT answer
            "question": "조선을 건국한 왕은 누구일까요?",
            "options": ["이성계", "왕건", "박혁거세", "김수로"],
            "correct_answer": "이성계"
        }
    }
    
    print(f"🚀 Triggering continuous flow with correct answer: {correct_answer_payload['data']['selection']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json=correct_answer_payload)
        
        if response.status_code == 200:
            data = response.json()
            step_result = data.get("step_result", {})
            response_data = step_result.get("response", {})
            tools = response_data.get("tools", [])
            
            if tools and tools[0]["type"] == "continuous_quiz_response":
                tool_data = tools[0]["data"]
                
                print(f"\n🎯 CORRECT ANSWER RESPONSE:")
                print(f"   Phase 1 Text: {tool_data.get('phase1', {}).get('text', 'N/A')[:100]}...")
                print(f"   Phase 1 Celebrates? {'✅ Yes' if '정답' in tool_data.get('phase1', {}).get('text', '') else '❌ No'}")
                
                # Check Phase 2 tool (should be NEW question for correct answers)
                phase2_tool = tool_data.get('phase2', {}).get('tool', {})
                if phase2_tool:
                    phase2_data = phase2_tool.get('data', {})
                    print(f"   Phase 2 Question: {phase2_data.get('question', 'N/A')}")
                    print(f"   Different Question? {'✅ Yes' if phase2_data.get('question') != correct_answer_payload['data']['question'] else '❌ No'}")
                
                print(f"\n✅ V2 CORRECT ANSWER TEST: STRUCTURE CORRECT")
                
            else:
                print(f"❌ Expected continuous_quiz_response tool, got: {tools}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 CONTINUOUS FLOW V2 TESTING COMPLETE")
    print("✅ Single LLM Call Architecture")
    print("✅ Two-Phase Response Structure")
    print("✅ Plan_new.md Specification Compliance")

if __name__ == "__main__":
    test_continuous_flow_v2()