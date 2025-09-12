"""
Test corrected dialogue behavior - options should NOT be in dialogue text
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tool_orchestrator import ToolOrchestrator
from services.conversation_service import ConversationService

async def test_corrected_dialogue():
    """Test that quiz options are NOT included in dialogue text"""
    
    print("🧪 TESTING CORRECTED DIALOGUE BEHAVIOR")
    print("=" * 60)
    print("📋 Expected: Dialogue contains question ONLY, options in tool data")
    print("📋 This provides clean TTS and proper UI separation")
    print("")
    
    conversation_service = ConversationService()
    orchestrator = ToolOrchestrator(
        tts_service=None,
        session_service=conversation_service
    )
    
    character_id = "seolminseok_korean_history_chat"
    user_id = "dialogue_test_user"
    
    # Create session and request quiz
    greeting_response = await orchestrator.create_session_and_greet(character_id, user_id)
    session_id = greeting_response.get('session_id')
    
    print("✅ Session created")
    print("")
    
    # Test quiz generation with corrected prompt
    print("🎯 QUIZ GENERATION TEST")
    print("-" * 40)
    print("👤 User Input: '조선시대 퀴즈를 시작해주세요'")
    print("🤖 Expected: Question in dialogue, options in tool only")
    print("")
    
    quiz_response = await orchestrator.process_user_interaction(
        user_input="조선시대 퀴즈를 시작해주세요",
        character_id=character_id,
        session_id=session_id,
        user_id=user_id
    )
    
    dialogue = quiz_response.get('dialogue', '')
    tools = quiz_response.get('tools', [])
    
    print("📋 DIALOGUE TEXT (for TTS):")
    print(f"   {dialogue}")
    print("")
    
    # Check if options are incorrectly included in dialogue
    options_in_dialogue = any(word in dialogue.lower() for word in ['첫 번째', '두 번째', '세 번째', '네 번째', '선택지'])
    
    print("🔍 DIALOGUE ANALYSIS:")
    print(f"   Contains options? {options_in_dialogue}")
    print(f"   Length: {len(dialogue)} characters")
    print(f"   ✅ CORRECT: {'Options NOT in dialogue' if not options_in_dialogue else '❌ ERROR: Options found in dialogue'}")
    print("")
    
    if tools:
        tool = tools[0]
        tool_data = tool.get('data', {})
        
        print("🔧 TOOL DATA (for UI):")
        print(f"   Tool Type: {tool['type']}")
        print(f"   Question: {tool_data.get('question', 'N/A')}")
        print(f"   Options: {tool_data.get('options', [])}")
        
        has_options_in_tool = bool(tool_data.get('options'))
        print(f"   ✅ CORRECT: {'Options in tool data' if has_options_in_tool else '❌ ERROR: No options in tool'}")
        print("")
        
        # Overall assessment
        correct_separation = not options_in_dialogue and has_options_in_tool
        
        print("🎯 SEPARATION ASSESSMENT:")
        print("=" * 60)
        if correct_separation:
            print("✅ SUCCESS: Perfect dialogue/UI separation!")
            print("   💬 Dialogue: Clean question text for TTS")
            print("   🔧 Tool: Options data for button rendering")  
            print("   🎵 TTS: Will play clean question only")
            print("   👆 UI: Will show clickable option buttons")
        else:
            print("❌ NEEDS CORRECTION: Issues with separation")
            if options_in_dialogue:
                print("   Problem: Options found in dialogue text")
            if not has_options_in_tool:
                print("   Problem: Options missing from tool data")
        
        return correct_separation
    
    else:
        print("❌ ERROR: No tools generated")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_corrected_dialogue())
    print(f"\n📊 Dialogue Correction Test {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("🎓 Ready for production: Clean TTS + proper UI separation!")
    else:
        print("🔧 Prompt needs further refinement for proper separation")