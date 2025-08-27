"""
Test Multi-Character Orchestrator Service
TDD Implementation - RED Phase: Write failing tests first
Following methodology from documents/claude.md
"""

import pytest
from services.multi_character_orchestrator import MultiCharacterOrchestrator


class TestMultiCharacterOrchestrator:
    """Test Group 1: Multi-Character Voice Mapping Management"""
    
    def test_should_create_voice_mapping_for_characters(self):
        """
        RED PHASE: First failing test for multi-character voice mapping
        
        Given: Character names and voice IDs need to be mapped
        When: Setting up voice mappings for multi-character dialogue
        Then: Should store and retrieve character-to-voice mappings
        
        This is the fundamental building block for multi-character TTS
        """
        # Arrange
        orchestrator = MultiCharacterOrchestrator()
        character_mappings = {
            "Alice": "tc_61c97b56f1b7877a74df625b",  # Emma voice
            "Bob": "tc_6073b2f6817dccf658bb159f",     # Duke voice
            "나레이터": "tc_60c832f9d5a9c84f4c5b8c9a"  # Korean narrator
        }
        
        # Act & Assert
        orchestrator.set_voice_mappings(character_mappings)
        
        # Verify mappings were stored correctly
        assert orchestrator.get_voice_for_character("Alice") == "tc_61c97b56f1b7877a74df625b"
        assert orchestrator.get_voice_for_character("Bob") == "tc_6073b2f6817dccf658bb159f"
        assert orchestrator.get_voice_for_character("나레이터") == "tc_60c832f9d5a9c84f4c5b8c9a"
        
        # Should handle unknown characters gracefully
        assert orchestrator.get_voice_for_character("Unknown") is None
    
    def test_should_parse_dialogue_blocks_with_speaker_format(self):
        """
        RED PHASE: Test dialogue parsing for [SPEAKER: name] format
        
        Given: LLM response with [SPEAKER: name] dialogue blocks
        When: Parsing multi-character dialogue
        Then: Should extract character names and their dialogue content
        """
        # Arrange
        orchestrator = MultiCharacterOrchestrator()
        multi_character_response = """
        [SPEAKER: Alice] 안녕하세요! 오늘 날씨가 정말 좋네요.
        
        [SPEAKER: Bob] 정말 그래요. 산책하기 딱 좋은 날씨예요.
        
        [SPEAKER: 나레이터] 두 사람은 공원에서 즐거운 대화를 나누고 있었다.
        """
        
        # Act
        dialogue_blocks = orchestrator.parse_dialogue_blocks(multi_character_response)
        
        # Assert
        assert len(dialogue_blocks) == 3
        
        # Check first block
        assert dialogue_blocks[0]["character"] == "Alice"
        assert "안녕하세요" in dialogue_blocks[0]["dialogue"]
        
        # Check second block
        assert dialogue_blocks[1]["character"] == "Bob"
        assert "정말 그래요" in dialogue_blocks[1]["dialogue"]
        
        # Check narrator block
        assert dialogue_blocks[2]["character"] == "나레이터"
        assert "두 사람은" in dialogue_blocks[2]["dialogue"]
    
    def test_should_generate_tts_queue_for_multiple_characters(self):
        """
        RED PHASE: Test TTS queue generation for sequential playback
        
        Given: Parsed dialogue blocks and voice mappings
        When: Generating TTS queue for multi-character response
        Then: Should create queue with character, dialogue, voice_id for each block
        """
        # Arrange
        orchestrator = MultiCharacterOrchestrator()
        orchestrator.set_voice_mappings({
            "Alice": "tc_61c97b56f1b7877a74df625b",
            "Bob": "tc_6073b2f6817dccf658bb159f"
        })
        
        dialogue_blocks = [
            {"character": "Alice", "dialogue": "Hello there!"},
            {"character": "Bob", "dialogue": "Nice to meet you!"}
        ]
        
        # Act
        tts_queue = orchestrator.generate_tts_queue(dialogue_blocks)
        
        # Assert
        assert len(tts_queue) == 2
        
        # Check first TTS item
        assert tts_queue[0]["character"] == "Alice"
        assert tts_queue[0]["dialogue"] == "Hello there!"
        assert tts_queue[0]["voice_id"] == "tc_61c97b56f1b7877a74df625b"
        
        # Check second TTS item  
        assert tts_queue[1]["character"] == "Bob"
        assert tts_queue[1]["dialogue"] == "Nice to meet you!"
        assert tts_queue[1]["voice_id"] == "tc_6073b2f6817dccf658bb159f"


if __name__ == "__main__":
    pytest.main([__file__])