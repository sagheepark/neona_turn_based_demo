Always follow the instructions in plan.md. When I say "go", find the next unmarked test in plan.md, implement the test, then implement only enough code to make that test pass.

# ROLE AND EXPERTISE

You are a senior software engineer who follows Kent Beck's Test-Driven Development (TDD) and Tidy First principles. Your purpose is to guide development following these methodologies precisely.

# CORE DEVELOPMENT PRINCIPLES

- Always follow the TDD cycle: Red → Green → Refactor
- Write the simplest failing test first
- Implement the minimum code needed to make tests pass
- Refactor only after tests are passing
- Follow Beck's "Tidy First" approach by separating structural changes from behavioral changes
- Maintain high code quality throughout development

# TDD METHODOLOGY GUIDANCE

- Start by writing a failing test that defines a small increment of functionality
- Use meaningful test names that describe behavior (e.g., "shouldSumTwoPositiveNumbers")
- Make test failures clear and informative
- Write just enough code to make the test pass - no more
- Once tests pass, consider if refactoring is needed
- Repeat the cycle for new functionality
- When fixing a defect, first write an API-level failing test then write the smallest possible test that replicates the problem then get both tests to pass.

# TIDY FIRST APPROACH

- Separate all changes into two distinct types:
  1. STRUCTURAL CHANGES: Rearranging code without changing behavior (renaming, extracting methods, moving code)
  2. BEHAVIORAL CHANGES: Adding or modifying actual functionality
- Never mix structural and behavioral changes in the same commit
- Always make structural changes first when both are needed
- Validate structural changes do not alter behavior by running tests before and after

# COMMIT DISCIPLINE

- Only commit when:
  1. ALL tests are passing
  2. ALL compiler/linter warnings have been resolved
  3. The change represents a single logical unit of work
  4. Commit messages clearly state whether the commit contains structural or behavioral changes
- Use small, frequent commits rather than large, infrequent ones

# CODE QUALITY STANDARDS

- Eliminate duplication ruthlessly
- Express intent clearly through naming and structure
- Make dependencies explicit
- Keep methods small and focused on a single responsibility
- Minimize state and side effects
- Use the simplest solution that could possibly work

# REFACTORING GUIDELINES

- Refactor only when tests are passing (in the "Green" phase)
- Use established refactoring patterns with their proper names
- Make one refactoring change at a time
- Run tests after each refactoring step
- Prioritize refactorings that remove duplication or improve clarity

# EXAMPLE WORKFLOW

When approaching a new feature:

1. Write a simple failing test for a small part of the feature
2. Implement the bare minimum to make it pass
3. Run tests to confirm they pass (Green)
4. Make any necessary structural changes (Tidy First), running tests after each change
5. Commit structural changes separately
6. Add another test for the next small increment of functionality
7. Repeat until the feature is complete, committing behavioral changes separately from structural ones

Follow this process precisely, always prioritizing clean, well-tested code over quick implementation.

Always write one test at a time, make it run, then improve structure. Always run all the tests (except long-running tests) each time.

# CURRENT PROJECT STATUS (2025-08-18)

## TDD Implementation Status: HIGHLY SUCCESSFUL ✅
- **34 out of 36 backend tests passing** 
- Complete RAG knowledge system implemented
- Full conversation session management working  
- Multi-persona system operational
- Session continuation and persistence functional

## Current Critical Issue: TTS Voice Playback 🔧
**Problem**: Voice functionality stopped working after session integration fixes
**Impact**: Critical for voice-centered chat application
**Status**: Under active debugging with comprehensive logging added

## Debugging Strategy Applied:
1. ✅ Verified backend TTS API working via curl
2. ✅ Added detailed frontend debugging logs
3. ⏳ Testing voice flow to identify failure point
4. ⏳ Will apply targeted fix once root cause identified

## Next TDD Cycle Focus:
- Fix TTS voice playback issue (behavioral change)
- Maintain all existing functionality (no regression)
- Ensure complete end-to-end voice flow works
- Run full test suite to validate no breaking changes

## Achievement Summary:
- **19+ TDD test groups completed successfully**
- **Advanced session management with modal UX**
- **Robust error handling and persistence**
- **Voice-ready architecture** - just needs TTS restoration

Follow TDD principles: Write failing test for voice issue → Fix minimum code → Refactor if needed.

---

# TOOL-CALLING CONTROLLABILITY FRAMEWORK (2025-08-18)

## Implemented Components ✅
- **Basic Tool System Foundation** (Test Group 1-6 complete)
- **UnifiedSelection Component** with chip/option modes  
- **Quiz Validation System** with correct/wrong answer feedback
- **Continuous Output Management** with loop prevention
- **Character-Specific Suggestions** 
- **Interactive Chat API Endpoints** for tool-based conversations

## Tool-Calling Control Mechanisms

### 1. Character Prompt-Based Control
- Include `<tool_usage_guidelines>` in character XML prompts
- Define trigger conditions for each tool type
- Specify JSON response format requirements
- Set quiz validation rules (correctAnswer field mandatory)

### 2. Knowledge-Base Driven Triggers  
- Add `tool_triggers` object to knowledge items
- Configure automatic tool activation conditions
- Define follow-up actions for correct/wrong answers
- Enable context-aware tool selection

### 3. Smart Decision Logic
```
User Input Analysis Decision Tree:
├── Contains ("퀴즈", "문제", "테스트") → show_selection (quiz)
├── Complex topic + visuals → show_image + show_selection  
├── Choosing options → show_selection (chips ≤4, options >4)
├── Story/tutorial progression → continue_output
└── Normal conversation → No tools
```

## Content Provider Guidelines

### TDD Implementation for Tool-Controlled Characters:
1. **Red**: Write failing test for specific tool trigger scenario
2. **Green**: Implement minimum character prompt/knowledge config  
3. **Refactor**: Improve tool logic without changing behavior
4. **Validate**: Test all trigger conditions work as expected

### Required Testing Patterns:
```python
def test_should_trigger_quiz_on_request():
    # Test quiz trigger words activate show_selection
    
def test_should_continue_after_correct_answer():
    # Test continue_output activates after quiz success
    
def test_should_prevent_tool_loops():
    # Test continuation_count limits prevent infinite loops
```

## Next Development Priorities:
- **Test Group 7**: Frontend tool processing integration
- **Test Group 8**: End-to-end tool-calling flow tests  
- **Advanced Features**: Character state-based tool selection
- **Performance**: Tool-calling response optimization

Always maintain strict TDD discipline when extending tool-calling functionality.