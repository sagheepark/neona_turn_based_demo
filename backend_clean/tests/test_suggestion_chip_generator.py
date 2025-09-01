"""
Test suite for SuggestionChipGenerator - handles character-specific suggestion chips
Following TDD methodology: Red -> Green -> Refactor
"""
import pytest
from services.suggestion_chip_generator import SuggestionChipGenerator


class TestSuggestionChipGenerator:
    """Test Group 5: Character-Specific Suggestion Chips"""
    
    def test_should_generate_seol_minseok_chips(self):
        """
        Test 5.1: shouldGenerateSeolMinseokChips
        Red phase: This test should fail because SuggestionChipGenerator doesn't exist yet
        """
        # Arrange
        generator = SuggestionChipGenerator()
        context = {
            "character_id": "seol_min_seok",
            "conversation_state": "initial"
        }
        
        # Act
        chips = generator.generate_chips(context)
        
        # Assert
        assert '3·1 운동에 대해 알려주세요' in chips
        assert '조선시대 왕들 이야기' in chips
        assert len(chips) >= 3
        
    def test_should_generate_contextual_chips(self):
        """
        Test 5.2: shouldGenerateContextualChips
        Red phase: This test checks if contextual chips are generated based on conversation state
        """
        # Arrange
        generator = SuggestionChipGenerator()
        context = {
            "character_id": "dr_python",
            "last_message": "파이썬 리스트에 대해 배워볼까요?",
            "conversation_topic": "python_basics"
        }
        
        # Act
        chips = generator.generate_chips(context)
        
        # Assert
        assert any('예제' in chip for chip in chips)
        assert any('연습' in chip for chip in chips)