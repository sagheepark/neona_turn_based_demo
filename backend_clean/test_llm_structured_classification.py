#!/usr/bin/env python3
"""
Test 15.1: shouldClassifyContentWithStructuredOutput
Test 15.2: shouldHandleNonQuizContentCorrectly
RED phase: LLM should classify content using structured output
Purpose: LLM-Based Structured Classification System
"""

import pytest
import asyncio
from typing import Dict, List, Any


class TestLLMStructuredClassification:
    """Test LLM-based structured content classification"""
    
    def test_should_classify_content_with_structured_output(self):
        """
        Test that LLM can classify quiz content with structured output
        """
        # Arrange & Act
        try:
            from services.llm_structured_classifier import LLMStructuredClassifier
            classifier = LLMStructuredClassifier()
            
            quiz_content = "다음 중 조선을 건국한 인물은? A) 이성계 B) 세종대왕 C) 이순신 D) 신사임당"
            
            # Since the method is async, we need to run it in an event loop
            result = asyncio.run(
                classifier.classify_content(quiz_content, character_id="seol_min_seok_quiz")
            )
            
        except ImportError:
            # Expected to fail initially
            assert False, "LLMStructuredClassifier service should exist"
        except Exception as e:
            # Expected to fail during RED phase
            assert False, f"LLM structured classification failed: {e}"
        
        # Assert - Should have proper structured output
        assert result.content_type == "quiz", f"Should classify as quiz, got {result.content_type}"
        assert result.confidence > 0.8, f"Should have high confidence, got {result.confidence}"
        assert "detected_elements" in result.__dict__, "Should have detected_elements"
        assert "options" in result.detected_elements, "Should detect quiz options"
        assert "이성계" in str(result.detected_elements["options"]), "Should detect '이성계' as an option"
        assert len(result.detected_elements["options"]) == 4, f"Should detect 4 options, got {len(result.detected_elements['options'])}"
        assert "show_selection" in result.suggested_tools, "Should suggest show_selection tool"
        
        print(f"✅ LLM structured classification working: {result.content_type} with {result.confidence:.2f} confidence")

    def test_should_handle_non_quiz_content_correctly(self):
        """
        Test that LLM correctly classifies non-quiz content
        """
        try:
            from services.llm_structured_classifier import LLMStructuredClassifier
            classifier = LLMStructuredClassifier()
            
            # Test with plain text content (not a quiz)
            plain_text = "안녕하세요! 오늘 날씨가 정말 좋네요. 어떻게 지내고 계신가요?"
            
            result = asyncio.run(
                classifier.classify_content(plain_text, character_id="seol_min_seok_quiz")
            )
            
        except ImportError:
            assert False, "LLMStructuredClassifier should be implemented"
        except Exception as e:
            assert False, f"Non-quiz content classification failed: {e}"
        
        # Assert - Should not classify as quiz
        assert result.content_type != "quiz", f"Should not classify plain text as quiz, got {result.content_type}"
        assert result.confidence >= 0.0, "Should have valid confidence score"
        assert result.suggested_tools != ["show_selection"] or len(result.suggested_tools) == 0, "Should not suggest quiz tools for plain text"
        
        print(f"✅ Non-quiz content handled correctly: {result.content_type} with {result.confidence:.2f} confidence")

    def test_should_extract_quiz_elements_properly(self):
        """
        Test that quiz elements are extracted correctly from Korean content
        """
        try:
            from services.llm_structured_classifier import LLMStructuredClassifier
            classifier = LLMStructuredClassifier()
            
            # Test with complex Korean quiz
            complex_quiz = """
            역사 문제입니다. 다음 중 조선시대의 대표적인 문화유산은 무엇인가요?
            A) 불국사와 석굴암
            B) 경복궁과 창덕궁  
            C) 해인사 팔만대장경
            D) 석빙고와 첨성대
            """
            
            result = asyncio.run(
                classifier.classify_content(complex_quiz, character_id="seol_min_seok_quiz")
            )
            
        except Exception as e:
            assert False, f"Quiz element extraction failed: {e}"
        
        # Assert - Should extract elements properly
        assert result.content_type == "quiz", "Should classify as quiz"
        assert "question" in result.detected_elements, "Should extract the main question"
        assert "조선시대" in result.detected_elements.get("question", ""), "Question should contain '조선시대'"
        assert len(result.detected_elements["options"]) >= 4, "Should extract all 4 options"
        
        # Check that options contain expected content
        options_text = str(result.detected_elements["options"])
        assert "불국사" in options_text, "Should detect '불국사' option"
        assert "경복궁" in options_text, "Should detect '경복궁' option"
        assert "해인사" in options_text, "Should detect '해인사' option"
        
        print(f"✅ Quiz elements extracted properly: {len(result.detected_elements['options'])} options detected")


if __name__ == "__main__":
    # Run the tests
    test_instance = TestLLMStructuredClassification()
    
    try:
        print("🔴 Running Test 15.1 & 15.2: LLM Structured Classification")
        print("-" * 60)
        
        # Test 1: Basic structured output classification
        test_instance.test_should_classify_content_with_structured_output()
        print("✅ Test 1 passed: LLM structured classification working")
        
        # Test 2: Non-quiz content handling
        test_instance.test_should_handle_non_quiz_content_correctly()
        print("✅ Test 2 passed: Non-quiz content handled correctly")
        
        # Test 3: Quiz element extraction
        test_instance.test_should_extract_quiz_elements_properly()
        print("✅ Test 3 passed: Quiz elements extracted properly")
        
        print("-" * 60)
        print("🟢 All tests passed!")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        print("This is expected in RED phase - LLM structured classification needs work")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")