#!/usr/bin/env python3
"""
Debug parse_quiz_answer function to understand the parsing issue
"""

import re

def debug_parse_quiz_answer(user_message: str, question_text: str):
    """Debug version of parse_quiz_answer with detailed logging"""
    print("🔍 DEBUGGING PARSE_QUIZ_ANSWER")
    print("=" * 50)
    print(f"📝 User Message: '{user_message}'")
    print(f"📝 Question Text: '{question_text}'")
    print()
    
    # Extract user choice (A, B, C, D, 1, 2, 3, 4)
    user_choice = None
    choice_patterns = [
        r'([A-D])\)',  # A), B), C), D)
        r'([1-4])\.',  # 1., 2., 3., 4.
        r'([1-4])\)',  # 1), 2), 3), 4)
        r'([A-D])',    # A, B, C, D
        r'([1-4])'     # 1, 2, 3, 4
    ]
    
    print("🎯 TESTING USER CHOICE PATTERNS:")
    for i, pattern in enumerate(choice_patterns):
        match = re.search(pattern, user_message)
        if match:
            print(f"   Pattern {i+1} '{pattern}' → MATCH: '{match.group(1)}'")
            if not user_choice:
                user_choice = match.group(1)
        else:
            print(f"   Pattern {i+1} '{pattern}' → NO MATCH")
    
    print(f"\n✅ Final user_choice: '{user_choice}'")
    
    if not user_choice:
        print("❌ Could not parse user choice")
        return {"error": "Could not parse user choice"}
    
    # Extract all options from question
    options = []
    option_patterns = [
        r'([1-4])\.\s*(\S+)',  # 1. option text (simple word capture)
        r'([1-4])\)\s*(\S+)',  # 1) option text (simple word capture) 
        r'([A-D])\)\s*(\S+)'   # A) option text (simple word capture)
    ]
    
    print("\n🎯 TESTING QUESTION OPTION PATTERNS:")
    for i, pattern in enumerate(option_patterns):
        matches = re.findall(pattern, question_text)
        if matches:
            print(f"   Pattern {i+1} '{pattern}' → MATCHES: {matches}")
            if not options:
                options = matches
        else:
            print(f"   Pattern {i+1} '{pattern}' → NO MATCHES")
    
    print(f"\n✅ Final options: {options}")
    
    if not options:
        print("❌ Could not parse question options")
        return {"error": "Could not parse question options"}
    
    # Map user choice to option content
    choice_mapping = {}
    print("\n🗺️  BUILDING CHOICE MAPPING:")
    for i, (choice_key, option_text) in enumerate(options):
        choice_mapping[choice_key] = option_text.strip()
        print(f"   Direct mapping: '{choice_key}' → '{option_text.strip()}'")
        
        # Also map numeric/letter equivalents
        if choice_key.isdigit():
            letter = chr(ord('A') + int(choice_key) - 1)
            choice_mapping[letter] = option_text.strip()
            print(f"   Cross mapping: '{letter}' → '{option_text.strip()}'")
        else:
            number = str(ord(choice_key) - ord('A') + 1)
            choice_mapping[number] = option_text.strip()
            print(f"   Cross mapping: '{number}' → '{option_text.strip()}'")
    
    print(f"\n📋 Complete choice_mapping: {choice_mapping}")
    
    user_option_text = choice_mapping.get(user_choice)
    print(f"🎯 Looking up user_choice '{user_choice}' → '{user_option_text}'")
    
    if not user_option_text:
        print(f"❌ Invalid choice {user_choice}")
        return {"error": f"Invalid choice {user_choice}"}
    
    result = {
        "user_choice": user_choice,
        "user_option_text": user_option_text,
        "all_options": choice_mapping,
        "question_text": question_text
    }
    
    print(f"\n✅ SUCCESS! Parsed result: {result}")
    return result

if __name__ == "__main__":
    # Test the exact failing case
    user_message = "2) 1443년"
    question_text = "좋습니다! 조선시대 퀴즈를 시작해보겠습니다! 세종대왕이 훈민정음을 만든 해는 언제일까요? 1) 1433년 2) 1443년 3) 1453년 4) 1463년"
    
    result = debug_parse_quiz_answer(user_message, question_text)