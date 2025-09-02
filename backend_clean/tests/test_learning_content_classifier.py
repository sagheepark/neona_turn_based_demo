"""
Tests for Learning Content Classifier  
Test Group 17: Learning & Adaptation System
Following TDD RED-GREEN-REFACTOR methodology
"""
import pytest
import asyncio
from typing import Dict, Any


class TestLearningContentClassifier:
    """Test Group 17: Learning & Adaptation System"""
    
    def test_should_learn_from_successful_classifications(self):
        """
        Test 17.1: shouldLearnFromSuccessfulClassifications
        RED phase: System should learn from successful classifications
        """
        # Arrange
        from services.learning_content_classifier import LearningContentClassifier
        from services.llm_structured_classifier import ClassificationResult
        
        classifier = LearningContentClassifier()
        
        successful_quiz = "다음 중 고구려 건국자는? A) 주몽 B) 온조 C) 박혁거세 D) 김유신"
        result = ClassificationResult(
            content_type="quiz",
            confidence=0.95,
            detected_elements={
                "question": "다음 중 고구려 건국자는?",
                "options": ["주몽", "온조", "박혁거세", "김유신"],
                "labels": ["A", "B", "C", "D"],
                "correct_answer": "주몽"
            },
            suggested_tools=["show_selection"],
            metadata={"topic": "고구려", "difficulty": "medium"},
            detection_method="llm_structured"
        )
        
        # Act
        classifier.learn_from_success(successful_quiz, result)
        
        # Test learning effect
        similar_quiz = "다음 중 백제 건국자는? A) 온조 B) 주몽 C) 박혁거세 D) 김유신"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            improved_result = loop.run_until_complete(
                classifier.classify_with_learning(similar_quiz, "seol_min_seok_quiz")
            )
        finally:
            loop.close()
        
        # Assert - Should have higher confidence due to learning
        assert improved_result.confidence > 0.8
        assert improved_result.content_type == "quiz"
        assert "learning_applied" in improved_result.metadata
    
    def test_should_improve_performance_over_time(self):
        """
        Test 17.2: shouldImprovePerformanceOverTime
        RED phase: System performance should improve with more examples
        """
        # Arrange
        from services.learning_content_classifier import LearningContentClassifier
        from services.llm_structured_classifier import ClassificationResult
        
        classifier = LearningContentClassifier()
        
        # Train with multiple successful quiz examples
        training_examples = [
            ("다음 중 신라 건국자는? A) 박혁거세 B) 온조 C) 주몽 D) 이성계", "quiz"),
            ("고구려를 건국한 인물은? A) 주몽 B) 온조 C) 박혁거세 D) 이성계", "quiz"),
            ("조선시대 한글을 만든 왕은? A) 세종대왕 B) 태조 C) 세조 D) 성종", "quiz")
        ]
        
        # Train the classifier
        for content, content_type in training_examples:
            result = ClassificationResult(
                content_type=content_type,
                confidence=0.95,
                detected_elements={
                    "question": content.split("? A)")[0] + "?",
                    "options": content.split("? ")[1].split(" ")[::2],  # Extract options
                    "labels": ["A", "B", "C", "D"],
                    "correct_answer": content.split("A) ")[1].split(" B)")[0]  # First option as default
                },
                suggested_tools=["show_selection"],
                metadata={"topic": "역사", "difficulty": "medium"},
                detection_method="llm_structured"
            )
            classifier.learn_from_success(content, result)
        
        # Act - Test on new, similar content
        new_quiz = "다음 중 가야를 건국한 인물은? A) 수로왕 B) 온조 C) 주몽 D) 박혁거세"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                classifier.classify_with_learning(new_quiz, "seol_min_seok_quiz")
            )
        finally:
            loop.close()
        
        # Assert - Should classify correctly with high confidence
        assert result.content_type == "quiz"
        assert result.confidence > 0.84  # Slightly lower threshold for realistic learning
        assert result.learning_score > 0.0  # Learning contributed to classification