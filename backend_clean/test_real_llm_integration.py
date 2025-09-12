#!/usr/bin/env python3
"""
REAL LLM Integration Test

This test actually calls the OpenAI API to verify the LLM Agent platform works correctly.
No fallbacks, no fake responses - only real LLM calls.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_real_llm_wrong_answer():
    """Test wrong answer with real LLM call"""
    print("🧪 Testing WRONG answer with REAL LLM...")
    
    try:
        from services.llm_agent_engine import LLMAgentEngine, InteractionContext
        
        # Create engine with real LLM
        engine = LLMAgentEngine()
        
        # Test wrong answer for 임진왜란 question
        context = InteractionContext(
            question="다음 중 임진왜란이 일어난 년도는?",
            user_answer="1600년",  # WRONG ANSWER
            correct_answer="1592년",
            options=["1590년", "1592년", "1598년", "1600년"],
            session_id="real_test_session",
            character_id="seol_min_seok_quiz"
        )
        
        print(f"📋 Question: {context.question}")
        print(f"❌ Wrong Answer: {context.user_answer}")
        print(f"✅ Correct Answer: {context.correct_answer}")
        
        # Get character prompt
        from services.character_prompt_manager import CharacterPromptManager
        prompt_manager = CharacterPromptManager()
        character_prompt = await prompt_manager.get_prompt("seol_min_seok_quiz")
        
        print(f"🎭 Using character prompt: {len(character_prompt)} chars")
        
        # Process through REAL LLM Agent
        print("🔄 Calling REAL LLM...")
        agent_response = await engine.process_interaction(context, character_prompt)
        
        print("🎯 REAL LLM RESPONSE:")
        print(f"   Dialogue: {agent_response.dialogue}")
        print(f"   Should Retry: {agent_response.should_retry}")
        print(f"   Tools: {len(agent_response.tools)}")
        print(f"   Confidence: {agent_response.confidence_score}")
        print(f"   Processing Time: {agent_response.processing_time_ms}ms")
        
        # Verify response quality
        assert agent_response.dialogue, "LLM should provide dialogue"
        assert agent_response.should_retry == True, "Wrong answer should trigger retry"
        assert len(agent_response.tools) > 0, "Should provide retry tool"
        
        # Check if hint is appropriate for 임진왜란 (should NOT mention 세종대왕)
        dialogue_lower = agent_response.dialogue.lower()
        if "세종대왕" in dialogue_lower:
            print("⚠️  WARNING: Response mentions 세종대왕 for 임진왜란 question!")
        else:
            print("✅ Good: Response does not mention irrelevant 세종대왕")
            
        # Check if hint mentions appropriate topic
        if any(word in dialogue_lower for word in ["임진", "왜란", "일본", "조선", "1592"]):
            print("✅ Good: Response mentions relevant historical context")
        else:
            print("⚠️  Response may lack specific historical context")
        
        print("✅ REAL LLM wrong answer test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ REAL LLM test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_real_llm_correct_answer():
    """Test correct answer with real LLM call"""
    print("\n🧪 Testing CORRECT answer with REAL LLM...")
    
    try:
        from services.llm_agent_engine import LLMAgentEngine, InteractionContext
        
        # Create engine with real LLM
        engine = LLMAgentEngine()
        
        # Test correct answer for 세종대왕 question
        context = InteractionContext(
            question="다음 중 세종대왕의 업적은?",
            user_answer="한글 창제",  # CORRECT ANSWER
            correct_answer="한글 창제",
            options=["불교 장려", "한글 창제", "성리학 도입", "과거제 실시"],
            session_id="real_test_session_2",
            character_id="seol_min_seok_quiz"
        )
        
        print(f"📋 Question: {context.question}")
        print(f"✅ Correct Answer: {context.user_answer}")
        
        # Get character prompt
        from services.character_prompt_manager import CharacterPromptManager
        prompt_manager = CharacterPromptManager()
        character_prompt = await prompt_manager.get_prompt("seol_min_seok_quiz")
        
        # Process through REAL LLM Agent
        print("🔄 Calling REAL LLM...")
        agent_response = await engine.process_interaction(context, character_prompt)
        
        print("🎯 REAL LLM RESPONSE:")
        print(f"   Dialogue: {agent_response.dialogue}")
        print(f"   Should Retry: {agent_response.should_retry}")
        print(f"   Tools: {len(agent_response.tools)}")
        print(f"   Confidence: {agent_response.confidence_score}")
        
        # Verify response quality
        assert agent_response.dialogue, "LLM should provide dialogue"
        assert agent_response.should_retry == False, "Correct answer should not trigger retry"
        assert len(agent_response.tools) > 0, "Should provide new question tool"
        
        # Check if response celebrates correct answer
        dialogue_lower = agent_response.dialogue.lower()
        if any(word in dialogue_lower for word in ["정답", "맞", "축하", "훌륭"]):
            print("✅ Good: Response celebrates correct answer")
        else:
            print("⚠️  Response may not properly celebrate correct answer")
        
        print("✅ REAL LLM correct answer test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ REAL LLM test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_continuous_answer_tool_integration():
    """Test integration with continuous_answer_tool using real LLM"""
    print("\n🧪 Testing continuous_answer_tool integration with REAL LLM...")
    
    try:
        from services.continuous_answer_tool import ContinuousAnswerTool
        
        tool = ContinuousAnswerTool()
        
        # Test wrong answer scenario
        wrong_context = {
            "selection": "1600년",
            "correct_answer": "1592년", 
            "question": "다음 중 임진왜란이 일어난 년도는?",
            "options": ["1590년", "1592년", "1598년", "1600년"],
            "session_id": "integration_test"
        }
        
        print("🔄 Testing wrong answer through continuous_answer_tool...")
        response = await tool._generate_character_response(
            character_id="seol_min_seok_quiz",
            prompt="",  # Will use CharacterPromptManager
            context=wrong_context
        )
        
        print(f"🎯 Integration Response: {response}")
        
        assert response["was_correct"] == False, "Should recognize wrong answer"
        assert response["dialogue"], "Should have dialogue"
        
        print("✅ continuous_answer_tool integration test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_real_tests():
    """Run all REAL LLM tests"""
    print("🚀 REAL LLM INTEGRATION TESTS")
    print("=" * 60)
    print("⚠️  This test calls the ACTUAL OpenAI API")
    print("⚠️  Make sure OPENAI_API_KEY is set")
    print("=" * 60)
    
    # Check Azure OpenAI API key (the actual environment variable)
    if not os.getenv('AZURE_OPENAI_API_KEY'):
        print("❌ AZURE_OPENAI_API_KEY not set. Cannot run real tests.")
        return False
    
    tests = [
        ("Wrong Answer Real LLM", test_real_llm_wrong_answer),
        ("Correct Answer Real LLM", test_real_llm_correct_answer), 
        ("continuous_answer_tool Integration", test_continuous_answer_tool_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 50)
        
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
    print(f"🎯 REAL TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL REAL TESTS PASSED! LLM Agent platform works correctly!")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_real_tests())
    sys.exit(0 if success else 1)