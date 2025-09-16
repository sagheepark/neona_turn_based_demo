## Prompt Optimization Templates (Simple, Drop‑in Replacements)

This document provides concise prompt templates that preserve your existing logic and flows while reducing token usage ~30%+. These are drop‑in replacements for the appended prompt sections per case and a lighter system wrapper. No behavior changes; only shorter prompts.

### How the final prompt is currently built
- Character base prompt from `CharacterPromptManager.get_prompt(character_id)`
- Optional Relevant Knowledge block (top 3, plain lines)
- Appended stage‑specific section from `ToolOrchestrator._build_context_aware_prompt()`
- System wrapper in `LLMAgentEngine.process_with_tools()` that adds tool definitions and JSON output guidelines

The three conversation stages in your flow:
- greeting → greet + topic selection (`show_selection` with `selection_mode='topic'`)
- topic_selected → acknowledge + first quiz (`show_selection` with `selection_mode='quiz_question'`)
- quiz_active + user_answered_quiz → evaluate answer (`continuous_quiz_response`)

---

## 1) Global JSON Output Rules (reuse across all stages)

Use this short rules block instead of long repeated explanations. Keep it once in the system wrapper or append briefly when needed.

```
JSON OUTPUT RULES:
- Output valid JSON only (no prose around it).
- Strings use literal \n for sentence breaks (backslash + n). Do not use real newlines inside JSON values.
- Example: {"text": "첫 문장.\n둘째 문장."}
```

---

## 2) Relevant Knowledge (unchanged, just compact rendering)

Keep your existing behavior, but ensure it is short:

```
RELEVANT KNOWLEDGE:
- {item1}
- {item2}
- {item3}
```

---

## 3) Stage Appends — Drop‑in Minimal Replacements

These replace the large appended blocks inside `_build_context_aware_prompt()` while preserving logic.

### 3.1 Greeting stage

Replace the current greeting append with:

```
현재 상황: 초기 인사
역할: 따뜻하게 인사하고 주제 선택지를 제시하세요.
도구: show_selection (selection_mode='topic')
필수 JSON:
{
  "dialogue": "자연스러운 인사 및 소개",
  "tool": {
    "type": "show_selection",
    "data": {
      "question": "공부할 주제를 골라볼까요?",
      "options": ["조선", "고려", "삼국", "현대"],
      "selection_mode": "topic"
    }
  }
}
```

Notes:
- Keep dialogue friendly and TTS‑ready (use \n between sentences if multi‑sentence).

### 3.2 Topic selected stage

Replace the current topic_selected append with:

```
현재 상황: 사용자가 방금 주제 '{topic}'를 선택함
역할: 선택을 인정하고 첫 번째 퀴즈를 제시하세요.
도구: show_selection (selection_mode='quiz_question')
요구사항:
- '{topic}' 관련 구체적 문제 1개
- 보기 4개 (한글 텍스트)
- correct_answer는 보기 중 정확한 답으로 설정

필수 JSON:
{
  "dialogue": "격려 + 문제 도입 문장",
  "tool": {
    "type": "show_selection",
    "data": {
      "question": "{topic} 첫 문제",
      "options": ["보기A", "보기B", "보기C", "보기D"],
      "correct_answer": "정답 보기 텍스트",
      "selection_mode": "quiz_question"
    }
  }
}
```

Notes:
- Do not speak all options in dialogue; options are shown as buttons.

### 3.3 Quiz active (user answered) stage

Replace the very long quiz evaluation block with this compact version:

```
현재 상황: 퀴즈 답변 평가
문제: "{current_question}"
선택지: {current_options}
사용자 답변: "{current_user_input}"

역할:
- 위 문제와 선택지를 기준으로 사용자의 답이 맞는지 판단
- 정답일 때: Phase1 축하 + 간단한 이유, Phase2 새 문제 제시
- 오답일 때: Phase1 격려 + 힌트(정답 미공개), Phase2 동일 문제/선택지 재제시

도구: continuous_quiz_response (반드시 사용)
Phase1 규칙: 한국어 70자 내외, 자연스러운 TTS 문장, 정답 공개 금지(오답시)

필수 JSON:
{
  "dialogue": "짧은 안내 문장",
  "tool": {
    "type": "continuous_quiz_response",
    "data": {
      "phase1": { "text": "격려 또는 축하 문장들(문장 사이 \n)", "delay_ms": 3000 },
      "phase2": {
        "text": "다음 진행 문장",
        "tool": {
          "type": "show_selection",
          "data": {
            "question": "(정답일 때: 새 문제 / 오답일 때: 동일 문제)",
            "options": {current_options},
            "correct_answer": "정답일 땐 새 문제의 정답, 오답일 땐 기존 문제의 정답",
            "selection_mode": "quiz_question"
          }
        }
      }
    }
  }
}
```

Notes:
- 예시 JSON 전체 출력 대신, 위 구조만 정확히 따르게 지시합니다.
- 긴 예시와 서술은 제거하고, 핵심 규칙(정답 미공개, 70자 내외, \n 사용)만 유지합니다.

---

## 4) Lighter System Wrapper (for `LLMAgentEngine.process_with_tools`)

Replace the long wrapper content with this concise version. It keeps the tool use behavior and JSON requirement while reducing tokens.

```
{CHARACTER_PROMPT}

AVAILABLE TOOLS: {TOOL_NAMES_ONLY}

RESPONSE FORMAT:
{
  "dialogue": "TTS‑friendly text (use literal \n between sentences)",
  "tool": { "type": "tool_name", "data": {"..."} } | null
}

GUIDELINES:
- Stay in character and follow the current stage instructions.
- Use tools for UI interactions (topic selection, quizzes, continuous responses).
- Never reveal the correct answer when the student is wrong.
```

Tips:
- If possible, provide only tool names (e.g., ["show_selection", "continuous_quiz_response"]) rather than full JSON definitions to cut tokens. Behavior remains the same; the frontend already knows schemas.

---

## 5) Token Reduction Summary (Est.)

- Greeting append: ~250 → ~120 tokens (−50%+)
- Topic append: ~300 → ~150 tokens (−50%+)
- Quiz evaluation append: ~1,800–2,400 → ~400–600 tokens (−70%+)
- System wrapper: ~400 → ~150 tokens (−60%+)
- Overall per request: ~30%+ reduction depending on stage and tools dump size

---

## 6) Drop‑in Checklists (Copy/Paste Targets)

- `_build_context_aware_prompt()`
  - Greeting: replace with section 3.1
  - Topic selected: replace with section 3.2
  - Quiz active: replace with section 3.3
  - Keep the short "RELEVANT KNOWLEDGE" block (section 2) when available
- `LLMAgentEngine.process_with_tools()`
  - Replace system wrapper body with section 4
  - If feasible, pass tool names instead of dumping full tool JSON

All replacements preserve your current logic (tool types, phases, no‑reveal rule, TTS string rules) and simply compress wording to save tokens.


