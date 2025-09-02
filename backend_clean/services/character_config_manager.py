"""
Character Configuration Manager
Manages provider-controllable content classification configurations per character
"""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, field_validator
from dataclasses import dataclass


class ContentTypeDefinition(BaseModel):
    """Defines a content type with its classification rules and tools"""
    name: str
    detection_patterns: List[str] = []
    llm_classification_prompt: Optional[str] = None
    required_tools: List[str] = []
    confidence_threshold: float = 0.7
    metadata_schema: Dict[str, Any] = {}
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Content type name cannot be empty")
        return v.strip()
    
    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence_threshold(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v


class CharacterContentConfig(BaseModel):
    """Complete configuration for a character's content classification"""
    character_id: str
    content_types: Dict[str, ContentTypeDefinition] = {}
    classification_strategy: Literal["pattern_first", "llm_first", "hybrid"] = "hybrid"
    global_confidence_threshold: float = 0.7
    fallback_strategy: Literal["conservative", "aggressive", "adaptive"] = "conservative"
    learning_enabled: bool = True
    cache_ttl: int = 3600  # Cache time-to-live in seconds


class CharacterConfigManager:
    """Manages character-specific content classification configurations"""
    
    def __init__(self):
        self._configs = {}
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize configurations for known characters"""
        
        # Quiz character configuration
        quiz_content_type = ContentTypeDefinition(
            name="quiz",
            detection_patterns=[
                r"(.+?)\?\s*([A-D]\)[^A-D]*)+",  # Korean quiz pattern
                r"다음 중.*\?.*[A-D]\)",           # "다음 중" quiz indicators
                r"(.+?연도는\?)\s*([A-D]\)[^A-D]*)+"  # Year-based questions
            ],
            llm_classification_prompt="""
            Analyze if this Korean content is a multiple-choice quiz question.
            Look for:
            - A question ending with ?
            - Multiple choice options labeled A), B), C), D)
            - Educational Korean content about history
            
            If it's a quiz, extract:
            - The main question
            - All answer options
            - The most likely correct answer
            """,
            required_tools=["show_selection"],
            confidence_threshold=0.8,
            metadata_schema={
                "question": "str",
                "options": "List[str]", 
                "labels": "List[str]",
                "correct_answer": "str",
                "topic": "str",
                "difficulty": "str"
            }
        )
        
        seol_min_seok_quiz_config = CharacterContentConfig(
            character_id="seol_min_seok_quiz",
            content_types={"quiz": quiz_content_type},
            classification_strategy="hybrid",
            global_confidence_threshold=0.7,
            fallback_strategy="adaptive",
            learning_enabled=True
        )
        
        self._configs["seol_min_seok_quiz"] = seol_min_seok_quiz_config
    
    def get_character_config(self, character_id: str) -> CharacterContentConfig:
        """Get configuration for a specific character"""
        if character_id in self._configs:
            return self._configs[character_id]
        
        # Return default configuration for unknown characters
        return CharacterContentConfig(
            character_id=character_id,
            content_types={},
            classification_strategy="hybrid",
            global_confidence_threshold=0.7,
            fallback_strategy="conservative",
            learning_enabled=False
        )
    
    def register_content_type(
        self, 
        character_id: str, 
        content_type: ContentTypeDefinition
    ) -> None:
        """Register a new content type for a character"""
        if character_id not in self._configs:
            self._configs[character_id] = CharacterContentConfig(character_id=character_id)
        
        self._configs[character_id].content_types[content_type.name] = content_type
    
    def update_character_config(
        self, 
        character_id: str, 
        config: CharacterContentConfig
    ) -> None:
        """Update complete configuration for a character"""
        config.character_id = character_id  # Ensure consistency
        self._configs[character_id] = config
    
    def list_characters(self) -> List[str]:
        """List all configured character IDs"""
        return list(self._configs.keys())
    
    def get_content_types_for_character(self, character_id: str) -> Dict[str, ContentTypeDefinition]:
        """Get all content types configured for a character"""
        config = self.get_character_config(character_id)
        return config.content_types