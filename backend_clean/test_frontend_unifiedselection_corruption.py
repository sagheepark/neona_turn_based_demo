#!/usr/bin/env python3
"""
Test script to reproduce the frontend UnifiedSelection corruption issue

This simulates the scenario where repeated tool calls cause frontend flow corruption.
"""

import requests
import json
import time
from typing import Dict

API_BASE = "http://localhost:8001"

def test_repeated_unifiedselection_calls():
    """Test that simulates the frontend UnifiedSelection corruption issue"""
    print("🧪 Testing repeated UnifiedSelection calls corruption issue...")
    
    # Create a session
    session_response = requests.post(f"{API_BASE}/api/sessions/start", json={
        "user_id": "unified_test",
        "character_id": "seol_min_seok_quiz"
    })
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False
    
    response_data = session_response.json()
    # Handle both new session and existing session cases
    if "session_id" in response_data:
        session_id = response_data["session_id"]
    elif response_data.get("data", {}).get("previous_sessions"):
        # Use existing session
        session_id = response_data["data"]["previous_sessions"][0]["session_id"]
    else:
        print(f"❌ Unexpected session response format: {response_data}")
        return False
    print(f"✅ Session created: {session_id}")
    
    # Step 1: Get greeting (this should show topic selection)
    print("\n📝 Step 1: Getting greeting...")
    response1 = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "안녕하세요",
        "user_id": "unified_test"
    })
    
    if response1.status_code != 200:
        print(f"❌ Greeting failed: {response1.status_code}")
        return False
    
    greeting_data = response1.json()
    print(f"✅ Greeting received. Tools: {len(greeting_data.get('tools', []))}")
    if greeting_data.get('tools'):
        print(f"   First tool type: {greeting_data['tools'][0].get('type')}")
        print(f"   First tool options: {greeting_data['tools'][0].get('data', {}).get('options', [])}")
    
    # Step 2: Select topic RAPIDLY (simulating user clicking fast)
    print("\n📝 Step 2: Selecting topic rapidly...")
    
    # Rapid fire topic selections (simulating frontend state corruption)
    for i in range(3):
        print(f"   Quick selection #{i+1}: 조선시대")
        response = requests.post(f"{API_BASE}/api/platform-chat", json={
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_input": "조선시대",
            "user_id": "unified_test"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"     ✅ Response #{i+1}: {len(data.get('tools', []))} tools")
            if data.get('tools'):
                tool = data['tools'][0]
                print(f"       Tool type: {tool.get('type')}")
                if tool.get('data', {}).get('options'):
                    print(f"       Options: {tool['data']['options'][:2]}...") # First 2 options
        else:
            print(f"     ❌ Response #{i+1} failed: {response.status_code}")
        
        # Very short delay to simulate rapid clicking
        time.sleep(0.1)
    
    print("\n📝 Step 3: Checking final state...")
    
    # Step 3: Try to answer a quiz question to see if flow is corrupted
    answer_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz", 
        "session_id": session_id,
        "user_input": "태조 이성계",
        "user_id": "unified_test"
    })
    
    if answer_response.status_code == 200:
        answer_data = answer_response.json()
        print(f"✅ Answer response received")
        print(f"   Dialogue preview: {answer_data.get('dialogue', '')[:100]}...")
        print(f"   Tools count: {len(answer_data.get('tools', []))}")
        
        # Check if we get the proper continuous_quiz_response structure
        tools = answer_data.get('tools', [])
        if tools:
            first_tool = tools[0]
            tool_type = first_tool.get('type')
            print(f"   Tool type: {tool_type}")
            
            if tool_type == 'continuous_quiz_response':
                print("   ✅ Got proper continuous_quiz_response structure")
                return True
            elif tool_type == 'show_selection':
                print("   ⚠️  Got show_selection instead of continuous_quiz_response")
                print("   This might indicate flow corruption!")
                return False
            else:
                print(f"   ⚠️  Got unexpected tool type: {tool_type}")
                return False
        else:
            print("   ⚠️  No tools in response - flow might be corrupted")
            return False
    else:
        print(f"❌ Answer response failed: {answer_response.status_code}")
        return False

def main():
    """Run the UnifiedSelection corruption test"""
    print("🚀 Frontend UnifiedSelection Corruption Test")
    print("=" * 60)
    
    success = test_repeated_unifiedselection_calls()
    
    print(f"\n🎯 Test Result:")
    if success:
        print("   ✅ Quiz flow maintained proper structure")
        print("   🎉 UnifiedSelection corruption test PASSED")
    else:
        print("   ❌ Quiz flow showed corruption signs") 
        print("   🚨 UnifiedSelection corruption test FAILED")
        print("   💡 Recommendation: Fix frontend state management for currentTools")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)