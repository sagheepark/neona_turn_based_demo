#!/usr/bin/env python3
"""
COMPLETE Continuous Flow Test
Tests BOTH steps of the continuous flow:
1. Step 0: Feedback generation (triggered by quiz feedback)  
2. Step 1: Next question generation (triggered by audio completion)
"""

import asyncio
from services.continuous_answer_tool import ContinuousAnswerTool, ToolTriggerEvent
from services.platform_content_classifier import PlatformContentClassifier

async def test_complete_two_step_flow():
    """Test complete two-step continuous flow execution"""
    
    print("🚀 TESTING COMPLETE TWO-STEP CONTINUOUS FLOW")
    print("="*60)
    
    continuous_tool = ContinuousAnswerTool()
    classifier = PlatformContentClassifier()
    
    # Simulate quiz feedback response
    llm_feedback_response = "정답입니다! 훌륭해요!"
    context = {
        "character_id": "seol_min_seok_quiz",
        "user_message": "1번",
        "conversation_phase": "post_greeting"
    }
    
    session_id = "test_session_complete_flow"
    
    print(f"📝 Testing LLM feedback: '{llm_feedback_response}'")
    print(f"📝 User answer: '{context['user_message']}'")
    
    try:
        # STEP 1: Trigger the flow (executes feedback generation)
        print(f"\n🔄 STEP 1: Triggering continuous flow...")
        
        trigger_event = ToolTriggerEvent(
            session_id=session_id,
            character_id="seol_min_seok_quiz", 
            tool_type="continue_feedback_flow",
            data={
                "user_id": "test_user",
                "user_message": context["user_message"],
                "trigger_type": "quiz_feedback",
                "context": context,
                "feedback_response": llm_feedback_response
            }
        )
        
        step1_result = await continuous_tool.trigger_flow(trigger_event)
        
        if not step1_result or not hasattr(step1_result, 'step_result'):
            print("❌ STEP 1 FAILED: No result from trigger_flow")
            return False
        
        step1_response = step1_result.step_result.response
        if isinstance(step1_response, dict):
            step1_dialogue = step1_response.get('dialogue', '')
        else:
            step1_dialogue = str(step1_response)
            
        print(f"✅ STEP 1 COMPLETED:")
        print(f"   Step ID: {step1_result.step_result.step_id}")
        print(f"   Response: '{step1_dialogue[:100]}...'")
        print(f"   Flow continues: {step1_result.flow_continues}")
        print(f"   Next trigger: {step1_result.step_result.next_trigger}")
        
        # Verify step 1 is feedback only
        has_feedback = any(word in step1_dialogue for word in ['정답', '훌륭', '맞습니다'])
        has_next_question = '다음 문제' in step1_dialogue or '문제:' in step1_dialogue
        
        if not has_feedback:
            print("❌ STEP 1 FAILED: No feedback detected")
            return False
            
        if has_next_question:
            print("❌ STEP 1 FAILED: Contains next question (should be feedback only)")
            return False
            
        print("✅ STEP 1 VERIFIED: Contains feedback, no next question")
        
        # STEP 2: Progress the flow (executes next question generation)
        print(f"\n🔄 STEP 2: Progressing flow (simulating audio completion)...")
        
        if not step1_result.flow_continues:
            print("❌ STEP 2 FAILED: Flow doesn't continue")
            return False
        
        step2_result = await continuous_tool.progress_flow(
            session_id=session_id,
            trigger_type="audio_completion",
            data={"audio_completed": True}
        )
        
        if not step2_result or not hasattr(step2_result, 'step_result'):
            print("❌ STEP 2 FAILED: No result from progress_flow")
            return False
            
        step2_response = step2_result.step_result.response
        if isinstance(step2_response, dict):
            step2_dialogue = step2_response.get('dialogue', '')
        else:
            step2_dialogue = str(step2_response)
            
        print(f"✅ STEP 2 COMPLETED:")
        print(f"   Step ID: {step2_result.step_result.step_id}")
        print(f"   Response: '{step2_dialogue[:100]}...'")
        print(f"   Flow continues: {step2_result.flow_continues}")
        
        # Verify step 2 is next question
        has_new_question = any(word in step2_dialogue for word in ['문제', '질문', '퀴즈', '선택', '①', '②', '연도는'])
        
        if not has_new_question:
            print("❌ STEP 2 FAILED: No new question detected")
            print(f"   Full response: '{step2_dialogue}'")
            return False
            
        print("✅ STEP 2 VERIFIED: Contains new question")
        
        # FINAL VERIFICATION
        print(f"\n{'='*60}")
        print("🎉 COMPLETE CONTINUOUS FLOW TEST PASSED!")
        print(f"✅ Step 1 (Feedback): '{step1_dialogue[:50]}...'")
        print(f"✅ Step 2 (Question): '{step2_dialogue[:50]}...'")
        print("✅ Two separate, orchestrated responses generated!")
        print("✅ No more combined responses!")
        
        return True
        
    except Exception as e:
        print(f"❌ COMPLETE FLOW TEST FAILED: {e}")
        return False

async def main():
    """Run complete continuous flow test"""
    print("🧪 COMPLETE CONTINUOUS FLOW EXECUTION TEST")
    print("=" * 60)
    
    success = await test_complete_two_step_flow()
    
    print(f"\n{'=' * 60}")
    
    if success:
        print("🎉 SUCCESS: Complete continuous flow working!")
        print("✅ Both steps execute separately")
        print("✅ Feedback and next question are properly separated")
        print("✅ Platform-grade quiz conversation achieved!")
    else:
        print("❌ FAILURE: Continuous flow incomplete")
        print("❌ Missing second step execution")
        print("❌ Still need to debug flow progression")

if __name__ == "__main__":
    asyncio.run(main())