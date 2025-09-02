# Quiz UI Enhancement Requirements

## 🎯 **Core Issues to Fix**

### 1. **TTS/Voice Generation**
- **Problem**: TTS fails for quiz responses (❌ TTS FAILED: No audio data generated)
- **Requirement**: Quiz responses must have voice/audio like regular chat
- **Success Criteria**: Audio file returned in API response for quiz messages

### 2. **Content Separation** 
- **Problem**: Chat text includes A/B/C/D options: "다음 중 세종대왕의 업적은? A) 한글 창제 B) 불교 장려 C) 몽골 침입 D) 일제강점"
- **Requirement**: Chat text should only show question part: "다음 중 세종대왕의 업적은?"
- **Success Criteria**: Chat bubble shows clean question text without options

### 3. **UI Container Removal**
- **Problem**: Large white floating container with rounded corners
- **Requirement**: Remove floating container, show options directly
- **Success Criteria**: No white background container around quiz options

### 4. **UI Positioning**
- **Problem**: Quiz UI positioned in center/floating
- **Requirement**: Position quiz options in bottom-right, above text input
- **Success Criteria**: Options appear as compact overlay above input area

### 5. **Question Duplication**
- **Problem**: Question appears in both chat bubble AND quiz options header
- **Requirement**: Question should only appear in chat bubble
- **Success Criteria**: Options area shows only A/B/C/D choices, no question text

## 🔧 **Technical Implementation Plan**

### Backend Changes Required:

#### 1. **TTS Fix for Quiz Character**
- **Issue**: `seol_min_seok_quiz` TTS failing
- **Location**: `main.py` TTS generation section
- **Fix**: Ensure quiz character uses proper TTS service
- **Test**: Verify audio returned in API response

#### 2. **Content Response Modification**  
- **Issue**: Platform classifier needs to return clean dialogue text
- **Location**: `services/platform_content_classifier.py`
- **Fix**: Extract only question part from LLM response for dialogue field
- **Logic**: Split response at "? A)" and use question part for dialogue

### Frontend Changes Required:

#### 1. **Quiz Component Redesign**
- **Issue**: Current floating container UI
- **Location**: Quiz component (likely in components/tools/)
- **Fix**: Remove container styling, make compact
- **Style**: Remove white background, borders, shadows

#### 2. **Positioning System**
- **Issue**: Center-positioned floating quiz
- **Fix**: Position absolute/fixed in bottom-right area
- **Layout**: Above text input, right-aligned, compact

#### 3. **Content Display Logic**
- **Issue**: Question duplication in options area
- **Fix**: Options component should only show choices, not question
- **Logic**: Remove question header from quiz options display

## ✅ **Checklist for Implementation**

### Backend Tasks:
- [ ] **Fix TTS Generation**: Ensure quiz responses generate audio
- [ ] **Modify Content Response**: Extract clean question text for dialogue
- [ ] **Test API Response**: Verify audio field populated
- [ ] **Test Content Separation**: Verify dialogue contains only question

### Frontend Tasks:
- [ ] **Remove Quiz Container**: Remove white floating container styling
- [ ] **Reposition Quiz UI**: Move to bottom-right above input
- [ ] **Fix Content Duplication**: Remove question from options header
- [ ] **Style Compact UI**: Make quiz options compact and unobtrusive
- [ ] **Test Responsive Design**: Ensure works on different screen sizes

### Integration Testing:
- [ ] **End-to-End Test**: Request quiz through API
- [ ] **Voice Playback**: Verify audio plays correctly
- [ ] **UI Positioning**: Verify options appear in correct location
- [ ] **Content Validation**: Verify no duplication of question text
- [ ] **User Experience**: Verify intuitive and clean interface

## 🎨 **Desired End State**

### Chat Flow:
1. **User Request**: "조선시대 퀴즈 내주세요"
2. **Chat Bubble**: "좋습니다! 다음 중 세종대왕의 업적은?" (clean question only)
3. **Voice Plays**: Question audio automatically plays
4. **Quiz Options**: Compact A/B/C/D buttons appear bottom-right above input
5. **No Containers**: No floating white boxes or unnecessary UI elements

### Visual Result:
```
[Chat Bubble: "다음 중 세종대왕의 업적은?"] 🔊

                                    [A] 한글 창제  [B] 불교 장려
                                    [C] 몽골 침입  [D] 일제강점
                                    ────────────────────────────
                                    [ 메시지 입력... ]
```

## 📊 **Priority Order**
1. **HIGH**: Fix TTS generation (critical for user experience)
2. **HIGH**: Remove question from dialogue text (content clarity)  
3. **MEDIUM**: Reposition quiz UI (user interface improvement)
4. **MEDIUM**: Remove floating container (clean design)
5. **LOW**: Fix question duplication (polish improvement)