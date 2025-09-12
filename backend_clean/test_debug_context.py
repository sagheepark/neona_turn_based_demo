"""
Debug Context Awareness - Check state analysis and prompts
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tool_orchestrator import ToolOrchestrator
from services.conversation_service import ConversationService

async def debug_context_analysis():
    """Debug the context analysis step by step"""
    
    print("🐛 DEBUG: Context Analysis")
    print("=" * 50)
    
    # Initialize services
    conversation_service = ConversationService()
    orchestrator = ToolOrchestrator(
        tts_service=None,
        session_service=conversation_service
    )
    
    character_id = "seolminseok_korean_history_chat"
    user_id = "test_user"
    
    # Step 1: Create session and greeting
    greeting_response = await orchestrator.create_session_and_greet(
        character_id=character_id,
        user_id=user_id
    )
    session_id = greeting_response.get('session_id')
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Simulate topic selection
    print("\n🔍 DEBUG: Topic Selection")
    topic_response = await orchestrator.process_user_interaction(
        user_input="조선시대",
        character_id=character_id,
        session_id=session_id,
        user_id=user_id
    )
    print(f"Topic response tools: {len(topic_response.get('tools', []))}")
    if topic_response.get('tools'):
        print(f"Tool type: {topic_response['tools'][0]['type']}")
        print(f"Selection mode: {topic_response['tools'][0]['data'].get('selection_mode')}")
    
    # Step 3: Debug quiz answer detection
    print("\n🔍 DEBUG: Quiz Answer Detection")
    
    # Manually check what's in chat history
    chat_history = await orchestrator._get_chat_history(session_id)
    print(f"Chat history length: {len(chat_history)}")
    for i, msg in enumerate(chat_history):
        print(f"  Message {i}: {msg['role']} - '{msg['content'][:100]}...'")
    
    # Test state analysis directly
    print("\n🔍 DEBUG: State Analysis for Quiz Answer")
    user_answer = "세종대왕"  # Wrong answer from test
    
    state = orchestrator._analyze_conversation_state(chat_history, user_answer)
    print(f"Detected state: {state}")
    
    # Test context-aware prompt
    character_prompt = await orchestrator.character_manager.get_prompt(character_id)
    available_tools = orchestrator.tool_handler.get_tool_definitions_json()
    
    enhanced_prompt = orchestrator._build_context_aware_prompt(
        character_prompt, state, available_tools
    )
    
    print(f"\n🔍 DEBUG: Enhanced Prompt")
    print("=" * 30)
    print(enhanced_prompt)
    print("=" * 30)
    
    # Now test the actual quiz answer
    print(f"\n🔍 DEBUG: Processing Quiz Answer")
    quiz_response = await orchestrator.process_user_interaction(
        user_input=user_answer,
        character_id=character_id,
        session_id=session_id,
        user_id=user_id
    )
    
    print(f"Quiz answer response: {quiz_response}")

if __name__ == "__main__":
    asyncio.run(debug_context_analysis())