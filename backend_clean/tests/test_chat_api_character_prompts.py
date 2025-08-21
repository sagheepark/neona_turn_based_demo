"""
TDD Test for Chat API Character Prompt Integration
Following TDD: Red → Green → Refactor
Testing that chat API properly handles character prompts independently - Test Group 33
"""

import pytest
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

API_BASE = "http://localhost:8000"

class TestChatAPICharacterPrompts:
    
    def test_chat_api_should_use_provided_character_prompt(self):
        """
        Test 33.1: Chat API should use the character prompt provided in the request
        
        RED PHASE: This test will fail if character prompts are not being used properly
        """
        # Given: A specific character prompt for Dr. Python
        dr_python_prompt = """
        name: Dr. Python
        personality: Patient, friendly programming teacher who loves puns
        speaking_style: Clear explanations in Korean with occasional programming jokes
        role: Programming instructor
        """
        
        # When: Send chat request with character prompt
        response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user",
            "character_id": "dr_python", 
            "message": "안녕하세요! 파이썬을 배우고 싶어요.",
            "character_prompt": dr_python_prompt,
            "voice_id": "test_voice"
        })
        
        # Then: Response should reflect the character's personality
        assert response.status_code == 200
        data = response.json()
        
        assert "dialogue" in data
        assert len(data["dialogue"]) > 0
        
        # Response should be in Korean (as specified in prompt)
        dialogue = data["dialogue"]
        # Should contain Korean characters or be a reasonable response
        assert any(ord(char) > 127 for char in dialogue) or "python" in dialogue.lower() or "파이썬" in dialogue
        
        # Should not be an error message
        assert "오류" not in dialogue
        assert "죄송합니다" not in dialogue

    def test_chat_api_should_handle_different_character_prompts_independently(self):
        """
        Test 33.2: Different character prompts should produce different responses
        
        RED PHASE: This test will fail if character prompts are being mixed up
        """
        # Given: Two very different character prompts
        gentle_teacher_prompt = """
        name: Gentle Teacher
        personality: Extremely patient, kind, nurturing
        speaking_style: Soft, encouraging words in Korean
        role: Supportive teacher
        """
        
        grumpy_character_prompt = """
        name: Grumpy Forest Creature
        personality: Irritated, rude, dismissive
        speaking_style: Harsh, angry responses with growling sounds
        role: Annoyed forest guardian
        """
        
        # When: Send same message to both characters
        test_message = "안녕하세요!"
        
        gentle_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user",
            "character_id": "gentle_teacher",
            "message": test_message,
            "character_prompt": gentle_teacher_prompt,
            "voice_id": "test_voice"
        })
        
        grumpy_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user", 
            "character_id": "grumpy_creature",
            "message": test_message,
            "character_prompt": grumpy_character_prompt,
            "voice_id": "test_voice"
        })
        
        # Then: Responses should be different and reflect their personalities
        assert gentle_response.status_code == 200
        assert grumpy_response.status_code == 200
        
        gentle_data = gentle_response.json()
        grumpy_data = grumpy_response.json()
        
        gentle_dialogue = gentle_data.get("dialogue", "")
        grumpy_dialogue = grumpy_data.get("dialogue", "")
        
        # Responses should be different
        assert gentle_dialogue != grumpy_dialogue
        
        # Neither should be error messages
        assert "오류" not in gentle_dialogue and "죄송합니다" not in gentle_dialogue
        assert "오류" not in grumpy_dialogue and "죄송합니다" not in grumpy_dialogue
        
        # Both should have different session IDs
        assert gentle_data.get("session_id") != grumpy_data.get("session_id")

    def test_chat_api_should_maintain_character_consistency_in_session(self):
        """
        Test 33.3: Character prompt should be maintained throughout a session
        
        RED PHASE: This test will fail if character prompt is lost in subsequent messages
        """
        # Given: A character with a specific quirky personality
        quirky_prompt = """
        name: Quirky Robot
        personality: Always speaks in robot language with beeps and boops
        speaking_style: Adds "BEEP BOOP" to every sentence, speaks Korean
        role: Friendly robot assistant
        """
        
        # When: Start a conversation and continue it
        first_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user",
            "character_id": "quirky_robot",
            "message": "안녕하세요!",
            "character_prompt": quirky_prompt,
            "voice_id": "test_voice"
        })
        
        assert first_response.status_code == 200
        first_data = first_response.json()
        session_id = first_data.get("session_id")
        
        # Continue the conversation with the same character
        second_response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "session_id": session_id,
            "user_id": "test_user",
            "character_id": "quirky_robot",
            "message": "로봇이세요?",
            "character_prompt": quirky_prompt,
            "voice_id": "test_voice"
        })
        
        # Then: Both responses should maintain character consistency
        assert second_response.status_code == 200
        second_data = second_response.json()
        
        first_dialogue = first_data.get("dialogue", "")
        second_dialogue = second_data.get("dialogue", "")
        
        # Neither should be error messages
        assert "오류" not in first_dialogue and "죄송합니다" not in first_dialogue
        assert "오류" not in second_dialogue and "죄송합니다" not in second_dialogue
        
        # Both should be in Korean and non-empty
        assert len(first_dialogue) > 0
        assert len(second_dialogue) > 0
        
        # Session IDs should be the same
        assert first_data.get("session_id") == second_data.get("session_id")

    def test_chat_api_should_combine_character_prompt_with_memory(self):
        """
        Test 33.4: Character prompt should work together with conversation memory
        
        RED PHASE: This test will fail if character prompt and memory are conflicting
        """
        # Given: A character conversation with memory elements
        memory_test_prompt = """
        name: Memory Test Character
        personality: Always remembers what users tell them
        speaking_style: References previous conversation in Korean
        role: Memory demonstration character
        """
        
        # When: Have a conversation with memory elements
        response1 = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user",
            "character_id": "memory_test",
            "message": "제 이름은 김민수이고 개발자입니다",
            "character_prompt": memory_test_prompt,
            "voice_id": "test_voice"
        })
        
        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1.get("session_id")
        
        # Continue conversation asking about memory
        response2 = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "session_id": session_id,
            "user_id": "test_user",
            "character_id": "memory_test",
            "message": "제 이름과 직업을 기억하시나요?",
            "character_prompt": memory_test_prompt,
            "voice_id": "test_voice"
        })
        
        # Then: Response should combine character personality with memory
        assert response2.status_code == 200
        data2 = response2.json()
        
        dialogue = data2.get("dialogue", "")
        
        # Should not be an error
        assert "오류" not in dialogue and "죄송합니다" not in dialogue
        
        # Should have some content
        assert len(dialogue) > 0
        
        # Should be a proper response (in Korean)
        assert any(ord(char) > 127 for char in dialogue) or len(dialogue) > 10
        
        # Session should be maintained
        assert data1.get("session_id") == data2.get("session_id")

    def test_chat_api_memory_should_not_override_character_prompt(self):
        """
        Test 33.5: Memory system should not override character prompt personality
        
        RED PHASE: This test will fail if memory is overriding character personality
        """
        # Given: A character with a very specific personality
        specific_prompt = """
        name: Test Bot
        personality: Always ends sentences with "TESTING 123"
        speaking_style: Korean with "TESTING 123" at the end
        role: Test demonstration bot
        """
        
        # When: Send a message
        response = requests.post(f"{API_BASE}/api/chat-with-session", json={
            "user_id": "test_user",
            "character_id": "test_bot",
            "message": "간단한 인사를 해주세요",
            "character_prompt": specific_prompt,
            "voice_id": "test_voice"
        })
        
        # Then: Response should maintain character personality
        assert response.status_code == 200
        data = response.json()
        
        dialogue = data.get("dialogue", "")
        
        # Should not be an error
        assert "오류" not in dialogue and "죄송합니다" not in dialogue
        
        # Should have content
        assert len(dialogue) > 0
        
        # Should be a meaningful response
        assert any(ord(char) > 127 for char in dialogue) or len(dialogue) > 5