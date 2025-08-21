"""
Character Mood Service for dynamic image expressions
Minimal implementation for TDD Green phase
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class CharacterMoodService:
    def __init__(self):
        self.moods_path = Path("character_moods")
        self.moods_path.mkdir(exist_ok=True)
        self.moods_cache = {}
        self._load_all_moods()
    
    def _load_all_moods(self):
        """Load all character moods from storage"""
        for mood_file in self.moods_path.glob("*.json"):
            character_id = mood_file.stem
            with open(mood_file, 'r', encoding='utf-8') as f:
                self.moods_cache[character_id] = json.load(f)
    
    def set_character_moods(self, character_id: str, moods: Dict) -> Dict:
        """
        Set mood configuration for a character
        Minimal implementation for TDD Green phase
        """
        # Save moods to file
        mood_file = self.moods_path / f"{character_id}.json"
        with open(mood_file, 'w', encoding='utf-8') as f:
            json.dump(moods, f, ensure_ascii=False, indent=2)
        
        # Update cache
        self.moods_cache[character_id] = moods
        
        return {"success": True}
    
    def detect_mood(self, character_id: str, text: str) -> str:
        """
        Detect mood from conversation text
        Minimal implementation for TDD Green phase
        """
        if character_id not in self.moods_cache:
            return "default"
        
        moods = self.moods_cache[character_id]
        text_lower = text.lower()
        
        # Check each mood's trigger keywords
        for mood_name, mood_data in moods.items():
            if mood_name == "default":
                continue
            
            if "trigger_keywords" in mood_data:
                for keyword in mood_data["trigger_keywords"]:
                    if keyword.lower() in text_lower:
                        return mood_name
        
        return "default"
    
    def get_mood_data(self, character_id: str, mood_name: str) -> Optional[Dict]:
        """
        Get mood data for a character
        Minimal implementation for TDD Green phase
        """
        if character_id not in self.moods_cache:
            return None
        
        moods = self.moods_cache[character_id]
        return moods.get(mood_name)
    
    def get_character_moods(self, character_id: str) -> Dict:
        """
        Get all moods for a character
        """
        return self.moods_cache.get(character_id, {})