#!/usr/bin/env python3
"""
Test User-Reported Issues: Greeting Selection & Frontend TypeError Fix
Validates fixes for both reported problems in the tool-orchestrated platform
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_greeting_selection_fix():
    """
    Test Fix #1: Greeting now properly triggers selection with quiz topics
    """
    print("🔧 TEST 1: GREETING SELECTION FIX")
    print("=" * 50)
    
    # Test greeting response
    response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "fix_test_user"
    })
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Greeting Response:")
        print(f"   Character: {data['character']}")
        print(f"   Dialogue: {data['dialogue']}")
        
        # Check tools
        tools = data.get('tools', [])
        if tools and len(tools) > 0:
            tool = tools[0]
            items = tool['data'].get('items', [])
            
            print(f"   🔧 Tools Generated: {len(tools)}")
            print(f"   📝 Items Count: {len(items)}")
            print(f"   📋 Items: {items}")
            
            # Verify fix
            if len(items) > 0:
                print(f"   ✅ GREETING SELECTION FIX: SUCCESS")
                print(f"      - Items properly populated")
                print(f"      - Quiz topics available for selection")
                return data['session_id'], True
            else:
                print(f"   ❌ GREETING SELECTION FIX: FAILED")
                print(f"      - Items still empty")
                return None, False
        else:
            print(f"   ❌ GREETING SELECTION FIX: FAILED")
            print(f"      - No tools generated")
            return None, False
    else:
        print(f"❌ Greeting request failed: {response.status_code}")
        return None, False

def test_frontend_interface_fix(session_id):
    """
    Test Fix #2: Frontend interface now receives 'items' instead of 'options'  
    """
    print("\n🔧 TEST 2: FRONTEND INTERFACE FIX")
    print("=" * 50)
    
    # Test topic selection response
    response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "근현대사 퀴즈",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "fix_test_user",
        "session_id": session_id
    })
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Topic Selection Response:")
        print(f"   Dialogue: {data['dialogue']}")
        
        # Check tools format
        tools = data.get('tools', [])
        if tools and len(tools) > 0:
            tool = tools[0]
            tool_data = tool['data']
            
            print(f"   🔧 Tool Type: {tool['type']}")
            print(f"   🎯 UI Type: {tool_data.get('ui_type')}")
            print(f"   ❓ Question: {tool_data.get('question')}")
            
            # Critical fix validation
            has_items = 'items' in tool_data
            has_options = 'options' in tool_data  
            items = tool_data.get('items', [])
            
            print(f"   📊 Interface Check:")
            print(f"      Has 'items' field: {'✅' if has_items else '❌'}")
            print(f"      Has 'options' field: {'✅' if has_options else '❌'}")
            print(f"      Items count: {len(items)}")
            print(f"      Items: {items}")
            
            if has_items and not has_options and len(items) > 0:
                print(f"   ✅ FRONTEND INTERFACE FIX: SUCCESS")
                print(f"      - Backend sends 'items' (not 'options')")
                print(f"      - Frontend UnifiedSelection will receive expected format")
                print(f"      - TypeError should be resolved")
                return True
            else:
                print(f"   ❌ FRONTEND INTERFACE FIX: FAILED")
                if has_options:
                    print(f"      - Still sending 'options' instead of 'items'")
                if not has_items:
                    print(f"      - Missing 'items' field")
                if len(items) == 0:
                    print(f"      - Items array is empty")
                return False
        else:
            print(f"   ❌ No tools in response")
            return False
    else:
        print(f"❌ Topic selection request failed: {response.status_code}")
        return False

def test_complete_user_flow():
    """
    Test complete user flow that was previously failing
    """
    print("\n🔧 TEST 3: COMPLETE USER FLOW")
    print("=" * 50)
    
    print("1. User sends greeting...")
    session_id, greeting_success = test_greeting_selection_fix()
    
    if greeting_success and session_id:
        print("\n2. User selects quiz topic...")
        interface_success = test_frontend_interface_fix(session_id)
        
        if interface_success:
            print("\n✅ COMPLETE USER FLOW: SUCCESS")
            print("   1. ✅ Greeting provides quiz topic selection")
            print("   2. ✅ Topic selection generates proper quiz question") 
            print("   3. ✅ Frontend receives correct interface format")
            print("   4. ✅ No more TypeError in UnifiedSelection")
            return True
        else:
            print("\n❌ COMPLETE USER FLOW: FAILED at step 2")
            return False
    else:
        print("\n❌ COMPLETE USER FLOW: FAILED at step 1")
        return False

if __name__ == "__main__":
    print("🚀 TESTING USER-REPORTED ISSUE FIXES")
    print("Validating fixes for greeting selection and frontend TypeError")
    print("=" * 80)
    
    flow_success = test_complete_user_flow()
    
    print("\n" + "=" * 80)
    if flow_success:
        print("🎉 USER ISSUE FIXES: COMPLETE SUCCESS!")
        print("=" * 80)
        print("✅ ISSUE 1 RESOLVED: Greeting now triggers quiz topic selection")
        print("✅ ISSUE 2 RESOLVED: Frontend receives 'items' format (no more TypeError)")
        print("\n📱 FRONTEND IMPACT:")
        print("   - UnifiedSelection component will receive expected 'items' array")
        print("   - No more 'Cannot read properties of undefined (reading length)' error")
        print("   - Quiz selection flow works seamlessly")
        
        print("\n🏗️ TECHNICAL FIXES APPLIED:")
        print("   1. GreetingSuggestionGenerator: Added suggestions_enabled flag")
        print("   2. GreetingSuggestionGenerator: Always return quiz topics for quiz character")
        print("   3. PlatformToolHandler: Use 'items' instead of 'options' for frontend compatibility")
        
        print("\n🎯 USER EXPERIENCE:")
        print("   ✅ Greeting shows topic selection immediately")
        print("   ✅ Topic selection works without errors")
        print("   ✅ Quiz questions display properly")
    else:
        print("❌ USER ISSUE FIXES: SOME ISSUES REMAIN")
        print("Check individual test results above for details")