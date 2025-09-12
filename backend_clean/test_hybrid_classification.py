#!/usr/bin/env python3
"""
Test 16.1: shouldFusePatternAndLLMResults
Test 16.2: shouldResolveDisagreementBetweenMethods
RED phase: System should combine pattern and LLM classification results
Purpose: Confidence-Scored Hybrid System
"""

import pytest
from typing import Dict, List, Any


class TestHybridClassification:
    """Test hybrid content classification system"""
    
    def test_should_fuse_pattern_and_llm_results(self):
        """
        Test that system properly fuses pattern and LLM classification results
        """
        # Arrange & Act
        try:
            from services.hybrid_content_classifier import HybridContentClassifier
            from services.llm_structured_classifier import ClassificationResult
            
            classifier = HybridContentClassifier()
            
            # Pattern result (high confidence)
            pattern_result = ClassificationResult(
                content_type="quiz",
                confidence=0.9,
                detected_elements={"question": "조선 건국자는?", "options": ["이성계", "세종대왕"]},
                suggested_tools=["show_selection"],
                metadata={"pattern_matched": True},
                detection_method="pattern"
            )
            
            # LLM result (agrees with pattern)
            llm_result = ClassificationResult(
                content_type="quiz", 
                confidence=0.85,
                detected_elements={"question": "조선 건국자는?", "options": ["이성계", "세종대왕"]},
                suggested_tools=["show_selection"],
                metadata={"llm_analyzed": True},
                detection_method="llm"
            )
            
            # Act - Fuse the results
            fused_result = classifier.fuse_results(pattern_result, llm_result)
            
        except ImportError:
            assert False, "HybridContentClassifier and ClassificationResult should exist"
        except Exception as e:
            assert False, f"Result fusion failed: {e}"
        
        # Assert - Should boost confidence when methods agree
        assert fused_result.content_type == "quiz", f"Should maintain quiz type, got {fused_result.content_type}"
        assert fused_result.confidence > llm_result.confidence, f"Should boost confidence from {llm_result.confidence} to {fused_result.confidence}"
        assert fused_result.confidence > pattern_result.confidence, f"Should boost confidence above pattern confidence {pattern_result.confidence}"
        assert fused_result.detection_method == "hybrid", f"Should use hybrid method, got {fused_result.detection_method}"
        assert fused_result.confidence <= 1.0, "Confidence should not exceed 1.0"
        
        # Should merge metadata
        assert "pattern_matched" in fused_result.metadata, "Should include pattern metadata"
        assert "llm_analyzed" in fused_result.metadata, "Should include LLM metadata"
        
        print(f"✅ Pattern and LLM fusion working: {fused_result.confidence:.3f} confidence (boosted from {max(pattern_result.confidence, llm_result.confidence):.3f})")

    def test_should_resolve_disagreement_between_methods(self):
        """
        Test that system properly resolves disagreements between methods
        """
        try:
            from services.hybrid_content_classifier import HybridContentClassifier
            from services.llm_structured_classifier import ClassificationResult
            
            classifier = HybridContentClassifier()
            
            # Pattern result thinks it's a quiz (high confidence)
            pattern_result = ClassificationResult(
                content_type="quiz",
                confidence=0.9,
                detected_elements={"question": "What is your favorite color?", "options": ["Red", "Blue"]},
                suggested_tools=["show_selection"],
                metadata={"pattern_matched": True},
                detection_method="pattern"
            )
            
            # LLM result thinks it's just text (lower confidence)
            llm_result = ClassificationResult(
                content_type="text", 
                confidence=0.7,
                detected_elements={"message": "Casual question about preferences"},
                suggested_tools=[],
                metadata={"llm_analyzed": True},
                detection_method="llm"
            )
            
            # Act - Resolve disagreement
            resolved_result = classifier.fuse_results(pattern_result, llm_result)
            
        except Exception as e:
            assert False, f"Disagreement resolution failed: {e}"
        
        # Assert - Should choose higher confidence result (pattern in this case)
        assert resolved_result.content_type == "quiz", f"Should choose pattern result (quiz), got {resolved_result.content_type}"
        assert resolved_result.confidence == pattern_result.confidence, f"Should use pattern confidence {pattern_result.confidence}, got {resolved_result.confidence}"
        assert "pattern_preferred" in resolved_result.detection_method, f"Should indicate pattern was preferred, got {resolved_result.detection_method}"
        
        print(f"✅ Disagreement resolution working: chose {resolved_result.content_type} with {resolved_result.confidence:.3f} confidence")

    def test_should_handle_llm_only_classification(self):
        """
        Test that system handles cases where only LLM classification is available
        """
        try:
            from services.hybrid_content_classifier import HybridContentClassifier
            from services.llm_structured_classifier import ClassificationResult
            
            classifier = HybridContentClassifier()
            
            # Only LLM result available (no pattern match)
            llm_result = ClassificationResult(
                content_type="quiz", 
                confidence=0.85,
                detected_elements={"question": "복잡한 한국어 문제", "options": ["선택지1", "선택지2"]},
                suggested_tools=["show_selection"],
                metadata={"llm_analyzed": True},
                detection_method="llm"
            )
            
            # Act - Fuse with no pattern result
            result = classifier.fuse_results(None, llm_result)
            
        except Exception as e:
            assert False, f"LLM-only classification failed: {e}"
        
        # Assert - Should adjust confidence slightly down for lack of confirmation
        assert result.content_type == "quiz", f"Should maintain quiz type, got {result.content_type}"
        assert result.confidence < llm_result.confidence, f"Should reduce confidence from {llm_result.confidence} to {result.confidence}"
        assert result.detection_method == "llm_only", f"Should indicate LLM only, got {result.detection_method}"
        assert result.confidence >= 0.0, "Confidence should not go below 0"
        
        print(f"✅ LLM-only classification working: {result.confidence:.3f} confidence (adjusted from {llm_result.confidence:.3f})")

    def test_should_calculate_confidence_scores_correctly(self):
        """
        Test that confidence score calculation works properly
        """
        try:
            from services.hybrid_content_classifier import HybridContentClassifier
            
            classifier = HybridContentClassifier()
            
            # Test agreement boost
            agreement_score = classifier.calculate_confidence_score(0.8, 0.85, agreement=True)
            assert agreement_score > 0.85, f"Agreement should boost confidence above 0.85, got {agreement_score}"
            assert agreement_score <= 1.0, f"Confidence should not exceed 1.0, got {agreement_score}"
            
            # Test disagreement penalty
            disagreement_score = classifier.calculate_confidence_score(0.9, 0.7, agreement=False)
            assert disagreement_score <= 0.9, f"Disagreement should not exceed max confidence, got {disagreement_score}"
            assert disagreement_score >= 0.0, f"Confidence should not go below 0, got {disagreement_score}"
            
            # Test LLM-only adjustment
            llm_only_score = classifier.calculate_confidence_score(None, 0.8, agreement=False)
            assert llm_only_score < 0.8, f"LLM-only should reduce confidence below 0.8, got {llm_only_score}"
            assert llm_only_score >= 0.0, f"Confidence should not go below 0, got {llm_only_score}"
            
            print(f"✅ Confidence scoring working: agreement={agreement_score:.3f}, disagreement={disagreement_score:.3f}, llm_only={llm_only_score:.3f}")
            
        except Exception as e:
            assert False, f"Confidence score calculation failed: {e}"


if __name__ == "__main__":
    # Run the tests
    test_instance = TestHybridClassification()
    
    try:
        print("🔴 Running Test 16.1 & 16.2: Hybrid Classification System")
        print("-" * 60)
        
        # Test 1: Fusion when methods agree
        test_instance.test_should_fuse_pattern_and_llm_results()
        print("✅ Test 1 passed: Pattern and LLM fusion working")
        
        # Test 2: Resolution when methods disagree
        test_instance.test_should_resolve_disagreement_between_methods()
        print("✅ Test 2 passed: Disagreement resolution working")
        
        # Test 3: LLM-only handling
        test_instance.test_should_handle_llm_only_classification()
        print("✅ Test 3 passed: LLM-only classification working")
        
        # Test 4: Confidence calculation
        test_instance.test_should_calculate_confidence_scores_correctly()
        print("✅ Test 4 passed: Confidence scoring working")
        
        print("-" * 60)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - hybrid classification needs work")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")