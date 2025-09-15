#!/usr/bin/env python3
"""
Test Dr. Genie Science Quiz Character Fix
This test verifies that the Dr. Genie science character works end-to-end
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8001"

async def test_dr_genie_science_quiz():
    """Test Dr. Genie science quiz character complete flow"""
    print("🧪 Testing Dr. Genie Science Quiz Character...")
    
    character_id = "dr_genie_science_quiz"
    session_id = f"test_dr_genie_{int(time.time())}"
    
    # Step 1: Test greeting
    print("1️⃣ Testing greeting...")
    greeting_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
        "user_input": "",
        "character_id": character_id,
        "session_id": session_id
    })
    
    if greeting_response.status_code == 200:
        greeting_data = greeting_response.json()
        print(f"✅ Greeting success: {greeting_data.get('text', 'No text')[:100]}...")
        print(f"   Has audio: {bool(greeting_data.get('audio_url'))}")
        print(f"   Has tools: {len(greeting_data.get('tools', []))}")
        if greeting_data.get('tools'):
            tool = greeting_data['tools'][0]
            print(f"   Tool type: {tool.get('type')}")
            print(f"   Options: {len(tool.get('data', {}).get('options', []))} choices")
    else:
        print(f"❌ Greeting failed: {greeting_response.status_code} - {greeting_response.text}")
        return
    
    # Step 2: Select topic
    if greeting_data.get('tools') and len(greeting_data['tools']) > 0:
        print("2️⃣ Testing topic selection...")
        tool_data = greeting_data['tools'][0]['data']
        if 'options' in tool_data and len(tool_data['options']) > 0:
            selected_topic = tool_data['options'][0]  # Select first topic
            
            topic_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                "user_input": selected_topic,
                "character_id": character_id,
                "session_id": session_id
            })
            
            if topic_response.status_code == 200:
                topic_data = topic_response.json()
                print(f"✅ Topic selection success: {topic_data.get('text', 'No text')[:100]}...")
                print(f"   Has audio: {bool(topic_data.get('audio_url'))}")
                print(f"   Has tools: {len(topic_data.get('tools', []))}")
                if topic_data.get('tools'):
                    tool = topic_data['tools'][0]
                    print(f"   Tool type: {tool.get('type')}")
                    if tool.get('data', {}).get('question'):
                        print(f"   Question: {tool['data']['question'][:50]}...")
                        print(f"   Options: {tool['data'].get('options', [])}")
            else:
                print(f"❌ Topic selection failed: {topic_response.status_code} - {topic_response.text}")
                return
            
            # Step 3: Answer quiz question (wrong answer)
            if topic_data.get('tools') and len(topic_data['tools']) > 0:
                print("3️⃣ Testing quiz answer (wrong)...")
                quiz_tool = topic_data['tools'][0]['data']
                if 'options' in quiz_tool and len(quiz_tool['options']) > 1:
                    # Select second option (likely wrong)
                    wrong_answer = quiz_tool['options'][1]
                    
                    quiz_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                        "user_input": wrong_answer,
                        "character_id": character_id,
                        "session_id": session_id
                    })
                    
                    if quiz_response.status_code == 200:
                        quiz_data = quiz_response.json()
                        print(f"✅ Quiz answer success: {quiz_data.get('text', 'No text')[:100]}...")
                        print(f"   Has audio: {bool(quiz_data.get('audio_url'))}")
                        print(f"   Has tools: {len(quiz_data.get('tools', []))}")
                        
                        # Check if it's NOT the error message
                        if "죄송합니다. 잠시 문제가 있었습니다" in quiz_data.get('text', ''):
                            print(f"❌ Still getting error message!")
                            return False
                        else:
                            print(f"✅ No error message - quiz flow working!")
                            return True
                    else:
                        print(f"❌ Quiz answer failed: {quiz_response.status_code} - {quiz_response.text}")
                        return False
    
    return False

if __name__ == "__main__":
    result = asyncio.run(test_dr_genie_science_quiz())
    if result:
        print("🎉 Dr. Genie Science Quiz character is working!")
    else:
        print("❌ Dr. Genie Science Quiz character still has issues")