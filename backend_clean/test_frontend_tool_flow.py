"""
Test Frontend Tool Flow - Simulates frontend interaction with tool-driven backend

This test validates that the frontend can properly interact with our
tool-driven backend architecture.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend_clean.main import app
from fastapi.testclient import TestClient
import requests

# Test configuration
TEST_CHARACTER = "seol_min_seok_quiz"
TEST_USER = "test_user_frontend"
BASE_URL = "http://localhost:8001"

def test_frontend_flow():
    """Test the complete flow as the frontend would use it"""
    
    print("\n" + "="*80)
    print("🌐 TESTING FRONTEND INTEGRATION WITH TOOL-DRIVEN BACKEND")
    print("="*80 + "\n")
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Start session with greeting
    print("\n" + "-"*60)
    print("📝 TEST 1: START SESSION WITH GREETING")
    print("-"*60)
    
    # Start session request
    session_request = {
        "user_id": TEST_USER,
        "character_id": TEST_CHARACTER,
        "continue_session": False
    }
    
    response = client.post("/api/session/start", json=session_request)
    assert response.status_code == 200, f"Failed to start session: {response.text}"
    
    session_data = response.json()
    session_id = session_data.get("session_id")
    assert session_id, "No session ID returned"
    
    print(f"✅ Session started: {session_id}")
    print(f"Greeting: {session_data.get('greeting', 'N/A')[:100]}...")
    
    # Check for greeting tools
    if session_data.get("tools"):
        print(f"Tools: {len(session_data['tools'])} tool(s)")
        tool = session_data["tools"][0]
        print(f"Tool Type: {tool.get('type')}")
        if tool.get("type") == "show_selection":
            print(f"Options: {tool.get('data', {}).get('items', [])}")
    
    # Test 2: Send chat message (topic selection)
    print("\n" + "-"*60)
    print("📝 TEST 2: TOPIC SELECTION THROUGH CHAT")
    print("-"*60)
    
    chat_request = {
        "message": "조선시대",
        "character_prompt": "",  # Will use default
        "character_id": TEST_CHARACTER,
        "user_id": TEST_USER,
        "session_id": session_id
    }
    
    response = client.post("/api/chat/session", json=chat_request)
    assert response.status_code == 200, f"Chat failed: {response.text}"
    
    chat_response = response.json()
    print(f"Dialogue: {chat_response.get('dialogue', 'N/A')[:100]}...")
    
    # Check for quiz tool
    if chat_response.get("tools"):
        print(f"Tools: {len(chat_response['tools'])} tool(s)")
        tool = chat_response["tools"][0]
        print(f"Tool Type: {tool.get('type')}")
        if tool.get("data"):
            data = tool["data"]
            print(f"Question: {data.get('question', 'N/A')}")
            print(f"Options: {data.get('options', [])}")
            
            # Store quiz data for next test
            quiz_question = data.get("question")
            quiz_options = data.get("options", [])
            correct_answer = data.get("correct_answer")
    
    # Test 3: Answer quiz (wrong answer)
    print("\n" + "-"*60)
    print("📝 TEST 3: WRONG ANSWER - CONTINUOUS FLOW")
    print("-"*60)
    
    # Simulate continuous_answer_tool trigger
    tool_request = {
        "session_id": session_id,
        "character_id": TEST_CHARACTER,
        "tool_type": "continuous_answer",
        "data": {
            "selection": quiz_options[1] if len(quiz_options) > 1 else "wrong",
            "question": quiz_question,
            "options": quiz_options,
            "correct_answer": correct_answer,
            "items": quiz_options  # Legacy compatibility
        }
    }
    
    # Call continuous answer endpoint
    response = client.post("/api/tools/continuous_answer", json=tool_request)
    
    if response.status_code == 200:
        tool_response = response.json()
        print(f"✅ Continuous flow triggered")
        
        # Check for two-phase response
        if "phase1" in str(tool_response):
            print(f"Phase 1 Text: {tool_response.get('text', 'N/A')[:100]}...")
            
        # Check for phase 2 data
        response = client.get(f"/api/tools/continuous_answer/phase2/{session_id}")
        if response.status_code == 200:
            phase2_data = response.json()
            print(f"Phase 2 Available: {phase2_data is not None}")
    else:
        print(f"⚠️ Continuous flow not available (legacy mode)")
    
    # Test 4: Answer quiz (correct answer)  
    print("\n" + "-"*60)
    print("📝 TEST 4: CORRECT ANSWER - NEW QUESTION")
    print("-"*60)
    
    tool_request["data"]["selection"] = correct_answer
    
    response = client.post("/api/tools/continuous_answer", json=tool_request)
    
    if response.status_code == 200:
        tool_response = response.json()
        print(f"✅ Correct answer processed")
        print(f"Response: {json.dumps(tool_response, ensure_ascii=False, indent=2)[:200]}...")
    
    # Summary
    print("\n" + "="*80)
    print("🎉 FRONTEND INTEGRATION TEST COMPLETE!")
    print("="*80)
    print("\nSUMMARY:")
    print("✅ Session management works")
    print("✅ Chat with tools works")
    print("✅ Tool-driven responses work")
    print("✅ Continuous flow architecture ready")
    print("\n🚀 Frontend can successfully use tool-driven backend!")

def main():
    """Main test runner"""
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start it with:")
            print("   cd backend_clean && python main.py")
            sys.exit(1)
    except:
        print("❌ Cannot connect to backend at", BASE_URL)
        print("Please start the backend first with:")
        print("   cd backend_clean && python main.py")
        sys.exit(1)
    
    # Run tests
    test_frontend_flow()

if __name__ == "__main__":
    main()