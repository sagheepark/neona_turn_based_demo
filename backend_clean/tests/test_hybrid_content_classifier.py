"""
Tests for Hybrid Content Classifier  
Test Group 16: Confidence-Scored Hybrid System
Following TDD RED-GREEN-REFACTOR methodology
"""
import pytest
import asyncio
from typing import Dict, Any


class TestHybridContentClassifier:
    """Test Group 16: Confidence-Scored Hybrid System"""
    
    def test_should_fuse_pattern_and_llm_results(self):
        """
        Test 16.1: shouldFusePatternAndLLMResults
        RED phase: System should combine pattern and LLM classification results
        """
        # Arrange
        from services.hybrid_content_classifier import HybridContentClassifier
        from services.llm_structured_classifier import ClassificationResult
        
        classifier = HybridContentClassifier()
        
        # Pattern result (high confidence)
        pattern_result = ClassificationResult(
            content_type="quiz",
            confidence=0.9,
            detected_elements={
                "question": "조선 건국자는?", 
                "options": ["이성계", "세종대왕"],
                "labels": ["A", "B"],
                "correct_answer": "이성계"
            },
            suggested_tools=["show_selection"],
            metadata={"topic": "조선시대", "difficulty": "medium"},
            detection_method="pattern"
        )
        
        # LLM result (agrees with pattern)
        llm_result = ClassificationResult(
            content_type="quiz", 
            confidence=0.85,
            detected_elements={
                "question": "조선 건국자는?", 
                "options": ["이성계", "세종대왕"],
                "labels": ["A", "B"],
                "correct_answer": "이성계"
            },
            suggested_tools=["show_selection"],
            metadata={"topic": "조선시대", "difficulty": "medium"},
            detection_method="llm"
        )
        
        # Act
        fused_result = classifier.fuse_results(pattern_result, llm_result)
        
        # Assert - Confidence should be boosted when both agree
        assert fused_result.confidence > 0.9
        assert fused_result.content_type == "quiz"
        assert fused_result.detection_method == "hybrid"
        assert fused_result.detected_elements["correct_answer"] == "이성계"
    
    def test_should_resolve_disagreement_between_methods(self):
        """
        Test 16.2: shouldResolveDisagreementBetweenMethods
        RED phase: Handle cases where pattern and LLM disagree
        """
        # Arrange
        from services.hybrid_content_classifier import HybridContentClassifier
        from services.llm_structured_classifier import ClassificationResult
        
        classifier = HybridContentClassifier()
        
        # Pattern thinks it's a quiz (lower confidence)
        pattern_result = ClassificationResult(
            content_type="quiz",
            confidence=0.6,
            detected_elements={"question": "test"},
            suggested_tools=["show_selection"],
            metadata={},
            detection_method="pattern"
        )
        
        # LLM thinks it's regular text (higher confidence)  
        llm_result = ClassificationResult(
            content_type="text",
            confidence=0.85,
            detected_elements={},
            suggested_tools=[],
            metadata={"topic": "conversation"},
            detection_method="llm"
        )
        
        # Act
        fused_result = classifier.fuse_results(pattern_result, llm_result)
        
        # Assert - Should choose higher confidence result
        assert fused_result.content_type == "text"
        assert fused_result.confidence == 0.85
        assert fused_result.detection_method == "llm_preferred"
    
    def test_should_boost_confidence_when_methods_agree(self):
        """
        Test 16.3: shouldBoostConfidenceWhenMethodsAgree
        RED phase: Confidence boost when both methods agree on classification
        """
        # Arrange
        from services.hybrid_content_classifier import HybridContentClassifier
        from services.llm_structured_classifier import ClassificationResult
        
        classifier = HybridContentClassifier()
        
        # Both methods agree but with moderate confidence
        pattern_result = ClassificationResult(
            content_type="quiz",
            confidence=0.75,
            detected_elements={"question": "test quiz"},
            suggested_tools=["show_selection"],
            metadata={},
            detection_method="pattern"
        )
        
        llm_result = ClassificationResult(
            content_type="quiz",
            confidence=0.8,
            detected_elements={"question": "test quiz"},
            suggested_tools=["show_selection"],
            metadata={},
            detection_method="llm"
        )
        
        # Act
        fused_result = classifier.fuse_results(pattern_result, llm_result)
        
        # Assert - Final confidence should be higher than either individual method
        assert fused_result.confidence > max(pattern_result.confidence, llm_result.confidence)
        assert fused_result.confidence > 0.85  # Significant boost
        assert fused_result.detection_method == "hybrid"
        assert fused_result.content_type == "quiz"