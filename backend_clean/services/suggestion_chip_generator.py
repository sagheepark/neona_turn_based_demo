"""
Suggestion Chip Generator - Generates character-specific suggestion chips
Minimal implementation following TDD principles
"""
from typing import Dict, Any, List


class SuggestionChipGenerator:
    """Generates contextual suggestion chips based on character and conversation state"""
    
    def generate_chips(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate suggestion chips based on context
        
        Args:
            context: Dictionary containing character_id, conversation_state, etc.
            
        Returns:
            List of suggestion chip strings
        """
        character_id = context.get('character_id', '')
        conversation_state = context.get('conversation_state', '')
        last_message = context.get('last_message', '')
        conversation_topic = context.get('conversation_topic', '')
        
        # Character-specific chips for Seol Min Seok (Korean history teacher)
        if character_id == 'seol_min_seok':
            if conversation_state == 'initial':
                return [
                    '3·1 운동에 대해 알려주세요',
                    '조선시대 왕들 이야기',
                    '한국 전쟁의 역사'
                ]
        
        # Character-specific chips for Dr. Python (programming teacher)
        if character_id == 'dr_python':
            if conversation_topic == 'python_basics' and '리스트' in last_message:
                return [
                    '리스트 예제를 보여주세요',
                    '리스트 연습 문제',
                    '다른 자료형과 비교'
                ]
        
        # Default chips
        return ['안녕하세요', '도움이 필요해요', '설명해주세요']