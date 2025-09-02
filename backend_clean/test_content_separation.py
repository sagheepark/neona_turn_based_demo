#!/usr/bin/env python3
"""
Test Content Separation - P1 Quiz UI Fix
Verify that quiz dialogue is properly separated from options
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.platform_content_classifier import PlatformContentClassifier

async def test_content_separation():
    """Test the content separation logic for quiz responses"""
    print("🧪 TESTING P1: Content Separation (dialogue vs options)")
    print("=" * 60)
    
    # Initialize platform classifier
    classifier = PlatformContentClassifier()
    
    # Test with typical quiz response that includes both question and options
    full_quiz_response = "다음 중 세종대왕의 업적은? A) 한글 창제 B) 불교 장려 C) 몽골 침입 D) 일제강점"
    
    print(f"📝 Original LLM Response:")
    print(f"   '{full_quiz_response}'")
    print()
    
    # Analyze for tools
    context = {
        "character_id": "seol_min_seok_quiz",
        "conversation_phase": "post_greeting",
        "user_message": "조선시대 퀴즈 내주세요"
    }
    
    try:
        detected_tools = await classifier.analyze_for_tools(full_quiz_response, context)
        
        if detected_tools:
            print(f"✅ Platform Classifier detected {len(detected_tools)} tools")
            first_tool = detected_tools[0]
            print(f"   Tool type: {first_tool['type']}")
            
            if first_tool['type'] == 'show_selection':
                quiz_data = first_tool.get('data', {})
                clean_question = quiz_data.get('question', '')
                options = quiz_data.get('items', [])
                
                print(f"🎯 CONTENT SEPARATION RESULT:")
                print(f"   Clean Question: '{clean_question}'")
                print(f"   Extracted Options: {options}")
                print()
                
                # Verify separation worked correctly
                if clean_question and clean_question != full_quiz_response:
                    print(f"✅ SUCCESS: Content separated correctly!")
                    print(f"   - Chat dialogue will show: '{clean_question}'")
                    print(f"   - Quiz UI will show: {len(options)} options")
                    print(f"   - Question duplication eliminated ✅")
                    print(f"   - Clean presentation achieved ✅")
                else:
                    print(f"❌ ISSUE: Content separation did not work as expected")
                    
            else:
                print(f"❌ ISSUE: Tool detected but not quiz type")
        else:
            print(f"❌ No tools detected - quiz pattern might not be recognized")
            
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_content_separation())