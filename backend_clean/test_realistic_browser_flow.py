#!/usr/bin/env python3
"""
Realistic Browser Flow Test
Tests exactly what happens in the browser frontend:
1. User loads page → greeting with topics
2. User clicks topic → quiz question with proper text (not truncated)
3. User clicks answer → continuous flow displays feedback text + audio
4. After audio → second LLM call shows next quiz with UI
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional

BASE_URL = "http://localhost:8000"

class BrowserFlowTester:
    def __init__(self):
        self.session_id = None
        self.current_tools = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log with clear indicators"""
        emoji = {
            "BROWSER": "🌐",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "DEBUG": "🔍",
            "UI": "🖥️",
            "AUDIO": "🎵",
            "FLOW": "🔄"
        }.get(level, "📝")
        print(f"{emoji} {message}")
        
    def test_browser_step_1_page_load(self) -> bool:
        """Step 1: User loads character page (browser behavior)"""
        self.log("BROWSER STEP 1: User loads 설민석 quiz character page", "BROWSER")
        
        try:
            # This mimics what happens when user opens the character page
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "안녕하세요",
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz",
                "user_id": "browser_user"
            })
            
            if response.status_code != 200:
                self.log(f"Page load failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            self.session_id = data.get("session_id")
            self.current_tools = data.get("tools", [])
            
            # Verify what user sees
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            
            self.log(f"  User sees greeting: {dialogue[:60]}...", "UI")
            self.log(f"  Audio provided: {len(audio) if audio else 0} bytes", "AUDIO")
            self.log(f"  Topic options: {len(self.current_tools)} available", "UI")
            
            if self.current_tools:
                topics = self.current_tools[0].get("data", {}).get("items", [])
                self.log(f"  Topics: {topics}", "DEBUG")
            
            return len(self.current_tools) > 0 and self.session_id
            
        except Exception as e:
            self.log(f"Page load error: {e}", "ERROR")
            return False
    
    def test_browser_step_2_topic_click(self) -> bool:
        """Step 2: User clicks on topic (조선시대 퀴즈)"""
        self.log("BROWSER STEP 2: User clicks '조선시대 퀴즈' topic", "BROWSER")
        
        if not self.current_tools:
            self.log("No topics available to click", "ERROR")
            return False
            
        try:
            # User clicks first topic
            topic = self.current_tools[0]["data"]["items"][0]  # "조선시대 퀴즈"
            self.log(f"  Clicking topic: {topic}", "UI")
            
            # Frontend sends this as regular message (no correct_answer in greeting)
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": topic,
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz",
                "user_id": "browser_user",
                "session_id": self.session_id
            })
            
            if response.status_code != 200:
                self.log(f"Topic click failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            quiz_tools = data.get("tools", [])
            
            # This is the KEY TEST - user should see full question text
            self.log(f"  User sees quiz intro: {dialogue}", "UI")
            self.log(f"  Audio provided: {len(audio) if audio else 0} bytes", "AUDIO")
            
            if quiz_tools:
                quiz_data = quiz_tools[0]["data"]
                self.log(f"  Quiz question: {quiz_data.get('question', 'MISSING')}", "UI")
                self.log(f"  Quiz options: {quiz_data.get('items', [])}", "UI")
                self.log(f"  Correct answer: {quiz_data.get('correct_answer', 'MISSING')}", "DEBUG")
                
                # Store for next step
                self.current_tools = quiz_tools
                
                # Verify question is in dialogue OR in quiz data
                has_question_in_dialogue = "세종대왕" in dialogue or len(dialogue) > 50
                has_quiz_structure = quiz_data.get("question") and quiz_data.get("items")
                
                return has_question_in_dialogue and has_quiz_structure
            else:
                self.log("  No quiz tools generated!", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Topic click error: {e}", "ERROR")
            return False
    
    def test_browser_step_3_quiz_answer(self) -> bool:
        """Step 3: User clicks quiz answer → continuous flow"""
        self.log("BROWSER STEP 3: User clicks quiz answer", "BROWSER")
        
        if not self.current_tools:
            self.log("No quiz to answer", "ERROR")
            return False
            
        try:
            quiz_data = self.current_tools[0]["data"]
            correct_answer = quiz_data.get("correct_answer")
            
            if not correct_answer:
                self.log("No correct answer available", "ERROR")
                return False
                
            self.log(f"  User clicks: {correct_answer}", "UI")
            
            # Frontend triggers continuous flow (has correct_answer)
            response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
                "session_id": self.session_id,
                "character_id": "seol_min_seok_quiz",
                "tool_type": "show_selection",
                "data": {
                    "selection": correct_answer,
                    "correct_answer": correct_answer,
                    "question": quiz_data.get("question", ""),
                    "items": quiz_data.get("items", [])
                }
            })
            
            if response.status_code != 200:
                self.log(f"Continuous flow failed: {response.status_code}", "ERROR")
                return False
                
            flow_result = response.json()
            step_result = flow_result.get("step_result", {})
            
            if not step_result:
                self.log("No step result from continuous flow", "ERROR")
                return False
                
            # This is what handleFlowStepResult receives
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            # Critical test: UI should display this as normal message
            self.log(f"  Frontend receives feedback text: {dialogue[:100]}...", "UI")
            self.log(f"  Frontend receives audio: {len(audio) if audio else 0} bytes", "AUDIO") 
            self.log(f"  Flow continues: {flow_result.get('flow_continues', False)}", "FLOW")
            
            # Verify this is educational feedback
            has_feedback = any(word in dialogue for word in ["정답", "훌륭", "맞습니다"])
            has_dialogue = len(dialogue) > 10
            has_audio = audio and len(audio) > 1000
            
            if not has_dialogue:
                self.log("  ERROR: No dialogue text for UI", "ERROR")
            if not has_audio:
                self.log("  ERROR: No audio for playback", "ERROR")
            if not has_feedback:
                self.log("  ERROR: No educational feedback", "ERROR")
                
            return has_dialogue and has_audio and has_feedback
            
        except Exception as e:
            self.log(f"Quiz answer error: {e}", "ERROR")
            return False
    
    def test_browser_step_4_flow_continuation(self) -> bool:
        """Step 4: After audio plays → second LLM call → next quiz UI"""
        self.log("BROWSER STEP 4: Audio finishes → automatic next step", "BROWSER")
        
        try:
            # Simulate audio completion (frontend calls this automatically)
            self.log("  Audio finished playing, triggering next step...", "AUDIO")
            
            response = requests.post(f"{BASE_URL}/api/continuous-flow/progress", json={
                "session_id": self.session_id,
                "trigger_type": "audio_completion"
            })
            
            if response.status_code != 200:
                self.log(f"Flow progress failed: {response.status_code}", "ERROR")
                return False
                
            progress_result = response.json()
            step_result = progress_result.get("step_result", {})
            
            if not step_result:
                self.log("No second step result", "ERROR")
                return False
                
            # This is the second LLM output
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            # Critical test: Should be next quiz question
            self.log(f"  Second LLM output: {dialogue}", "UI")
            self.log(f"  Second audio: {len(audio) if audio else 0} bytes", "AUDIO")
            
            # Check if it looks like a quiz (has A), B), etc.)
            import re
            is_quiz_format = bool(re.search(r'[①-④]|[A-D]\)|[1-4]\)', dialogue))
            has_question = "?" in dialogue or "언제" in dialogue or "무엇" in dialogue
            
            self.log(f"  Is quiz format: {is_quiz_format}", "DEBUG")
            self.log(f"  Has question: {has_question}", "DEBUG")
            
            # Verify this would display properly in UI
            has_dialogue = len(dialogue) > 10
            has_audio = audio and len(audio) > 1000
            is_next_quiz = is_quiz_format and has_question
            
            if not has_dialogue:
                self.log("  ERROR: No dialogue for second UI update", "ERROR")
            if not has_audio:
                self.log("  ERROR: No audio for second playback", "ERROR")
            if not is_next_quiz:
                self.log("  ERROR: Second output is not a quiz question", "ERROR")
                
            return has_dialogue and has_audio and is_next_quiz
            
        except Exception as e:
            self.log(f"Flow continuation error: {e}", "ERROR")
            return False
    
    def run_complete_browser_test(self) -> bool:
        """Run complete browser simulation"""
        self.log("="*80, "BROWSER")
        self.log("🌐 COMPLETE BROWSER FLOW SIMULATION", "BROWSER")
        self.log("Testing: Page Load → Topic Click → Quiz Answer → Flow Continuation", "BROWSER")
        self.log("="*80, "BROWSER")
        
        steps = [
            ("Page Load", self.test_browser_step_1_page_load),
            ("Topic Click", self.test_browser_step_2_topic_click),  
            ("Quiz Answer", self.test_browser_step_3_quiz_answer),
            ("Flow Continuation", self.test_browser_step_4_flow_continuation)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*50}", "BROWSER")
            success = step_func()
            results[step_name] = success
            
            if not success:
                self.log(f"❌ FAILED at {step_name}", "ERROR")
                break
            else:
                self.log(f"✅ PASSED {step_name}", "SUCCESS")
                
            time.sleep(1)  # Simulate user interaction delay
        
        # Summary
        self.log("\n" + "="*80, "BROWSER")
        self.log("📊 BROWSER SIMULATION RESULTS", "BROWSER")
        self.log("="*80, "BROWSER")
        
        all_passed = True
        for step, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"{step}: {status}", "BROWSER")
            if not passed:
                all_passed = False
        
        self.log("\n" + "="*80, "BROWSER")
        if all_passed:
            self.log("🎉 COMPLETE BROWSER FLOW SUCCESS!", "SUCCESS")
            self.log("✅ Quiz text displays properly", "SUCCESS")
            self.log("✅ Continuous flow updates UI text", "SUCCESS")
            self.log("✅ Audio plays at each step", "SUCCESS")
            self.log("✅ Next quiz appears automatically", "SUCCESS")
        else:
            self.log("⚠️ BROWSER FLOW ISSUES DETECTED", "ERROR")
            
        return all_passed
        
    def debug_failures(self):
        """Debug specific failure points"""
        self.log("\n🔧 DEBUGGING GUIDE FOR FRONTEND:", "DEBUG")
        self.log("1. Hard refresh browser (Ctrl+Shift+R)", "DEBUG")
        self.log("2. Check browser console for handleFlowStepResult logs", "DEBUG")
        self.log("3. Verify setMessages and setCurrentAudio are called", "DEBUG")
        self.log("4. Check if shouldStartTyping state affects display", "DEBUG")

if __name__ == "__main__":
    tester = BrowserFlowTester()
    success = tester.run_complete_browser_test()
    
    if not success:
        tester.debug_failures()
        
    exit(0 if success else 1)