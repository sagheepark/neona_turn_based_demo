"""
Tests for LLM Structured Classifier
Test Group 15: LLM-Based Structured Classification
Following TDD RED-GREEN-REFACTOR methodology
"""
import pytest
import asyncio
from typing import Dict, Any, List


class TestLLMStructuredClassifier:
    """Test Group 15: LLM-Based Structured Classification"""
    
    def test_should_classify_content_with_structured_output(self):
        """
        Test 15.1: shouldClassifyContentWithStructuredOutput  
        RED phase: LLM should classify content using structured output
        """
        # Arrange
        from services.llm_structured_classifier import LLMStructuredClassifier
        classifier = LLMStructuredClassifier()
        
        quiz_content = "다음 중 조선을 건국한 인물은? A) 이성계 B) 세종대왕 C) 이순신 D) 신사임당"
        
        # Act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                classifier.classify_content(quiz_content, character_id="seol_min_seok_quiz")
            )
        finally:
            loop.close()
        
        # Assert
        assert result.content_type == "quiz"
        assert result.confidence > 0.8
        assert "이성계" in result.detected_elements["options"]
        assert len(result.detected_elements["options"]) == 4
        assert "show_selection" in result.suggested_tools
        assert result.detected_elements["question"] is not None
        assert result.detected_elements["correct_answer"] is not None
    
    def test_should_handle_non_quiz_content_correctly(self):
        """
        Test 15.2: shouldHandleNonQuizContentCorrectly
        RED phase: Should correctly classify non-quiz content
        """
        # Arrange
        from services.llm_structured_classifier import LLMStructuredClassifier
        classifier = LLMStructuredClassifier()
        
        regular_content = "안녕하세요! 오늘 날씨가 참 좋네요. 어떤 역사 이야기가 궁금하신가요?"
        
        # Act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                classifier.classify_content(regular_content, character_id="seol_min_seok_quiz")
            )
        finally:
            loop.close()
        
        # Assert
        assert result.content_type == "text" or result.content_type == "unknown"
        assert result.confidence < 0.5  # Low confidence for non-quiz content
        assert len(result.suggested_tools) == 0  # No tools for regular text
    
    def test_should_extract_quiz_metadata_accurately(self):
        """
        Test 15.3: shouldExtractQuizMetadataAccurately
        RED phase: Should extract detailed metadata from quiz content
        """
        # Arrange
        from services.llm_structured_classifier import LLMStructuredClassifier
        classifier = LLMStructuredClassifier()
        
        complex_quiz = "다음 중 1592년 임진왜란 당시 활약한 조선 장군은? A) 이순신 B) 세종대왕 C) 신사임당 D) 김유신"
        
        # Act
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                classifier.classify_content(complex_quiz, character_id="seol_min_seok_quiz")
            )
        finally:
            loop.close()
        
        # Assert
        assert result.content_type == "quiz"
        assert result.confidence > 0.8
        assert result.detected_elements["question"].startswith("다음 중")
        assert len(result.detected_elements["options"]) == 4
        assert result.detected_elements["labels"] == ["A", "B", "C", "D"] 
        assert result.detected_elements["correct_answer"] == "이순신"  # LLM should know correct answer
        assert result.metadata.get("topic", "").lower() in ["조선시대", "임진왜란", "역사", "일반"]
        assert result.metadata.get("difficulty") in ["easy", "medium", "hard"]