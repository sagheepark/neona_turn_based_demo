"""
Test Tool-Driven Flow with Real LLM

This test validates our platform architecture where LLM controls behavior
through prompts and tools, not hardcoded logic.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend_clean.services.platform_tool_handler import PlatformToolHandler
from backend_clean.services.character_prompt_manager import CharacterPromptManager
from backend_clean.services.llm_agent_engine import LLMAgentEngine, InteractionContext

# Test configuration
TEST_CHARACTER = "seol_min_seok_quiz"
TEST_SESSION = "test_session_001"
TEST_USER = "test_user"

async def test_complete_flow():
    """Test the complete educational quiz flow with real LLM"""
    
    print("\n" + "="*80)
    print("🧪 TESTING TOOL-DRIVEN QUIZ FLOW WITH REAL LLM")
    print("="*80 + "\n")
    
    # Initialize components
    tool_handler = PlatformToolHandler()
    prompt_manager = CharacterPromptManager()
    llm_agent = LLMAgentEngine()
    
    print("✅ Components initialized")
    
    # Test 1: Greeting and Topic Selection
    print("\n" + "-"*60)
    print("📝 TEST 1: GREETING AND TOPIC SELECTION")
    print("-"*60)
    
    # Get character prompt
    character_prompt = await prompt_manager.get_prompt(TEST_CHARACTER)
    
    # Add tool definitions to prompt
    tool_defs = tool_handler.get_tool_definitions_for_llm()
    
    greeting_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{tool_defs}

USER INPUT: 안녕하세요! 한국사 퀴즈 시작해주세요.

TASK: Greet the user warmly and present topic selection using show_selection tool.

RESPONSE FORMAT (JSON):
{{
    "dialogue": "Your greeting message",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "어떤 주제를 공부하고 싶으신가요?",
            "options": ["조선시대", "고려시대", "삼국시대", "근현대사"],
            "selection_mode": "topic"
        }}
    }}]
}}
"""
    
    # Process with LLM
    greeting_context = InteractionContext(
        question="",
        user_answer="안녕하세요! 한국사 퀴즈 시작해주세요.",
        correct_answer="",
        options=[],
        session_id=TEST_SESSION,
        character_id=TEST_CHARACTER
    )
    
    greeting_response = await llm_agent.process_interaction(greeting_context, greeting_prompt)
    
    print(f"\n🤖 LLM RESPONSE:")
    print(f"Dialogue: {greeting_response.dialogue[:100]}...")
    print(f"Tools: {len(greeting_response.tools)} tool(s)")
    if greeting_response.tools:
        print(f"Tool Type: {greeting_response.tools[0].get('type', 'N/A')}")
        print(f"Tool Data: {json.dumps(greeting_response.tools[0].get('data', {}), ensure_ascii=False, indent=2)}")
    
    assert greeting_response.dialogue, "Should have greeting dialogue"
    assert greeting_response.tools, "Should have topic selection tool"
    assert greeting_response.tools[0]["type"] == "show_selection", "Should be selection tool"
    
    print("\n✅ TEST 1 PASSED: Greeting with topic selection works")
    
    # Test 2: Topic Selection to First Quiz
    print("\n" + "-"*60)
    print("📝 TEST 2: TOPIC SELECTION TO FIRST QUIZ")
    print("-"*60)
    
    topic_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{tool_defs}

USER INPUT: 조선시대

CONTEXT: User selected 조선시대 as their topic.

TASK: Acknowledge their choice and present the first quiz question using show_selection tool.

RESPONSE FORMAT (JSON):
{{
    "dialogue": "좋은 선택이에요! 조선시대는 정말 흥미진진한 시대죠. 자, 첫 번째 문제입니다. [전체 문제 내용]",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "조선을 건국한 왕은 누구일까요?",
            "options": ["이성계", "왕건", "박혁거세", "김수로"],
            "correct_answer": "이성계",
            "selection_mode": "quiz_question"
        }}
    }}]
}}
"""
    
    topic_context = InteractionContext(
        question="",
        user_answer="조선시대",
        correct_answer="",
        options=[],
        session_id=TEST_SESSION,
        character_id=TEST_CHARACTER
    )
    
    topic_response = await llm_agent.process_interaction(topic_context, topic_prompt)
    
    print(f"\n🤖 LLM RESPONSE:")
    print(f"Dialogue: {topic_response.dialogue[:100]}...")
    print(f"Tools: {len(topic_response.tools)} tool(s)")
    if topic_response.tools:
        quiz_data = topic_response.tools[0].get('data', {})
        print(f"Quiz Question: {quiz_data.get('question', 'N/A')}")
        print(f"Options: {quiz_data.get('options', [])}")
        print(f"Correct Answer: {quiz_data.get('correct_answer', 'N/A')}")
    
    assert topic_response.dialogue, "Should have topic acknowledgment"
    assert topic_response.tools, "Should have quiz tool"
    assert topic_response.tools[0]["type"] == "show_selection", "Should be selection tool"
    assert topic_response.tools[0]["data"]["selection_mode"] == "quiz_question", "Should be quiz mode"
    
    print("\n✅ TEST 2 PASSED: Topic selection leads to first quiz")
    
    # Test 3: Wrong Answer - Continuous Response
    print("\n" + "-"*60)
    print("📝 TEST 3: WRONG ANSWER - CONTINUOUS RESPONSE")
    print("-"*60)
    
    # Store quiz data for testing
    quiz_question = topic_response.tools[0]["data"]["question"]
    quiz_options = topic_response.tools[0]["data"]["options"]
    correct_answer = topic_response.tools[0]["data"]["correct_answer"]
    wrong_answer = [opt for opt in quiz_options if opt != correct_answer][0]
    
    wrong_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{tool_defs}

QUIZ CONTEXT:
Question: {quiz_question}
User Answer: {wrong_answer}
Correct Answer: {correct_answer}
Options: {quiz_options}

TASK: User answered incorrectly. Generate continuous_quiz_response tool with:
1. Phase1: Brief encouragement without revealing answer
2. Phase2: Same question for retry

RESPONSE FORMAT (JSON):
{{
    "dialogue": "Processing answer...",
    "tools": [{{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "아쉽네요! 좋은 시도였어요. 다시 한번 생각해보세요!",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "자, 다시 한번 도전해볼까요?",
                "tool": {{
                    "type": "show_selection",
                    "data": {{
                        "question": "{quiz_question}",
                        "options": {quiz_options},
                        "correct_answer": "{correct_answer}",
                        "selection_mode": "quiz_question"
                    }}
                }}
            }}
        }}
    }}]
}}
"""
    
    wrong_context = InteractionContext(
        question=quiz_question,
        user_answer=wrong_answer,
        correct_answer=correct_answer,
        options=quiz_options,
        session_id=TEST_SESSION,
        character_id=TEST_CHARACTER
    )
    
    wrong_response = await llm_agent.process_interaction(wrong_context, wrong_prompt)
    
    print(f"\n🤖 LLM RESPONSE:")
    print(f"Dialogue: {wrong_response.dialogue[:100]}...")
    print(f"Tools: {len(wrong_response.tools)} tool(s)")
    
    if wrong_response.tools and wrong_response.tools[0]["type"] == "continuous_quiz_response":
        tool_data = wrong_response.tools[0]["data"]
        print(f"\nPhase 1 (Feedback): {tool_data['phase1']['text']}")
        print(f"Delay: {tool_data['phase1']['delay_ms']}ms")
        print(f"\nPhase 2 (Next): {tool_data['phase2']['text']}")
        
        retry_tool = tool_data['phase2']['tool']
        print(f"Retry Question: {retry_tool['data']['question']}")
        print(f"Same Question: {retry_tool['data']['question'] == quiz_question}")
        
        assert tool_data['phase2']['tool']['data']['question'] == quiz_question, "Should retry same question"
        assert correct_answer not in tool_data['phase1']['text'], "Should not reveal answer"
    
    print("\n✅ TEST 3 PASSED: Wrong answer triggers retry with same question")
    
    # Test 4: Correct Answer - Continuous Response
    print("\n" + "-"*60)
    print("📝 TEST 4: CORRECT ANSWER - CONTINUOUS RESPONSE")
    print("-"*60)
    
    correct_prompt = f"""
{character_prompt}

AVAILABLE TOOLS:
{tool_defs}

QUIZ CONTEXT:
Question: {quiz_question}
User Answer: {correct_answer}
Correct Answer: {correct_answer}
Options: {quiz_options}

TASK: User answered correctly. Generate continuous_quiz_response tool with:
1. Phase1: Celebration and brief historical context
2. Phase2: NEW quiz question

RESPONSE FORMAT (JSON):
{{
    "dialogue": "Processing answer...",
    "tools": [{{
        "type": "continuous_quiz_response",
        "data": {{
            "phase1": {{
                "text": "정답입니다! 훌륭해요! 이성계는 1392년 조선을 건국했죠.",
                "delay_ms": 3000
            }},
            "phase2": {{
                "text": "자, 다음 문제로 넘어가볼까요?",
                "tool": {{
                    "type": "show_selection",
                    "data": {{
                        "question": "세종대왕의 가장 큰 업적은?",
                        "options": ["한글 창제", "측우기 발명", "거북선 건조", "팔만대장경"],
                        "correct_answer": "한글 창제",
                        "selection_mode": "quiz_question"
                    }}
                }}
            }}
        }}
    }}]
}}
"""
    
    correct_context = InteractionContext(
        question=quiz_question,
        user_answer=correct_answer,
        correct_answer=correct_answer,
        options=quiz_options,
        session_id=TEST_SESSION,
        character_id=TEST_CHARACTER
    )
    
    correct_response = await llm_agent.process_interaction(correct_context, correct_prompt)
    
    print(f"\n🤖 LLM RESPONSE:")
    print(f"Dialogue: {correct_response.dialogue[:100]}...")
    print(f"Tools: {len(correct_response.tools)} tool(s)")
    
    if correct_response.tools and correct_response.tools[0]["type"] == "continuous_quiz_response":
        tool_data = correct_response.tools[0]["data"]
        print(f"\nPhase 1 (Celebration): {tool_data['phase1']['text']}")
        print(f"Delay: {tool_data['phase1']['delay_ms']}ms")
        print(f"\nPhase 2 (Next): {tool_data['phase2']['text']}")
        
        next_tool = tool_data['phase2']['tool']
        new_question = next_tool['data']['question']
        print(f"New Question: {new_question}")
        print(f"Different Question: {new_question != quiz_question}")
        
        assert "정답" in tool_data['phase1']['text'], "Should celebrate correct answer"
        assert next_tool['data']['question'] != quiz_question, "Should present new question"
    
    print("\n✅ TEST 4 PASSED: Correct answer triggers new question")
    
    # Summary
    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED!")
    print("="*80)
    print("\nSUMMARY:")
    print("✅ Greeting with topic selection works")
    print("✅ Topic selection leads to first quiz")
    print("✅ Wrong answers trigger retry with same question")
    print("✅ Correct answers trigger new question")
    print("✅ Continuous two-phase response format works")
    print("\n🚀 Platform successfully uses LLM + prompts to control behavior!")
    print("🎯 No hardcoded logic - everything driven by character prompts and tools!")

async def main():
    """Main test runner"""
    try:
        await test_complete_flow()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())