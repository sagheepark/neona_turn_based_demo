# Debug Checklist: Frontend Selection Issues

## Problem Analysis

Based on console logs, we have multiple interconnected issues:

### Issue 1: Code Version Mismatch
- **Symptom**: Console shows old log format, missing new debug logs
- **Likely Cause**: Frontend cache/hot reload not picking up changes
- **Solution**: Hard refresh browser (Ctrl+Shift+R) or restart Next.js dev server

### Issue 2: Wrong Flow Logic
- **Symptom**: `forceFlow: true` for greeting selections 
- **Root Cause**: Default correct answer being added: `'A) 한글 창제'`
- **Impact**: Makes topic selection look like quiz answer

### Issue 3: Continuous Flow Result Not Displaying
- **Symptom**: Flow triggers but no UI update
- **Root Cause**: `handleFlowStepResult` expects specific text patterns
- **Impact**: User sees no response after clicking

### Issue 4: Missing Audio
- **Symptom**: `audioLength: undefined`, "No audio in chat response"
- **Cause**: TTS service issues or audio processing failure

## Testing Checklist

### Step 1: Verify Code Updates Applied
- [ ] See `🆕 UPDATED CODE VERSION` in console when clicking
- [ ] See `🚨 SELECTION TYPE CHECK:` logs with correct values
- [ ] `correctAnswer: ''` (empty) for greeting tools
- [ ] `correctAnswer: 'actual_answer'` for quiz tools

### Step 2: Verify Logic Flow
- [ ] Greeting selection → `📝 Using regular message send`
- [ ] Quiz answer → `🚀 Triggering continuous flow`
- [ ] No more default `'A) 한글 창제'` in greeting flows

### Step 3: Verify UI Updates
- [ ] Greeting click → New message appears in chat
- [ ] Quiz answer → Educational feedback appears
- [ ] Tools cleared after selection
- [ ] Next question appears (if applicable)

### Step 4: Verify Audio
- [ ] Chat responses include audio data
- [ ] Audio plays automatically (after user interaction)
- [ ] TTS service responds successfully

## Implementation Plan

### Fix 1: Ensure Code Updates Applied
```bash
# Kill and restart Next.js dev server
# Hard refresh browser: Ctrl+Shift+R or Cmd+Shift+R
```

### Fix 2: Improve Logic Detection
```javascript
// Better detection logic
const hasCorrectAnswer = currentTool?.data?.correct_answer && 
                        currentTool?.data?.correct_answer !== ''
const isQuizAnswer = hasCorrectAnswer && 
                    currentTool?.data?.selection_mode === 'quiz_question'
```

### Fix 3: Fix Flow Result Display
```javascript
// Add more debugging to handleFlowStepResult
console.log('🎯 Step result dialogue:', stepResult.response?.dialogue)
console.log('🎯 Pattern test result:', hasQuizOptions)
```

### Fix 4: Debug Audio Issues
```javascript
// Add audio debugging
console.log('🎵 Audio data:', stepResult.response?.audio)
console.log('🎵 Audio length:', stepResult.response?.audio?.length)
```

## Test Scenarios

### Scenario 1: Topic Selection (Should Use Regular Message)
1. Load page with 설민석 quiz character
2. Click "조선시대 퀴즈" from greeting
3. **Expected**: 
   - Console: `📝 Using regular message send`
   - UI: New message appears, quiz question shows
   - Audio: Plays if available

### Scenario 2: Quiz Answer (Should Use Continuous Flow)  
1. Answer quiz question (click option)
2. **Expected**:
   - Console: `🚀 Triggering continuous flow`
   - UI: Educational feedback appears
   - Audio: Plays if available

## Success Criteria

- [ ] Code version logs appear in console
- [ ] Topic selections work (no more continuous flow for greetings)
- [ ] Quiz answers work (continuous flow with feedback)
- [ ] Audio plays consistently
- [ ] No error logs in console
- [ ] Smooth user experience without clicks being ignored

## Debugging Tools

### Console Log Templates
```javascript
// Add these to verify behavior
console.log('🔍 Tool data:', JSON.stringify(currentTool?.data, null, 2))
console.log('🔍 Has correct answer:', !!currentTool?.data?.correct_answer)
console.log('🔍 Selection mode:', currentTool?.data?.selection_mode)
```

### Backend Log Monitoring
```bash
# Watch backend logs for continuous flow triggers
tail -f backend.log | grep "Triggering continuous flow"
```