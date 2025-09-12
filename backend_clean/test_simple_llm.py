"""
Simple LLM test to isolate the tool orchestration issue
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_agent_engine import LLMAgentEngine
from services.character_prompt_manager import CharacterPromptManager
from services.platform_tool_handler import PlatformToolHandler

async def test_simple_llm_call():
    """Test just the LLM call without orchestrator"""
    print("🧠 Testing simple LLM call")
    
    try:
        # Initialize components
        llm_engine = LLMAgentEngine()
        character_manager = CharacterPromptManager()
        tool_handler = PlatformToolHandler()
        
        # Get character prompt and tools
        character_prompt = await character_manager.get_prompt("seolminseok_korean_history_chat")
        available_tools = tool_handler.get_tool_definitions_json()
        
        print(f"✅ Character prompt loaded: {len(character_prompt)} characters")
        print(f"✅ Available tools: {list(available_tools.keys())}")
        
        # Test simple LLM call
        user_input = ""  # Empty for greeting
        chat_history = []
        
        print("🔄 Calling LLM...")
        llm_response = await llm_engine.process_with_tools(
            user_input=user_input,
            character_prompt=character_prompt,
            chat_history=chat_history,
            available_tools=available_tools
        )
        
        print(f"✅ LLM Response: {llm_response}")
        
        # Test tool execution if tool is present
        if llm_response.get('tool'):
            print("🔧 Testing tool execution...")
            tool_result = await tool_handler.execute_tool(
                tool_type=llm_response['tool']['type'],
                data=llm_response['tool']['data']
            )
            print(f"✅ Tool Result: {tool_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_llm_call())
    print(f"Test {'✅ PASSED' if success else '❌ FAILED'}")