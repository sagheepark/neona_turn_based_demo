# 🚀 Continuous Answer Tool Architecture: Proactive Multi-Step Character Interactions

## 🎯 **VISION: World-Class Proactive AI Character Platform**

Enable characters to conduct **intelligent multi-step conversations** where user actions trigger **continuous, proactive responses** without manual prompts. Starting with quiz interactions, expanding to complex character scenarios.

---

## 📋 **REQUIREMENTS ANALYSIS**

### **Current Quiz Flow (Static):**
```
User: "조선시대 퀴즈"
→ LLM: Quiz with A/B/C/D options
→ User selects: "A) 한글 창제" 
→ LLM: "정답입니다!" [END]
```

### **Desired Continuous Flow (Proactive):**
```
User: "조선시대 퀴즈"  
→ LLM: Quiz with A/B/C/D options
→ User selects: "A) 한글 창제"
→ CONTINUOUS TOOL TRIGGERED:
   ├─ Step 1: LLM feedback + TTS: "정답입니다! 세종대왕이 1443년에..." 🔊
   ├─ [Audio plays, user listens]
   └─ Step 2: Auto-trigger next LLM: "다음 문제입니다. 임진왜란은?" 🔊
```

### **Key Requirements:**
- ✅ **Multi-step orchestration**: Answer → Feedback → Next Question
- ✅ **Audio-driven progression**: Next step triggers after TTS completion
- ✅ **Proactive character**: No "ready for next?" prompts
- ✅ **Provider customizable**: Different quiz styles, character behaviors
- ✅ **Platform extensible**: Support various character use cases

---

## 🏗️ **ARCHITECTURE: 4-Layer Continuous Tool System**

```
┌─────────────────────────────────────────────────────────────┐
│                    PROVIDER LAYER                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────────── │
│  │ Character       │ │  Flow           │ │   Provider      ││
│  │ Behavior        │ │ Definitions     │ │   Documentation ││
│  │ Patterns        │ │ (JSON Config)   │ │   & Examples    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 ORCHESTRATION LAYER                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ Continuous      │ │   Multi-Step    │ │  Audio-Driven   ││
│  │ Flow Engine     │ │   Planner       │ │  Progression    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Tool State    │ │     LLM         │ │   TTS + Audio   ││
│  │   Management    │ │   Orchestrator  │ │   Completion    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Quiz UI       │ │  Audio Player   │ │   Progress      ││
│  │   Components    │ │  with Callbacks │ │   Indicators    ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 **LAYER 1: Continuous Flow Engine**

### **Core Concept: Flow-Based Tool System**
```python
class ContinuousAnswerTool:
    """
    Orchestrates multi-step character interactions triggered by user actions
    """
    
    def __init__(self):
        self.flow_definitions = self.load_flow_configs()
        self.active_flows = {}  # session_id -> FlowState
        
    async def trigger_flow(self, trigger_event: ToolTriggerEvent) -> FlowExecution:
        """
        Main entry point for continuous flows
        """
        flow_config = self.get_flow_config(trigger_event.character_id, trigger_event.tool_type)
        
        if not flow_config:
            return None
            
        # Initialize flow state
        flow_state = FlowState(
            session_id=trigger_event.session_id,
            character_id=trigger_event.character_id,
            flow_config=flow_config,
            trigger_data=trigger_event.data
        )
        
        self.active_flows[trigger_event.session_id] = flow_state
        
        # Execute first step
        return await self.execute_flow_step(flow_state, step_index=0)
```

### **Flow Configuration System:**
```python
# Example: Quiz Continuous Flow Configuration
QUIZ_FLOW_CONFIG = {
    "flow_id": "quiz_continuous_v1",
    "character_types": ["seol_min_seok_quiz", "history_teacher"],
    "trigger": {
        "tool_type": "show_selection",
        "event": "user_selection"
    },
    "steps": [
        {
            "step_id": "feedback_generation",
            "type": "llm_response",
            "prompt_template": "quiz_feedback_prompt",
            "context": {
                "user_answer": "${trigger_data.selection}",
                "correct_answer": "${trigger_data.correct_answer}",
                "question": "${trigger_data.question}"
            },
            "audio_enabled": True,
            "next_trigger": "audio_completion"
        },
        {
            "step_id": "next_action_decision",
            "type": "llm_response", 
            "condition": "audio_completion",
            "prompt_template": "quiz_next_step_prompt",
            "context": {
                "was_correct": "${step_0.result.was_correct}",
                "character_personality": "${character.proactive_level}"
            },
            "audio_enabled": True,
            "next_trigger": null  # End of flow
        }
    ],
    "prompts": {
        "quiz_feedback_prompt": """
        You just received the user's answer: ${user_answer}
        The correct answer was: ${correct_answer}
        
        Provide enthusiastic feedback and explanation. Be encouraging and educational.
        Then prepare to give the next question proactively.
        """,
        "quiz_next_step_prompt": """
        ${was_correct ? 
          "Great! The user got it right. Give them the next challenging question." :
          "The user got it wrong but learned something. Give them a related question to build confidence."
        }
        
        Be proactive - don't ask if they're ready. Just naturally transition to the next question.
        """
    }
}
```

---

## 🔄 **LAYER 2: Multi-Step Orchestration**

### **Flow State Management:**
```python
@dataclass
class FlowState:
    session_id: str
    character_id: str
    flow_config: Dict
    current_step: int = 0
    step_results: List[Dict] = field(default_factory=list)
    trigger_data: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
class FlowOrchestrator:
    async def execute_flow_step(self, flow_state: FlowState, step_index: int) -> StepResult:
        """Execute a single step in the continuous flow"""
        
        step_config = flow_state.flow_config["steps"][step_index]
        
        if step_config["type"] == "llm_response":
            return await self.execute_llm_step(flow_state, step_config)
        elif step_config["type"] == "wait_condition":
            return await self.setup_condition_wait(flow_state, step_config)
        elif step_config["type"] == "tool_action":
            return await self.execute_tool_action(flow_state, step_config)
            
    async def execute_llm_step(self, flow_state: FlowState, step_config: Dict) -> StepResult:
        """Execute LLM generation step with context injection"""
        
        # Build context from previous steps and trigger data
        context = self.build_step_context(flow_state, step_config["context"])
        
        # Get prompt template and inject context
        prompt_template = flow_state.flow_config["prompts"][step_config["prompt_template"]]
        final_prompt = self.inject_context(prompt_template, context)
        
        # Generate LLM response
        response = await self.llm_service.generate_response(
            character_id=flow_state.character_id,
            prompt=final_prompt,
            context=context
        )
        
        # Generate TTS if enabled
        audio_data = None
        if step_config.get("audio_enabled", False):
            audio_data = await self.tts_service.generate_audio(
                text=response.dialogue,
                character_id=flow_state.character_id
            )
        
        return StepResult(
            step_id=step_config["step_id"],
            response=response,
            audio=audio_data,
            next_trigger=step_config.get("next_trigger")
        )
```

---

## 🎵 **LAYER 3: Audio-Driven Progression**

### **Audio Completion Detection System:**
```typescript
// Frontend: Enhanced AudioPlayer with flow callbacks
interface AudioPlayerProps {
  audioBase64: string
  onPlayEnd?: () => void
  onFlowStepComplete?: (stepId: string) => void  // NEW
  flowContext?: {
    sessionId: string
    stepId: string
    nextStepTrigger?: string
  }
}

export function AudioPlayer({ 
  audioBase64, 
  onPlayEnd, 
  onFlowStepComplete,
  flowContext
}: AudioPlayerProps) {
  const handleAudioEnd = () => {
    onPlayEnd?.()
    
    // Trigger next step in continuous flow
    if (flowContext?.nextStepTrigger === 'audio_completion') {
      onFlowStepComplete?.(flowContext.stepId)
    }
  }
  
  useEffect(() => {
    if (audio) {
      audio.addEventListener('ended', handleAudioEnd)
      return () => audio.removeEventListener('ended', handleAudioEnd)
    }
  }, [audio, flowContext])
}
```

### **Flow Progression API:**
```python
@app.post("/api/continuous-flow/progress")
async def progress_continuous_flow(request: FlowProgressRequest):
    """
    API endpoint for progressing continuous flows
    Called when conditions are met (e.g., audio completion)
    """
    
    flow_state = continuous_tool.get_active_flow(request.session_id)
    if not flow_state:
        return {"error": "No active flow"}
    
    # Check if condition is met for progression
    if request.trigger_type == "audio_completion":
        next_step_index = flow_state.current_step + 1
        
        if next_step_index < len(flow_state.flow_config["steps"]):
            # Execute next step
            result = await continuous_tool.execute_flow_step(
                flow_state, next_step_index
            )
            
            return {
                "status": "step_executed",
                "step_result": result,
                "flow_continues": True
            }
        else:
            # Flow completed
            continuous_tool.complete_flow(request.session_id)
            return {
                "status": "flow_completed",
                "flow_continues": False
            }
    
    return {"error": "Invalid trigger"}
```

---

## 🎨 **LAYER 4: Provider Customization System**

### **Character Behavior Patterns:**
```json
{
  "character_profiles": {
    "seol_min_seok_quiz": {
      "proactive_level": "high",
      "interaction_style": "enthusiastic_teacher",
      "flow_preferences": {
        "quiz_flow": {
          "feedback_detail": "comprehensive",
          "next_question_delay": "immediate_after_audio",
          "encouragement_style": "motivational"
        }
      }
    },
    "gentle_tutor": {
      "proactive_level": "medium", 
      "interaction_style": "supportive_guide",
      "flow_preferences": {
        "quiz_flow": {
          "feedback_detail": "gentle_correction",
          "next_question_delay": "pause_for_reflection",
          "encouragement_style": "supportive"
        }
      }
    }
  }
}
```

### **Provider Configuration Documentation:**
```markdown
# Continuous Flow Configuration Guide

## Creating Custom Quiz Flows

### Basic Configuration:
```json
{
  "flow_id": "your_custom_quiz_flow",
  "character_types": ["your_character_id"],
  "trigger": {
    "tool_type": "show_selection",
    "event": "user_selection"
  },
  "steps": [...]
}
```

### Available Step Types:
- `llm_response`: Generate character response
- `wait_condition`: Wait for external trigger
- `tool_action`: Execute additional tools

### Context Variables:
- `${trigger_data.*}`: Access trigger event data
- `${step_N.result.*}`: Access previous step results
- `${character.*}`: Access character configuration
```

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Phase 1: Core Continuous Tool (Week 1)**
- ✅ Implement `ContinuousAnswerTool` class
- ✅ Create flow configuration system
- ✅ Build basic multi-step orchestration
- ✅ Test with simple quiz feedback flow

### **Phase 2: Audio-Driven Progression (Week 2)**
- ✅ Enhance AudioPlayer with flow callbacks
- ✅ Implement audio completion triggers
- ✅ Create `/api/continuous-flow/progress` endpoint
- ✅ Test complete quiz → feedback → next question flow

### **Phase 3: Provider Customization (Week 3)**
- ✅ Build character behavior pattern system
- ✅ Create provider configuration documentation
- ✅ Implement flow template system
- ✅ Test with multiple character types

### **Phase 4: Platform Features (Week 4)**
- ✅ Add flow debugging and monitoring
- ✅ Implement error handling and recovery
- ✅ Create flow analytics and insights
- ✅ Performance optimization

---

## 🎯 **SPECIFIC QUIZ USE CASE IMPLEMENTATION**

### **Quiz Flow Trigger Integration:**
```python
# Update platform_content_classifier.py
def _convert_to_quiz_tool(self, classification_result) -> Dict[str, Any]:
    detected_elements = classification_result.detected_elements
    
    return {
        "type": "show_selection",
        "continuous_enabled": True,  # NEW: Enable continuous flow
        "flow_config": "quiz_continuous_v1",  # NEW: Specify flow
        "data": {
            "question": detected_elements.get("question", ""),
            "items": detected_elements.get("options", []),
            "correctAnswer": detected_elements.get("correct_answer", ""),
            "metadata": {
                "labels": detected_elements.get("labels", []),
                "continuous_context": {  # NEW: Context for continuous flow
                    "quiz_topic": classification_result.metadata.get("topic"),
                    "difficulty": classification_result.metadata.get("difficulty")
                }
            }
        }
    }
```

### **Frontend Integration:**
```typescript
const handleToolSelection = (selection: string) => {
  console.log('Tool selection:', selection)
  
  // Check if tool supports continuous flow
  if (currentTools[0].continuous_enabled) {
    // Trigger continuous flow instead of normal chat
    triggerContinuousFlow({
      sessionId,
      toolType: currentTools[0].type,
      selection,
      correctAnswer: currentTools[0].data.correctAnswer,
      flowConfig: currentTools[0].flow_config
    })
  } else {
    // Legacy behavior
    setCurrentTools([])
    handleSend(selection)
  }
}

const triggerContinuousFlow = async (flowData: ContinuousFlowTrigger) => {
  const response = await fetch('/api/continuous-flow/trigger', {
    method: 'POST',
    body: JSON.stringify(flowData)
  })
  
  const result = await response.json()
  
  if (result.step_result) {
    // Display first step (feedback) with audio
    displayFlowStep(result.step_result)
  }
}
```

---

## 🏆 **EXPECTED OUTCOMES**

### **Immediate Benefits:**
- ✅ **Proactive quiz interactions**: Character automatically provides feedback and next questions
- ✅ **Seamless user experience**: No manual prompts, audio-driven progression
- ✅ **Character personality**: Different quiz styles per character configuration

### **Platform Benefits:**
- ✅ **Extensible architecture**: Easy to add new continuous flow types (polls, games, tutorials)
- ✅ **Provider customization**: Character creators can configure behavior patterns
- ✅ **Developer experience**: Clear configuration system with documentation

### **Future Capabilities:**
- ✅ **Complex conversations**: Multi-branching dialogues, conditional responses
- ✅ **Advanced interactions**: Storytelling flows, educational sequences, therapeutic conversations
- ✅ **AI-driven adaptation**: Flows that adapt based on user responses and engagement

---

## 💡 **WHY THIS IS WORLD-CLASS**

1. **🎯 Problem-Solving Excellence**: Directly solves the proactive quiz interaction challenge
2. **🏗️ Platform Architecture**: Extensible system supporting diverse character use cases
3. **👥 Provider-Friendly**: Clear customization with documentation and examples
4. **🚀 Future-Proof**: Foundation for advanced conversational AI experiences
5. **⚡ Performance**: Efficient flow state management and audio-driven progression

**This architecture transforms static character interactions into dynamic, proactive conversations that feel naturally intelligent and engaging.**
