#!/usr/bin/env python3
"""
Realistic test to verify that LLM generates text with \n separators as instructed.
This simulates the actual prompt that would be sent to the LLM in a quiz scenario.
"""

import os
import json
import asyncio
from openai import AsyncOpenAI

# Simulate the character prompt (from character_prompt_manager.py)
CHARACTER_PROMPT = """You are 설민석, an enthusiastic Korean history teacher who makes learning fun and engaging.

🎤 CRITICAL TTS & UI SEPARATION REQUIREMENT:
Your 'dialogue' field should contain ONLY:
- Your educational response to the student
- The quiz question spoken naturally
- DO NOT include answer options in dialogue (they appear as buttons)
- Smooth transitions for professional audio delivery
- When writing multiple sentences, always use '\\n' as a delimiter between sentences in your text or dialogue field.

CORRECT DIALOGUE EXAMPLE FOR QUIZZES:
"좋은 선택이에요!\\n 조선시대는 정말 흥미진진한 시대죠.\\n 자, 그럼 첫 번째 문제를 시작해볼까요?\\n 조선을 건국한 왕은 누구일까요?"

TOOL PROVIDES THE OPTIONS:
- Options appear as clickable buttons in UI
- Students click buttons, not hearing all options in audio
- This creates cleaner user experience

INTERACTION FLOW:
1. Start with warm greeting introducing yourself
2. When greeting done, use 'show_selection' tool to let student choose topic
3. When topic chosen, use 'show_selection' tool to present first quiz
4. When student answers quiz, MANDATORY use 'continuous_quiz_response' tool

PERSONALITY:
- Enthusiastic and encouraging
- Use historical anecdotes
- Build confidence through positive reinforcement

BEHAVIORAL RULES FOR TTS:
- ALWAYS include complete educational narrative for natural speech
- Use smooth transitions between concepts
- Include quiz question in dialogue, but NOT the answer options
- Options appear as buttons, students don't need to hear all choices

TOOL USAGE WITH CLEAN SEPARATION:
- Use show_selection tool for UI display of options
- Dialogue field contains question and context for TTS
- Frontend displays dialogue text AND shows option buttons separately
- Students hear the question, see the options, click to answer

IMPORTANT: 
- ALWAYS use tools for interactions
- Selections from students will appear as their input
- Maintain educational flow between questions
- Generate complete text for professional TTS audio experience"""

# Simulate the quiz response prompt (from tool_orchestrator.py)
QUIZ_RESPONSE_PROMPT = """
사용자가 퀴즈 선택지를 선택했습니다. 다음과 같이 응답해 주세요:

퀴즈 정보:
* 문제: "조선을 건국한 왕은 누구인가요?"
* 선택지: ["태조 이성계", "세종대왕", "태종 이방원", "정조"]
* 정답: 당신의 지식을 사용하여 선택지에서 정답 찾기

중요:
- 당신의 지식을 사용하여 "태조 이성계"을 평가하세요 - 제공된 "정답" 필드에 의존하지 마세요.
- Phase1 의 text 길이는 한국어 기준 70자 정도로 제한해 주세요.
- 오답인 경우 Phase1 응답에서 절대로 정답을 언급하지 마세요.
- 정답 예시, 오답 예시를 준수해 주세요.
- 정답, 오답이 아닌 요청을 받은 경우, 아래 응답 형식을 준수하되, Phase1 에서 user_input 에 알맞은 응답을 제공하고, Phase2 에서는 정확히 같은 문제를 다시 제시하세요.
- Phase1, Phase2 모두에서 text 에 문장이 여러 개인 경우, \\n 을 사용하여 문장을 구분해 주세요.

정답 예시:
{
    "dialogue": "정답에 대한 축하 메시지",
    "tool": {
        "type": "continuous_quiz_response", 
        "data": {
            "phase1": {
                "text": "정답입니다.\\n [왜 맞는지 설명]",
                "delay_ms": 3000
            },
            "phase2": {
                "text": "다음 문제로 넘어가볼까요?\\n [새로운 문제]",
                "tool": {
                    "type": "show_selection",
                    "data": {
                        "title": "새로운 문제 제목",
                        "options": ["선택지1", "선택지2", "선택지3", "선택지4"]
                    }
                }
            }
        }
    },
    "character": "seol_min_seok_quiz",
    "emotion": "happy",
    "speed": 1.0
}

오답 예시:
{
    "dialogue": "오답에 대한 격려 메시지",
    "tool": {
        "type": "continuous_quiz_response",
        "data": {
            "phase1": {
                "text": "아쉽네요.\\n 다시 한번 생각해보세요!",
                "delay_ms": 2000
            },
            "phase2": {
                "text": "힌트를 드릴게요.\\n [힌트 제공] 다시 선택해보세요!",
                "tool": {
                    "type": "show_selection",
                    "data": {
                        "title": "같은 문제 (재시도)",
                        "options": ["태조 이성계", "세종대왕", "태종 이방원", "정조"]
                    }
                }
            }
        }
    },
    "character": "seol_min_seok_quiz", 
    "emotion": "normal",
    "speed": 1.0
}

현재 사용자 입력: "태조 이성계"

IMPORTANT: You must respond ONLY with a valid JSON object in exactly this format above.
"""

async def test_realistic_prompt():
    """Test the actual LLM with the realistic prompt"""
    
    # Initialize OpenAI client (using same config as backend)
    client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    # Combine character prompt + quiz response prompt (as done in actual system)
    full_prompt = f"{CHARACTER_PROMPT}\n\n{QUIZ_RESPONSE_PROMPT}"
    
    print("=" * 80)
    print("🧪 REALISTIC NEWLINE SEPARATOR TEST")
    print("=" * 80)
    print(f"📝 Full prompt length: {len(full_prompt)} characters")
    newline_check = '\\n' in full_prompt
    print(f"🔍 Newline instructions found: {newline_check}")
    print()
    
    try:
        print("🚀 Sending request to Azure OpenAI...")
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = response.choices[0].message.content.strip()
        
        print("✅ LLM Response received!")
        print("=" * 50)
        print("RAW RESPONSE:")
        print(response_text)
        print("=" * 50)
        
        # Try to parse JSON
        try:
            parsed_response = json.loads(response_text)
            print("✅ JSON parsing successful!")
            print()
            
            # Check dialogue field
            dialogue = parsed_response.get('dialogue', '')
            print(f"📢 DIALOGUE FIELD: '{dialogue}'")
            has_literal_newlines = '\\n' in dialogue
            has_actual_newlines = '\n' in dialogue
            print(f"🔍 Contains literal \\n separators: {has_literal_newlines}")
            print(f"🔍 Contains actual newlines: {has_actual_newlines}")
            
            if has_literal_newlines:
                sentences = dialogue.split('\\n')
                print(f"📝 Split by literal \\n into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            elif has_actual_newlines:
                sentences = dialogue.split('\n')
                print(f"📝 Split by actual newlines into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            print()
            
            # Check phase1 text
            phase1_text = parsed_response.get('tool', {}).get('data', {}).get('phase1', {}).get('text', '')
            print(f"🎯 PHASE1 TEXT: '{phase1_text}'")
            has_literal_p1 = '\\n' in phase1_text
            has_actual_p1 = '\n' in phase1_text
            print(f"🔍 Contains literal \\n separators: {has_literal_p1}")
            print(f"🔍 Contains actual newlines: {has_actual_p1}")
            
            if has_literal_p1:
                sentences = phase1_text.split('\\n')
                print(f"📝 Split by literal \\n into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            elif has_actual_p1:
                sentences = phase1_text.split('\n')
                print(f"📝 Split by actual newlines into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            print()
            
            # Check phase2 text
            phase2_text = parsed_response.get('tool', {}).get('data', {}).get('phase2', {}).get('text', '')
            print(f"🎯 PHASE2 TEXT: '{phase2_text}'")
            has_literal_p2 = '\\n' in phase2_text
            has_actual_p2 = '\n' in phase2_text
            print(f"🔍 Contains literal \\n separators: {has_literal_p2}")
            print(f"🔍 Contains actual newlines: {has_actual_p2}")
            
            if has_literal_p2:
                sentences = phase2_text.split('\\n')
                print(f"📝 Split by literal \\n into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            elif has_actual_p2:
                sentences = phase2_text.split('\n')
                print(f"📝 Split by actual newlines into {len(sentences)} sentences:")
                for i, sentence in enumerate(sentences, 1):
                    print(f"   {i}. '{sentence.strip()}'")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("Raw response was not valid JSON")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure your Azure OpenAI environment variables are set:")
        print("- AZURE_OPENAI_API_KEY")
        print("- AZURE_OPENAI_ENDPOINT") 
        print("- AZURE_OPENAI_DEPLOYMENT_NAME")

if __name__ == "__main__":
    asyncio.run(test_realistic_prompt())
