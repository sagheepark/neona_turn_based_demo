#!/usr/bin/env python3
"""
Check which backend route handles each character
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_character_routing():
    print("🔍 TESTING CHARACTER ROUTING")
    
    characters = [
        "dr_genie_science_quiz",
        "seol_min_seok_quiz",
        "seolminseok_korean_history_chat"
    ]
    
    for char in characters:
        print(f"\n📋 Testing {char}")
        
        # Test platform-chat endpoint
        try:
            response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                "user_input": "",
                "character_id": char,
                "session_id": None,
                "user_id": "debug_user"
            })
            
            if response.status_code == 200:
                print(f"  ✅ platform-chat works for {char}")
            else:
                print(f"  ❌ platform-chat failed for {char}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ platform-chat error for {char}: {e}")
            
        # Test any other endpoints
        try:
            response = requests.post(f"{BASE_URL}/api/chat/interactive", json={
                "message": "",
                "character_id": char
            })
            
            if response.status_code == 200:
                print(f"  ✅ chat/interactive works for {char}")
            else:
                print(f"  ❌ chat/interactive failed for {char}: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ chat/interactive error for {char}: {e}")

if __name__ == "__main__":
    test_character_routing()