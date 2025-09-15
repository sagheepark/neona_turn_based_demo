#!/usr/bin/env python3
"""
Debug Character Greeting Generation
Compare how seol_min_seok_quiz vs dr_genie_science_quiz handle greeting generation
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_character_greeting(character_id, character_name):
    """Test greeting generation for a character"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing {character_name} ({character_id})")
    print(f"{'='*60}")
    
    # Test greeting generation via platform-chat
    payload = {
        "user_input": "",
        "character_id": character_id,
        "session_id": None,
        "user_id": "debug_user"
    }
    
    try:
        print("📡 Sending greeting request...")
        print(f"   URL: {BASE_URL}/api/platform-chat")
        print(f"   Character ID: {character_id}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{BASE_URL}/api/platform-chat", json=payload, timeout=30)
        
        print(f"\n📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS")
            print(f"   Dialogue: {data.get('dialogue', 'MISSING')[:100]}...")
            print(f"   Character: {data.get('character', 'MISSING')}")
            print(f"   Audio URL: {bool(data.get('audio_url'))}")
            print(f"   Session ID: {data.get('session_id', 'MISSING')}")
            print(f"   Tools: {len(data.get('tools', []))} tools")
            
            if data.get('tools'):
                for i, tool in enumerate(data['tools']):
                    print(f"     Tool {i+1}: {tool.get('type', 'NO_TYPE')}")
                    if tool.get('data'):
                        tool_data = tool['data']
                        print(f"       Question: {tool_data.get('question', 'NO_QUESTION')}")
                        print(f"       Options: {len(tool_data.get('options', tool_data.get('items', [])))} options")
            
            return True
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("🔍 CHARACTER GREETING DEBUG COMPARISON")
    print("="*60)
    
    characters = [
        ("seol_min_seok_quiz", "설민석 Korean History Quiz"),
        ("dr_genie_science_quiz", "Dr. Genie Science Quiz")
    ]
    
    results = {}
    
    for character_id, character_name in characters:
        results[character_id] = test_character_greeting(character_id, character_name)
    
    print(f"\n{'='*60}")
    print("🏁 FINAL COMPARISON")
    print(f"{'='*60}")
    
    for character_id, character_name in characters:
        status = "✅ WORKING" if results[character_id] else "❌ FAILED"
        print(f"{character_name}: {status}")
    
    print("\n🔍 This debug shows the exact difference in greeting generation")
    print("   between working and non-working characters.")

if __name__ == "__main__":
    main()