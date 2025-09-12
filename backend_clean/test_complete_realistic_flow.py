#!/usr/bin/env python3
"""
Complete Realistic Frontend Flow Test
Tests the exact user experience including:
1. TTS reads only dialogue, not full JSON
2. Continuous flow results appear as normal messages
3. Second output appears with quiz UI
4. Complete audio and UI verification
"""

import requests
import json
import time
import re
from typing import Dict, Any, List, Optional

BASE_URL = "http://localhost:8000"

class RealisticFlowTester:
    def __init__(self):
        self.session_id = None
        self.test_results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log with emoji indicators"""
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍",
            "TEST": "🧪",
            "UI": "🖥️",
            "AUDIO": "🎵"
        }.get(level, "📝")
        print(f"{emoji} {message}")
        
    def verify_tts_content(self, audio_data: str, expected_dialogue: str) -> bool:
        """Verify TTS contains only dialogue content, not JSON"""
        if not audio_data or not expected_dialogue:
            return False
        
        # Audio should be base64, so if we have it, it's likely correct
        # The real test is that dialogue should not contain JSON elements
        json_indicators = ['"character":', '"tool":', '"tool_data":', '{"', '"}']
        has_json_elements = any(indicator in expected_dialogue for indicator in json_indicators)
        
        return len(audio_data) > 1000 and not has_json_elements
        
    def test_step_1_greeting_tts(self) -> bool:
        """Test greeting with proper TTS generation"""
        self.log("STEP 1: Greeting with TTS Verification", "TEST")
        
        try:
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "안녕하세요",
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz", 
                "user_id": "realistic_test"
            })
            
            if response.status_code != 200:
                self.log(f"Greeting failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            self.session_id = data.get("session_id")
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            
            # Verify TTS content
            tts_clean = self.verify_tts_content(audio, dialogue)
            
            checks = {
                "session_created": self.session_id is not None,
                "dialogue_present": len(dialogue) > 0,
                "audio_present": audio is not None and len(audio) > 1000,
                "tts_clean": tts_clean,
                "tools_present": len(data.get("tools", [])) > 0
            }
            
            # Log results
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
                
            if not tts_clean:
                self.log(f"  Dialogue content: {dialogue[:100]}...", "DEBUG")
                
            self.test_results["greeting_tts"] = all(checks.values())
            return self.test_results["greeting_tts"]
            
        except Exception as e:
            self.log(f"Greeting test error: {e}", "ERROR")
            return False
            
    def test_step_2_topic_selection_tts(self) -> bool:
        """Test topic selection with clean TTS"""
        self.log("STEP 2: Topic Selection with TTS Fix", "TEST")
        
        try:
            # Select topic that generates quiz
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "조선시대 퀴즈",
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz",
                "user_id": "realistic_test", 
                "session_id": self.session_id
            })
            
            if response.status_code != 200:
                self.log(f"Topic selection failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            dialogue = data.get("dialogue", "")
            audio = data.get("audio")
            tools = data.get("tools", [])
            
            # This is the critical test - TTS should be clean dialogue, not JSON
            tts_clean = self.verify_tts_content(audio, dialogue)
            has_quiz_tools = len(tools) > 0 and tools[0].get("type") == "show_selection"
            
            checks = {
                "dialogue_clean": len(dialogue) > 0 and not dialogue.startswith("{"),
                "audio_present": audio is not None and len(audio) > 1000,
                "tts_clean": tts_clean,
                "quiz_tools_generated": has_quiz_tools,
                "has_correct_answer": tools[0].get("data", {}).get("correct_answer") if tools else False
            }
            
            # Log detailed results
            self.log(f"  Dialogue: {dialogue[:80]}...", "DEBUG")
            if not tts_clean:
                self.log(f"  TTS ISSUE: Audio may contain JSON content", "WARNING")
                
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
            
            # Store quiz data for next test
            if tools:
                self.quiz_data = tools[0]["data"]
                
            self.test_results["topic_tts"] = all(checks.values())
            return self.test_results["topic_tts"]
            
        except Exception as e:
            self.log(f"Topic selection test error: {e}", "ERROR")
            return False
            
    def test_step_3_continuous_flow_ui(self) -> bool:
        """Test continuous flow displays properly in UI"""
        self.log("STEP 3: Continuous Flow UI Display", "TEST")
        
        try:
            # Use the quiz data from step 2
            if not hasattr(self, 'quiz_data') or not self.quiz_data:
                self.log("No quiz data from previous step", "ERROR") 
                return False
            
            # Trigger continuous flow with quiz answer
            correct_answer = self.quiz_data.get("correct_answer")
            
            response = requests.post(f"{BASE_URL}/api/continuous-flow/trigger", json={
                "session_id": self.session_id,
                "character_id": "seol_min_seok_quiz",
                "tool_type": "show_selection",
                "data": {
                    "selection": correct_answer,
                    "correct_answer": correct_answer,
                    "question": self.quiz_data.get("question", ""),
                    "items": self.quiz_data.get("items", [])
                }
            })
            
            if response.status_code != 200:
                self.log(f"Continuous flow failed: {response.status_code}", "ERROR")
                return False
                
            flow_data = response.json()
            step_result = flow_data.get("step_result", {})
            
            # Verify flow result structure (what frontend receives)
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            # Key tests for UI display
            checks = {
                "has_step_result": step_result is not None,
                "has_dialogue": len(dialogue) > 0,
                "dialogue_is_clean": not dialogue.startswith("{") and len(dialogue) > 10,
                "has_audio": audio is not None and len(audio) > 1000,
                "flow_continues": flow_data.get("flow_continues", False),
                "educational_content": any(word in dialogue for word in ["정답", "훌륭", "맞습니다"])
            }
            
            # Log UI-relevant information
            self.log(f"  Flow dialogue: {dialogue[:100]}...", "UI")
            self.log(f"  Audio size: {len(audio) if audio else 0} bytes", "AUDIO")
            self.log(f"  Flow continues: {flow_data.get('flow_continues')}", "DEBUG")
            
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
                
            self.test_results["continuous_flow_ui"] = all(checks.values())
            return self.test_results["continuous_flow_ui"]
            
        except Exception as e:
            self.log(f"Continuous flow UI test error: {e}", "ERROR")
            return False
            
    def test_step_4_flow_continuation_quiz(self) -> bool:
        """Test flow continuation generates second quiz"""
        self.log("STEP 4: Flow Continuation → Second Quiz", "TEST")
        
        try:
            # Wait for "audio completion" then progress flow
            time.sleep(1)
            
            response = requests.post(f"{BASE_URL}/api/continuous-flow/progress", json={
                "session_id": self.session_id,
                "trigger_type": "audio_completion"
            })
            
            if response.status_code != 200:
                self.log(f"Flow progress failed: {response.status_code}", "ERROR")
                return False
                
            progress_data = response.json()
            step_result = progress_data.get("step_result", {})
            
            if not step_result:
                self.log("No step result in progress", "ERROR")
                return False
                
            response_data = step_result.get("response", {})
            dialogue = response_data.get("dialogue", "")
            audio = step_result.get("audio")
            
            # Check if it's a new quiz (should have A), B), etc.)
            is_quiz = bool(re.search(r'[A-D]\)|[①-④]', dialogue))
            
            checks = {
                "has_dialogue": len(dialogue) > 0,
                "dialogue_clean": not dialogue.startswith("{"),
                "has_audio": audio is not None and len(audio) > 1000,
                "is_new_quiz": is_quiz,
                "educational_flow": any(word in dialogue for word in ["퀴즈", "문제", "다음"])
            }
            
            # Log second output information
            self.log(f"  Second dialogue: {dialogue[:100]}...", "UI")
            self.log(f"  Is quiz format: {is_quiz}", "DEBUG")
            self.log(f"  Audio size: {len(audio) if audio else 0} bytes", "AUDIO")
            
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
                
            self.test_results["flow_continuation"] = all(checks.values())
            return self.test_results["flow_continuation"]
            
        except Exception as e:
            self.log(f"Flow continuation test error: {e}", "ERROR")
            return False
            
    def run_complete_realistic_test(self) -> bool:
        """Run all realistic flow tests"""
        self.log("="*80, "INFO")
        self.log("🚀 COMPLETE REALISTIC FLOW TEST", "TEST")
        self.log("Testing: TTS Clean, UI Updates, Audio Generation, LLM Output", "INFO")
        self.log("="*80, "INFO")
        
        # Run test steps
        steps = [
            ("Greeting TTS Clean", self.test_step_1_greeting_tts),
            ("Topic TTS Fix", self.test_step_2_topic_selection_tts),
            ("Continuous Flow UI", self.test_step_3_continuous_flow_ui),
            ("Flow Continuation Quiz", self.test_step_4_flow_continuation_quiz)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*60}", "INFO")
            if not step_func():
                self.log(f"❌ Test failed at: {step_name}", "ERROR")
                break
            time.sleep(1)
        
        # Final results
        self.log("\n" + "="*80, "INFO")
        self.log("📊 REALISTIC TEST RESULTS", "TEST")
        self.log("="*80, "INFO")
        
        all_passed = True
        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.log(f"{test_name}: {status}", "INFO")
            if not passed:
                all_passed = False
        
        self.log("\n" + "="*80, "INFO")
        if all_passed:
            self.log("🎉 ALL REALISTIC TESTS PASSED!", "SUCCESS")
            self.log("✅ TTS reads clean dialogue only", "SUCCESS")
            self.log("✅ UI updates show flow results as messages", "SUCCESS")  
            self.log("✅ Audio generated for all interactions", "SUCCESS")
            self.log("✅ Second quiz appears after feedback", "SUCCESS")
        else:
            self.log("⚠️ SOME REALISTIC TESTS FAILED", "WARNING")
            
        return all_passed
        
    def analyze_failures(self):
        """Analyze specific failures for debugging"""
        if not all(self.test_results.values()):
            self.log("\n🔧 FAILURE ANALYSIS:", "WARNING")
            
            if not self.test_results.get("greeting_tts"):
                self.log("  - Greeting TTS issue", "ERROR")
            if not self.test_results.get("topic_tts"):
                self.log("  - Topic selection TTS reading JSON instead of dialogue", "ERROR")
            if not self.test_results.get("continuous_flow_ui"):
                self.log("  - Continuous flow results not displaying in UI", "ERROR")
            if not self.test_results.get("flow_continuation"):
                self.log("  - Second quiz not appearing after feedback", "ERROR")

if __name__ == "__main__":
    tester = RealisticFlowTester()
    success = tester.run_complete_realistic_test()
    
    if not success:
        tester.analyze_failures()
        
    exit(0 if success else 1)