#!/usr/bin/env python3
"""
Comprehensive Test for 설민석 AI 퀴즈 튜터 Flow
Tests the complete quiz flow with UI triggers and continuous flow
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

class SeolMinSeokQuizTester:
    def __init__(self):
        self.session_id = None
        self.current_tools = []
        self.user_id = "test_seolminseok_quiz"
        self.character_id = "seol_min_seok_quiz"
        
    def log(self, message: str, level: str = "INFO"):
        """Log with clear indicators"""
        emoji = {
            "TEST": "🧪",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "DEBUG": "🔍",
            "UI": "🖥️",
            "AUDIO": "🎵",
            "FLOW": "🔄",
            "QUIZ": "📝"
        }.get(level, "📝")
        print(f"{emoji} {message}")
        
    def test_step_1_greeting_with_suggestions(self) -> bool:
        """Step 1: User greets → Get greeting with quiz topic suggestions"""
        self.log("STEP 1: Testing greeting with quiz topic suggestions", "TEST")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "안녕하세요",
                "character_prompt": "당신은 설민석 선생님입니다. 한국사를 재미있게 가르치는 퀴즈 튜터입니다.",
                "character_id": self.character_id,
                "user_id": self.user_id
            })
            
            if response.status_code != 200:
                self.log(f"Greeting failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            self.session_id = data.get("session_id")
            self.current_tools = data.get("tools", [])
            
            # Verify response components
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            
            self.log(f"  Greeting received: {dialogue[:60]}...", "UI")
            self.log(f"  Audio provided: {'YES' if audio else 'NO'} ({len(audio) if audio else 0} bytes)", "AUDIO")
            self.log(f"  Topic suggestions: {len(self.current_tools)} tools available", "UI")
            
            # Check if quiz suggestions are provided
            if self.current_tools:
                quiz_tool = self.current_tools[0]
                if quiz_tool.get("type") == "show_selection":
                    topics = quiz_tool.get("data", {}).get("items", [])
                    self.log(f"  Available topics: {topics}", "QUIZ")
                else:
                    self.log(f"  Tool type: {quiz_tool.get('type')} (expected: show_selection)", "ERROR")
            
            # Validate success criteria
            has_greeting = len(dialogue) > 0
            has_audio = audio is not None
            has_quiz_tools = len(self.current_tools) > 0 and self.current_tools[0].get("type") == "show_selection"
            
            return has_greeting and has_quiz_tools
            
        except Exception as e:
            self.log(f"Greeting error: {e}", "ERROR")
            return False
    
    def test_step_2_topic_selection_quiz_ui(self) -> bool:
        """Step 2: User selects topic → Quiz question with UI"""
        self.log("STEP 2: Testing topic selection and quiz UI generation", "TEST")
        
        if not self.current_tools:
            self.log("No topics available from greeting", "ERROR")
            return False
            
        try:
            # Select first topic (조선시대 퀴즈)
            topic = self.current_tools[0]["data"]["items"][0]
            self.log(f"  Selecting topic: {topic}", "UI")
            
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": topic,
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": self.character_id,
                "user_id": self.user_id,
                "session_id": self.session_id
            })
            
            if response.status_code != 200:
                self.log(f"Topic selection failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            quiz_tools = data.get("tools", [])
            
            # CRITICAL CHECK: Dialogue should include the quiz question
            self.log(f"  Quiz dialogue: {dialogue}", "QUIZ")
            self.log(f"  Audio provided: {'YES' if audio else 'NO'}", "AUDIO")
            
            if quiz_tools:
                quiz_data = quiz_tools[0].get("data", {})
                question = quiz_data.get("question", "MISSING")
                options = quiz_data.get("items", [])
                correct = quiz_data.get("correct_answer", "MISSING")
                
                self.log(f"  Quiz question: {question}", "QUIZ")
                self.log(f"  Quiz options: {options}", "UI")
                self.log(f"  Correct answer: {correct}", "DEBUG")
                
                # Store for next step
                self.current_tools = quiz_tools
                
                # CRITICAL VALIDATION: Check if dialogue contains the question
                has_question_in_dialogue = any(word in dialogue for word in ["무엇", "언제", "누구", "어디", "왜", "어떤", "?"])
                has_quiz_structure = quiz_data.get("question") and quiz_data.get("items")
                has_audio = audio is not None
                
                if not has_question_in_dialogue:
                    self.log("  ⚠️ WARNING: Question text not found in dialogue!", "ERROR")
                
                return has_question_in_dialogue and has_quiz_structure and has_audio
            else:
                self.log("  No quiz tools generated!", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Topic selection error: {e}", "ERROR")
            return False
    
    def test_step_3_answer_triggers_flow(self) -> bool:
        """Step 3: User answers → Continuous flow triggered with feedback"""
        self.log("STEP 3: Testing answer submission and continuous flow trigger", "TEST")
        
        if not self.current_tools:
            self.log("No quiz available to answer", "ERROR")
            return False
            
        try:
            quiz_data = self.current_tools[0]["data"]
            correct_answer = quiz_data.get("correct_answer")
            
            self.log(f"  Submitting answer: {correct_answer}", "UI")
            
            # Trigger continuous flow with answer
            response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
                "session_id": self.session_id,
                "character_id": self.character_id,
                "tool_type": "show_selection",
                "data": {
                    "selection": correct_answer,
                    "correct_answer": correct_answer,
                    "question": quiz_data.get("question", ""),
                    "items": quiz_data.get("items", [])
                }
            })
            
            if response.status_code != 200:
                self.log(f"Flow trigger failed: {response.status_code}", "ERROR")
                return False
                
            flow_result = response.json()
            step_result = flow_result.get("step_result", {})
            
            # First LLM output: Educational feedback
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            self.log(f"  Feedback dialogue: {dialogue[:100]}...", "UI")
            self.log(f"  Feedback audio: {'YES' if audio else 'NO'} ({len(audio) if audio else 0} bytes)", "AUDIO")
            self.log(f"  Flow continues: {flow_result.get('flow_continues', False)}", "FLOW")
            
            # Validate feedback content
            has_feedback = any(word in dialogue for word in ["정답", "훌륭", "맞습니다", "잘했"])
            has_dialogue = len(dialogue) > 10
            has_audio = audio is not None
            flow_continues = flow_result.get('flow_continues', False)
            
            if not has_feedback:
                self.log("  ⚠️ WARNING: No educational feedback in response", "ERROR")
                
            return has_dialogue and has_audio and flow_continues
            
        except Exception as e:
            self.log(f"Answer submission error: {e}", "ERROR")
            return False
    
    def test_step_4_second_llm_next_quiz(self) -> bool:
        """Step 4: After audio → Second LLM call → Next quiz question"""
        self.log("STEP 4: Testing automatic second LLM call for next quiz", "TEST")
        
        try:
            # Simulate audio completion triggering next step
            self.log("  Simulating audio completion...", "AUDIO")
            time.sleep(1)
            
            response = requests.post(f"{BASE_URL}/api/continuous-flow/progress", json={
                "session_id": self.session_id,
                "trigger_type": "audio_completion"
            })
            
            if response.status_code != 200:
                self.log(f"Flow progress failed: {response.status_code}", "ERROR")
                return False
                
            progress_result = response.json()
            step_result = progress_result.get("step_result", {})
            
            # Second LLM output: Next quiz question
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            self.log(f"  Next quiz dialogue: {dialogue}", "QUIZ")
            self.log(f"  Next quiz audio: {'YES' if audio else 'NO'}", "AUDIO")
            
            # Check if it's a quiz format
            import re
            is_quiz_format = bool(re.search(r'[①-④]|[A-D]\)|[1-4]\)', dialogue))
            has_question = "?" in dialogue or any(word in dialogue for word in ["무엇", "언제", "누구"])
            has_dialogue = len(dialogue) > 10
            has_audio = audio is not None
            
            self.log(f"  Is quiz format: {is_quiz_format}", "DEBUG")
            self.log(f"  Has question: {has_question}", "DEBUG")
            
            if not (is_quiz_format or has_question):
                self.log("  ⚠️ WARNING: Next output doesn't look like a quiz!", "ERROR")
                
            return has_dialogue and has_audio and (is_quiz_format or has_question)
            
        except Exception as e:
            self.log(f"Flow continuation error: {e}", "ERROR")
            return False
    
    def test_step_5_mixed_conversation(self) -> bool:
        """Step 5: User asks different question during quiz → Normal response"""
        self.log("STEP 5: Testing mixed conversation (non-quiz question)", "TEST")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "설민석 선생님 나이가 어떻게 되시나요?",
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": self.character_id,
                "user_id": self.user_id,
                "session_id": self.session_id
            })
            
            if response.status_code != 200:
                self.log(f"Mixed conversation failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            tools = data.get("tools", [])
            
            self.log(f"  Non-quiz response: {dialogue[:100]}...", "UI")
            self.log(f"  Audio provided: {'YES' if audio else 'NO'}", "AUDIO")
            self.log(f"  Tools generated: {len(tools)}", "DEBUG")
            
            # Should respond naturally without quiz tools
            has_dialogue = len(dialogue) > 10
            has_audio = audio is not None
            no_quiz_tools = len(tools) == 0 or tools[0].get("type") != "show_selection"
            
            return has_dialogue and has_audio and no_quiz_tools
            
        except Exception as e:
            self.log(f"Mixed conversation error: {e}", "ERROR")
            return False
    
    def run_complete_test(self) -> bool:
        """Run complete 설민석 quiz flow test"""
        self.log("="*80, "TEST")
        self.log("🧪 COMPREHENSIVE 설민석 AI 퀴즈 튜터 FLOW TEST", "TEST")
        self.log("Testing complete quiz flow with UI triggers and continuous flow", "TEST")
        self.log("="*80, "TEST")
        
        steps = [
            ("Greeting with Suggestions", self.test_step_1_greeting_with_suggestions),
            ("Topic Selection → Quiz UI", self.test_step_2_topic_selection_quiz_ui),
            ("Answer → Continuous Flow", self.test_step_3_answer_triggers_flow),
            ("Second LLM → Next Quiz", self.test_step_4_second_llm_next_quiz),
            ("Mixed Conversation", self.test_step_5_mixed_conversation)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*50}", "TEST")
            success = step_func()
            results[step_name] = success
            
            if not success:
                self.log(f"❌ FAILED at {step_name}", "ERROR")
                # Continue testing other steps even if one fails
            else:
                self.log(f"✅ PASSED {step_name}", "SUCCESS")
                
            time.sleep(1)  # Simulate user interaction delay
        
        # Summary
        self.log("\n" + "="*80, "TEST")
        self.log("📊 TEST RESULTS SUMMARY", "TEST")
        self.log("="*80, "TEST")
        
        all_passed = True
        for step, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"{step}: {status}", "TEST")
            if not passed:
                all_passed = False
        
        self.log("\n" + "="*80, "TEST")
        if all_passed:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
            self.log("✅ Greeting with quiz suggestions works", "SUCCESS")
            self.log("✅ Quiz UI generation works", "SUCCESS")
            self.log("✅ Continuous flow triggers properly", "SUCCESS")
            self.log("✅ Second LLM generates next quiz", "SUCCESS")
            self.log("✅ Mixed conversation works", "SUCCESS")
        else:
            self.log("⚠️ SOME TESTS FAILED - CHECK ISSUES ABOVE", "ERROR")
            
        return all_passed

if __name__ == "__main__":
    tester = SeolMinSeokQuizTester()
    success = tester.run_complete_test()
    exit(0 if success else 1)