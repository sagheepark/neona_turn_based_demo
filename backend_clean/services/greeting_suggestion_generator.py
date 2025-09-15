"""
Greeting Suggestion Generator - Generates contextual greeting suggestions
Minimal implementation following TDD principles
"""
from typing import Dict, Any, List


class GreetingSuggestionGenerator:
    """Generates contextual suggestions after character greetings"""
    
    def generate_greeting_suggestions(self, greeting_context: Dict[str, Any]) -> List[str]:
        """
        Generate greeting suggestions based on context
        
        Args:
            greeting_context: Dictionary containing character info and greeting details
            
        Returns:
            List of contextual suggestion strings
        """
        suggestions_enabled = greeting_context.get('suggestions_enabled', False)
        if not suggestions_enabled:
            return []
        
        character_id = greeting_context.get('character_id', '')
        greeting_message = greeting_context.get('greeting_message', '')
        
        # Character-specific suggestions for quiz characters
        if character_id == 'seol_min_seok_quiz':
            # Korean history quiz topics
            return [
                '조선시대 퀴즈',
                '근현대사 퀴즈', 
                '일제강점기 퀴즈',
                '랜덤 퀴즈 시작'
            ]
        elif character_id == 'dr_genie_science_quiz':
            # Science quiz topics
            return [
                '물리 퀴즈',
                '화학 퀴즈',
                '생물학 퀴즈', 
                '랜덤 과학 퀴즈'
            ]
        
        # Default suggestions for enabled characters
        if suggestions_enabled:
            return [
                '대화 시작하기',
                '도움말 보기',
                '기능 알아보기'
            ]
        
        return []
    
    def generate_for_character(self, character: Dict[str, Any]) -> List[str]:
        """
        Generate suggestions for a character, respecting the greeting_suggestions_enabled flag
        
        Args:
            character: Character dictionary with id, name, greeting_suggestions_enabled, etc.
            
        Returns:
            List of suggestion strings, or empty list if disabled
        """
        # Check if suggestions are enabled for this character
        suggestions_enabled = character.get('greeting_suggestions_enabled', False)
        
        if not suggestions_enabled:
            return []
        
        # Build context for existing generator method
        greeting_context = {
            'suggestions_enabled': True,
            'character_id': character.get('id', ''),
            'greeting_message': character.get('greetings', [''])[0] if character.get('greetings') else ''
        }
        
        return self.generate_greeting_suggestions(greeting_context)