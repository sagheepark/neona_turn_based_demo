#!/usr/bin/env python3
"""
LLM Agent Integration Test

Tests the new LLM-driven platform implementation to ensure:
1. LLMAgentEngine processes interactions correctly
2. CharacterPromptManager provides user-controllable prompts
3. Integration with continuous_answer_tool works
4. Fallback systems function when LLM is unavailable
5. Complete end-to-end quiz functionality
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_llm_agent_engine():
    """Test LLMAgentEngine core functionality"""
    print("🧪 Testing LLMAgentEngine...")
    
    try:
        from services.llm_agent_engine import LLMAgentEngine, InteractionContext, AgentResponse
        
        # Create engine
        engine = LLMAgentEngine()
        
        # Test context creation
        context = InteractionContext(
            question="다음 중 세종대왕의 업적은?",
            user_answer="한글 창제",
            correct_answer="한글 창제",
            options=["불교 장려", "한글 창제", "성리학 도입", "과거제 실시"],
            session_id="test_session",
            character_id="seolminseok_korean_history_chat"
        )
        
        # Verify context properties
        assert context.is_correct == True, "Context should recognize correct answer"
        assert context.attempt_count == 0, "Initial attempt count should be 0"
        
        print("✅ InteractionContext creation successful")
        
        # Test fallback response (LLM not available)
        character_prompt = "You are a Korean history teacher."
        response = await engine._fallback_response(context)
        
        assert isinstance(response, AgentResponse), "Should return AgentResponse"
        assert response.dialogue, "Response should have dialogue"
        
        print("✅ Fallback response generation successful")
        print(f"   Sample fallback dialogue: {response.dialogue[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLMAgentEngine test failed: {e}")
        return False

async def test_character_prompt_manager():
    """Test CharacterPromptManager functionality"""
    print("🧪 Testing CharacterPromptManager...")
    
    try:
        from services.character_prompt_manager import CharacterPromptManager
        
        # Create manager
        manager = CharacterPromptManager()
        
        # Test getting default prompt
        prompt = await manager.get_prompt("seolminseok_korean_history_chat")
        assert prompt, "Should return a prompt"
        assert "설민석" in prompt, "Should contain character name"
        assert "tool" in prompt.lower(), "Should contain tool instructions"
        
        print("✅ Default prompt retrieval successful")
        print(f"   Prompt length: {len(prompt)} chars")
        
        # Test prompt validation
        validation_result = await manager._validate_character_prompt(prompt)
        assert validation_result.is_valid, "Default prompt should be valid"
        
        print("✅ Prompt validation successful")
        
        # Test updating character prompt
        custom_prompt = """You are a strict Korean history teacher.
        
        TOOL USAGE:
        - If correct: celebrate and use show_selection for new question
        - If wrong: be firm and use show_selection for retry
        
        STYLE: Formal and educational"""
        
        success = await manager.update_character_prompt("test_character", custom_prompt)
        assert success, "Should successfully update prompt"
        
        # Verify custom prompt is stored
        retrieved_prompt = await manager.get_prompt("test_character")
        assert "strict" in retrieved_prompt.lower(), "Should contain custom content"
        
        print("✅ Custom prompt update successful")
        
        # Test character listing
        characters = await manager.list_characters()
        assert len(characters) >= 3, "Should have default characters"
        assert "test_character" in characters, "Should include new character"
        
        print("✅ Character listing successful")
        print(f"   Total characters: {len(characters)}")
        
        return True
        
    except Exception as e:
        print(f"❌ CharacterPromptManager test failed: {e}")
        return False

async def test_continuous_answer_tool_integration():
    """Test integration with continuous_answer_tool"""
    print("🧪 Testing continuous_answer_tool integration...")
    
    try:
        from services.continuous_answer_tool import ContinuousAnswerTool
        
        # Create tool instance
        tool = ContinuousAnswerTool()
        
        # Test context extraction
        test_context = {
            "selection": "한글 창제",
            "correct_answer": "한글 창제",
            "question": "다음 중 세종대왕의 업적은?",
            "options": ["불교 장려", "한글 창제", "성리학 도입", "과거제 실시"],
            "session_id": "test_session_123"
        }
        
        quiz_context = tool._extract_quiz_context(test_context)
        
        assert quiz_context["user_answer"] == "한글 창제", "Should extract user answer"
        assert quiz_context["correct_answer"] == "한글 창제", "Should extract correct answer"
        assert quiz_context["quiz_question"], "Should extract question"
        assert len(quiz_context["options"]) == 4, "Should extract all options"
        
        print("✅ Context extraction successful")
        
        # Test character response generation with LLM agent
        response = await tool._generate_character_response(
            character_id="seolminseok_korean_history_chat",
            prompt="test_prompt",
            context=test_context
        )
        
        assert response, "Should generate response"
        assert "character" in response, "Should have character field"
        assert "dialogue" in response, "Should have dialogue"
        assert "was_correct" in response, "Should have correctness indicator"
        
        print("✅ Character response generation successful")
        print(f"   Response character: {response['character']}")
        print(f"   Dialogue preview: {response['dialogue'][:100]}...")
        
        # Test with wrong answer
        wrong_context = test_context.copy()
        wrong_context["selection"] = "불교 장려"  # Wrong answer
        
        wrong_response = await tool._generate_character_response(
            character_id="seolminseok_korean_history_chat",
            prompt="test_prompt",
            context=wrong_context
        )
        
        assert wrong_response["was_correct"] == False, "Should recognize wrong answer"
        assert "tools" in wrong_response or "아쉽게도" in wrong_response["dialogue"], "Should provide feedback"
        
        print("✅ Wrong answer handling successful")
        
        return True
        
    except Exception as e:
        print(f"❌ continuous_answer_tool integration test failed: {e}")
        return False

async def test_end_to_end_quiz_flow():
    """Test complete quiz flow with LLM agent"""
    print("🧪 Testing end-to-end quiz flow...")
    
    try:
        from services.continuous_answer_tool import ContinuousAnswerTool
        
        tool = ContinuousAnswerTool()
        
        # Simulate complete quiz interaction
        quiz_context = {
            "character_id": "seolminseok_korean_history_chat",
            "user_answer": "한글 창제",
            "correct_answer": "한글 창제", 
            "quiz_question": "다음 중 세종대왕의 업적은?",
            "options": ["불교 장려", "한글 창제", "성리학 도입", "과거제 실시"],
            "session_id": "quiz_flow_test",
            "step_results": []
        }
        
        # Test correct answer flow
        correct_response = await tool._generate_character_response(
            character_id="seolminseok_korean_history_chat",
            prompt="",
            context=quiz_context
        )
        
        assert correct_response["was_correct"] == True, "Should handle correct answer"
        
        # Check if tools are provided for progression or fallback is working
        has_progression = ("tools" in correct_response and correct_response["tools"]) or "다음" in correct_response["dialogue"]
        assert has_progression, "Should provide next question or indicate progression"
        
        print("✅ Correct answer flow successful")
        
        # Test wrong answer flow
        quiz_context["user_answer"] = "불교 장려"  # Wrong answer
        
        wrong_response = await tool._generate_character_response(
            character_id="seolminseok_korean_history_chat", 
            prompt="",
            context=quiz_context
        )
        
        assert wrong_response["was_correct"] == False, "Should handle wrong answer"
        
        # Check for retry behavior
        has_retry = ("tools" in wrong_response and wrong_response["tools"]) or "다시" in wrong_response["dialogue"]
        assert has_retry, "Should provide retry mechanism"
        
        print("✅ Wrong answer flow successful")
        
        # Verify no answer revelation in wrong response
        correct_answer = quiz_context["correct_answer"]
        dialogue = wrong_response["dialogue"]
        
        # The dialogue shouldn't reveal the correct answer directly
        revealed_answer = correct_answer in dialogue and "정답은" in dialogue
        if not revealed_answer:
            print("✅ Answer revelation prevention successful")
        else:
            print("⚠️  Warning: Wrong answer dialogue may reveal correct answer")
        
        return True
        
    except Exception as e:
        print(f"❌ End-to-end quiz flow test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling and fallback systems"""
    print("🧪 Testing error handling and fallbacks...")
    
    try:
        from services.llm_agent_engine import LLMAgentEngine, InteractionContext
        
        # Test emergency fallback
        engine = LLMAgentEngine()
        
        context = InteractionContext(
            question="Test question",
            user_answer="wrong",
            correct_answer="right", 
            options=["wrong", "right"],
            session_id="test"
        )
        
        # Test emergency fallback for wrong answer
        fallback_response = await engine._emergency_fallback_response(context)
        
        assert fallback_response.dialogue, "Emergency fallback should provide dialogue"
        assert fallback_response.reasoning == "Emergency fallback for wrong answer", "Should have proper reasoning"
        
        print("✅ Emergency fallback successful")
        
        # Test with correct answer
        context.user_answer = "right"
        
        correct_fallback = await engine._emergency_fallback_response(context)
        assert "정답" in correct_fallback.dialogue, "Should celebrate correct answer"
        
        print("✅ Emergency fallback for correct answer successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_performance():
    """Test basic performance characteristics"""
    print("🧪 Testing performance characteristics...")
    
    try:
        from services.character_prompt_manager import CharacterPromptManager
        import time
        
        manager = CharacterPromptManager()
        
        # Test prompt retrieval speed
        start_time = time.time()
        
        for i in range(10):
            prompt = await manager.get_prompt("seolminseok_korean_history_chat")
            assert prompt, f"Prompt retrieval {i} failed"
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        assert avg_time < 0.01, f"Prompt retrieval too slow: {avg_time:.4f}s"
        
        print(f"✅ Performance test successful: {avg_time*1000:.2f}ms average")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

async def run_all_tests():
    """Run all LLM agent integration tests"""
    print("🚀 Starting LLM Agent Integration Tests")
    print("=" * 60)
    
    tests = [
        ("LLMAgentEngine Core", test_llm_agent_engine),
        ("CharacterPromptManager", test_character_prompt_manager),
        ("continuous_answer_tool Integration", test_continuous_answer_tool_integration),
        ("End-to-End Quiz Flow", test_end_to_end_quiz_flow),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 40)
        
        try:
            success = await test_func()
            if success:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! LLM Agent platform is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Review implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)