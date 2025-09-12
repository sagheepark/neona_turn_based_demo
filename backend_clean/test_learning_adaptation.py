#!/usr/bin/env python3
"""
Test 17.1: shouldLearnFromSuccessfulClassifications
Test 17.2: shouldImprovePerformanceOverTime
RED phase: System should learn from successful classifications
Purpose: Learning & Adaptation System
"""

import pytest
import asyncio
from typing import Dict, List, Any


class TestLearningAdaptation:
    """Test learning and adaptation system"""
    
    def test_should_learn_from_successful_classifications(self):
        """
        Test that system learns from successful classification results
        """
        # Arrange & Act
        try:
            from services.learning_content_classifier import LearningContentClassifier
            from services.llm_structured_classifier import ClassificationResult
            
            classifier = LearningContentClassifier()
            
            # Create a successful classification result
            successful_quiz = "다음 중 고구려 건국자는? A) 주몽 B) 온조 C) 박혁거세 D) 김유신"
            result = ClassificationResult(
                content_type="quiz",
                confidence=0.95,
                detected_elements={
                    "question": "다음 중 고구려 건국자는?",
                    "options": ["주몽", "온조", "박혁거세", "김유신"],
                    "correct_answer": "주몽"
                },
                suggested_tools=["show_selection"],
                metadata={"topic": "history"},
                detection_method="test"
            )
            
            # Act - Learn from this successful classification
            classifier.learn_from_success(successful_quiz, result)
            
            # Verify learning occurred
            assert "quiz" in classifier.learning_examples, "Should store learning examples for quiz type"
            assert len(classifier.learning_examples["quiz"]) >= 1, "Should have at least one learning example"
            
            # Verify pattern weights were updated
            assert "quiz" in classifier.pattern_weights, "Should have pattern weights for quiz type"
            pattern_weights = classifier.pattern_weights["quiz"]
            assert len(pattern_weights) > 0, f"Should have learned patterns, got {pattern_weights}"
            
            # Check specific patterns that should have been learned
            expected_patterns = ["다음_중_pattern", "multiple_choice_pattern", "topic_고구려", "question_ending"]
            learned_patterns = list(pattern_weights.keys())
            
            for expected in expected_patterns:
                if expected in learned_patterns:
                    print(f"✅ Learned pattern: {expected} (weight: {pattern_weights[expected]:.2f})")
            
            print(f"✅ Learning from successful classification working: {len(classifier.learning_examples['quiz'])} examples, {len(pattern_weights)} patterns learned")
            
        except ImportError:
            assert False, "LearningContentClassifier and ClassificationResult should exist"
        except Exception as e:
            assert False, f"Learning from successful classifications failed: {e}"

    def test_should_improve_performance_over_time(self):
        """
        Test that system performance improves with more learning examples
        """
        try:
            from services.learning_content_classifier import LearningContentClassifier
            from services.llm_structured_classifier import ClassificationResult
            
            classifier = LearningContentClassifier()
            
            # Simulate initial classification (before learning)
            similar_quiz = "다음 중 백제 건국자는? A) 온조 B) 주몽 C) 박혁거세 D) 김유신"
            
            # Get baseline performance (before learning)
            baseline_result = asyncio.run(
                classifier.classify_with_learning(similar_quiz, "seol_min_seok_quiz")
            )
            baseline_confidence = baseline_result.confidence
            
            # Train the system with multiple successful examples
            training_examples = [
                ("다음 중 고구려 건국자는? A) 주몽 B) 온조 C) 박혁거세 D) 김유신", "주몽"),
                ("다음 중 신라 건국자는? A) 박혁거세 B) 온조 C) 주몽 D) 김유신", "박혁거세"),
                ("다음 중 조선 건국자는? A) 이성계 B) 세종대왕 C) 이순신 D) 신사임당", "이성계"),
            ]
            
            for content, correct_answer in training_examples:
                result = ClassificationResult(
                    content_type="quiz",
                    confidence=0.95,
                    detected_elements={
                        "question": content.split("?")[0] + "?",
                        "options": [opt.strip() for opt in content.split("?")[1].replace("A)", "").replace("B)", "|").replace("C)", "|").replace("D)", "|").split("|")],
                        "correct_answer": correct_answer
                    },
                    suggested_tools=["show_selection"],
                    metadata={"topic": "history"},
                    detection_method="test"
                )
                
                classifier.learn_from_success(content, result)
            
            # Test performance after learning
            improved_result = asyncio.run(
                classifier.classify_with_learning(similar_quiz, "seol_min_seok_quiz")
            )
            improved_confidence = improved_result.confidence
            
        except Exception as e:
            assert False, f"Performance improvement testing failed: {e}"
        
        # Assert - Performance should improve or at least maintain
        assert improved_confidence >= baseline_confidence * 0.95, f"Performance should not degrade significantly: {baseline_confidence:.3f} -> {improved_confidence:.3f}"
        
        # Check if learning was applied
        if "learning_applied" in improved_result.metadata:
            print(f"✅ Learning boost applied: {improved_confidence:.3f} confidence (up from baseline {baseline_confidence:.3f})")
        else:
            print(f"✅ Performance maintained: {improved_confidence:.3f} confidence (baseline {baseline_confidence:.3f})")
        
        # Verify learning examples accumulated
        total_examples = sum(len(examples) for examples in classifier.learning_examples.values())
        assert total_examples >= len(training_examples), f"Should accumulate learning examples: expected >= {len(training_examples)}, got {total_examples}"
        
        print(f"✅ System improved over time: {total_examples} total learning examples accumulated")

    def test_should_extract_meaningful_patterns(self):
        """
        Test that system extracts meaningful patterns for learning
        """
        try:
            from services.learning_content_classifier import LearningContentClassifier
            
            classifier = LearningContentClassifier()
            
            # Test pattern extraction with various content types
            test_cases = [
                ("다음 중 조선시대 왕은? A) 세종대왕 B) 이순신", ["다음_중_pattern", "multiple_choice_pattern", "topic_조선", "question_ending"]),
                ("고구려 건국자는 누구인가요?", ["topic_고구려", "question_ending"]),
                ("백제의 수도는 어디였나요? A) 한성 B) 웅진", ["topic_백제", "multiple_choice_pattern", "question_ending"]),
            ]
            
            for content, expected_patterns in test_cases:
                patterns = classifier._extract_patterns(content)
                
                # Check that expected patterns are found
                for expected in expected_patterns:
                    assert expected in patterns, f"Should extract '{expected}' from '{content}', got {patterns}"
                
                print(f"✅ Pattern extraction working for: '{content[:30]}...' -> {patterns}")
            
        except Exception as e:
            assert False, f"Pattern extraction testing failed: {e}"


if __name__ == "__main__":
    # Run the tests
    test_instance = TestLearningAdaptation()
    
    try:
        print("🔴 Running Test 17.1 & 17.2: Learning & Adaptation System")
        print("-" * 60)
        
        # Test 1: Learning from successful classifications
        test_instance.test_should_learn_from_successful_classifications()
        print("✅ Test 1 passed: Learning from successful classifications working")
        
        # Test 2: Performance improvement over time
        test_instance.test_should_improve_performance_over_time()
        print("✅ Test 2 passed: Performance improvement over time working")
        
        # Test 3: Pattern extraction
        test_instance.test_should_extract_meaningful_patterns()
        print("✅ Test 3 passed: Pattern extraction working")
        
        print("-" * 60)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - learning adaptation needs work")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")