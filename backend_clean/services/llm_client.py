"""
LLM Client for Context-Aware Quiz Analysis and Generation

This service replaces hardcoded quiz responses with intelligent LLM-driven analysis:
1. Analyzes quiz answers for correctness
2. Provides educational feedback matching specific topics
3. Generates appropriate next steps (new quiz vs retry)
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded when this module is imported
load_dotenv()

logger = logging.getLogger(__name__)

class QuizLLMClient:
    def __init__(self):
        # Use Azure OpenAI like the main system
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-15-preview"
            )
            self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            logger.info("✅ QuizLLMClient initialized with Azure OpenAI")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure OpenAI client: {e}")
            raise RuntimeError(f"Cannot initialize QuizLLMClient: {e}")
        
    async def analyze_quiz_answer(self, quiz_context: Dict, character_name: str = "설민석", character_prompt: str = None) -> Dict:
        """
        First LLM Call: Analyze quiz answer and provide educational feedback
        
        Args:
            quiz_context: {
                "quiz_question": "actual question text",
                "user_answer": "user's selected answer", 
                "correct_answer": "the correct answer",
                "options": ["all", "available", "options"]
            }
            character_name: Name of the character (for personality)
            
        Returns:
            {
                "dialogue": "educational feedback text",
                "was_correct": True/False,
                "next_action": "new_quiz" or "retry_quiz",
                "educational_content": "detailed explanation"
            }
        """
        
        try:
            if character_prompt:
                # Use the character prompt when provided
                print(f"🎯 DEBUG: Using character prompt: {character_prompt[:200]}...")
                prompt = f"""{character_prompt}

CURRENT QUIZ ANALYSIS CONTEXT:
퀴즈 문제: {quiz_context.get('quiz_question', '')}
선택지: {quiz_context.get('options', [])}
학생 답변: {quiz_context.get('user_answer', '')}
정답: {quiz_context.get('correct_answer', '')}

1. 학생의 답변이 정답인지 판단하세요
2. 위에서 제공된 캐릭터 지침에 따라 피드백을 제공하세요
3. 다음 행동을 결정하세요 (정답이면 새 문제, 오답이면 재시도)

반드시 다음 JSON 형식으로만 답변하세요:
{{
    "dialogue": "학생에게 할 말",
    "was_correct": true 또는 false,
    "next_action": "new_quiz" 또는 "retry_quiz",
    "educational_content": "교육 내용"
}}

JSON 외의 다른 텍스트는 포함하지 마세요."""
            else:
                # Fallback to original prompt when no character prompt provided
                prompt = f"""당신은 한국사 전문가 {character_name} 선생님입니다. 학생이 제출한 퀴즈 답변을 분석해주세요.

퀴즈 문제: {quiz_context.get('quiz_question', '')}
선택지: {quiz_context.get('options', [])}
학생 답변: {quiz_context.get('user_answer', '')}
정답: {quiz_context.get('correct_answer', '')}

다음 작업을 수행하세요:

1. 학생의 답변이 정답인지 판단하세요
2. {character_name} 선생님의 열정적이고 친근한 톤으로 교육적 피드백을 제공하세요:
   - 정답인 경우: 축하와 함께 해당 주제에 대한 상세한 역사적 설명
   - 오답인 경우: 격려와 함께 정답에 대한 힌트와 간단한 설명
3. 다음 행동을 결정하세요 (정답이면 새 문제, 오답이면 재시도)

반드시 다음 JSON 형식으로만 답변하세요:
{{
    "dialogue": "학생에게 할 말 (자연스럽고 교육적으로)",
    "was_correct": true 또는 false,
    "next_action": "new_quiz" 또는 "retry_quiz",
    "educational_content": "상세한 교육 내용"
}}

JSON 외의 다른 텍스트는 포함하지 마세요."""

            response = await self._call_openai_api(prompt)
            
            # Parse and validate response
            result = self._parse_and_validate_analysis(response)
            
            logger.info(f"Quiz analysis completed - Correct: {result.get('was_correct')}, Action: {result.get('next_action')}")
            return result
            
        except Exception as e:
            logger.error(f"Quiz analysis failed: {e}")
            return self._fallback_analysis_response(quiz_context)
    
    async def generate_next_step(self, analysis_result: Dict, quiz_history: List, character_name: str = "설민석") -> Dict:
        """
        Second LLM Call: Generate next quiz question or retry current one
        
        Args:
            analysis_result: Result from analyze_quiz_answer
            quiz_history: List of previous questions to avoid repetition
            character_name: Character name for personality
            
        Returns:
            {
                "dialogue": "introduction to next step",
                "tools": [quiz_tool_structure] or None for retry
            }
        """
        
        try:
            if analysis_result["next_action"] == "new_quiz":
                return await self._generate_new_quiz(analysis_result, quiz_history, character_name)
            else:
                return await self._generate_retry_encouragement(analysis_result, character_name)
                
        except Exception as e:
            logger.error(f"Next step generation failed: {e}")
            return self._fallback_next_step_response(analysis_result)
    
    async def _generate_new_quiz(self, analysis_result: Dict, quiz_history: List, character_name: str) -> Dict:
        """Generate a new Korean history quiz question"""
        
        previous_questions = [q.get('question', '') for q in quiz_history[-3:]]  # Last 3 to avoid repetition
        
        prompt = f"""당신은 한국사 전문가 {character_name} 선생님입니다. 새로운 한국사 퀴즈 문제를 만들어주세요.

이전 분석 결과: {analysis_result}
최근 문제들 (반복 피하기): {previous_questions}

다음 요구사항을 만족하는 새로운 한국사 문제를 생성하세요:

1. 조선시대, 고려시대, 일제강점기, 근현대사 등 다양한 시대 포함
2. 적절한 난이도 (중학생 수준)
3. 명확한 정답과 그럴듯한 오답들
4. 교육적 가치가 있는 내용
5. {character_name} 선생님의 친근하고 격려하는 톤

CRITICAL: dialogue 필드에는 반드시 완전한 문제 텍스트를 포함해야 합니다.
형식: "자, 다음 문제입니다. [문제 전체 내용]"

반드시 다음 JSON 형식으로만 답변하세요:
{{
    "dialogue": "자, 다음 문제입니다. [여기에 문제 전체 내용을 포함하세요]",
    "tools": [{{
        "type": "show_selection",
        "data": {{
            "question": "동일한 퀴즈 문제 (dialogue에 포함된 것과 동일)",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "correct_answer": "정답 (선택지 중 하나와 정확히 일치)",
            "selection_mode": "quiz_question"
        }}
    }}]
}}

JSON 외의 다른 텍스트는 포함하지 마세요."""

        response = await self._call_openai_api(prompt)
        result = self._parse_and_validate_next_step(response)
        
        logger.info(f"New quiz generated: {result.get('tools', [{}])[0].get('data', {}).get('question', 'Unknown')}")
        return result
    
    async def _generate_retry_encouragement(self, analysis_result: Dict, character_name: str) -> Dict:
        """Generate encouragement for retrying the same question"""
        
        prompt = f"""당신은 한국사 전문가 {character_name} 선생님입니다. 학생이 틀린 답을 했으므로 격려하며 다시 시도하도록 안내해주세요.

이전 분석: {analysis_result}

학생을 격려하고 힌트를 바탕으로 다시 생각해보도록 유도하는 말을 해주세요.
{character_name} 선생님의 따뜻하고 격려하는 톤을 유지하세요.

반드시 다음 JSON 형식으로만 답변하세요:
{{
    "dialogue": "격려하며 다시 시도하도록 유도하는 말",
    "tools": null
}}

JSON 외의 다른 텍스트는 포함하지 마세요."""

        response = await self._call_openai_api(prompt)
        result = self._parse_and_validate_next_step(response)
        
        logger.info("Retry encouragement generated")
        return result
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with error handling and retry logic for rate limiting"""
        
        max_retries = 3
        base_delay = 2.0  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                print(f"🔧 LLM API CALL - Attempt {attempt + 1}/{max_retries}")
                print(f"🔧 Prompt length: {len(prompt)} chars")
                
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a Korean history expert teacher. Always respond in valid JSON format."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500
                    )
                )
                
                # Extract and validate response content
                content = response.choices[0].message.content
                
                if content is None:
                    raise ValueError("Azure OpenAI returned None content")
                
                content = content.strip()
                
                if not content:
                    raise ValueError("Azure OpenAI returned empty content")
                
                print(f"✅ LLM API SUCCESS - Response length: {len(content)} chars")
                print(f"🔧 Response preview: {content[:100]}...")
                
                return content
                
            except Exception as e:
                print(f"❌ LLM API ATTEMPT {attempt + 1} FAILED: {e}")
                print(f"❌ Error type: {type(e).__name__}")
                
                # If this is the last attempt, raise the exception
                if attempt == max_retries - 1:
                    logger.error(f"OpenAI API call failed after {max_retries} attempts: {e}")
                    logger.error(f"Prompt was: {prompt[:200]}...")
                    raise
                
                # Wait before retrying with exponential backoff
                delay = base_delay * (2 ** attempt)  # 2s, 4s, 8s
                print(f"⏰ Retrying in {delay}s due to: {e}")
                await asyncio.sleep(delay)
    
    def _parse_and_validate_analysis(self, response: str) -> Dict:
        """Parse and validate quiz analysis response"""
        
        try:
            print(f"🔧 JSON PARSING ANALYSIS: Raw response length: {len(response)} chars")
            print(f"🔧 JSON PARSING ANALYSIS: Response preview: {response[:200]}...")
            
            # Handle markdown code blocks - extract JSON from ```json ... ```
            json_text = response.strip()
            
            if not json_text:
                raise ValueError("Empty response from LLM")
            
            if json_text.startswith('```json') and json_text.endswith('```'):
                # Extract content between ```json and ```
                json_text = json_text[7:-3].strip()  # Remove ```json and ```
                print(f"🔧 JSON PARSING ANALYSIS: Extracted from ```json block: {json_text[:100]}...")
            elif json_text.startswith('```') and json_text.endswith('```'):
                # Extract content between ``` and ``` (generic code blocks)
                json_text = json_text[3:-3].strip()  # Remove ``` and ```
                print(f"🔧 JSON PARSING ANALYSIS: Extracted from ``` block: {json_text[:100]}...")
            else:
                print(f"🔧 JSON PARSING ANALYSIS: Using raw text: {json_text[:100]}...")
            
            if not json_text:
                raise ValueError("Empty JSON content after extraction")
            
            data = json.loads(json_text)
            print(f"✅ JSON PARSING ANALYSIS SUCCESS: Loaded {len(data)} fields")
            
            # Validate required fields
            required_fields = ['dialogue', 'was_correct', 'next_action', 'educational_content']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate values
            if not isinstance(data['was_correct'], bool):
                raise ValueError("was_correct must be boolean")
                
            if data['next_action'] not in ['new_quiz', 'retry_quiz']:
                logger.warning(f"Unexpected next_action value: '{data['next_action']}', raw response: {response[:200]}...")
                # Try to infer correct value from context
                if data.get('was_correct', False):
                    data['next_action'] = 'new_quiz'
                    logger.info(f"Auto-corrected next_action to 'new_quiz' for correct answer")
                else:
                    data['next_action'] = 'retry_quiz'
                    logger.info(f"Auto-corrected next_action to 'retry_quiz' for incorrect answer")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError("Invalid JSON response from LLM")
        except ValueError as e:
            logger.error(f"Analysis validation failed: {e}")
            raise
    
    def _parse_and_validate_next_step(self, response: str) -> Dict:
        """Parse and validate next step response"""
        
        try:
            # Handle markdown code blocks - extract JSON from ```json ... ```
            json_text = response.strip()
            if json_text.startswith('```json') and json_text.endswith('```'):
                # Extract content between ```json and ```
                json_text = json_text[7:-3].strip()  # Remove ```json and ```
            elif json_text.startswith('```') and json_text.endswith('```'):
                # Extract content between ``` and ``` (generic code blocks)
                json_text = json_text[3:-3].strip()  # Remove ``` and ```
            
            # Fix common JSON issues from LLM
            # Replace single quotes with double quotes
            import re
            # Only replace single quotes that are used for strings, not within strings
            json_text = re.sub(r"'([^']*)'", r'"\1"', json_text)
            
            data = json.loads(json_text)
            
            # Validate required fields
            if 'dialogue' not in data:
                raise ValueError("Missing dialogue field")
            
            # If tools exist, validate structure
            if data.get('tools'):
                tools = data['tools']
                if not isinstance(tools, list) or len(tools) != 1:
                    raise ValueError("tools must be a list with exactly one item")
                
                tool = tools[0]
                # Allow both show_selection and continuous_quiz_response tools
                valid_tool_types = ['show_selection', 'continuous_quiz_response']
                if tool.get('type') not in valid_tool_types:
                    raise ValueError(f"tool type must be one of {valid_tool_types}, got {tool.get('type')}")
                    
                tool_data = tool.get('data', {})
                
                # Different validation based on tool type
                if tool.get('type') == 'show_selection':
                    required_data_fields = ['question', 'options', 'correct_answer', 'selection_mode']
                    for field in required_data_fields:
                        if field not in tool_data:
                            raise ValueError(f"Missing tool data field: {field}")
                elif tool.get('type') == 'continuous_quiz_response':
                    # Validate continuous_quiz_response structure
                    if 'phase1' not in tool_data or 'phase2' not in tool_data:
                        raise ValueError("continuous_quiz_response must have phase1 and phase2")
                    if 'text' not in tool_data.get('phase1', {}):
                        raise ValueError("phase1 must have text field")
                    if 'text' not in tool_data.get('phase2', {}) or 'tool' not in tool_data.get('phase2', {}):
                        raise ValueError("phase2 must have text and tool fields")
                
                # Validate correct_answer is in options (only for show_selection)
                if tool.get('type') == 'show_selection':
                    correct_answer = tool_data['correct_answer'].strip()
                    options = [opt.strip() for opt in tool_data['options']]
                    
                    if correct_answer not in options:
                        # Try case-insensitive matching
                        if correct_answer.lower() not in [opt.lower() for opt in options]:
                            logger.warning(f"❌ Correct answer validation failed:")
                            logger.warning(f"   correct_answer: '{correct_answer}'")
                            logger.warning(f"   options: {options}")
                            # Try to fix by finding the closest match
                            for opt in options:
                                if correct_answer in opt or opt in correct_answer:
                                    logger.warning(f"   🔧 Auto-fixing: '{correct_answer}' → '{opt}'")
                                    tool_data['correct_answer'] = opt
                                    break
                            else:
                                raise ValueError(f"correct_answer '{correct_answer}' must be one of the options: {options}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse next step JSON: {e}")
            logger.error(f"Raw response: {response}")
            raise ValueError("Invalid JSON response from LLM")
        except ValueError as e:
            logger.error(f"Next step validation failed: {e}")
            raise
    
    def _fallback_analysis_response(self, quiz_context: Dict) -> Dict:
        """DISABLED FALLBACK - MUST USE REAL LLM"""
        raise Exception(f"LLM Client analysis fallback disabled! This indicates the system is using Korean text fallbacks instead of the actual LLM integration. Quiz context: {quiz_context}")
    
    def _fallback_next_step_response(self, analysis_result: Dict) -> Dict:
        """DISABLED FALLBACK - MUST USE REAL LLM"""
        raise Exception(f"LLM Client next step fallback disabled! This indicates the system is using Korean text fallbacks instead of the actual LLM integration. Analysis result: {analysis_result}")
    
    def _generate_dynamic_fallback_quiz(self) -> Dict:
        """Generate dynamic quiz questions for fallback logic"""
        import random
        
        # Pool of different Korean history quiz questions
        quiz_pool = [
            {
                "question": "다음 중 조선 전기의 대표적인 과학 기구는?",
                "options": ["측우기", "천체망원경", "현미경", "온도계"],
                "correct_answer": "측우기"
            },
            {
                "question": "임진왜란이 발발한 연도는?",
                "options": ["1592년", "1598년", "1587년", "1605년"],
                "correct_answer": "1592년"
            },
            {
                "question": "조선시대 집현전의 역할은?",
                "options": ["학문 연구", "군사 훈련", "상업 관리", "농업 지도"],
                "correct_answer": "학문 연구"
            },
            {
                "question": "다음 중 고구려의 수도가 아닌 것은?",
                "options": ["서라벌", "국내성", "평양성", "졸본성"],
                "correct_answer": "서라벌"
            },
            {
                "question": "백제를 건국한 인물은?",
                "options": ["온조왕", "주몽", "박혁거세", "김수로"],
                "correct_answer": "온조왕"
            },
            {
                "question": "신라 화랑도의 목적은?",
                "options": ["청소년 교육", "상업 발전", "농업 개선", "종교 보급"],
                "correct_answer": "청소년 교육"
            },
            {
                "question": "다음 중 조선 후기의 사건은?",
                "options": ["정조의 화성 건설", "몽골 침입", "고구려 건국", "삼국통일"],
                "correct_answer": "정조의 화성 건설"
            },
            {
                "question": "고려시대 몽골 침입은 총 몇 차례 있었나?",
                "options": ["7차례", "5차례", "3차례", "9차례"],
                "correct_answer": "7차례"
            },
            {
                "question": "조선 태조의 본명은?",
                "options": ["이성계", "이방원", "이도", "이수"],
                "correct_answer": "이성계"
            }
        ]
        
        # Select a random quiz from the pool
        selected_quiz = random.choice(quiz_pool)
        
        print(f"🎲 LLM CLIENT: Generated fallback quiz '{selected_quiz['question']}'")
        
        return selected_quiz

# Global instance
quiz_llm_client = QuizLLMClient()