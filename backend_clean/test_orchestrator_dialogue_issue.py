#!/usr/bin/env python3
"""
Test to diagnose why tool orchestrator sometimes doesn't generate audio
Focus on checking if dialogue field is present in LLM responses
"""

import requests
import time
import json

API_BASE = "http://localhost:8001"

def test_orchestrator_dialogue_consistency():
    """Test multiple calls to see when dialogue is missing"""
    
    print("🧪 Testing Tool Orchestrator Dialogue Consistency...")
    print("=" * 60)
    
    results = []
    
    for test_num in range(5):
        print(f"\n🎯 Test {test_num + 1}: Creating session and testing dialogue generation")
        
        # Create a new session  
        create_response = requests.post(f"{API_BASE}/api/sessions/create", json={
            "user_id": f"dialogue_test_{test_num}",
            "character_id": "seol_min_seok_quiz"
        })
        
        if create_response.status_code != 200:
            print(f"❌ Session creation failed: {create_response.status_code}")
            continue
            
        session_data = create_response.json()
        session_id = session_data.get("data", {}).get("session", {}).get("session_id")
        
        if not session_id:
            print(f"❌ No session_id returned: {session_data}")
            continue
        
        print(f"✅ Session created: {session_id}")
        
        # Test platform-chat with simple greeting
        platform_response = requests.post(f"{API_BASE}/api/platform-chat", json={
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_input": "안녕하세요 선생님", 
            "user_id": f"dialogue_test_{test_num}"
        })
        
        if platform_response.status_code == 200:
            platform_data = platform_response.json()
            
            dialogue = platform_data.get('dialogue', '')
            audio_url = platform_data.get('audio_url')
            tools = platform_data.get('tools', [])
            
            result = {
                'test_num': test_num + 1,
                'session_id': session_id,
                'has_dialogue': bool(dialogue),
                'dialogue_length': len(dialogue) if dialogue else 0,
                'dialogue_preview': dialogue[:100] + '...' if dialogue and len(dialogue) > 100 else dialogue,
                'has_audio_url': bool(audio_url),
                'audio_url_length': len(audio_url) if audio_url else 0,
                'tools_count': len(tools),
                'tools_types': [tool.get('type') for tool in tools] if tools else []
            }
            
            results.append(result)
            
            print(f"   📝 Has dialogue: {result['has_dialogue']} ({result['dialogue_length']} chars)")
            print(f"   🎵 Has audio URL: {result['has_audio_url']} ({result['audio_url_length']} chars)")
            print(f"   🔧 Tools count: {result['tools_count']} {result['tools_types']}")
            if result['dialogue_preview']:
                print(f"   📄 Dialogue preview: '{result['dialogue_preview']}'")
        else:
            print(f"❌ Platform-chat failed: {platform_response.status_code}")
        
        # Wait between tests to avoid rate limiting
        time.sleep(1)
    
    # Analyze results
    print(f"\n📊 ANALYSIS OF {len(results)} TESTS:")
    dialogue_success = sum(1 for r in results if r['has_dialogue'])
    audio_success = sum(1 for r in results if r['has_audio_url'])
    
    print(f"   📝 Dialogue generation: {dialogue_success}/{len(results)} ({dialogue_success/len(results)*100:.1f}%)")
    print(f"   🎵 Audio URL generation: {audio_success}/{len(results)} ({audio_success/len(results)*100:.1f}%)")
    
    # Show cases where dialogue exists but audio doesn't
    missing_audio_with_dialogue = [r for r in results if r['has_dialogue'] and not r['has_audio_url']]
    if missing_audio_with_dialogue:
        print(f"\n🚨 CASES WITH DIALOGUE BUT NO AUDIO ({len(missing_audio_with_dialogue)}):")
        for r in missing_audio_with_dialogue:
            print(f"   Test {r['test_num']}: {r['dialogue_length']} chars dialogue, no audio")
            print(f"      Preview: '{r['dialogue_preview']}'")
    
    # Show cases where there's no dialogue at all
    no_dialogue = [r for r in results if not r['has_dialogue']]
    if no_dialogue:
        print(f"\n❌ CASES WITH NO DIALOGUE ({len(no_dialogue)}):")
        for r in no_dialogue:
            print(f"   Test {r['test_num']}: No dialogue generated at all")
            print(f"      Tools: {r['tools_types']}")
    
    print(f"\n🎯 DIAGNOSIS:")
    if dialogue_success == len(results) and audio_success == len(results):
        print(f"   ✅ Tool orchestrator working consistently - all tests generated dialogue + audio")
    elif dialogue_success == len(results) and audio_success < len(results):
        print(f"   🚨 LLM generates dialogue but TTS service fails - audio generation issue")
    elif dialogue_success < len(results):
        print(f"   🚨 LLM sometimes doesn't generate dialogue - check LLM agent or prompts")
    else:
        print(f"   ❓ Mixed results - need deeper investigation")
    
    return results

def main():
    print("🚀 Testing Tool Orchestrator Dialogue Consistency")
    print("=" * 60)
    
    results = test_orchestrator_dialogue_consistency()
    
    print(f"\n📊 FINAL SUMMARY:")
    if results:
        all_have_dialogue = all(r['has_dialogue'] for r in results)
        all_have_audio = all(r['has_audio_url'] for r in results)
        
        if all_have_dialogue and all_have_audio:
            print("   ✅ Tool orchestrator consistently generating dialogue + audio")
            print("   💡 Audio issue may be intermittent or context-specific")
        elif all_have_dialogue and not all_have_audio:
            print("   🚨 LLM consistently generates dialogue but TTS generation fails")
            print("   🔧 Need to fix TTS service calling or error handling")
        else:
            print("   🚨 Inconsistent dialogue generation from LLM agent")
            print("   🔧 Need to fix LLM agent prompts or response parsing")
    else:
        print("   ❌ All tests failed - check server status")
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)