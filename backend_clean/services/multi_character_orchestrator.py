"""
Multi-Character Orchestrator Service
TDD Implementation - GREEN phase: Minimal implementation to make tests pass
Following methodology from documents/claude.md
"""

import re
from typing import Dict, List, Optional


class MultiCharacterOrchestrator:
    """
    Service for managing multi-character voice dialogues with sequential TTS playback
    Implements voice mapping, dialogue parsing, and TTS queue generation
    """
    
    def __init__(self):
        """Initialize orchestrator with empty voice mappings"""
        self.voice_mappings: Dict[str, str] = {}
    
    def set_voice_mappings(self, character_mappings: Dict[str, str]) -> None:
        """
        Set character to voice ID mappings for TTS generation
        
        Args:
            character_mappings: Dict mapping character names to voice IDs
        """
        self.voice_mappings = character_mappings.copy()
    
    def get_voice_for_character(self, character_name: str) -> Optional[str]:
        """
        Get voice ID for a character name
        
        Args:
            character_name: Name of the character
            
        Returns:
            Voice ID if mapped, None if not found
        """
        return self.voice_mappings.get(character_name)
    
    def parse_dialogue_blocks(self, multi_character_response: str) -> List[Dict[str, str]]:
        """
        Parse multi-character dialogue response into structured blocks
        
        Expects format: [SPEAKER: name] dialogue content
        
        Args:
            multi_character_response: Raw LLM response with speaker blocks
            
        Returns:
            List of dicts with 'character' and 'dialogue' keys
        """
        dialogue_blocks = []
        
        # Regex pattern to match [SPEAKER: name] followed by dialogue
        pattern = r'\[SPEAKER:\s*([^\]]+)\]\s*([^\[\n]*(?:\n(?!\[)[^\[\n]*)*)'
        
        matches = re.findall(pattern, multi_character_response.strip(), re.MULTILINE | re.DOTALL)
        
        for character_name, dialogue_content in matches:
            # Clean up the character name and dialogue
            character = character_name.strip()
            dialogue = dialogue_content.strip()
            
            if character and dialogue:
                dialogue_blocks.append({
                    "character": character,
                    "dialogue": dialogue
                })
        
        return dialogue_blocks
    
    def generate_tts_queue(self, dialogue_blocks: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generate TTS queue from dialogue blocks using voice mappings
        
        Args:
            dialogue_blocks: List of character/dialogue pairs
            
        Returns:
            List of TTS items with character, dialogue, and voice_id
        """
        tts_queue = []
        
        for block in dialogue_blocks:
            character = block["character"]
            dialogue = block["dialogue"]
            voice_id = self.get_voice_for_character(character)
            
            # Only add to queue if we have a voice mapping for this character
            if voice_id:
                tts_queue.append({
                    "character": character,
                    "dialogue": dialogue,
                    "voice_id": voice_id
                })
        
        return tts_queue