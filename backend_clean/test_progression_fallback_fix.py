#!/usr/bin/env python3
"""
Test and fix the progression fallback issue where wrong answers return to first quiz
CRITICAL BUG: Lines 602-603 and other hardcoded fallbacks in ToolOrchestrator cause regression
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend_clean directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from services.tool_orchestrator import ToolOrchestrator
from services.llm_agent_engine import LLMAgentEngine
from services.character_prompt_manager import CharacterPromptManager
from services.session_service import SessionService
from services.knowledge_service import KnowledgeService
from services.tts_service import TTSService

async def test_progression_fallback_issue():
    """Test that demonstrates the progression fallback bug"""
    
    print("🔍 TESTING: Progression fallback bug reproduction")
    
    # Create test orchestrator
    session_service = SessionService()
    knowledge_service = KnowledgeService()
    tts_service = TTSService()
    
    llm_engine = LLMAgentEngine()
    character_manager = CharacterPromptManager()
    
    orchestrator = ToolOrchestrator(
        llm_agent_engine=llm_engine,
        character_prompt_manager=character_manager,
        session_service=session_service,
        knowledge_service=knowledge_service,
        tts_service=tts_service
    )
    
    # Simulate chat history with second question
    test_chat_history = [
        {
            "role": "assistant",
            "content": "첫 번째 문제입니다!",
            "tools": [{
                "type": "show_selection",
                "data": {
                    "question": "고구려의 창건자는 누구일까요?",
                    "options": ["주몽", "고국천왕", "광개토대왕", "동명성왕"],
                    "correct_answer": "주몽",
                    "selection_mode": "quiz_question"
                }
            }]
        },
        {
            "role": "user", 
            "content": "주몽"
        },
        {
            "role": "assistant",
            "content": "정답입니다! 다음 문제로 가볼까요?",
            "tools": [{
                "type": "show_selection", 
                "data": {
                    "question": "세종대왕이 창제한 문자는 무엇일까요?",  # SECOND QUESTION
                    "options": ["한글", "한자", "가나", "로마자"],
                    "correct_answer": "한글",
                    "selection_mode": "quiz_question"
                }
            }]
        },
        {
            "role": "user",
            "content": "한자"  # WRONG ANSWER to SECOND question
        }
    ]
    
    print("📋 Current chat history:")
    for i, msg in enumerate(test_chat_history):
        print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
        if 'tools' in msg:
            for tool in msg['tools']:
                if tool['type'] == 'show_selection' and 'question' in tool.get('data', {}):
                    print(f"     Question: {tool['data']['question']}")
    
    print("\n🔍 Testing _extract_current_question_context:")
    current_question_context = orchestrator._extract_current_question_context(test_chat_history)
    print(f"Extracted question: {current_question_context.get('question', 'NONE')}")
    print(f"Extracted correct answer: {current_question_context.get('correct_answer', 'NONE')}")
    
    print("\n🔍 Testing _extract_last_question_from_history:")  
    last_question = orchestrator._extract_last_question_from_history(test_chat_history)
    print(f"Fallback question: {last_question}")
    
    print("\n🔍 Testing _extract_correct_answer_from_history:")
    correct_answer = orchestrator._extract_correct_answer_from_history(test_chat_history)  
    print(f"Fallback correct answer: {correct_answer}")
    
    # CRITICAL TEST: This should maintain SECOND question, not fallback to FIRST
    expected_question = "세종대왕이 창제한 문자는 무엇일까요?"
    expected_answer = "한글"
    
    success = True
    
    if current_question_context.get('question') != expected_question:
        print(f"\n❌ PROGRESSION FALLBACK BUG DETECTED!")
        print(f"   Expected question: {expected_question}")
        print(f"   Actual question:   {current_question_context.get('question')}")
        success = False
    
    if current_question_context.get('correct_answer') != expected_answer:
        print(f"\n❌ CORRECT ANSWER FALLBACK BUG DETECTED!")  
        print(f"   Expected answer: {expected_answer}")
        print(f"   Actual answer:   {current_question_context.get('correct_answer')}")
        success = False
        
    if success:
        print(f"\n✅ QUIZ PROGRESSION WORKING CORRECTLY")
    else:
        print(f"\n❌ QUIZ PROGRESSION BUG CONFIRMED - Wrong answers cause fallback to first question")
        
    return success

async def main():
    """Main test execution"""
    
    print("=" * 80)
    print("🧪 TESTING PROGRESSION FALLBACK BUG")
    print("=" * 80)
    
    success = await test_progression_fallback_issue()
    
    if success:
        print("\n🎉 All tests passed - no progression fallback issue")
        return 0
    else:
        print("\n🚨 CRITICAL BUG: Progression fallback issue confirmed")
        print("Root cause: Hardcoded fallbacks in ToolOrchestrator force return to first question")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)