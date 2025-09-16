#!/usr/bin/env python3
"""
Debug script to examine what the LLM Agent Engine is actually returning
"""

import asyncio
import sys
sys.path.append('.')
from main import global_tool_orchestrator
import json

async def debug_llm_response():
    """Debug the LLM response structure to understand why TTS isn't triggered"""
    
    print("🔍 LLM RESPONSE DEBUG")
    print("="*60)
    
    # Test the same flow that was failing
    session_id = "debug_llm_response"
    character_id = "seol_min_seok_quiz"
    user_input = "근현대사"
    
    print(f"Testing: '{user_input}' -> {character_id}")
    print(f"Session: {session_id}")
    print()
    
    try:
        # Call tool orchestrator but capture intermediate steps
        orchestrator = global_tool_orchestrator
        
        # Step 1: Call the orchestrator
        print("🚀 STEP 1: Calling tool orchestrator...")
        result = await orchestrator.process_user_interaction(
            session_id=session_id,
            user_input=user_input,
            character_id=character_id
        )
        
        print("🔍 STEP 2: Analyzing result structure...")
        print(f"   - Result type: {type(result)}")
        print(f"   - Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print(f"   - dialogue: {repr(result.get('dialogue', 'MISSING'))}")
            print(f"   - dialogue type: {type(result.get('dialogue'))}")
            print(f"   - dialogue length: {len(result.get('dialogue', ''))}")
            print(f"   - audio_url: {repr(result.get('audio_url', 'MISSING'))}")
            print(f"   - tools: {len(result.get('tools', []))} tools")
            
            if result.get('tools'):
                print(f"   - tool types: {[tool.get('type', 'unknown') for tool in result.get('tools', [])]}")
        
        # Check if dialogue exists but is empty/falsy
        dialogue = result.get('dialogue') if isinstance(result, dict) else None
        print()
        print("🔍 STEP 3: Dialogue evaluation...")
        print(f"   - dialogue exists: {dialogue is not None}")
        print(f"   - dialogue truthy: {bool(dialogue)}")
        print(f"   - dialogue stripped: {bool(dialogue and dialogue.strip()) if dialogue else False}")
        
        if dialogue:
            print(f"   - First 100 chars: {repr(dialogue[:100])}")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    result = await debug_llm_response()
    
    print("\n" + "="*60)
    if result and isinstance(result, dict):
        dialogue = result.get('dialogue')
        audio_url = result.get('audio_url')
        
        if dialogue and dialogue.strip():
            if audio_url:
                print("✅ CONCLUSION: Dialogue exists AND audio generated")
                print("   🎉 AUDIO GENERATION IS WORKING!")
            else:
                print("❌ CONCLUSION: Dialogue exists but NO audio generated")
                print("   🔍 This is the BUG - TTS generation is not working")
        else:
            print("❌ CONCLUSION: No dialogue in LLM response")
            print("   🔍 LLM Agent Engine is not returning dialogue")
    else:
        print("❌ CONCLUSION: Invalid or no result from tool orchestrator")
    
    return bool(result and result.get('audio_url'))

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)