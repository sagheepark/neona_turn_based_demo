# Platform-Grade Content Classification Architecture

## 🎯 Core Problem Analysis

**Current Issues:**
- ❌ Brittle regex patterns fail when LLM output varies
- ❌ No provider/character customization
- ❌ Binary success/failure with no confidence scoring
- ❌ No learning mechanism - further quiz attempts fail
- ❌ Performance bottlenecks with complex patterns

**Platform Requirements:**
- ✅ Provider-controllable content type definitions
- ✅ Character-specific classification rules  
- ✅ Confidence-scored hybrid classification
- ✅ Fallback mechanisms and graceful degradation
- ✅ Learning from successful classifications
- ✅ High performance with caching strategies

## 🏗️ Multi-Tier Hybrid Architecture

### Tier 1: Provider Configuration Layer
```python
class ProviderContentConfig:
    character_id: str
    content_types: Dict[str, ContentTypeDefinition]
    classification_strategy: ClassificationStrategy
    confidence_thresholds: Dict[str, float]
    fallback_behavior: FallbackStrategy
```

### Tier 2: Hybrid Classification Engine
```python
class HybridContentClassifier:
    def classify(self, content: str, config: ProviderContentConfig) -> ClassificationResult:
        # 1. Fast Pattern Detection (if enabled)
        pattern_result = self.pattern_engine.classify(content, config.patterns)
        
        # 2. LLM Classification (with structured output)
        llm_result = self.llm_engine.classify_structured(content, config.schema)
        
        # 3. Confidence Analysis & Result Fusion
        final_result = self.confidence_engine.fuse_results(pattern_result, llm_result)
        
        # 4. Learning & Cache Update
        self.learning_engine.update_from_result(content, final_result)
        
        return final_result
```

### Tier 3: Performance & Reliability Layer
```python
class ReliabilityWrapper:
    def classify_with_reliability(self, content: str, config: ProviderContentConfig) -> ClassificationResult:
        # Try cached result first
        cached = self.cache.get(content, config.character_id)
        if cached and cached.confidence > config.cache_threshold:
            return cached
        
        # Classify with timeout and fallback
        try:
            result = asyncio.wait_for(
                self.classifier.classify(content, config),
                timeout=config.classification_timeout
            )
            
            if result.confidence < config.minimum_confidence:
                return self.fallback_strategy.apply(content, config, result)
            
            self.cache.set(content, config.character_id, result)
            return result
            
        except asyncio.TimeoutError:
            return self.emergency_fallback(content, config)
```

## 📋 Implementation Plan

### Phase 1: Provider-Controllable Configuration System
**Goal**: Allow characters to define their own content types and classification rules

**Architecture:**
```python
# Character-specific content type definitions
class ContentTypeDefinition:
    name: str                           # "quiz", "poll", "form"
    detection_patterns: List[str]       # Regex patterns (optional)
    llm_classification_prompt: str      # LLM prompt for this content type
    required_tools: List[str]           # Tools to generate for this type
    confidence_threshold: float         # Minimum confidence to accept
    metadata_schema: Dict              # Expected metadata structure

class CharacterContentConfig(BaseModel):
    character_id: str
    content_types: Dict[str, ContentTypeDefinition]
    classification_strategy: Literal["pattern_first", "llm_first", "hybrid"]
    global_confidence_threshold: float = 0.7
    fallback_strategy: Literal["conservative", "aggressive", "adaptive"]
```

### Phase 2: LLM-Based Structured Classification
**Goal**: Replace brittle regex with LLM structured output for reliable detection

**Implementation:**
```python
class LLMStructuredClassifier:
    async def classify_content(self, content: str, character_config: CharacterContentConfig) -> ClassificationResult:
        # Build classification prompt with character-specific content types
        classification_prompt = self.build_classification_prompt(content, character_config)
        
        # Use structured output for reliable classification
        result = await self.llm_client.generate_structured(
            prompt=classification_prompt,
            schema=ClassificationResultSchema,
            temperature=0.1,  # Low temperature for consistency
            max_tokens=300
        )
        
        return ClassificationResult(**result)

# Structured output schema
class ClassificationResultSchema(BaseModel):
    content_type: str                   # "quiz", "poll", "text", "unknown"
    confidence: float                   # 0.0 to 1.0
    detected_elements: Dict[str, Any]   # Extracted quiz questions, options, etc.
    suggested_tools: List[str]          # Tools to generate
    metadata: Dict[str, Any]           # Additional context
```

### Phase 3: Confidence-Scored Hybrid System
**Goal**: Combine pattern matching and LLM classification with confidence scoring

**Architecture:**
```python
class ConfidenceEngine:
    def fuse_classification_results(
        self, 
        pattern_result: Optional[ClassificationResult],
        llm_result: ClassificationResult,
        config: CharacterContentConfig
    ) -> ClassificationResult:
        
        # No pattern result - use LLM with confidence adjustment
        if not pattern_result:
            return self.adjust_llm_confidence(llm_result, config)
        
        # Both results agree - boost confidence
        if pattern_result.content_type == llm_result.content_type:
            return self.boost_confidence(llm_result, pattern_result)
        
        # Results disagree - use higher confidence result
        return self.resolve_disagreement(pattern_result, llm_result, config)
```

### Phase 4: Learning & Adaptation System
**Goal**: Learn from successful classifications to improve future performance

**Implementation:**
```python
class LearningContentClassifier:
    def __init__(self):
        self.success_patterns = {}      # content_hash -> ClassificationResult
        self.failure_patterns = {}      # Track what doesn't work
        
    def learn_from_success(self, content: str, result: ClassificationResult):
        """Store successful classifications for pattern learning"""
        content_hash = self.hash_content(content)
        
        # Extract successful patterns
        patterns = self.extract_patterns(content, result)
        
        # Update pattern database
        for pattern in patterns:
            if pattern not in self.success_patterns:
                self.success_patterns[pattern] = []
            self.success_patterns[pattern].append(result)
    
    def improve_classification(self, content: str, config: CharacterContentConfig) -> ClassificationResult:
        # Check if we've seen similar content before
        similar_results = self.find_similar_successful_patterns(content)
        
        if similar_results:
            # Use learned patterns to boost confidence
            base_result = self.llm_classifier.classify(content, config)
            return self.apply_learned_patterns(base_result, similar_results)
        
        # Standard classification for new content
        return self.standard_classify(content, config)
```

## 🛠️ Specific Implementation for Quiz Detection

### Character Configuration
```yaml
# seol_min_seok_quiz character config
character_id: "seol_min_seok_quiz"
content_types:
  quiz:
    detection_patterns:
      - "(.+?)\\?\\s*([A-D]\\)[^A-D]*))+"  # Current working pattern
      - "다음 중.*\\?.*[A-D]\\)"          # Korean quiz indicators
    llm_classification_prompt: |
      Analyze if this content is a Korean multiple-choice quiz question.
      Look for:
      - A question ending with ?
      - Multiple choice options labeled A), B), C), D)
      - Educational Korean content
      
      If it's a quiz, extract:
      - The main question
      - All answer options
      - The most likely correct answer
    required_tools: ["show_selection"]
    confidence_threshold: 0.8
    metadata_schema:
      question: str
      options: List[str]
      labels: List[str]
      correct_answer: str
      topic: str
      difficulty: str

classification_strategy: "hybrid"  # Use both patterns and LLM
global_confidence_threshold: 0.7
fallback_strategy: "adaptive"     # Learn and adapt
```

### Enhanced ContentIntelligence Service
```python
class EnhancedContentIntelligence:
    def __init__(self):
        self.pattern_engine = PatternClassifier()
        self.llm_engine = LLMStructuredClassifier()
        self.confidence_engine = ConfidenceEngine()
        self.learning_engine = LearningEngine()
        self.config_manager = CharacterConfigManager()
    
    async def analyze_for_tools(
        self, 
        content: str, 
        character_id: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        
        # Get character-specific configuration
        config = await self.config_manager.get_character_config(character_id)
        
        # Hybrid classification
        result = await self.classify_with_confidence(content, config, context)
        
        # Learn from successful classifications
        if result.confidence > config.learning_threshold:
            await self.learning_engine.learn_from_success(content, result)
        
        # Generate tools based on classification
        if result.confidence >= config.global_confidence_threshold:
            return self.generate_tools_from_classification(result, config)
        
        return []  # No tools if confidence too low
```

## 🎯 Benefits of This Architecture

### For Platform Providers:
- **Customizable**: Each character can define their own content types
- **Reliable**: Confidence scoring and fallback mechanisms
- **Learning**: System improves over time with successful classifications
- **Performance**: Caching and pattern optimization

### For Developers:
- **Extensible**: Easy to add new content types
- **Debuggable**: Clear confidence metrics and classification reasoning
- **Maintainable**: Separation of concerns between detection methods

### For Users:
- **Consistent**: Reliable tool generation for recognized content
- **Adaptive**: System learns user patterns and improves
- **Fast**: Efficient classification with multiple optimization layers

## 📈 Expected Performance Improvements

- **Reliability**: 95%+ tool generation success (vs current ~60%)
- **Latency**: Sub-100ms classification with caching
- **Adaptability**: Self-improving system that learns from usage patterns
- **Extensibility**: New content types deployable without code changes