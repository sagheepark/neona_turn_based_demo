"""
LLM Structured Classifier
Uses LLM with structured output for reliable content classification
"""
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from services.character_config_manager import CharacterConfigManager
import os
from openai import AsyncAzureOpenAI


@dataclass
class ClassificationResult:
    """Result of content classification with confidence and metadata"""
    content_type: str
    confidence: float
    detected_elements: Dict[str, Any] 
    suggested_tools: List[str]
    metadata: Dict[str, Any]
    detection_method: str = "llm_structured"


class LLMStructuredClassifier:
    """LLM-based content classifier using structured output"""
    
    def __init__(self):
        self.config_manager = CharacterConfigManager()
        self.azure_client = self._initialize_azure_client()
        
        # Classification schema for structured output
        self.classification_schema = {
            "type": "object",
            "properties": {
                "content_type": {
                    "type": "string",
                    "enum": ["quiz", "poll", "form", "text", "unknown"]
                },
                "confidence": {
                    "type": "number", 
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "detected_elements": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "labels": {
                            "type": "array", 
                            "items": {"type": "string"}
                        },
                        "correct_answer": {"type": "string"}
                    }
                },
                "suggested_tools": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "difficulty": {
                            "type": "string",
                            "enum": ["easy", "medium", "hard"]
                        }
                    }
                }
            },
            "required": ["content_type", "confidence", "detected_elements", "suggested_tools", "metadata"]
        }
    
    def _initialize_azure_client(self) -> Optional[AsyncAzureOpenAI]:
        """Initialize Azure OpenAI client if available"""
        try:
            return AsyncAzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
        except Exception as e:
            print(f"⚠️ Azure OpenAI client initialization failed: {e}")
            return None
    
    async def classify_content(
        self, 
        content: str, 
        character_id: str
    ) -> ClassificationResult:
        """Classify content using LLM with structured output"""
        
        # Get character-specific configuration
        config = self.config_manager.get_character_config(character_id)
        
        # Build classification prompt
        classification_prompt = self._build_classification_prompt(content, config)
        
        # Use Azure OpenAI if available, otherwise fall back to pattern matching
        if self.azure_client:
            try:
                return await self._classify_with_azure_llm(content, classification_prompt, config)
            except Exception as e:
                print(f"⚠️ LLM classification failed, using fallback: {e}")
                return self._classify_with_fallback(content, config)
        else:
            return self._classify_with_fallback(content, config)
    
    def _build_classification_prompt(self, content: str, config) -> str:
        """Build classification prompt based on character configuration"""
        
        content_types_desc = []
        for name, content_type in config.content_types.items():
            content_types_desc.append(f"""
{name}: {content_type.llm_classification_prompt or f'Detect {name} content'}
Required tools: {content_type.required_tools}
""")
        
        prompt = f"""
Analyze this Korean content and classify it accurately:

Content: "{content}"

Available content types:
{"".join(content_types_desc)}

Instructions:
1. Determine the most appropriate content type
2. Provide confidence score (0.0-1.0) based on how certain you are
3. If it's a quiz, extract:
   - The main question
   - All answer options (A, B, C, D choices)
   - The option labels [A, B, C, D]
   - The correct answer (use your knowledge)
4. Suggest appropriate tools based on content type
5. Provide metadata like topic and difficulty

Respond with JSON matching this exact structure:
{{
    "content_type": "quiz|poll|form|text|unknown",
    "confidence": 0.0-1.0,
    "detected_elements": {{
        "question": "extracted question text",
        "options": ["option1", "option2", "option3", "option4"],
        "labels": ["A", "B", "C", "D"], 
        "correct_answer": "the correct option text"
    }},
    "suggested_tools": ["tool1", "tool2"],
    "metadata": {{
        "topic": "subject area",
        "difficulty": "easy|medium|hard"
    }}
}}
"""
        return prompt
    
    async def _classify_with_azure_llm(
        self, 
        content: str, 
        prompt: str, 
        config
    ) -> ClassificationResult:
        """Classify using Azure OpenAI with structured output"""
        
        try:
            response = await self.azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result_data = json.loads(json_match.group())
            else:
                result_data = json.loads(response_text)
            
            return ClassificationResult(
                content_type=result_data.get("content_type", "unknown"),
                confidence=result_data.get("confidence", 0.0),
                detected_elements=result_data.get("detected_elements", {}),
                suggested_tools=result_data.get("suggested_tools", []),
                metadata=result_data.get("metadata", {}),
                detection_method="llm_structured"
            )
            
        except Exception as e:
            print(f"❌ Azure OpenAI structured classification failed: {e}")
            return self._classify_with_fallback(content, config)
    
    def _classify_with_fallback(self, content: str, config) -> ClassificationResult:
        """Fallback classification using pattern matching and heuristics"""
        
        # Check for quiz patterns
        for content_type_name, content_type in config.content_types.items():
            if content_type_name == "quiz":
                if self._matches_quiz_pattern(content):
                    return self._extract_quiz_with_heuristics(content)
        
        # Default to text classification
        return ClassificationResult(
            content_type="text",
            confidence=0.3,
            detected_elements={},
            suggested_tools=[],
            metadata={"topic": "general", "difficulty": "unknown"},
            detection_method="fallback_heuristic"
        )
    
    def _matches_quiz_pattern(self, content: str) -> bool:
        """Check if content matches quiz patterns"""
        quiz_patterns = [
            r'(.+?)\?\s*([A-D]\)[^A-D]*)+',
            r'다음 중.*\?.*[A-D]\)',
            r'(.+?연도는\?)\s*([A-D]\)[^A-D]*)+'
        ]
        
        for pattern in quiz_patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        return False
    
    def _extract_quiz_with_heuristics(self, content: str) -> ClassificationResult:
        """Extract quiz data using pattern matching heuristics"""
        
        # Extract question and options using regex
        match = re.search(r'(.+?\?)\s*((?:[A-D]\)[^A-D]*)+)', content)
        if not match:
            return ClassificationResult(
                content_type="text",
                confidence=0.2,
                detected_elements={},
                suggested_tools=[],
                metadata={},
                detection_method="fallback_failed"
            )
        
        question = match.group(1).strip()
        options_text = match.group(2).strip()
        
        # Extract individual options
        option_pattern = r'([A-D])\)\s*([^A-D]+?)(?=[A-D]\)|$)'
        option_matches = re.findall(option_pattern, options_text)
        
        if not option_matches:
            return ClassificationResult(
                content_type="text",
                confidence=0.2,
                detected_elements={},
                suggested_tools=[],
                metadata={},
                detection_method="fallback_failed"
            )
        
        options = [match[1].strip() for match in option_matches]
        labels = [match[0] for match in option_matches]
        
        # Simple heuristic for correct answer (first option as default)
        correct_answer = options[0] if options else ""
        
        return ClassificationResult(
            content_type="quiz",
            confidence=0.85,
            detected_elements={
                "question": question,
                "options": options,
                "labels": labels,
                "correct_answer": correct_answer
            },
            suggested_tools=["show_selection"],
            metadata={"topic": "일반", "difficulty": "medium"},
            detection_method="fallback_pattern"
        )