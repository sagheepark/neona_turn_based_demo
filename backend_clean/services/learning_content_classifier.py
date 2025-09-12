"""
Learning Content Classifier
Extends hybrid classification with learning capabilities
"""
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from services.llm_structured_classifier import ClassificationResult, LLMStructuredClassifier
from services.hybrid_content_classifier import HybridContentClassifier
from services.character_config_manager import CharacterConfigManager


@dataclass
class LearningExample:
    """Represents a successful classification example for learning"""
    content_hash: str
    content_type: str
    confidence: float
    detected_elements: Dict
    metadata: Dict
    timestamp: float
    character_id: str


class LearningContentClassifier:
    """Content classifier with learning and adaptation capabilities"""
    
    def __init__(self):
        self.llm_classifier = LLMStructuredClassifier()
        self.hybrid_classifier = HybridContentClassifier()
        self.config_manager = CharacterConfigManager()
        
        # Learning storage (in production, this would use persistent storage)
        self.learning_examples: Dict[str, List[LearningExample]] = {}
        self.pattern_weights: Dict[str, Dict[str, float]] = {}
        
    def learn_from_success(self, content: str, result: ClassificationResult) -> None:
        """Learn from a successful classification result"""
        import time
        
        # Create content hash for deduplication
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Create learning example
        example = LearningExample(
            content_hash=content_hash,
            content_type=result.content_type,
            confidence=result.confidence,
            detected_elements=result.detected_elements,
            metadata=result.metadata,
            timestamp=time.time(),
            character_id="default"  # Could be parameterized
        )
        
        # Store the example
        if result.content_type not in self.learning_examples:
            self.learning_examples[result.content_type] = []
        
        # Avoid duplicates
        existing_hashes = {ex.content_hash for ex in self.learning_examples[result.content_type]}
        if content_hash not in existing_hashes:
            self.learning_examples[result.content_type].append(example)
            self._update_pattern_weights(content, result)
    
    def _update_pattern_weights(self, content: str, result: ClassificationResult) -> None:
        """Update pattern weights based on successful classification"""
        
        # Extract key patterns from successful content
        patterns = self._extract_patterns(content)
        
        content_type = result.content_type
        if content_type not in self.pattern_weights:
            self.pattern_weights[content_type] = {}
        
        # Increase weights for patterns that led to successful classification
        for pattern in patterns:
            if pattern not in self.pattern_weights[content_type]:
                self.pattern_weights[content_type][pattern] = 0.1
            else:
                # Increment weight but cap at 1.0
                self.pattern_weights[content_type][pattern] = min(
                    1.0, 
                    self.pattern_weights[content_type][pattern] + 0.1
                )
    
    def _extract_patterns(self, content: str) -> List[str]:
        """Extract key patterns from content for learning"""
        patterns = []
        
        # Extract structural patterns
        if "다음 중" in content:
            patterns.append("다음_중_pattern")
        
        if "? A)" in content and "B)" in content:
            patterns.append("multiple_choice_pattern")
        
        # Extract topic patterns
        historical_keywords = ["조선", "고구려", "백제", "신라", "가야", "건국", "왕", "대왕"]
        for keyword in historical_keywords:
            if keyword in content:
                patterns.append(f"topic_{keyword}")
        
        # Extract question patterns
        if "?" in content:
            patterns.append("question_ending")
        
        return patterns
    
    async def classify_with_learning(
        self, 
        content: str, 
        character_id: str
    ) -> ClassificationResult:
        """Classify content using learning-enhanced hybrid approach"""
        
        # Get base LLM classification
        base_result = await self.llm_classifier.classify_content(content, character_id)
        
        # Apply learning enhancements
        learning_boost = self._calculate_learning_boost(content, base_result.content_type)
        learning_score = learning_boost
        
        # Boost confidence based on learning
        enhanced_confidence = min(1.0, base_result.confidence + learning_boost)
        
        # Add learning metadata
        enhanced_metadata = {**base_result.metadata}
        if learning_boost > 0:
            enhanced_metadata["learning_applied"] = True
            enhanced_metadata["learning_boost"] = learning_boost
        
        # Create enhanced result
        enhanced_result = ClassificationResult(
            content_type=base_result.content_type,
            confidence=enhanced_confidence,
            detected_elements=base_result.detected_elements,
            suggested_tools=base_result.suggested_tools,
            metadata=enhanced_metadata,
            detection_method=f"{base_result.detection_method}_+learning"
        )
        
        # Add learning_score attribute for test compatibility
        enhanced_result.learning_score = learning_score
        
        # Use hybrid fusion (pattern + LLM with learning)
        final_result = self.hybrid_classifier.fuse_results(None, enhanced_result)
        final_result.learning_score = learning_score
        
        return final_result
    
    def _calculate_learning_boost(self, content: str, predicted_type: str) -> float:
        """Calculate confidence boost based on learning history"""
        
        if predicted_type not in self.learning_examples:
            return 0.0
        
        # Extract patterns from current content
        content_patterns = self._extract_patterns(content)
        
        if predicted_type not in self.pattern_weights:
            return 0.0
        
        # Calculate boost based on pattern weights
        total_boost = 0.0
        pattern_matches = 0
        
        for pattern in content_patterns:
            if pattern in self.pattern_weights[predicted_type]:
                total_boost += self.pattern_weights[predicted_type][pattern]
                pattern_matches += 1
        
        # Average boost, scaled by number of examples we've learned from
        if pattern_matches > 0:
            avg_boost = total_boost / pattern_matches
            example_count = len(self.learning_examples[predicted_type])
            
            # Scale boost by learning experience (more examples = more confidence)
            experience_multiplier = min(1.0, example_count / 5.0)  # Max at 5 examples
            
            return avg_boost * experience_multiplier * 0.4  # Max 40% boost
        
        return 0.0
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learning progress"""
        stats = {
            "total_examples": sum(len(examples) for examples in self.learning_examples.values()),
            "content_types_learned": list(self.learning_examples.keys()),
            "pattern_weights_count": sum(len(weights) for weights in self.pattern_weights.values())
        }
        
        for content_type, examples in self.learning_examples.items():
            stats[f"{content_type}_examples"] = len(examples)
        
        return stats