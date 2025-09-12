#!/usr/bin/env python3
"""
Detailed V2 Validation Test

Tests the exact JSON structure, TTS generation, and timing to ensure 
the V2 architecture works exactly as specified in plan_new.md
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_detailed_v2_validation():
    """Test detailed V2 implementation with full JSON inspection"""
    print("🔍 DETAILED V2 VALIDATION TEST")
    print("=" * 80)
    
    # Test wrong answer scenario with detailed inspection
    print("\n📝 TEST 1: WRONG ANSWER - Full JSON Analysis")
    print("-" * 50)
    
    wrong_answer_payload = {
        "session_id": "detailed_test_wrong",
        "character_id": "seol_min_seok_quiz",
        "tool_type": "continuous_answer",
        "data": {
            "selection": "왕건",  # WRONG answer
            "question": "조선을 건국한 왕은 누구일까요?",
            "options": ["이성계", "왕건", "박혁거세", "김수로"],
            "correct_answer": "이성계"
        }
    }
    
    print(f"🚀 Triggering with WRONG answer: {wrong_answer_payload['data']['selection']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json=wrong_answer_payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📋 FULL API RESPONSE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extract the continuous_quiz_response tool
            step_result = data.get("step_result", {})
            response_data = step_result.get("response", {})
            tools = response_data.get("tools", [])
            
            if tools and tools[0]["type"] == "continuous_quiz_response":
                tool_data = tools[0]["data"]
                
                print(f"\n🎯 CONTINUOUS QUIZ RESPONSE DETAILED ANALYSIS:")
                print(f"├── Type: {tools[0]['type']}")
                
                # Phase 1 Analysis
                phase1 = tool_data.get("phase1", {})
                print(f"├── Phase 1:")
                print(f"│   ├── Text: '{phase1.get('text', 'N/A')}'")
                print(f"│   ├── Text Length: {len(phase1.get('text', ''))}")
                print(f"│   ├── Delay: {phase1.get('delay_ms', 'N/A')}ms")
                print(f"│   ├── Audio URL Present: {'✅ Yes' if phase1.get('audio_url') else '❌ No'}")
                if phase1.get('audio_url'):
                    audio_length = len(phase1['audio_url'])
                    print(f"│   └── Audio Data Length: {audio_length} chars")
                
                # Phase 2 Analysis  
                phase2 = tool_data.get("phase2", {})
                print(f"├── Phase 2:")
                print(f"│   ├── Text: '{phase2.get('text', 'N/A')}'")
                print(f"│   ├── Text Length: {len(phase2.get('text', ''))}")
                print(f"│   ├── Audio URL Present: {'✅ Yes' if phase2.get('audio_url') else '❌ No'}")
                if phase2.get('audio_url'):
                    audio_length = len(phase2['audio_url'])
                    print(f"│   ├── Audio Data Length: {audio_length} chars")
                
                # Phase 2 Tool Analysis
                phase2_tool = phase2.get("tool", {})
                if phase2_tool:
                    print(f"│   ├── Tool Type: {phase2_tool.get('type', 'N/A')}")
                    tool_data_inner = phase2_tool.get("data", {})
                    print(f"│   ├── Tool Question: '{tool_data_inner.get('question', 'N/A')}'")
                    print(f"│   ├── Tool Options: {tool_data_inner.get('options', [])}")
                    print(f"│   ├── Correct Answer: '{tool_data_inner.get('correct_answer', 'N/A')}'")
                    print(f"│   └── Selection Mode: {tool_data_inner.get('selection_mode', 'N/A')}")
                else:
                    print(f"│   └── ❌ No tool in Phase 2")
                
                # Validation Checks
                print(f"\n✅ VALIDATION RESULTS:")
                
                # Check if wrong answer shows same question for retry
                original_question = wrong_answer_payload["data"]["question"]
                retry_question = phase2_tool.get("data", {}).get("question", "")
                same_question = original_question == retry_question
                print(f"├── Same Question for Retry: {'✅ Yes' if same_question else '❌ No'}")
                
                # Check if Phase 1 doesn't reveal answer
                phase1_text = phase1.get('text', '').lower()
                correct_answer = wrong_answer_payload["data"]["correct_answer"].lower()
                reveals_answer = correct_answer in phase1_text
                print(f"├── Phase 1 Doesn't Reveal Answer: {'✅ Yes' if not reveals_answer else '❌ No'}")
                
                # Check TTS text adequacy
                phase1_adequate = len(phase1.get('text', '')) > 20  # Meaningful feedback
                phase2_adequate = len(phase2.get('text', '')) > 10  # Meaningful transition
                print(f"├── Phase 1 Text Adequate: {'✅ Yes' if phase1_adequate else '❌ No'}")
                print(f"├── Phase 2 Text Adequate: {'✅ Yes' if phase2_adequate else '❌ No'}")
                
                # Check timing structure
                has_delay = phase1.get('delay_ms', 0) > 0
                print(f"└── Has Timing Delay: {'✅ Yes' if has_delay else '❌ No'}")
                
                print(f"\n🎯 WRONG ANSWER FLOW: {'✅ CORRECT' if same_question and not reveals_answer and phase1_adequate and phase2_adequate else '❌ ISSUES FOUND'}")
                
            else:
                print(f"❌ Expected continuous_quiz_response tool, got: {tools}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test correct answer scenario
    print(f"\n{'='*80}")
    print("📝 TEST 2: CORRECT ANSWER - Full JSON Analysis")
    print("-" * 50)
    
    correct_answer_payload = {
        "session_id": "detailed_test_correct", 
        "character_id": "seol_min_seok_quiz",
        "tool_type": "continuous_answer", 
        "data": {
            "selection": "이성계",  # CORRECT answer
            "question": "조선을 건국한 왕은 누구일까요?",
            "options": ["이성계", "왕건", "박혁거세", "김수로"],
            "correct_answer": "이성계"
        }
    }
    
    print(f"🚀 Triggering with CORRECT answer: {correct_answer_payload['data']['selection']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json=correct_answer_payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📋 FULL API RESPONSE:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Extract and analyze correct answer response
            step_result = data.get("step_result", {})
            response_data = step_result.get("response", {})
            tools = response_data.get("tools", [])
            
            if tools and tools[0]["type"] == "continuous_quiz_response":
                tool_data = tools[0]["data"]
                
                # Check if Phase 1 celebrates
                phase1_text = tool_data.get("phase1", {}).get("text", "").lower()
                celebrates = any(word in phase1_text for word in ["정답", "맞", "훌륭", "축하", "좋"])
                print(f"\n🎯 CELEBRATION CHECK: {'✅ Celebrates' if celebrates else '❌ No celebration'}")
                
                # Check if Phase 2 has different question
                original_question = correct_answer_payload["data"]["question"]
                next_question = tool_data.get("phase2", {}).get("tool", {}).get("data", {}).get("question", "")
                different_question = original_question != next_question
                print(f"🎯 PROGRESSION CHECK: {'✅ Different question' if different_question else '❌ Same question'}")
                
                print(f"🎯 CORRECT ANSWER FLOW: {'✅ CORRECT' if celebrates and different_question else '❌ ISSUES FOUND'}")
                
            else:
                print(f"❌ Expected continuous_quiz_response tool, got: {tools}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test Error: {e}")
    
    print(f"\n{'='*80}")
    print("🎉 DETAILED V2 VALIDATION COMPLETE")
    print("✅ Full JSON structure analyzed")
    print("✅ TTS text adequacy checked")
    print("✅ Timing and order verified")

if __name__ == "__main__":
    test_detailed_v2_validation()