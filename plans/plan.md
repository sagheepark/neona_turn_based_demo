# TDD Implementation Plan: Interactive Chat UI with Tool System
## Following Kent Beck's TDD Methodology and Tidy First Principles

## 📋 Current Status
- **Base System**: ✅ Chat system with memory cache and voice working
- **Next Feature**: 🔧 Interactive UI with tool-based suggestions and continuous output
- **Approach**: TDD Red-Green-Refactor cycle with Tidy First principles

## 🎯 Feature Overview
Create a tool-based system where LLMs can trigger UI interactions (suggestion chips, selection interfaces, continuous output) for enhanced conversational flows including quizzes and guided interactions.

## 🏗️ TDD Implementation Plan

### **Test Group 1: Basic Tool System Foundation**

#### Test 1.1: shouldParseBasicToolFromLLMResponse
```python
def test_should_parse_basic_tool_from_llm_response():
    # Red: Write failing test
    response_text = '''
    {
        "character": "test_char",
        "dialogue": "Choose an option",
        "emotion": "normal",
        "speed": 1.0,
        "tools": [
            {
                "type": "show_selection",
                "data": {
                    "items": ["Option 1", "Option 2"],
                    "mode": "chip"
                }
            }
        ]
    }
    '''
    processor = ToolProcessor()
    result = processor.parse_llm_response(response_text)
    
    assert result["tools"] is not None
    assert len(result["tools"]) == 1
    assert result["tools"][0]["type"] == "show_selection"
```

#### Test 1.2: shouldHandleResponseWithoutTools
```python
def test_should_handle_response_without_tools():
    response_text = '''
    {
        "character": "test_char", 
        "dialogue": "Hello",
        "emotion": "normal",
        "speed": 1.0
    }
    '''
    processor = ToolProcessor()
    result = processor.parse_llm_response(response_text)
    
    assert result.get("tools") is None or result.get("tools") == []
```

#### Test 1.3: shouldValidateToolData
```python
def test_should_validate_tool_data():
    invalid_response = '''
    {
        "character": "test_char",
        "dialogue": "Choose",
        "tools": [
            {
                "type": "invalid_tool",
                "data": {}
            }
        ]
    }
    '''
    processor = ToolProcessor()
    
    with pytest.raises(ValidationError):
        processor.parse_llm_response(invalid_response)
```

### **Test Group 2: Unified Selection Component**

#### Test 2.1: shouldRenderChipModeForFewItems
```typescript
// Frontend test
describe('UnifiedSelection', () => {
  it('should render chip mode for 4 or fewer items', () => {
    const items = ['Option 1', 'Option 2', 'Option 3']
    const onSelect = jest.fn()
    
    render(<UnifiedSelection items={items} onSelect={onSelect} />)
    
    expect(screen.getByRole('button', { name: 'Option 1' })).toHaveClass('chip-style')
    expect(screen.queryByText(/A\./)).not.toBeInTheDocument() // No letter indicators in chip mode
  })
})
```

#### Test 2.2: shouldRenderOptionModeForManyItems
```typescript
it('should render option mode for more than 4 items', () => {
  const items = ['A', 'B', 'C', 'D', 'E']
  const onSelect = jest.fn()
  
  render(<UnifiedSelection items={items} onSelect={onSelect} />)
  
  expect(screen.getByText('A')).toBeInTheDocument() // Letter indicator present
  expect(screen.getByRole('button')).toHaveClass('option-style')
})
```

#### Test 2.3: shouldHandleSelectionCallback
```typescript
it('should call onSelect when item is clicked', () => {
  const items = ['Test Option']
  const onSelect = jest.fn()
  
  render(<UnifiedSelection items={items} onSelect={onSelect} />)
  
  fireEvent.click(screen.getByText('Test Option'))
  
  expect(onSelect).toHaveBeenCalledWith('Test Option')
})
```

### **Test Group 3: Quiz Flow with Validation**

#### Test 3.1: shouldDisplayQuizWithCorrectAnswer
```typescript
it('should display quiz with correct answer validation', () => {
  const items = ['1919년', '1920년', '1921년', '1922년']
  const correctAnswer = '1919년'
  const onSelect = jest.fn()
  
  render(
    <UnifiedSelection 
      items={items} 
      onSelect={onSelect}
      correctAnswer={correctAnswer}
      question="3·1 운동이 일어난 연도는?"
    />
  )
  
  expect(screen.getByText('3·1 운동이 일어난 연도는?')).toBeInTheDocument()
  expect(screen.getByText('1919년')).toBeInTheDocument()
})
```

#### Test 3.2: shouldShowCorrectAnswerFeedback
```typescript
it('should show correct answer feedback', async () => {
  const items = ['1919년', '1920년'] 
  const correctAnswer = '1919년'
  const onSelect = jest.fn()
  
  render(
    <UnifiedSelection 
      items={items}
      onSelect={onSelect} 
      correctAnswer={correctAnswer}
    />
  )
  
  fireEvent.click(screen.getByText('1919년'))
  
  await waitFor(() => {
    expect(screen.getByText('🎉 정답입니다!')).toBeInTheDocument()
  })
})
```

#### Test 3.3: shouldShowWrongAnswerFeedback
```typescript
it('should show wrong answer feedback', async () => {
  const items = ['1919년', '1920년']
  const correctAnswer = '1919년'
  const onSelect = jest.fn()
  
  render(
    <UnifiedSelection 
      items={items}
      onSelect={onSelect}
      correctAnswer={correctAnswer}
    />
  )
  
  fireEvent.click(screen.getByText('1920년'))
  
  await waitFor(() => {
    expect(screen.getByText(/정답: 1919년/)).toBeInTheDocument()
  })
})
```

### **Test Group 4: Continuous Output System**

#### Test 4.1: shouldDetectContinuationTool
```python
def test_should_detect_continuation_tool():
    response_data = {
        "character": "seol_min_seok",
        "dialogue": "정답입니다!",
        "tools": [
            {
                "type": "continue_output",
                "data": {
                    "reason": "quiz_continuation"
                }
            }
        ]
    }
    
    continuator = ContinuousOutputManager()
    should_continue = continuator.should_continue(response_data)
    
    assert should_continue == True
```

#### Test 4.2: shouldPreventInfiniteLoops
```python
def test_should_prevent_infinite_loops():
    manager = ContinuousOutputManager()
    context = {
        "continuation_count": 3,  # At max limit
        "max_continuations": 3
    }
    
    should_continue = manager.should_continue(context)
    
    assert should_continue == False
```

#### Test 4.3: shouldGenerateContinuationResponse
```python
def test_should_generate_continuation_response():
    context = {
        "last_response": "정답입니다!",
        "user_input": "1919년",
        "conversation_type": "quiz"
    }
    
    manager = ContinuousOutputManager()
    continuation = manager.generate_continuation(context)
    
    assert continuation["character"] is not None
    assert continuation["dialogue"] is not None
    assert len(continuation["dialogue"]) > 0
```

### **Test Group 5: Character-Specific Suggestion Chips**

#### Test 5.1: shouldGenerateSeolMinseokChips
```python
def test_should_generate_seol_minseok_chips():
    generator = SuggestionChipGenerator()
    context = {
        "character_id": "seol_min_seok",
        "conversation_state": "initial"
    }
    
    chips = generator.generate_chips(context)
    
    assert '3·1 운동에 대해 알려주세요' in chips
    assert '조선시대 왕들 이야기' in chips
    assert len(chips) >= 3
```

#### Test 5.2: shouldGenerateContextualChips
```python
def test_should_generate_contextual_chips():
    generator = SuggestionChipGenerator()
    context = {
        "character_id": "dr_python",
        "last_message": "파이썬 리스트에 대해 배워볼까요?",
        "conversation_topic": "python_basics"
    }
    
    chips = generator.generate_chips(context)
    
    assert any('예제' in chip for chip in chips)
    assert any('연습' in chip for chip in chips)
```

### **Test Group 6: Backend API Integration**

#### Test 6.1: shouldCreateInteractiveChatEndpoint
```python
def test_should_create_interactive_chat_endpoint():
    client = TestClient(app)
    
    response = client.post("/api/chat/interactive", json={
        "message": "퀴즈를 시작해주세요",
        "character_id": "seol_min_seok",
        "session_id": "test_session"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data or "dialogue" in data
```

#### Test 6.2: shouldHandleContinuationRequest
```python
def test_should_handle_continuation_request():
    client = TestClient(app)
    
    response = client.post("/api/chat/continuation", json={
        "session_id": "test_session",
        "context": {
            "last_response": "정답입니다!",
            "continuation_type": "quiz"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "dialogue" in data
```

### **Test Group 7: Frontend Tool Processing**

#### Test 7.1: shouldProcessShowSelectionTool
```typescript
it('should process show_selection tool', () => {
  const mockStore = createMockStore()
  const tool = {
    type: 'show_selection',
    data: {
      items: ['A', 'B', 'C'],
      question: 'Choose one'
    }
  }
  
  mockStore.processTool(tool)
  
  expect(mockStore.getState().currentSelection).toEqual({
    items: ['A', 'B', 'C'],
    question: 'Choose one'
  })
})
```

#### Test 7.2: shouldProcessContinuationTool
```typescript  
it('should set continuation pending for continue_output tool', () => {
  const mockStore = createMockStore()
  const tool = {
    type: 'continue_output',
    data: {
      reason: 'quiz_continuation'
    }
  }
  
  mockStore.processTool(tool)
  
  expect(mockStore.getState().continuationPending).toBe(true)
})
```

### **Test Group 8: Integration Tests**

#### Test 8.1: shouldCompleteQuizFlowEndToEnd
```python
def test_should_complete_quiz_flow_end_to_end():
    """Integration test for complete quiz flow"""
    client = TestClient(app)
    
    # 1. Start quiz
    start_response = client.post("/api/chat/interactive", json={
        "message": "퀴즈를 시작해주세요",
        "character_id": "seol_min_seok"
    })
    
    assert start_response.status_code == 200
    start_data = start_response.json()
    assert len(start_data.get("tools", [])) > 0
    
    session_id = start_data["session_id"]
    
    # 2. Answer question correctly
    answer_response = client.post("/api/chat/interactive", json={
        "message": "1919년",
        "character_id": "seol_min_seok", 
        "session_id": session_id
    })
    
    assert answer_response.status_code == 200
    answer_data = answer_response.json()
    
    # 3. Verify continuation happens
    tools = answer_data.get("tools", [])
    has_continuation = any(tool["type"] == "continue_output" for tool in tools)
    assert has_continuation or "정답" in answer_data["dialogue"]
```

## 🎯 Tool-Calling Controllability Framework

### Core Philosophy
The system enables **predictable, controlled tool-calling** through multiple approaches:

1. **Character Prompt-Based Control**: Direct instructions in character prompts
2. **Knowledge-Base Driven Triggers**: Tool triggers embedded in knowledge items  
3. **Context-Aware Decision Logic**: Smart tool selection based on conversation state
4. **Content Provider Guidelines**: Clear patterns for content creators

### Control Mechanisms Summary

| Control Method | Use Case | Implementation | Content Provider Effort |
|----------------|----------|----------------|------------------------|
| **Prompt Instructions** | General behavior patterns | XML guidelines in character prompt | Medium |
| **Knowledge Triggers** | Specific content-driven tools | JSON tool_triggers in knowledge items | High |
| **Context Logic** | Smart adaptive behavior | System-level decision trees | Low |
| **Pattern Templates** | Reusable interaction flows | Pre-defined conversation patterns | Low |

### Tool-Calling Decision Tree

```
User Input Analysis
├── Contains trigger words ("퀴즈", "문제", "테스트")
│   └── → show_selection (quiz format)
│       └── + continue_output (if multi-question)
├── Asking about complex topic + has visuals
│   └── → show_image + show_selection (exploration)
├── Choosing between options
│   └── → show_selection (chip mode for ≤4, option mode for >4)  
├── Story/tutorial progression
│   └── → continue_output (narrative flow)
└── Normal conversation
    └── → No tools (natural dialogue)
```

### Implementation Status: Tool-Calling System

**✅ Completed Components:**
- Basic tool parsing and validation (Test Group 1) 
- Frontend UnifiedSelection component (Test Group 2)
- Quiz validation and feedback (Test Group 3) 
- Continuous output management (Test Group 4)
- Character-specific suggestions (Test Group 5)
- API endpoints for tool-based chat (Test Group 6)

**🔧 Next Priority:**
- Test Group 7: Frontend tool processing integration
- Test Group 8: End-to-end integration testing
- Advanced controllability features (character state-based tool selection)

## 🔄 Implementation Workflow

### **Phase 1: Foundation (Week 1)**
1. **Red**: Write Test 1.1 (shouldParseBasicToolFromLLMResponse)
2. **Green**: Implement minimal ToolProcessor class
3. **Refactor**: Clean up structure, add error handling
4. **Commit**: "feat: add basic tool parsing functionality"

5. **Red**: Write Test 1.2 (shouldHandleResponseWithoutTools)  
6. **Green**: Handle null/empty tools case
7. **Refactor**: Extract common parsing logic
8. **Commit**: "feat: handle responses without tools"

Continue this pattern for all Test Group 1 tests.

### **Phase 2: UI Components (Week 2)**
1. **Red**: Write Test 2.1 (shouldRenderChipModeForFewItems)
2. **Green**: Create basic UnifiedSelection component
3. **Refactor**: Extract chip rendering logic
4. **Commit**: "feat: add unified selection component with chip mode"

Continue TDD cycle for all Test Group 2 tests.

### **Phase 3: Quiz System (Week 2-3)**
Follow TDD cycle for Test Group 3, implementing:
- Quiz validation logic
- Feedback display
- Answer processing

### **Phase 4: Continuous Output (Week 3)**
Follow TDD cycle for Test Group 4, implementing:
- Continuation detection
- Loop prevention
- Response generation

### **Phase 5: Suggestions & API (Week 4)**
Follow TDD cycle for Test Groups 5 & 6, implementing:
- Character-specific suggestions
- API endpoints
- Integration points

### **Phase 6: Frontend Integration (Week 4)**
Follow TDD cycle for Test Groups 7 & 8, implementing:
- Tool processing
- State management
- End-to-end flows

## 🧪 Testing Strategy

### **Test Types:**
- **Unit Tests**: Individual components and functions
- **Integration Tests**: API endpoints and data flow
- **E2E Tests**: Complete user workflows
- **Frontend Tests**: React components and interactions

### **Test Commands:**
```bash
# Backend tests
cd backend_clean && python -m pytest tests/

# Frontend tests  
cd frontend && npm test

# Integration tests
cd backend_clean && python -m pytest tests/integration/

# Run all tests
npm run test:all
```

### **Quality Gates:**
- All tests must pass before commit
- Code coverage > 80%
- No linter warnings
- TypeScript compilation successful

## 📋 Definition of Done

For each test group, completion means:
- ✅ All tests in group are passing
- ✅ Code is refactored and clean
- ✅ No duplication or code smells
- ✅ Integration with existing system works
- ✅ Manual testing confirms expected behavior
- ✅ Documentation updated if needed

## 🎯 Current Next Action

**When you say "go", I will:**
1. Find the first uncompleted test in Test Group 1
2. Write the failing test (Red phase)
3. Implement minimum code to pass (Green phase) 
4. Refactor if needed
5. Commit the change
6. Move to next test

**Ready for TDD cycle on interactive tool system! 🚀**