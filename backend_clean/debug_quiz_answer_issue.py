#!/usr/bin/env python3
"""
Debug Quiz Answer Issue - Reproduces the exact problem scenario
"""

# Simulate the exact conversation flow that's causing issues
conversation_history = [
    "user: 안녕하세요! 한국사 퀴즈를 해보고 싶어요.",
    "assistant: 안녕하세요! 한국사 퀴즈를 함께 풀어볼까요? 어떤 주제로 시작하고 싶으신가요?",
    "user: 조선시대 퀴즈 시작해주세요",
    "assistant: 안녕하세요! 조선시대 퀴즈를 시작해보겠습니다! 조선시대는 정말 흥미로운 역사적 사건과 인물들로 가득하죠. 자, 첫 번째 문제 나갑니다!\n\n조선의 창업자인 태조 이성계가 조선을 건국한 해는 언제일까요?\n\n1. 1392년\n2. 1418년\n3. 1453년\n4. 1592년\n\n어떤 답이 맞을까요? 정답을 맞혀보세요!"
]

user_message = "B) 불교 장려"

def analyze_quiz_issue():
    """Debug the quiz answer matching issue"""
    
    print("🔍 ANALYZING QUIZ ANSWER ISSUE")
    print("=" * 50)
    
    # 1. Parse last question
    last_assistant_msg = None
    last_question = None
    
    for msg in reversed(conversation_history):
        if msg.startswith("assistant:") and not last_assistant_msg:
            last_assistant_msg = msg.replace("assistant:", "").strip()
            # Check if this message contains a quiz question
            if any(marker in last_assistant_msg for marker in ["1.", "2.", "3.", "4.", "A)", "B)", "C)", "D)"]):
                last_question = last_assistant_msg
                break
    
    print("📝 LAST QUESTION EXTRACTED:")
    print(f"   '{last_question[:100]}...'")
    print()
    
    # 2. Check quiz answer detection
    is_quiz_answer = any(marker in user_message for marker in ["1.", "2.", "3.", "4.", "A)", "B)", "C)", "D)"])
    
    print("🎯 QUIZ ANSWER DETECTION:")
    print(f"   User Message: '{user_message}'")
    print(f"   Is Quiz Answer: {is_quiz_answer}")
    print()
    
    # 3. Identify the mismatch problem
    print("⚠️  PROBLEM ANALYSIS:")
    
    # Extract options from question
    question_has_numbers = any(marker in last_question for marker in ["1.", "2.", "3.", "4."])
    question_has_letters = any(marker in last_question for marker in ["A)", "B)", "C)", "D)"])
    user_uses_letters = any(marker in user_message for marker in ["A)", "B)", "C)", "D)"])
    user_uses_numbers = any(marker in user_message for marker in ["1.", "2.", "3.", "4."])
    
    print(f"   Question has numbers (1. 2. 3. 4.): {question_has_numbers}")
    print(f"   Question has letters (A) B) C) D)): {question_has_letters}")
    print(f"   User used letters (A) B) C) D)): {user_uses_letters}")
    print(f"   User used numbers (1. 2. 3. 4.): {user_uses_numbers}")
    print()
    
    # 4. Show the format mismatch
    if question_has_numbers and user_uses_letters:
        print("🔴 FORMAT MISMATCH DETECTED:")
        print("   - Question uses numeric options (1. 1392년, 2. 1418년...)")  
        print("   - User answered with letter format (B) 불교 장려)")
        print("   - User's answer content doesn't match any question option")
        print()
        
        # 5. Show what the LLM receives
        print("🤖 WHAT LLM RECEIVES:")
        prompt_snippet = f"""
방금 제시한 퀴즈 문제:
{last_question}

사용자의 답변: {user_message}

**교육적 퀴즈 진행 규칙:**
1. 먼저 사용자 답변이 정답인지 오답인지 명확히 판단하세요.
"""
        print(prompt_snippet)
        
        print("❌ LLM CONFUSION:")
        print("   - Question asks about founding year with 4 year options")
        print("   - User answers with 'B) 불교 장려' (completely unrelated)")
        print("   - LLM tries to be helpful but instruction is contradictory")
        print("   - Result: Wrong educational feedback")
        
    return {
        'last_question': last_question,
        'user_message': user_message,
        'is_quiz_answer': is_quiz_answer,
        'format_mismatch': question_has_numbers and user_uses_letters
    }

def suggest_fixes():
    """Suggest specific fixes for the issue"""
    
    print("\n🔧 SUGGESTED FIXES:")
    print("=" * 50)
    
    print("1. 📋 BETTER ANSWER PARSING:")
    print("   - Extract user's choice (A, B, C, D or 1, 2, 3, 4)")
    print("   - Map to actual question options")  
    print("   - Validate answer exists in question")
    print()
    
    print("2. 🎯 IMPROVED ANSWER MATCHING:")
    print("   - Parse question to extract all options")
    print("   - Match user selection to option content")
    print("   - Handle both letter and number formats")
    print()
    
    print("3. 🔍 ANSWER VALIDATION:")
    print("   - Check if user's answer maps to valid option")
    print("   - Provide clear error if no match found")
    print("   - Ask user to choose from available options")
    print()
    
    print("4. 📚 ENHANCED LLM CONTEXT:")
    print("   - Clearly state which option user selected")
    print("   - Include the content of selected option")
    print("   - Make correct/incorrect determination explicit")

if __name__ == "__main__":
    result = analyze_quiz_issue()
    suggest_fixes()
    
    if result['format_mismatch']:
        print(f"\n🚨 ISSUE CONFIRMED: Format mismatch detected!")
        print("The user's answer format doesn't match the question format.")
    else:
        print(f"\n✅ No format mismatch found")