"""
Educational Quiz Flow Service
Implements proper pedagogical quiz logic with educational feedback

Quiz Logic:
- Wrong answer: (1) Review with hints, (2) Same question again  
- Right answer: (1) Educational reflection, (2) Next question
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
from services.character_service import character_service


class EducationalQuizFlow:
    """Educational quiz flow with proper pedagogical feedback"""
    
    def __init__(self):
        # Quiz question bank for 조선시대
        self.question_bank = {
            "조선시대": [
                {
                    "question": "다음 중 세종대왕의 업적은?",
                    "options": ["A) 한글 창제", "B) 불교 장려", "C) 몽골 침입", "D) 일제강점"],
                    "correct_answer": "A) 한글 창제",
                    "topic": "조선시대",
                    "educational_context": {
                        "why_correct": "세종대왕은 1443년 한글(훈민정음)을 창제하여 백성들이 쉽게 글을 배울 수 있도록 했습니다.",
                        "why_wrong": {
                            "B": "불교 장려는 고려시대의 특징입니다.",
                            "C": "몽골 침입은 고려시대 사건입니다.", 
                            "D": "일제강점은 1910-1945년 시기입니다."
                        },
                        "hint": "세종대왕 하면 가장 먼저 떠오르는 문화적 업적을 생각해보세요.",
                        "deeper_learning": "한글 창제는 단순한 문자 개발이 아니라 백성을 위한 민본사상의 실현이었습니다.",
                        "historical_significance": "이로 인해 조선의 문화와 교육이 크게 발전할 수 있었습니다."
                    }
                },
                {
                    "question": "조선시대 과거제도에서 가장 높은 시험은?",
                    "options": ["A) 생원시", "B) 진사시", "C) 문과", "D) 무과"],
                    "correct_answer": "C) 문과",
                    "topic": "조선시대",
                    "educational_context": {
                        "why_correct": "문과는 조선시대 최고의 관리 선발 시험으로 정승까지 오를 수 있었습니다.",
                        "why_wrong": {
                            "A": "생원시는 성균관 입학을 위한 예비시험입니다.",
                            "B": "진사시도 성균관 입학을 위한 예비시험입니다.",
                            "D": "무과는 무관을 선발하는 시험으로 문과보다 지위가 낮았습니다."
                        },
                        "hint": "조선시대 최고 관리가 되기 위한 시험을 생각해보세요.",
                        "deeper_learning": "과거제도는 능력에 따른 관리 선발로 조선의 안정적 통치를 가능하게 했습니다.",
                        "historical_significance": "이 제도로 문치주의 전통이 확립되었습니다."
                    }
                },
                {
                    "question": "임진왜란이 일어난 연도는?",
                    "options": ["A) 1588년", "B) 1592년", "C) 1597년", "D) 1598년"],
                    "correct_answer": "B) 1592년",
                    "topic": "조선시대",
                    "educational_context": {
                        "why_correct": "임진왜란은 1592년(임진년)에 시작되어 7년간 지속된 전쟁입니다.",
                        "why_wrong": {
                            "A": "1588년은 임진왜란 이전입니다.",
                            "C": "1597년은 정유재란이 시작된 해입니다.",
                            "D": "1598년은 도요토미 히데요시가 죽은 해입니다."
                        },
                        "hint": "임진왜란의 '임진'이 연도를 나타내는 간지입니다.",
                        "deeper_learning": "임진왜란은 조선의 국방력 한계를 보여주었지만 의병활동과 명군 지원으로 극복했습니다.",
                        "historical_significance": "이 전쟁을 통해 조선은 국방 체제를 정비하고 실학사상이 발달하게 되었습니다."
                    }
                }
            ]
        }
        
    async def process_answer(self, question_data: Dict[str, Any], user_answer: str, character_id: str) -> Dict[str, Any]:
        """
        Process user's quiz answer and return appropriate educational response
        """
        is_correct = user_answer.strip() == question_data["correct_answer"].strip()
        
        if is_correct:
            return await self._handle_correct_answer(question_data, user_answer, character_id)
        else:
            return await self._handle_wrong_answer(question_data, user_answer, character_id)
    
    async def _handle_correct_answer(self, question_data: Dict[str, Any], user_answer: str, character_id: str) -> Dict[str, Any]:
        """
        Handle correct answer: educational reflection + next question
        """
        educational_context = question_data["educational_context"]
        
        # Generate educational feedback with character voice
        feedback = await self.generate_character_feedback(
            character_id=character_id,
            is_correct=True,
            topic=question_data["topic"],
            educational_content=f"{educational_context['why_correct']} {educational_context.get('deeper_learning', '')} {educational_context.get('historical_significance', '')}"
        )
        
        # Generate next question
        next_question = await self.generate_next_question(
            question_data["topic"], 
            {"previous_topics": [question_data["question"]]}
        )
        
        return {
            "answer_correct": True,
            "feedback": feedback,
            "action": "next_question",
            "next_question": next_question,
            "educational_value": "high"
        }
    
    async def _handle_wrong_answer(self, question_data: Dict[str, Any], user_answer: str, character_id: str) -> Dict[str, Any]:
        """
        Handle wrong answer: hint + explanation + same question retry
        """
        educational_context = question_data["educational_context"]
        
        # Get why this specific answer is wrong
        wrong_explanation = ""
        for option_key, explanation in educational_context["why_wrong"].items():
            if option_key in user_answer:
                wrong_explanation = explanation
                break
        
        # Generate educational feedback with hint
        educational_content = f"아쉽게도 틀렸습니다. {wrong_explanation} {educational_context['hint']} 정답은 {question_data['correct_answer']}입니다. {educational_context['why_correct']}"
        
        feedback = await self.generate_character_feedback(
            character_id=character_id,
            is_correct=False,
            topic=question_data["topic"],
            educational_content=educational_content
        )
        
        return {
            "answer_correct": False,
            "feedback": feedback,
            "action": "retry_question",
            "next_question": question_data,  # Same question again
            "hint": educational_context["hint"],
            "educational_value": "medium"
        }
    
    async def generate_next_question(self, topic: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate next question maintaining educational continuity
        """
        if topic not in self.question_bank:
            # Fallback question if topic not found
            return self.question_bank["조선시대"][0]
        
        available_questions = self.question_bank[topic]
        
        # Filter out previously asked questions
        previous_topics = session_context.get("previous_topics", [])
        unused_questions = [q for q in available_questions if q["question"] not in previous_topics]
        
        if not unused_questions:
            # If all questions used, reset and start over
            unused_questions = available_questions
        
        # Return random question from unused pool
        return random.choice(unused_questions)
    
    async def generate_character_feedback(self, character_id: str, is_correct: bool, topic: str, educational_content: str) -> str:
        """
        Generate character-specific educational feedback
        """
        if character_id == "seol_min_seok_quiz":
            if is_correct:
                # 설민석's encouraging style for correct answers
                feedback_templates = [
                    f"정답입니다! 정말 훌륭해요! {educational_content} 여러분이 이렇게 역사를 잘 알고 계시니 정말 기쁩니다!",
                    f"맞습니다! 훌륭한 선택이에요! {educational_content} 역사 공부가 정말 잘 되고 있는 것 같아요!",
                    f"바로 그거예요! 정말 좋습니다! {educational_content} 이런 식으로 계속 공부하면 역사 박사가 될 수 있겠어요!"
                ]
            else:
                # DISABLED TEMPLATE FALLBACKS - MUST USE REAL LLM 
                raise Exception(f"Educational quiz template system disabled - this indicates the system is using hardcoded Korean templates instead of the LLM. The LLM should be generating responses, not fallback templates. Character: {character_id}, Correct: {is_correct}")
            
            return random.choice(feedback_templates)
        else:
            # Generic educational feedback for other characters
            if is_correct:
                return f"정답입니다. {educational_content}"
            else:
                return f"틀렸습니다. {educational_content}"