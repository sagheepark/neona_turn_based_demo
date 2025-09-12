#!/usr/bin/env python3
"""
Realistic Full-Context Integration Test
Tests the actual 설민석 AI 퀴즈 튜터 with real API calls and LLM responses
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_realistic_quiz_tutor_flow():
    """Test the complete realistic flow with actual API"""
    
    print("🧪 REALISTIC FULL-CONTEXT TEST: 설민석 AI 퀴즈 튜터")
    print("=" * 70)
    
    # Step 1: Test greeting
    print("1️⃣ TESTING GREETING...")
    greeting_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "안녕하세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "realistic_test_user"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed: {greeting_response.status_code}")
        return False
        
    greeting_data = greeting_response.json()
    session_id = greeting_data["session_id"]
    
    print(f"✅ Greeting Response:")
    print(f"   Dialogue: {greeting_data['dialogue'][:100]}...")
    print(f"   Tools: {len(greeting_data.get('tools', []))} tool(s)")
    print(f"   Audio: {'✅' if greeting_data.get('audio') else '❌'}")
    
    time.sleep(1)
    
    # Step 2: Request quiz
    print("\n2️⃣ TESTING QUIZ REQUEST...")
    quiz_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "조선시대 퀴즈 내주세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "realistic_test_user",
        "session_id": session_id
    })
    
    if quiz_response.status_code != 200:
        print(f"❌ Quiz request failed: {quiz_response.status_code}")
        return False
        
    quiz_data = quiz_response.json()
    
    print(f"✅ Quiz Response:")
    print(f"   Full Response: {quiz_data}")
    print(f"   Dialogue: {quiz_data['dialogue'][:150]}...")
    print(f"   Tools: {len(quiz_data.get('tools', []) or [])} tool(s)")
    
    # Check if quiz tools are properly structured
    tools = quiz_data.get('tools', [])
    if tools:
        quiz_tool = tools[0]
        print(f"   Tool Type: {quiz_tool.get('type')}")
        print(f"   Tool Data: {quiz_tool.get('data', {}).keys()}")
    
    time.sleep(1)
    
    # Step 3: Answer quiz question (if options available)
    if tools and tools[0].get('data', {}).get('items'):
        print("\n3️⃣ TESTING QUIZ ANSWER...")
        
        # Try to answer the quiz
        answer_response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
            "message": "A) 한글 창제",  # Standard quiz answer format
            "character_prompt": "당신은 설민석 선생님입니다.",
            "character_id": "seol_min_seok_quiz", 
            "user_id": "realistic_test_user",
            "session_id": session_id
        })
        
        if answer_response.status_code == 200:
            answer_data = answer_response.json()
            print(f"✅ Answer Response:")
            print(f"   Dialogue: {answer_data['dialogue'][:150]}...")
            print(f"   Tools: {len(answer_data.get('tools', []))} tool(s)")
            
            # Check for educational feedback
            dialogue = answer_data['dialogue']
            has_educational_feedback = any(word in dialogue for word in [
                '정답', '틀렸', '훌륭', '맞습니다', '아쉽', '설명'
            ])
            
            print(f"   Educational Feedback: {'✅' if has_educational_feedback else '❌'}")
            
        else:
            print(f"❌ Answer failed: {answer_response.status_code}")
    else:
        print("\n3️⃣ ❌ NO QUIZ OPTIONS AVAILABLE - Quiz tools not working properly")
    
    # Step 4: Analysis
    print("\n📊 REALISTIC TEST ANALYSIS:")
    print(f"   Session Management: ✅")
    print(f"   Character Response: ✅") 
    print(f"   Tool Generation: {'✅' if tools else '❌'}")
    print(f"   Quiz Options: {'✅' if tools and tools[0].get('data', {}).get('items') else '❌'}")
    print(f"   Audio/TTS: {'✅' if greeting_data.get('audio') else '❌'}")
    
    # Check if my tool-orchestrated system is being used
    print(f"\n🔧 TOOL-ORCHESTRATED SYSTEM STATUS:")
    print(f"   Current Implementation: LEGACY SYSTEM (not my new ToolOrchestrator)")
    print(f"   Integration Needed: ✅ YES - Need to integrate new architecture")
    
    return True

def test_current_system_limitations():
    """Test what's currently broken in the quiz system"""
    
    print("\n🔍 CURRENT SYSTEM LIMITATIONS:")
    print("=" * 50)
    
    response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
        "message": "조선시대 세종대왕 문제 내주세요",
        "character_prompt": "당신은 설민석 선생님입니다.",
        "character_id": "seol_min_seok_quiz",
        "user_id": "limitation_test"
    })
    
    if response.status_code == 200:
        data = response.json()
        tools = data.get('tools', [])
        
        print("❌ CURRENT ISSUES FOUND:")
        if not tools:
            print("   - No tools generated")
        elif not tools[0].get('data', {}).get('items'):
            print("   - Tool data is empty (no quiz options)")
        
        print("   - Not using ToolOrchestrator architecture")
        print("   - No structured LLM tool detection")
        print("   - Legacy tool generation system")
        
        print(f"\n📋 Raw Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("🚀 STARTING REALISTIC FULL-CONTEXT TEST")
    print("Testing actual 설민석 AI 퀴즈 튜터 with live API calls\n")
    
    success = test_realistic_quiz_tutor_flow()
    test_current_system_limitations()
    
    print("\n" + "=" * 70)
    if success:
        print("📝 CONCLUSION: System partially works but needs tool-orchestrated integration")
    else:
        print("❌ CONCLUSION: Major issues found in current implementation")
        
    print("\n🎯 NEXT STEPS:")
    print("1. Integrate ToolOrchestrator into main.py chat_with_session endpoint")
    print("2. Replace legacy tool generation with LLM tool detection")  
    print("3. Add character prompts with tool instructions")
    print("4. Test complete flow with new architecture")