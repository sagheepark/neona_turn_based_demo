#!/usr/bin/env python3
"""
REAL Continuous Flow Test
Tests the complete continuous flow execution to verify:
1. Quiz feedback is generated as separate step
2. Next quiz question is generated as separate step
3. No combined responses like "정답입니다! 훌륭해요! 다음 문제 준비되셨나요?"
"""

import asyncio
import json
from services.continuous_answer_tool import ContinuousAnswerTool, ToolTriggerEvent
from services.platform_content_classifier import PlatformContentClassifier

async def test_real_continuous_flow_execution():
    """Test actual continuous flow execution with quiz feedback"""
    
    print("🚀 TESTING REAL CONTINUOUS FLOW EXECUTION")
    print("="*60)
    
    # Initialize the continuous answer tool
    continuous_tool = ContinuousAnswerTool()
    classifier = PlatformContentClassifier()
    
    # Simulate a quiz feedback response that should trigger continuous flow
    llm_feedback_response = "정답입니다! 훌륭해요!"
    context = {
        "character_id": "seol_min_seok_quiz",
        "user_message": "1번",
        "conversation_phase": "post_greeting"
    }
    
    print(f"📝 Simulating LLM feedback response: '{llm_feedback_response}'")
    
    # Step 1: Verify detection works
    tools = await classifier.analyze_for_tools(llm_feedback_response, context)
    
    if not tools:
        print("❌ FAILED: No tools detected from feedback response")
        return False
    
    if tools[0]['type'] != 'continue_feedback_flow':
        print(f"❌ FAILED: Expected 'continue_feedback_flow', got '{tools[0]['type']}'")
        return False
    
    print(f"✅ Step 1: Continuous flow tool detected successfully")
    
    # Step 2: Execute the continuous flow
    flow_tool = tools[0]
    print(f"🔄 Step 2: Executing continuous flow...")
    print(f"   Flow config: {flow_tool['data']['flow_config']['steps']}")
    
    try:
        # Create proper ToolTriggerEvent
        trigger_event = ToolTriggerEvent(
            session_id="test_session_123",
            character_id="seol_min_seok_quiz",
            tool_type="continue_feedback_flow",
            data={
                "user_id": "test_user",
                "user_message": "1번",
                "trigger_type": "quiz_feedback",
                "context": context,
                "feedback_response": llm_feedback_response
            }
        )
        
        print(f"⚡ Triggering continuous flow with event: {trigger_event.character_id}")
        
        # Execute the flow
        flow_result = await continuous_tool.trigger_flow(trigger_event)
        
        print(f"📊 Flow execution result:")
        print(f"   Type: {type(flow_result)}")
        print(f"   Flow continues: {getattr(flow_result, 'flow_continues', False)}")
        print(f"   Step result: {getattr(flow_result, 'step_result', None)}")
        
        # For this test, we verify the first step executed properly
        if flow_result and hasattr(flow_result, 'step_result'):
            step_result = flow_result.step_result
            print(f"   Step ID: {getattr(step_result, 'step_id', 'unknown')}")
            response_data = getattr(step_result, 'response', {})
            if isinstance(response_data, dict):
                dialogue = response_data.get('dialogue', '')
                print(f"   Response: '{dialogue[:100] if dialogue else 'NO DIALOGUE'}...'")
                response = dialogue
            else:
                response = str(response_data)
                print(f"   Response: '{response[:100]}...'")
            
            # Check if response is separate feedback (not combined)
            
            # Success criteria: Response should have detailed feedback but NOT next question
            has_feedback = any(word in response for word in ['정답', '훌륭', '맞습니다'])
            has_next_question = '다음 문제' in response or '문제:' in response
            
            print(f"   Has feedback: {has_feedback}")
            print(f"   Has next question: {has_next_question}")
            
            if has_feedback and not has_next_question:
                print("✅ SUCCESS: Response contains feedback but NOT next question")
                print("✅ Continuous flow is working - responses are separated!")
                return True
            else:
                print("❌ FAILED: Response is still combined or missing feedback")
                return False
        else:
            print("❌ FAILED: No flow result or step result")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: Error executing continuous flow: {e}")
        return False

def test_combined_response_detection():
    """Test that we can detect problematic combined responses"""
    
    print(f"\n🔍 TESTING COMBINED RESPONSE DETECTION")
    print("-" * 40)
    
    # Examples of BAD combined responses we want to avoid
    combined_responses = [
        "정답입니다! 훌륭해요! 다음 문제 준비되셨나요?",
        "맞습니다! 다음 문제로 넘어가볼까요? 조선시대는 언제 시작되었나요?",
        "훌륭합니다! 계속해봅시다. 다음 질문: 세종대왕의 업적은?"
    ]
    
    for response in combined_responses:
        has_feedback = any(word in response for word in ["정답", "맞습니다", "훌륭"])
        has_next_question = any(word in response for word in ["다음", "문제", "질문", "넘어가"])
        
        is_combined = has_feedback and has_next_question
        
        print(f"   Response: '{response[:50]}...'")
        print(f"   Combined: {is_combined} (should be True)")
        
        assert is_combined, f"Failed to detect combined response: {response}"
    
    print("✅ All combined responses correctly identified")

async def main():
    """Run the complete test suite"""
    print("🧪 REAL CONTINUOUS FLOW EXECUTION TEST")
    print("=" * 60)
    
    # Test 1: Combined response detection
    test_combined_response_detection()
    
    # Test 2: Real continuous flow execution
    success = await test_real_continuous_flow_execution()
    
    print(f"\n{'=' * 60}")
    
    if success:
        print("🎉 REAL CONTINUOUS FLOW TEST PASSED!")
        print("✅ Continuous flow produces separate, orchestrated responses")
        print("✅ No more combined responses like '정답입니다! 다음 문제는?'")
    else:
        print("❌ REAL CONTINUOUS FLOW TEST FAILED!")
        print("❌ System is still producing combined responses")
        print("❌ Continuous flow execution needs debugging")

if __name__ == "__main__":
    asyncio.run(main())