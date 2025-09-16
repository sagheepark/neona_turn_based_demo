#!/usr/bin/env python3
"""
Test script to verify audio generation is working after TTS fix
"""

import asyncio
import sys
sys.path.append('.')
from main import global_tool_orchestrator

async def test_audio_generation():
    """Test the core audio generation flow"""
    
    print("🧪 AUDIO GENERATION TEST")
    print("="*50)
    
    # Test the flow that was failing before
    session_id = "audio_test"
    character_id = "seol_min_seok_quiz"
    user_input = "근현대사"
    
    print(f"Testing: {user_input} -> {character_id}")
    
    try:
        # This is the call that was failing with .get() method error
        result = await global_tool_orchestrator.process_user_interaction(
            session_id=session_id,
            user_input=user_input,
            character_id=character_id
        )
        
        print(f"✅ SUCCESS: Tool orchestrator returned result")
        print(f"   - Has dialogue: {bool(result.get('dialogue'))}")
        print(f"   - Has audio: {bool(result.get('audio_url'))}")
        print(f"   - Has tools: {len(result.get('tools', []))}")
        
        if result.get('audio_url'):
            audio_url = result['audio_url']
            if audio_url and audio_url.startswith('data:audio'):
                print(f"   - Audio URL: {audio_url[:50]}...{audio_url[-20:]}")
                print("✅ AUDIO GENERATION WORKING!")
                return True
            else:
                print(f"❌ Audio URL invalid: {audio_url}")
                return False
        else:
            print("⚠️  No audio URL returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_audio_generation()
    
    print("\n" + "="*50)
    if success:
        print("🎉 CONCLUSION: Audio generation is WORKING!")
        print("   The TypeCast -> SeolMinSeok TTS replacement was successful")
    else:
        print("❌ CONCLUSION: Audio generation still has issues")
        print("   Need further investigation")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)