#!/usr/bin/env python3
"""
Test: Educational Quiz Flow Logic
RED phase: Quiz should provide educational feedback and proper question flow
Purpose: Implement proper educational quiz logic with hints and reflection

Quiz Logic Requirements:
- Wrong answer: (1) Review with hints, (2) Same question again  
- Right answer: (1) Educational reflection, (2) Next question
"""

import pytest
import asyncio
from typing import Dict, List, Any


class TestEducationalQuizFlow:
    """Test educational quiz flow with proper pedagogical logic"""
    
    def test_should_handle_wrong_answer_with_hint_and_retry(self):
        """
        Test that wrong answers get educational hints and question retry
        """
        try:
            from services.educational_quiz_flow import EducationalQuizFlow
            
            quiz_flow = EducationalQuizFlow()
            
            # Arrange - Wrong answer scenario
            question_data = {
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
                    "hint": "세종대왕 하면 가장 먼저 떠오르는 문화적 업적을 생각해보세요."
                }
            }
            
            user_wrong_answer = "B) 불교 장려"
            
            # Act - Process wrong answer
            result = asyncio.run(
                quiz_flow.process_answer(question_data, user_wrong_answer, character_id="seol_min_seok_quiz")
            )
            
        except ImportError:
            assert False, "EducationalQuizFlow should be implemented"
        except Exception as e:
            assert False, f"Wrong answer processing failed: {e}"
        
        # Assert - Wrong answer should provide hint and retry
        assert result["answer_correct"] == False, "Should identify wrong answer"
        assert "hint" in result["feedback"], "Should provide educational hint"
        assert "불교 장려는 고려시대" in result["feedback"], "Should explain why answer is wrong"
        assert result["action"] == "retry_question", "Should retry same question"
        assert result["next_question"] == question_data, "Should provide same question again"
        
        # Should include educational reflection
        assert "세종대왕" in result["feedback"], "Should mention the correct historical figure"
        assert len(result["feedback"]) > 100, "Should provide substantial educational content"
        
        print(f"✅ Wrong answer handling: {result['action']} with educational feedback")

    def test_should_handle_right_answer_with_education_and_progression(self):
        """
        Test that right answers get educational reflection and next question
        """
        try:
            from services.educational_quiz_flow import EducationalQuizFlow
            
            quiz_flow = EducationalQuizFlow()
            
            # Arrange - Right answer scenario
            question_data = {
                "question": "다음 중 세종대왕의 업적은?",
                "options": ["A) 한글 창제", "B) 불교 장려", "C) 몽골 침입", "D) 일제강점"],
                "correct_answer": "A) 한글 창제",
                "topic": "조선시대",
                "educational_context": {
                    "why_correct": "세종대왕은 1443년 한글(훈민정음)을 창제하여 백성들이 쉽게 글을 배울 수 있도록 했습니다.",
                    "deeper_learning": "한글 창제는 단순한 문자 개발이 아니라 백성을 위한 민본사상의 실현이었습니다.",
                    "historical_significance": "이로 인해 조선의 문화와 교육이 크게 발전할 수 있었습니다."
                }
            }
            
            user_right_answer = "A) 한글 창제"
            
            # Act - Process right answer
            result = asyncio.run(
                quiz_flow.process_answer(question_data, user_right_answer, character_id="seol_min_seok_quiz")
            )
            
        except Exception as e:
            assert False, f"Right answer processing failed: {e}"
        
        # Assert - Right answer should provide education and next question
        assert result["answer_correct"] == True, "Should identify correct answer"
        assert "민본사상" in result["feedback"] or "백성" in result["feedback"], "Should provide deeper educational context"
        assert result["action"] == "next_question", "Should progress to next question"
        assert "next_question" in result, "Should provide new question"
        assert result["next_question"] != question_data, "Should be different question"
        
        # Should include educational reflection about historical significance
        assert "한글" in result["feedback"], "Should discuss the answer topic"
        assert len(result["feedback"]) > 150, "Should provide substantial educational reflection"
        
        # Next question should be related but different
        next_q = result["next_question"]
        assert "question" in next_q, "Next question should have proper structure"
        assert "조선" in next_q["question"] or "세종" in next_q["question"], "Should be topically related"
        
        print(f"✅ Right answer handling: {result['action']} with educational reflection")

    def test_should_maintain_educational_continuity(self):
        """
        Test that quiz maintains educational continuity across questions
        """
        try:
            from services.educational_quiz_flow import EducationalQuizFlow
            
            quiz_flow = EducationalQuizFlow()
            
            # Test sequence of questions maintains educational flow
            session_context = {
                "previous_topics": ["한글 창제"],
                "difficulty_level": "intermediate",
                "learning_progress": {"조선시대": 0.3}
            }
            
            # Generate next question based on context
            next_question = asyncio.run(
                quiz_flow.generate_next_question("조선시대", session_context)
            )
            
        except Exception as e:
            assert False, f"Educational continuity test failed: {e}"
        
        # Assert - Should maintain educational progression
        assert "question" in next_question, "Should generate valid question structure"
        assert "educational_context" in next_question, "Should include educational context"
        assert len(next_question["options"]) == 4, "Should have 4 options"
        
        # Should build on previous learning
        assert next_question["topic"] == "조선시대", "Should maintain topic continuity"
        
        print(f"✅ Educational continuity maintained: {next_question['question'][:50]}...")

    def test_should_integrate_with_seolminseok_character(self):
        """
        Test that quiz flow integrates with 설민석 character personality
        """
        try:
            from services.educational_quiz_flow import EducationalQuizFlow
            
            quiz_flow = EducationalQuizFlow()
            
            # Test character-specific feedback generation
            feedback = asyncio.run(
                quiz_flow.generate_character_feedback(
                    character_id="seol_min_seok_quiz",
                    is_correct=True,
                    topic="한글 창제",
                    educational_content="세종대왕의 민본사상 실현"
                )
            )
            
        except Exception as e:
            assert False, f"Character integration test failed: {e}"
        
        # Assert - Should have 설민석 character voice
        assert len(feedback) > 50, "Should provide substantial feedback"
        assert "여러분" in feedback or "정말" in feedback, "Should use 설민석's speaking style"
        
        # Should be educational and encouraging
        assert any(word in feedback for word in ["훌륭", "좋", "잘", "맞"]), "Should be encouraging"
        
        print(f"✅ Character integration working: 설민석 voice in feedback")


if __name__ == "__main__":
    # Run the tests
    test_instance = TestEducationalQuizFlow()
    
    try:
        print("🔴 Running Educational Quiz Flow Tests (RED Phase)")
        print("-" * 60)
        
        # Test 1: Wrong answer handling
        test_instance.test_should_handle_wrong_answer_with_hint_and_retry()
        print("✅ Test 1 passed: Wrong answer handling with hints")
        
        # Test 2: Right answer handling  
        test_instance.test_should_handle_right_answer_with_education_and_progression()
        print("✅ Test 2 passed: Right answer handling with education")
        
        # Test 3: Educational continuity
        test_instance.test_should_maintain_educational_continuity()
        print("✅ Test 3 passed: Educational continuity maintained")
        
        # Test 4: Character integration
        test_instance.test_should_integrate_with_seolminseok_character()
        print("✅ Test 4 passed: Character integration working")
        
        print("-" * 60)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - EducationalQuizFlow not implemented yet")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")