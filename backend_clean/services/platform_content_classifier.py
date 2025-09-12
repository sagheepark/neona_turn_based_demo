"""
Platform-Grade Content Classifier
Unified interface that integrates all classification components for production use
"""
import asyncio
from typing import Dict, Any, Optional, List
from services.character_config_manager import CharacterConfigManager
from services.llm_structured_classifier import LLMStructuredClassifier
from services.hybrid_content_classifier import HybridContentClassifier
from services.learning_content_classifier import LearningContentClassifier


class PlatformContentClassifier:
    """
    Production-ready content classifier that replaces ContentIntelligence
    Provides the same interface but with platform-grade capabilities
    """
    
    def __init__(self):
        self.learning_classifier = LearningContentClassifier()
        self.config_manager = CharacterConfigManager()
    
    async def analyze_for_tools(self, llm_response: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main analysis method - detects all possible tools from LLM response
        Compatible with existing ContentIntelligence interface
        """
        tools = []
        
        # Get character ID from context
        character_id = context.get("character_id", "default")
        
        try:
            # Use learning-enhanced classification
            result = await self.learning_classifier.classify_with_learning(
                llm_response, 
                character_id
            )
            
            # Convert classification result to tool format
            if result.content_type == "quiz" and result.confidence > 0.7:
                quiz_tool = self._convert_to_quiz_tool(result)
                tools.append(quiz_tool)
                
                # Learn from successful detection for future improvements
                if result.confidence > 0.8:
                    self.learning_classifier.learn_from_success(llm_response, result)
            
            # 🔥 NEW: Detect feedback responses that should trigger continuous flow
            elif self._is_quiz_feedback(llm_response, character_id):
                feedback_tool = self._create_feedback_continuous_tool(llm_response, context)
                tools.append(feedback_tool)
                print(f"🎯 CONTINUOUS FLOW: Detected feedback response - triggering multi-step flow")
            
            # Future: Add more content type handlers (polls, forms, etc.)
                
        except Exception as e:
            print(f"🧠 Platform classifier error: {e}")
            # Graceful fallback - no tools detected
            
        return tools
    
    def _convert_to_quiz_tool(self, classification_result) -> Dict[str, Any]:
        """Convert ClassificationResult to ContentIntelligence-compatible tool format"""
        
        detected_elements = classification_result.detected_elements
        
        return {
            "type": "show_selection",
            "data": {
                "question": detected_elements.get("question", ""),
                "items": detected_elements.get("options", []),
                "correctAnswer": detected_elements.get("correct_answer", ""),
                "metadata": {
                    "labels": detected_elements.get("labels", []),
                    "topic": classification_result.metadata.get("topic", "일반"),
                    "difficulty": classification_result.metadata.get("difficulty", "medium"),
                    "type": "quiz",
                    "confidence": classification_result.confidence,
                    "detection_method": classification_result.detection_method,
                    "platform_grade": True  # Mark as platform-grade detection
                }
            }
        }
    
    # Legacy compatibility methods
    def detect_quiz_patterns(self, content: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Legacy compatibility method - deprecated, use analyze_for_tools instead"""
        try:
            # Run async method synchronously for compatibility
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                character_id = context.get("character_id", "default")
                result = loop.run_until_complete(
                    self.learning_classifier.classify_with_learning(content, character_id)
                )
                
                if result.content_type == "quiz" and result.confidence > 0.7:
                    return {
                        "question": result.detected_elements.get("question", ""),
                        "options": result.detected_elements.get("options", []),
                        "labels": result.detected_elements.get("labels", []),
                        "correct_answer": result.detected_elements.get("correct_answer", ""),
                        "topic": result.metadata.get("topic", "일반"),
                        "difficulty": result.metadata.get("difficulty", "medium")
                    }
                return None
            finally:
                loop.close()
        except Exception as e:
            print(f"🧠 Legacy method error: {e}")
            return None
    
    def generate_quiz_tool(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy compatibility method"""
        return {
            "type": "show_selection",
            "data": {
                "question": quiz_data["question"],
                "items": quiz_data["options"],
                "correctAnswer": quiz_data["correct_answer"],
                "metadata": {
                    "labels": quiz_data["labels"],
                    "topic": quiz_data.get("topic", "일반"),
                    "difficulty": quiz_data.get("difficulty", "medium"),
                    "type": "quiz",
                    "platform_grade": True
                }
            }
        }
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get statistics about platform performance"""
        return {
            "classifier_type": "platform_grade",
            "learning_enabled": True,
            "learning_stats": self.learning_classifier.get_learning_stats(),
            "configured_characters": self.config_manager.list_characters()
        }
    
    def _is_quiz_feedback(self, response: str, character_id: str) -> bool:
        """
        Detect if response is quiz feedback that should trigger continuous flow
        Based on 2025 research: pattern-based + context-aware detection
        """
        # Pattern-based detection for Korean quiz feedback
        feedback_patterns = [
            r"정답.*!.*",  # "정답입니다!", "정답이에요!"
            r"맞.*습니다.*!",  # "맞습니다!", "맞아요!"
            r"훌륭.*!",  # "훌륭해요!", "훌륭합니다!"
            r".*정답.*다음.*문제.*준비.*",  # "정답입니다! 다음 문제 준비되셨나요?"
            r".*맞.*다음.*",  # "맞아요! 다음으로 넘어가볼까요?"
        ]
        
        # Check if character is quiz-enabled
        is_quiz_character = character_id == "seol_min_seok_quiz" or "quiz" in character_id
        
        # Check patterns
        import re
        for pattern in feedback_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                if is_quiz_character:
                    print(f"🎯 FEEDBACK DETECTED: Pattern '{pattern}' matched in '{response[:50]}...'")
                    return True
        
        return False
    
    def _create_feedback_continuous_tool(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create continuous flow tool for feedback responses
        Based on 2025 research: structured flow orchestration
        """
        return {
            "type": "continue_feedback_flow", 
            "data": {
                "trigger_type": "quiz_feedback",
                "character_id": context.get("character_id", ""),
                "user_message": context.get("user_message", ""),
                "feedback_response": response,
                "flow_config": {
                    "steps": [
                        {
                            "step_id": "feedback_generation",
                            "action": "llm_generate_detailed_feedback",
                            "audio_enabled": True,
                            "next_trigger": "audio_completion"
                        },
                        {
                            "step_id": "next_question_generation", 
                            "condition": "audio_completion",
                            "action": "llm_generate_next_question",
                            "audio_enabled": True,
                            "flow_end": True
                        }
                    ]
                },
                "metadata": {
                    "detection_method": "feedback_pattern",
                    "confidence": 0.95,
                    "platform_grade": True
                }
            }
        }