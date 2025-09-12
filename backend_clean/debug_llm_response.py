"""
Debug LLM response format to fix the 'type' error in tool orchestration
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_agent_engine import LLMAgentEngine
from services.character_prompt_manager import CharacterPromptManager

async def debug_llm_response():
    """Test what the LLM actually returns for topic selection"""
    
    print("🔍 DEBUGGING LLM RESPONSE FORMAT")
    print("=" * 60)
    
    # Setup
    character_manager = CharacterPromptManager()
    llm_engine = LLMAgentEngine()
    
    character_id = "seolminseok_korean_history_chat"
    character_prompt = await character_manager.get_prompt(character_id)
    
    # Simulate topic selection scenario
    user_input = "조선시대"
    chat_history = [
        {"role": "assistant", "content": "안녕하세요! 반갑습니다. 저는 설민석입니다. 한국 역사를 재미있고 흥미롭게 배워보는 시간을 가져볼까요? 여러분이 배우고 싶은 주제를 선택해 주세요!"}
    ]
    
    available_tools = [
        {
            "name": "show_selection",
            "description": "Display quiz question with multiple choice options to the user",
            "parameters": {
                "question": "str - The quiz question to display", 
                "options": "List[str] - List of multiple choice options",
                "correct_answer": "str - The correct answer from the options",
                "selection_mode": "str - Type of selection (quiz_question, topic, etc.)",
                "retry_mode": "bool - Whether this is a retry of the same question"
            }
        }
    ]
    
    print("📝 Input Parameters:")
    print(f"   User Input: {user_input}")
    print(f"   Chat History: {len(chat_history)} messages")
    print(f"   Available Tools: {len(available_tools)}")
    print("")
    
    try:
        # Call LLM and capture raw response
        print("🧠 Calling LLM...")
        llm_response = await llm_engine.process_with_tools(
            user_input=user_input,
            character_prompt=character_prompt,
            chat_history=chat_history,
            available_tools=available_tools
        )
        
        print("✅ LLM Response Received!")
        print("")
        
        print("📋 RAW LLM RESPONSE STRUCTURE:")
        print(f"   Type: {type(llm_response)}")
        print(f"   Keys: {list(llm_response.keys()) if isinstance(llm_response, dict) else 'Not a dict'}")
        print("")
        
        print("🔍 DETAILED RESPONSE ANALYSIS:")
        for key, value in llm_response.items():
            print(f"   {key}: {type(value)} = {value}")
        print("")
        
        # Check for the specific error case
        if 'tool' in llm_response:
            tool_data = llm_response['tool']
            print("🔧 TOOL DATA ANALYSIS:")
            print(f"   Tool Type: {type(tool_data)}")
            print(f"   Tool Keys: {list(tool_data.keys()) if isinstance(tool_data, dict) else 'Not a dict'}")
            
            if 'type' in tool_data:
                print(f"   Tool Type Value: {tool_data['type']}")
            else:
                print("   ❌ MISSING 'type' KEY - This is the error!")
                
            if 'data' in tool_data:
                print(f"   Tool Data: {tool_data['data']}")
            else:
                print("   ❌ MISSING 'data' KEY - This could cause issues!")
        else:
            print("❌ NO TOOL IN RESPONSE - This is unexpected!")
        
        return llm_response
        
    except Exception as e:
        print(f"❌ LLM Processing Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    response = asyncio.run(debug_llm_response())
    
    print("")
    print("🎯 DEBUGGING SUMMARY:")
    if response:
        print("✅ LLM call succeeded")
        print(f"   Response structure needs to match: {{'dialogue': str, 'tool': {{'type': str, 'data': dict}}}}")
        
        # Check if the response matches expected format
        expected_keys = ['dialogue', 'tool']
        has_expected_structure = all(key in response for key in expected_keys)
        
        if has_expected_structure and 'type' in response.get('tool', {}):
            print("✅ Response format looks correct!")
        else:
            print("❌ Response format needs fixing in LLMAgentEngine")
    else:
        print("❌ LLM call failed - check error details above")