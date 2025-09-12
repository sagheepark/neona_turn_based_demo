"""
Test greeting interaction only to isolate the issue
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tool_orchestrator import ToolOrchestrator
from services.conversation_service import ConversationService

async def test_greeting_only():
    """Test just the greeting to see what's failing"""
    
    print("🎬 Testing Greeting Only")
    print("=" * 40)
    
    try:
        # Initialize services
        conversation_service = ConversationService()
        orchestrator = ToolOrchestrator(
            tts_service=None,
            session_service=conversation_service
        )
        
        character_id = "seolminseok_korean_history_chat"
        user_id = "test_user"
        
        # Test direct process_user_interaction with empty input
        print("🔍 Testing process_user_interaction with empty input...")
        
        response = await orchestrator.process_user_interaction(
            user_input="",
            character_id=character_id,
            session_id=None,  # No session for greeting
            user_id=user_id
        )
        
        print(f"✅ Direct greeting response: {response}")
        
        # Test create_session_and_greet
        print("\n🔍 Testing create_session_and_greet...")
        
        response2 = await orchestrator.create_session_and_greet(
            character_id=character_id,
            user_id=user_id
        )
        
        print(f"✅ Session greeting response: {response2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_greeting_only())
    print(f"Test {'✅ PASSED' if success else '❌ FAILED'}")