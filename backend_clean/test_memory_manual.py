#!/usr/bin/env python3
"""
Manual Test for Character Memory System
Tests the complete flow: session creation → memory storage → memory recall
"""

import requests
import json
import sys

# Test configuration
API_BASE = "http://localhost:8000"
TEST_USER_ID = "memory_test_user"
TEST_CHARACTER_ID = "dr_python"
TEST_CHARACTER_PROMPT = """
name: Dr. Python
personality: Patient, friendly programming teacher
speaking_style: Clear explanations in Korean
age: 35
gender: Male
role: Programming instructor
backstory: Former software engineer turned educator with 15 years of experience
scenario: Teaching Python programming to beginners
"""

def test_memory_system():
    """Test the complete memory system flow"""
    print("🧪 Testing Character Memory System")
    print("=" * 50)
    
    session_id = None
    
    try:
        # Test 1: First conversation - User introduces themselves
        print("\n1️⃣ Testing initial conversation (user introduction)")
        response1 = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": TEST_USER_ID,
            "character_id": TEST_CHARACTER_ID,
            "message": "안녕하세요! 제 이름은 김철수입니다. 파이썬을 배우고 싶어요.",
            "character_prompt": TEST_CHARACTER_PROMPT,
            "voice_id": "test_voice"
        })
        
        if response1.status_code == 200:
            data1 = response1.json()
            session_id = data1.get("session_id")
            print(f"✅ Session created: {session_id}")
            print(f"Response: {data1.get('dialogue', 'No dialogue')}")
        else:
            print(f"❌ Failed to create session: {response1.status_code}")
            print(f"Error: {response1.text}")
            return False
        
        # Test 2: Continue conversation - Add more context
        print("\n2️⃣ Testing conversation continuation (adding context)")
        response2 = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "session_id": session_id,
            "user_id": TEST_USER_ID,
            "character_id": TEST_CHARACTER_ID,
            "message": "저는 서울에 살고 있고, 대학생입니다. 데이터 분석에 관심이 많아요.",
            "character_prompt": TEST_CHARACTER_PROMPT,
            "voice_id": "test_voice"
        })
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Message 2 sent")
            print(f"Response: {data2.get('dialogue', 'No dialogue')}")
        else:
            print(f"❌ Failed to send message 2: {response2.status_code}")
            return False
        
        # Test 3: Memory recall - Ask if character remembers
        print("\n3️⃣ Testing memory recall (asking about previous info)")
        response3 = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "session_id": session_id,
            "user_id": TEST_USER_ID,
            "character_id": TEST_CHARACTER_ID,
            "message": "제 이름과 관심분야를 기억하고 계시나요?",
            "character_prompt": TEST_CHARACTER_PROMPT,
            "voice_id": "test_voice"
        })
        
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"✅ Memory test message sent")
            print(f"Response: {data3.get('dialogue', 'No dialogue')}")
            
            # Check if response contains expected memory elements
            response_text = data3.get('dialogue', '').lower()
            has_name = '김철수' in data3.get('dialogue', '')
            has_interest = any(word in response_text for word in ['데이터', '분석', '서울', '대학'])
            
            print(f"\n🔍 Memory Analysis:")
            print(f"  - Contains name (김철수): {'✅' if has_name else '❌'}")
            print(f"  - Contains context (데이터분석/서울/대학): {'✅' if has_interest else '❌'}")
            
            if has_name or has_interest:
                print("🎉 Memory system is working!")
                return True
            else:
                print("❌ Memory system not working - no remembered information in response")
                return False
        else:
            print(f"❌ Failed to send memory test: {response3.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_backend_context():
    """Test the backend context generation directly"""
    print("\n🔧 Testing Backend Context Generation")
    print("=" * 50)
    
    try:
        # First, we need to create a session and add some messages manually
        from services.conversation_service import ConversationService
        
        service = ConversationService()
        
        # Create session
        session = service.create_session(TEST_USER_ID, TEST_CHARACTER_ID, None)
        session_id = session["session_id"]
        print(f"✅ Created test session: {session_id}")
        
        # Add test messages
        service.add_message_to_session(session_id, "user", "안녕하세요! 제 이름은 김철수입니다.", TEST_USER_ID)
        service.add_message_to_session(session_id, "assistant", "안녕하세요 김철수님! 만나서 반갑습니다.", TEST_USER_ID)
        service.add_message_to_session(session_id, "user", "파이썬을 배우고 싶어요. 저는 서울에 사는 대학생입니다.", TEST_USER_ID)
        service.add_message_to_session(session_id, "assistant", "파이썬은 좋은 선택이에요! 서울 대학생이시군요.", TEST_USER_ID)
        
        # Test enhanced AI context
        ai_context = service.get_enhanced_ai_context(session_id, TEST_USER_ID)
        
        print(f"\n📋 Enhanced AI Context:")
        print(f"  - Recent messages count: {len(ai_context.get('recent_messages', []))}")
        print(f"  - Has context prompt: {'✅' if ai_context.get('context_prompt') else '❌'}")
        
        context_prompt = ai_context.get('context_prompt', '')
        if context_prompt:
            print(f"\n📝 Context Prompt Preview:")
            print("-" * 40)
            print(context_prompt[:500] + "..." if len(context_prompt) > 500 else context_prompt)
            print("-" * 40)
            
            # Check if context contains actual messages
            has_actual_messages = '김철수' in context_prompt and '파이썬' in context_prompt
            print(f"\n🔍 Context Analysis:")
            print(f"  - Contains actual message content: {'✅' if has_actual_messages else '❌'}")
            print(f"  - Has 'Recent conversation history': {'✅' if 'Recent conversation history' in context_prompt else '❌'}")
            
            return has_actual_messages
        else:
            print("❌ No context prompt generated")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Character Memory Tests")
    
    # Test 1: Backend context generation
    backend_works = test_backend_context()
    
    # Test 2: Full API flow
    api_works = test_memory_system()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Backend Context Generation: {'✅ PASS' if backend_works else '❌ FAIL'}")
    print(f"Full API Memory Flow: {'✅ PASS' if api_works else '❌ FAIL'}")
    
    if backend_works and api_works:
        print("\n🎉 All tests passed! Memory system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)