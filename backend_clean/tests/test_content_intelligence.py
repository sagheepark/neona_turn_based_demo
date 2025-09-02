"""
Tests for ContentIntelligence Engine
Following TDD RED-GREEN-REFACTOR methodology from claude.md
"""
import pytest
from services.content_intelligence import ContentIntelligence


class TestContentIntelligence:
    """Test Group 13: Intelligent Content Parsing for Quiz Detection"""
    
    def test_should_detect_korean_multiple_choice_quiz(self):
        """
        Test 13.1: shouldDetectKoreanMultipleChoiceQuiz
        RED phase: This test should fail because ContentIntelligence doesn't exist yet
        """
        # Arrange
        intelligence = ContentIntelligence()
        llm_response = """
        다음 중 3·1 운동이 일어난 연도는?
        A) 1918년
        B) 1919년  
        C) 1920년
        D) 1921년
        """
        context = {
            "character_id": "seol_min_seok_quiz",
            "conversation_phase": "quiz"
        }
        
        # Act
        quiz_data = intelligence.detect_quiz_patterns(llm_response, context)
        
        # Assert
        assert quiz_data is not None
        assert quiz_data["question"] == "다음 중 3·1 운동이 일어난 연도는?"
        assert len(quiz_data["options"]) == 4
        assert "1918년" in quiz_data["options"]
        assert "1919년" in quiz_data["options"]
        assert "1920년" in quiz_data["options"]
        assert "1921년" in quiz_data["options"]
    
    def test_should_extract_quiz_options_with_labels(self):
        """
        Test 13.2: shouldExtractQuizOptionsWithLabels  
        RED phase: Tests option extraction with A-D labels
        """
        # Arrange
        intelligence = ContentIntelligence()
        llm_response = """
        조선시대 세종대왕이 만든 문자는?
        A) 한글
        B) 한자
        C) 가나
        D) 라틴 문자
        """
        
        # Act
        quiz_data = intelligence.detect_quiz_patterns(llm_response, {})
        
        # Assert
        assert quiz_data is not None
        assert len(quiz_data["options"]) == 4
        assert quiz_data["labels"] == ["A", "B", "C", "D"]
        assert quiz_data["options"][0] == "한글"
        assert quiz_data["options"][1] == "한자"
    
    def test_should_return_none_for_non_quiz_content(self):
        """
        Test 13.3: shouldReturnNoneForNonQuizContent
        RED phase: Should not detect quiz patterns in regular conversation
        """
        # Arrange
        intelligence = ContentIntelligence()
        regular_response = """
        안녕하세요! 오늘은 날씨가 참 좋네요. 
        한국사에 대해 어떤 것이 궁금하시나요?
        """
        
        # Act
        quiz_data = intelligence.detect_quiz_patterns(regular_response, {})
        
        # Assert
        assert quiz_data is None
    
    def test_should_generate_selection_tool_from_quiz_data(self):
        """
        Test 13.4: shouldGenerateSelectionToolFromQuizData
        RED phase: Should convert quiz data into tool format
        """
        # Arrange
        intelligence = ContentIntelligence()
        quiz_data = {
            "question": "3·1 운동이 일어난 연도는?",
            "options": ["1918년", "1919년", "1920년", "1921년"],
            "labels": ["A", "B", "C", "D"],
            "correct_answer": "1919년"
        }
        
        # Act
        tool = intelligence.generate_quiz_tool(quiz_data)
        
        # Assert
        assert tool["type"] == "show_selection"
        assert tool["data"]["question"] == "3·1 운동이 일어난 연도는?"
        assert tool["data"]["items"] == ["1918년", "1919년", "1920년", "1921년"]
        assert tool["data"]["correctAnswer"] == "1919년"
        assert "metadata" in tool["data"]
        assert tool["data"]["metadata"]["labels"] == ["A", "B", "C", "D"]