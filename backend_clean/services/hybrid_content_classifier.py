"""
Hybrid Content Classifier
Combines pattern-based and LLM-based classification with confidence scoring
"""
from typing import Optional
from services.llm_structured_classifier import ClassificationResult


class HybridContentClassifier:
    """Hybrid content classifier that combines multiple detection methods"""
    
    def __init__(self):
        self.confidence_boost_factor = 0.15  # Boost when methods agree
        self.disagreement_threshold = 0.1    # Threshold for considering results different
    
    def fuse_results(
        self, 
        pattern_result: Optional[ClassificationResult],
        llm_result: ClassificationResult
    ) -> ClassificationResult:
        """
        Fuse classification results from pattern and LLM methods
        
        Args:
            pattern_result: Result from pattern-based classification (can be None)
            llm_result: Result from LLM-based classification
            
        Returns:
            Fused classification result with confidence scoring
        """
        
        # If no pattern result, return LLM result with adjusted confidence
        if not pattern_result:
            return self._adjust_llm_only_result(llm_result)
        
        # Check if methods agree on content type
        if pattern_result.content_type == llm_result.content_type:
            return self._boost_confidence_for_agreement(pattern_result, llm_result)
        
        # Methods disagree - resolve by confidence
        return self._resolve_disagreement(pattern_result, llm_result)
    
    def _adjust_llm_only_result(self, llm_result: ClassificationResult) -> ClassificationResult:
        """Adjust confidence for LLM-only results"""
        # Slightly reduce confidence since we don't have pattern confirmation
        adjusted_confidence = max(0.0, llm_result.confidence - 0.05)
        
        return ClassificationResult(
            content_type=llm_result.content_type,
            confidence=adjusted_confidence,
            detected_elements=llm_result.detected_elements,
            suggested_tools=llm_result.suggested_tools,
            metadata=llm_result.metadata,
            detection_method="llm_only"
        )
    
    def _boost_confidence_for_agreement(
        self, 
        pattern_result: ClassificationResult,
        llm_result: ClassificationResult
    ) -> ClassificationResult:
        """Boost confidence when both methods agree"""
        
        # Calculate boosted confidence - use weighted average with boost
        base_confidence = max(pattern_result.confidence, llm_result.confidence)
        agreement_boost = self.confidence_boost_factor
        
        # Boost confidence but cap at 1.0
        boosted_confidence = min(1.0, base_confidence + agreement_boost)
        
        # Use LLM result as base (more detailed) but boost confidence
        # and merge metadata if available
        merged_metadata = {**llm_result.metadata}
        if pattern_result.metadata:
            merged_metadata.update(pattern_result.metadata)
        
        return ClassificationResult(
            content_type=llm_result.content_type,
            confidence=boosted_confidence,
            detected_elements=llm_result.detected_elements,  # LLM usually more detailed
            suggested_tools=llm_result.suggested_tools,
            metadata=merged_metadata,
            detection_method="hybrid"
        )
    
    def _resolve_disagreement(
        self, 
        pattern_result: ClassificationResult,
        llm_result: ClassificationResult
    ) -> ClassificationResult:
        """Resolve disagreement between methods by choosing higher confidence"""
        
        # Choose the result with higher confidence
        if pattern_result.confidence > llm_result.confidence:
            winner = pattern_result
            detection_method = "pattern_preferred"
        else:
            winner = llm_result  
            detection_method = "llm_preferred"
        
        # No penalty for disagreement - use winning confidence as-is
        adjusted_confidence = winner.confidence
        
        return ClassificationResult(
            content_type=winner.content_type,
            confidence=adjusted_confidence,
            detected_elements=winner.detected_elements,
            suggested_tools=winner.suggested_tools,
            metadata=winner.metadata,
            detection_method=detection_method
        )
    
    def calculate_confidence_score(
        self,
        pattern_confidence: Optional[float],
        llm_confidence: float,
        agreement: bool
    ) -> float:
        """
        Calculate final confidence score based on multiple factors
        
        Args:
            pattern_confidence: Confidence from pattern matching (None if not available)
            llm_confidence: Confidence from LLM classification
            agreement: Whether methods agree on classification
            
        Returns:
            Final confidence score between 0.0 and 1.0
        """
        
        if pattern_confidence is None:
            # LLM only - slight penalty for lack of confirmation
            return max(0.0, llm_confidence - 0.05)
        
        if agreement:
            # Methods agree - boost confidence
            base_confidence = max(pattern_confidence, llm_confidence)
            return min(1.0, base_confidence + self.confidence_boost_factor)
        else:
            # Methods disagree - use higher confidence with penalty
            higher_confidence = max(pattern_confidence, llm_confidence)
            return max(0.0, higher_confidence - 0.05)
    
    def get_fusion_strategy(
        self,
        pattern_result: Optional[ClassificationResult],
        llm_result: ClassificationResult
    ) -> str:
        """
        Determine which fusion strategy was used
        
        Returns:
            Strategy name for debugging/monitoring
        """
        
        if not pattern_result:
            return "llm_only"
        
        if pattern_result.content_type == llm_result.content_type:
            return "agreement_boost"
        else:
            return "disagreement_resolution"