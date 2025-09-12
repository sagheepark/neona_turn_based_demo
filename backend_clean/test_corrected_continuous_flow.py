#!/usr/bin/env python3
"""
Test the corrected continuous flow detection

This test verifies that:
1. User input (like "1번") does NOT trigger continuous flow detection
2. LLM responses with feedback patterns DO trigger continuous flow detection
3. The flow works as expected after the fix
"""

import asyncio
from services.platform_content_classifier import PlatformContentClassifier

def test_user_input_should_not_trigger():
    """User answers like '1번' should NOT trigger continuous flow"""
    classifier = PlatformContentClassifier()
    
    # Test typical user quiz answers
    user_inputs = ["1번", "2번", "3번", "4번", "A", "B", "C", "D", "정답은 1번입니다"]
    
    print("🧪 Testing user inputs that should NOT trigger continuous flow:")
    for user_input in user_inputs:
        result = classifier._is_quiz_feedback(user_input, "seol_min_seok_quiz")
        print(f"   User input '{user_input}': {result} (should be False)")
        assert not result, f"User input '{user_input}' incorrectly triggered continuous flow"
    
    print("✅ All user inputs correctly did NOT trigger continuous flow")

def test_llm_responses_should_trigger():
    """LLM feedback responses should trigger continuous flow"""
    classifier = PlatformContentClassifier()
    
    # Test typical LLM feedback responses
    llm_responses = [
        "정답입니다! 훌륭해요!",
        "맞습니다! 다음 문제로 넘어가볼까요?",
        "정답이에요! 역시 잘 아시네요.",
        "훌륭합니다! 계속 해봅시다.",
        "정답입니다! 다음 문제 준비되셨나요?"
    ]
    
    print("\n🧪 Testing LLM responses that SHOULD trigger continuous flow:")
    for response in llm_responses:
        result = classifier._is_quiz_feedback(response, "seol_min_seok_quiz")
        print(f"   LLM response '{response[:30]}...': {result} (should be True)")
        assert result, f"LLM response '{response}' failed to trigger continuous flow"
    
    print("✅ All LLM responses correctly triggered continuous flow")

async def test_analyze_for_tools():
    """Test the analyze_for_tools method with feedback patterns"""
    classifier = PlatformContentClassifier()
    
    # Test LLM response that should generate continuous flow tool
    llm_response = "정답입니다! 훌륭해요! 다음 문제 준비되셨나요?"
    context = {
        "character_id": "seol_min_seok_quiz",
        "user_message": "1번",
        "conversation_phase": "post_greeting"
    }
    
    print(f"\n🧪 Testing analyze_for_tools with LLM feedback response:")
    print(f"   LLM response: '{llm_response}'")
    
    tools = await classifier.analyze_for_tools(llm_response, context)
    
    print(f"   Detected tools: {len(tools)}")
    if tools:
        print(f"   First tool type: {tools[0]['type']}")
        print(f"   Tool data: {tools[0].get('data', {})}")
    
    # Should detect continuous flow tool for feedback
    assert len(tools) > 0, "Should detect at least one tool for feedback response"
    assert tools[0]['type'] == 'continue_feedback_flow', f"Expected 'continue_feedback_flow', got '{tools[0]['type']}'"
    
    print("✅ analyze_for_tools correctly detected continuous flow tool")

def main():
    """Run all tests"""
    print("🚀 Testing Corrected Continuous Flow Detection\n")
    print("="*60)
    
    # Test 1: User inputs should not trigger
    test_user_input_should_not_trigger()
    
    # Test 2: LLM responses should trigger
    test_llm_responses_should_trigger()
    
    # Test 3: analyze_for_tools integration
    asyncio.run(test_analyze_for_tools())
    
    print(f"\n{'='*60}")
    print("🎉 ALL TESTS PASSED!")
    print("✅ Continuous flow detection is now working correctly:")
    print("   - User inputs (1번, 2번, etc.) do NOT trigger flow")
    print("   - LLM feedback responses DO trigger flow")
    print("   - Integration with analyze_for_tools works properly")

if __name__ == "__main__":
    main()