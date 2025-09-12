"""
Test multiple LLM calls to capture problematic response formats
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_agent_engine import LLMAgentEngine
from services.character_prompt_manager import CharacterPromptManager
from services.platform_tool_handler import PlatformToolHandler

async def test_multiple_llm_calls():
    """Test multiple LLM calls to find problematic response formats"""
    
    print("🔍 Testing Multiple LLM Calls")
    print("=" * 50)
    
    try:
        # Initialize components
        llm_engine = LLMAgentEngine()
        character_manager = CharacterPromptManager()
        tool_handler = PlatformToolHandler()
        
        # Get components
        character_prompt = await character_manager.get_prompt("seolminseok_korean_history_chat")
        available_tools = tool_handler.get_tool_definitions_json()
        
        # Test multiple calls with same input
        for i in range(5):
            print(f"\n🔄 Call {i+1}:")
            try:
                llm_response = await llm_engine.process_with_tools(
                    user_input="",  # Empty for greeting
                    character_prompt=character_prompt,
                    chat_history=[],
                    available_tools=available_tools
                )
                
                print(f"✅ Success: {llm_response}")
                
                # Try tool execution
                if llm_response.get('tool'):
                    tool_result = await tool_handler.execute_tool(
                        tool_type=llm_response['tool']['type'],
                        data=llm_response['tool']['data']
                    )
                    print(f"✅ Tool executed successfully")
                else:
                    print(f"⚠️  No tool in response")
                    
            except Exception as e:
                print(f"❌ Call {i+1} failed: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_multiple_llm_calls())