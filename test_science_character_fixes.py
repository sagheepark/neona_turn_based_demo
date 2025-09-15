#!/usr/bin/env python3
"""
Test script to verify Dr. Genie science character fixes
Tests both greeting TTS and quiz flow functionality
"""

import requests
import json
import time

def test_science_character_greeting():
    """Test that science character greeting generates TTS"""
    
    print("🧪 Testing Science Character Greeting TTS...")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # Test science character greeting
        print(f"\n📋 Testing dr_genie_science_quiz greeting...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "dr_genie_science_quiz", 
            "user_id": "test_science_greeting"
        })
        
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ Response Status: {response.status_code}")
            print(f"📝 Dialogue: {data.get('dialogue', 'No dialogue')}")
            print(f"🔊 Audio URL: {data.get('audio_url', 'No audio URL')}")
            
            if data.get('dialogue') and data.get('dialogue').strip():
                print(f"✅ SUCCESS: Science character generated dialogue")
                if data.get('audio_url'):
                    print(f"✅ SUCCESS: TTS audio URL generated")
                else:
                    print(f"❌ ISSUE: No TTS audio URL generated")
            else:
                print(f"❌ ISSUE: Science character generated empty dialogue")
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {data}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_science_character_quiz_flow():
    """Test that science character quiz flow works"""
    
    print(f"\n🧪 Testing Science Character Quiz Flow...")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    try:
        # Create session and get greeting
        print(f"\n📋 Step 1: Creating session with science character...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "",
            "character_id": "dr_genie_science_quiz", 
            "user_id": "test_science_quiz"
        })
        
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Session: {session_id}")
        
        # Test topic selection
        print(f"\n📋 Step 2: Selecting science topic...")
        response = requests.post(f"{base_url}/api/platform-chat", json={
            "user_input": "물리",
            "character_id": "dr_genie_science_quiz",
            "user_id": "test_science_quiz",
            "session_id": session_id
        })
        
        data = response.json()
        print(f"✅ Topic selection response received")
        
        if data.get('tools') and len(data['tools']) > 0:
            quiz_tool = data['tools'][0]
            print(f"🔍 Tool type: {quiz_tool.get('type')}")
            
            if quiz_tool.get('type') == 'show_selection':
                quiz_data = quiz_tool.get('data', {})
                question = quiz_data.get('question', '')
                options = quiz_data.get('options', [])
                correct_answer = quiz_data.get('correct_answer', '')
                
                print(f"❓ Question: {question}")
                print(f"📝 Options: {options}")
                print(f"✅ Correct Answer: {correct_answer}")
                
                if question and options and correct_answer:
                    print(f"✅ SUCCESS: Science quiz generated properly")
                    
                    # Test answering correctly
                    print(f"\n📋 Step 3: Answering correctly with '{correct_answer}'...")
                    response = requests.post(f"{base_url}/api/platform-chat", json={
                        "user_input": correct_answer,
                        "character_id": "dr_genie_science_quiz",
                        "user_id": "test_science_quiz",
                        "session_id": session_id
                    })
                    
                    correct_data = response.json()
                    
                    if correct_data.get('tools') and correct_data['tools'][0].get('type') == 'continuous_quiz_response':
                        print(f"✅ SUCCESS: Continuous quiz response generated for correct answer")
                        
                        # Check for phase 2 with new question
                        phase2 = correct_data['tools'][0]['data'].get('phase2', {})
                        if phase2.get('tool', {}).get('data', {}).get('question'):
                            print(f"✅ SUCCESS: Phase 2 contains new quiz question")
                        else:
                            print(f"❌ ISSUE: Phase 2 missing new quiz question")
                    else:
                        print(f"❌ ISSUE: No continuous quiz response for correct answer")
                        
                else:
                    print(f"❌ ISSUE: Incomplete quiz data structure")
                    
            else:
                print(f"❌ ISSUE: Expected show_selection tool, got {quiz_tool.get('type')}")
        else:
            print(f"❌ ISSUE: No tools in response")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def compare_characters():
    """Compare science character with working seol_min_seok_quiz"""
    
    print(f"\n🧪 Comparing Characters...")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    for character_id in ["seol_min_seok_quiz", "dr_genie_science_quiz"]:
        print(f"\n📋 Testing {character_id}...")
        
        try:
            response = requests.post(f"{base_url}/api/platform-chat", json={
                "user_input": "",
                "character_id": character_id, 
                "user_id": f"test_compare_{character_id}"
            })
            
            data = response.json()
            
            print(f"  Status: {response.status_code}")
            print(f"  Has Dialogue: {bool(data.get('dialogue', '').strip())}")
            print(f"  Has Audio URL: {bool(data.get('audio_url'))}")
            print(f"  Has Tools: {len(data.get('tools', []))}")
            
        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    test_science_character_greeting()
    test_science_character_quiz_flow()
    compare_characters()