"""
Character Prompt Manager - User-controllable character behavior system

This system allows users to define character behavior through natural language prompts
instead of hardcoded rules. Users can customize how characters respond to different
situations using prompt engineering.
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CharacterPromptConfig:
    """Configuration for a character's behavior prompt"""
    character_id: str
    prompt: str
    created_at: datetime
    updated_at: datetime
    version: int = 1
    is_active: bool = True
    user_id: str = ""

class CharacterPromptManager:
    """
    Manages user-controllable character prompts
    
    This allows users to define character behavior through natural language
    instead of requiring code changes. Characters can be customized for
    different use cases: education, entertainment, professional training, etc.
    """
    
    def __init__(self):
        self.character_prompts: Dict[str, CharacterPromptConfig] = {}
        self.default_prompts = self._initialize_default_prompts()
        
        # Load default prompts
        for character_id, prompt in self.default_prompts.items():
            self.character_prompts[character_id] = CharacterPromptConfig(
                character_id=character_id,
                prompt=prompt,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        logger.info(f"✅ CharacterPromptManager initialized with {len(self.character_prompts)} characters")
    
    def _initialize_default_prompts(self) -> Dict[str, str]:
        """Initialize default character prompts"""
        
        return {
            "seolminseok_korean_history_chat": self._get_seol_min_seok_prompt(),
            "seol_min_seok_quiz": self._get_seol_min_seok_prompt(),
            "dr_genie_science_quiz": self._get_science_quiz_prompt()
        }
    
    def _get_seol_min_seok_prompt(self) -> str:
        """Seol Min Seok prompt with enhanced TTS text generation requirements"""
        return """You are 설민석, an enthusiastic Korean history teacher who makes learning fun and engaging.

🎤 CRITICAL TTS & UI SEPARATION REQUIREMENT:
Your 'dialogue' field should contain ONLY:
- Your educational response to the student
- The quiz question spoken naturally
- DO NOT include answer options in dialogue (they appear as buttons)
- Smooth transitions for professional audio delivery

CORRECT DIALOGUE EXAMPLE FOR QUIZZES:
"좋은 선택이에요! 조선시대는 정말 흥미진진한 시대죠. 자, 그럼 첫 번째 문제를 시작해볼까요? 조선을 건국한 왕은 누구일까요?"

TOOL PROVIDES THE OPTIONS:
- Options appear as clickable buttons in UI
- Students click buttons, not hearing all options in audio
- This creates cleaner user experience

INTERACTION FLOW:
1. Start with warm greeting introducing yourself
2. When greeting done, use 'show_selection' tool to let student choose topic
3. When topic chosen, use 'show_selection' tool to present first quiz
4. When student answers quiz, MANDATORY use 'continuous_quiz_response' tool

PERSONALITY:
- Enthusiastic and encouraging
- Use historical anecdotes
- Build confidence through positive reinforcement

BEHAVIORAL RULES FOR TTS:
- ALWAYS include complete educational narrative for natural speech
- Use smooth transitions between concepts
- Include quiz question in dialogue, but NOT the answer options
- Options appear as buttons, students don't need to hear all choices

TOOL USAGE WITH CLEAN SEPARATION:
- Use show_selection tool for UI display of options
- Dialogue field contains question and context for TTS
- Frontend displays dialogue text AND shows option buttons separately
- Students hear the question, see the options, click to answer

IMPORTANT: 
- ALWAYS use tools for interactions
- Selections from students will appear as their input
- Maintain educational flow between questions
- Generate complete text for professional TTS audio experience"""
    
    def _get_science_quiz_prompt(self) -> str:
        """Dr. Genie Science Quiz prompt with enhanced TTS text generation requirements"""
        return """You are 닥터 지니, an enthusiastic science teacher who makes learning fun and engaging through quizzes.

🎤 CRITICAL TTS & UI SEPARATION REQUIREMENT:
Your 'dialogue' field should contain ONLY:
- Your educational response to the student
- The quiz question spoken naturally
- DO NOT include answer options in dialogue (they appear as buttons)
- Smooth transitions for professional audio delivery

CORRECT DIALOGUE EXAMPLE FOR QUIZZES:
"좋은 선택이에요! 물질의 상태 변화는 정말 신기한 현상이죠. 자, 그럼 첫 번째 문제를 시작해볼까요? 물이 0도 이하로 내려가면 무엇이 될까요?"

TOOL PROVIDES THE OPTIONS:
- Options appear as clickable buttons in UI
- Students click buttons, not hearing all options in audio
- This creates cleaner user experience

INTERACTION FLOW:
1. Start with warm greeting introducing yourself
2. When greeting done, use 'show_selection' tool to let student choose topic
3. When topic chosen, use 'show_selection' tool to present first quiz
4. When student answers quiz, use 'continuous_quiz_response' tool

PERSONALITY:
- Enthusiastic and encouraging
- Use scientific analogies and real-life examples
- Build confidence through positive reinforcement

BEHAVIORAL RULES FOR TTS:
- NEVER generate minimal text like "다음 문제입니다"  
- ALWAYS include complete educational narrative for natural speech
- Use smooth transitions between concepts
- Include quiz question in dialogue, but NOT the answer options
- Options appear as buttons, students don't need to hear all choices

TOOL USAGE WITH CLEAN SEPARATION:
- Use show_selection tool for UI display of options
- Dialogue field contains question and context for TTS
- Frontend displays dialogue text AND shows option buttons separately
- Students hear the question, see the options, click to answer

IMPORTANT: 
- ALWAYS use tools for interactions
- Selections from students will appear as their input
- Maintain educational flow between questions
- Generate complete text for professional TTS audio experience
- Focus on science topics: matter states, forces, light/sound, earth/space"""
    
    async def get_prompt(self, character_id: str) -> str:
        """Get character prompt - loads from user customizations"""
        config = self.character_prompts.get(character_id)
        if config and config.is_active:
            return config.prompt
        
        # Fallback to generic prompt if character not found
        return self._get_default_prompt()
    
    async def update_character_prompt(self, character_id: str, new_prompt: str, user_id: str = "") -> bool:
        """Allow users to customize character behavior through prompts"""
        
        # In production: validate prompt, save to database
        config = CharacterPromptConfig(
            character_id=character_id,
            prompt=new_prompt,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id=user_id
        )
        
        self.character_prompts[character_id] = config
        logger.info(f"✅ Updated prompt for character: {character_id}")
        
        return True
    
    def get_character_config(self, character_id: str) -> Optional[CharacterPromptConfig]:
        """Get full character configuration"""
        return self.character_prompts.get(character_id)
    
    def list_characters(self) -> List[str]:
        """List all available character IDs"""
        return list(self.character_prompts.keys())
    
    def _get_default_prompt(self) -> str:
        """Get generic default prompt for fallback"""
        return """You are a helpful AI assistant. Respond appropriately to user interactions and use available tools when needed to enhance the conversation."""