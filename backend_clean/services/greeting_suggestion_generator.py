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
        
        # Character-specific suggestions for quiz-focused 설민석
        if character_id == 'seol_min_seok_quiz':
            if '퀴즈' in greeting_message:
                return [
                    '조선시대 퀴즈',
                    '근현대사 문제', 
                    '난이도 선택하기',
                    '랜덤 퀴즈 시작'
                ]
        
        # Default suggestions for enabled characters
        if suggestions_enabled:
            return [
                '대화 시작하기',
                '도움말 보기',
                '기능 알아보기'
            ]
        
        return []