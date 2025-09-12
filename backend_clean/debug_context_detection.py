"""
Debug context detection issue - why LLM doesn't use continuous_quiz_response
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tool_orchestrator import ToolOrchestrator
from services.conversation_service import ConversationService

async def debug_context_detection():
    """Debug why context detection isn't working for quiz answers"""
    
    print("🔍 DEBUGGING CONTEXT DETECTION")
    print("=" * 50)
    
    conversation_service = ConversationService()
    orchestrator = ToolOrchestrator(
        tts_service=None,
        session_service=conversation_service
    )
    
    character_id = "seolminseok_korean_history_chat"
    user_id = "test_user"
    
    # Create session and go through the flow step by step
    greeting_response = await orchestrator.create_session_and_greet(character_id, user_id)
    session_id = greeting_response.get('session_id')
    
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Select topic
    topic_response = await orchestrator.process_user_interaction(
        user_input="조선시대",
        character_id=character_id,
        session_id=session_id,
        user_id=user_id
    )
    
    print(f"✅ Topic selected, quiz generated")
    
    # Check session history before answering
    chat_history = await orchestrator._get_chat_history(session_id)
    print(f"\n📜 Current chat history ({len(chat_history)} messages):")
    for i, msg in enumerate(chat_history):
        print(f"  {i}: {msg.get('role', 'unknown')} -> {msg.get('content', '')[:100]}...")
    
    # Now test answer processing
    user_answer = "세종대왕"  # Wrong answer
    
    print(f"\n🎯 Testing user answer: '{user_answer}'")
    
    # Manually test state analysis
    conversation_state = orchestrator._analyze_conversation_state(chat_history, user_answer)
    print(f"\n🔍 Detected state: {conversation_state}")
    
    # Test the actual interaction
    answer_response = await orchestrator.process_user_interaction(
        user_input=user_answer,
        character_id=character_id,
        session_id=session_id,
        user_id=user_id
    )
    
    print(f"\n📋 Answer response:")
    tool_type = answer_response.get('tools', [{}])[0].get('type', 'none') if answer_response.get('tools') else 'none'
    print(f"  Tool used: {tool_type}")
    print(f"  Expected: continuous_quiz_response")
    print(f"  Match: {tool_type == 'continuous_quiz_response'}")
    
    # If it didn't work, let's check what the enhanced prompt looks like
    character_prompt = await orchestrator.character_manager.get_prompt(character_id)
    available_tools = orchestrator.tool_handler.get_tool_definitions_json()
    enhanced_prompt = orchestrator._build_context_aware_prompt(character_prompt, conversation_state, available_tools)
    
    print(f"\n📝 Enhanced prompt preview:")
    print(enhanced_prompt[-500:])  # Last 500 chars to see the enhancement
    
    return True

if __name__ == "__main__":
    asyncio.run(debug_context_detection())