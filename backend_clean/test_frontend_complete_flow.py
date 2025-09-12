#!/usr/bin/env python3
"""
TDD Frontend Complete Flow Test
Tests the entire user journey through the frontend, verifying:
1. Initial greeting with topic selection UI
2. Topic selection triggers quiz generation with audio
3. Quiz answer triggers continuous flow with feedback and audio
4. Second continuous flow step (next question or encouragement)
5. Complete UI updates and audio playback at each step
"""

import requests
import json
import time
import base64
from typing import Dict, Any, List, Optional

BASE_URL = "http://localhost:8000"

class FrontendFlowTester:
    def __init__(self):
        self.session_id = None
        self.current_tools = []
        self.messages = []
        self.test_results = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Log with emoji indicators"""
        emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍",
            "TEST": "🧪"
        }.get(level, "📝")
        print(f"{emoji} {message}")
        
    def verify_audio(self, audio_data: Optional[str]) -> bool:
        """Verify audio data is present and valid"""
        if not audio_data:
            return False
        # If it's a string with reasonable length, it's likely base64 audio
        if isinstance(audio_data, str) and len(audio_data) > 1000:
            return True
        return False
            
    def test_step_1_greeting(self) -> bool:
        """Step 1: Get initial greeting with topic selection tools"""
        self.log("STEP 1: Initial Greeting", "TEST")
        
        try:
            # Simulate frontend loading character page
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": "안녕하세요",
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz",
                "user_id": "frontend_test_user"
            })
            
            if response.status_code != 200:
                self.log(f"Greeting request failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            self.session_id = data.get("session_id")
            
            # Debug audio data
            audio_data = data.get("audio")
            self.log(f"  Audio data type: {type(audio_data)}", "DEBUG")
            if audio_data:
                self.log(f"  Audio data length: {len(audio_data)}", "DEBUG")
            
            # Verify response structure
            checks = {
                "session_id": self.session_id is not None,
                "dialogue": len(data.get("dialogue", "")) > 0,
                "tools_present": len(data.get("tools", [])) > 0,
                "audio_present": self.verify_audio(data.get("audio"))
            }
            
            # Verify tool structure for greeting
            if data.get("tools"):
                tool = data["tools"][0]
                tool_checks = {
                    "tool_type": tool.get("type") == "show_selection",
                    "has_items": len(tool.get("data", {}).get("items", [])) > 0,
                    "no_correct_answer": "correct_answer" not in tool.get("data", {}) or not tool["data"]["correct_answer"]
                }
                checks.update(tool_checks)
                self.current_tools = data["tools"]
            
            # Log results
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
            
            self.test_results["greeting"] = all(checks.values())
            
            if self.test_results["greeting"]:
                self.log("Greeting successful with topic selection tools", "SUCCESS")
                self.log(f"  Topics available: {tool.get('data', {}).get('items', [])}", "INFO")
            else:
                self.log("Greeting failed some checks", "ERROR")
                
            return self.test_results["greeting"]
            
        except Exception as e:
            self.log(f"Greeting test error: {e}", "ERROR")
            return False
            
    def test_step_2_topic_selection(self) -> bool:
        """Step 2: Select topic and get quiz question"""
        self.log("STEP 2: Topic Selection → Quiz Generation", "TEST")
        
        if not self.current_tools:
            self.log("No tools available from greeting", "ERROR")
            return False
            
        try:
            # Select first topic (조선시대 퀴즈)
            topic = self.current_tools[0]["data"]["items"][0]
            self.log(f"Selecting topic: {topic}", "INFO")
            
            # Frontend would send this as regular message (no correct_answer in greeting)
            response = requests.post(f"{BASE_URL}/api/chat-with-session", json={
                "message": topic,
                "character_prompt": "당신은 설민석 선생님입니다.",
                "character_id": "seol_min_seok_quiz",
                "user_id": "frontend_test_user",
                "session_id": self.session_id
            })
            
            if response.status_code != 200:
                self.log(f"Topic selection failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            
            # Verify quiz question generation
            checks = {
                "dialogue_present": len(data.get("dialogue", "")) > 0,
                "quiz_tools_present": len(data.get("tools", [])) > 0,
                "audio_present": self.verify_audio(data.get("audio"))
            }
            
            # Verify quiz tool structure
            if data.get("tools"):
                tool = data["tools"][0]
                quiz_checks = {
                    "tool_type": tool.get("type") == "show_selection",
                    "has_question": bool(tool.get("data", {}).get("question")),
                    "has_options": len(tool.get("data", {}).get("items", [])) > 0,
                    "has_correct_answer": bool(tool.get("data", {}).get("correct_answer")),
                    "is_quiz_mode": tool.get("data", {}).get("selection_mode") == "quiz_question"
                }
                checks.update(quiz_checks)
                self.current_tools = data["tools"]
                
                self.log(f"  Quiz question: {tool.get('data', {}).get('question', '')[:50]}...", "INFO")
                self.log(f"  Options: {tool.get('data', {}).get('items', [])}", "INFO")
                self.log(f"  Correct answer: {tool.get('data', {}).get('correct_answer')}", "DEBUG")
            
            # Log results
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
            
            self.test_results["topic_selection"] = all(checks.values())
            
            if self.test_results["topic_selection"]:
                self.log("Topic selection successful, quiz generated", "SUCCESS")
            else:
                self.log("Topic selection failed some checks", "ERROR")
                
            return self.test_results["topic_selection"]
            
        except Exception as e:
            self.log(f"Topic selection test error: {e}", "ERROR")
            return False
            
    def test_step_3_quiz_answer(self) -> bool:
        """Step 3: Answer quiz and trigger continuous flow"""
        self.log("STEP 3: Quiz Answer → Continuous Flow", "TEST")
        
        if not self.current_tools:
            self.log("No quiz tools available", "ERROR")
            return False
            
        try:
            quiz_tool = self.current_tools[0]
            quiz_data = quiz_tool["data"]
            correct_answer = quiz_data.get("correct_answer")
            
            if not correct_answer:
                self.log("No correct answer in quiz data", "ERROR")
                return False
                
            self.log(f"Answering with: {correct_answer}", "INFO")
            
            # Frontend triggers continuous flow for quiz answers
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
                self.log(f"Continuous flow trigger failed: {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"  Error details: {error_data}", "ERROR")
                except:
                    self.log(f"  Error text: {response.text}", "ERROR")
                return False
                
            data = response.json()
            
            # Verify continuous flow response
            checks = {
                "status_correct": data.get("status") == "flow_triggered",
                "has_step_result": data.get("step_result") is not None,
                "flow_continues": data.get("flow_continues", False),
                "has_next_step": data.get("next_step_index") is not None
            }
            
            # Verify step result content
            if data.get("step_result"):
                step = data["step_result"]
                step_checks = {
                    "has_response": step.get("response") is not None,
                    "has_dialogue": bool(step.get("response", {}).get("dialogue")),
                    "has_audio": self.verify_audio(step.get("audio")),
                    "has_feedback": any(word in step.get("response", {}).get("dialogue", "") 
                                      for word in ["정답", "훌륭", "맞습니다", "틀렸"])
                }
                checks.update(step_checks)
                
                dialogue = step.get("response", {}).get("dialogue", "")
                self.log(f"  Feedback: {dialogue[:100]}...", "INFO")
                self.log(f"  Audio size: {len(step.get('audio', '')) if step.get('audio') else 0} bytes", "DEBUG")
            
            # Log results
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
            
            self.test_results["quiz_answer"] = all(checks.values())
            
            if self.test_results["quiz_answer"]:
                self.log("Quiz answer processed, continuous flow triggered", "SUCCESS")
            else:
                self.log("Quiz answer failed some checks", "ERROR")
                
            return self.test_results["quiz_answer"]
            
        except Exception as e:
            self.log(f"Quiz answer test error: {e}", "ERROR")
            return False
            
    def test_step_4_flow_continuation(self) -> bool:
        """Step 4: Test flow continuation (next question or encouragement)"""
        self.log("STEP 4: Flow Continuation", "TEST")
        
        # Wait for audio to "complete" (simulate frontend behavior)
        time.sleep(2)
        
        try:
            # Trigger next step after audio completion
            response = requests.post(f"{BASE_URL}/api/continuous-flow/progress", json={
                "session_id": self.session_id,
                "trigger_type": "audio_completion"
            })
            
            if response.status_code != 200:
                self.log(f"Flow progress failed: {response.status_code}", "ERROR")
                return False
                
            data = response.json()
            
            # Verify next step
            checks = {
                "has_step_result": data.get("step_result") is not None,
                "has_dialogue": bool(data.get("step_result", {}).get("response", {}).get("dialogue")),
                "has_audio": self.verify_audio(data.get("step_result", {}).get("audio"))
            }
            
            # Check if new quiz or encouragement
            if data.get("step_result"):
                dialogue = data["step_result"]["response"]["dialogue"]
                checks["has_content"] = len(dialogue) > 0
                
                # Check for new quiz pattern
                if "?" in dialogue and any(c in dialogue for c in ["A)", "1)", "①"]):
                    self.log("  New quiz question detected", "INFO")
                else:
                    self.log("  Encouragement or summary detected", "INFO")
                    
                self.log(f"  Next dialogue: {dialogue[:100]}...", "INFO")
            
            # Log results
            for check, passed in checks.items():
                self.log(f"  {check}: {'✅' if passed else '❌'}", "DEBUG")
            
            self.test_results["flow_continuation"] = all(checks.values())
            
            if self.test_results["flow_continuation"]:
                self.log("Flow continuation successful", "SUCCESS")
            else:
                self.log("Flow continuation failed some checks", "ERROR")
                
            return self.test_results["flow_continuation"]
            
        except Exception as e:
            self.log(f"Flow continuation test error: {e}", "ERROR")
            return False
            
    def run_complete_test(self) -> bool:
        """Run all test steps in sequence"""
        self.log("="*80, "INFO")
        self.log("🚀 FRONTEND COMPLETE FLOW TEST", "TEST")
        self.log("="*80, "INFO")
        
        # Run test steps in order
        steps = [
            ("Greeting", self.test_step_1_greeting),
            ("Topic Selection", self.test_step_2_topic_selection),
            ("Quiz Answer", self.test_step_3_quiz_answer),
            ("Flow Continuation", self.test_step_4_flow_continuation)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n{'='*60}", "INFO")
            if not step_func():
                self.log(f"Test stopped at: {step_name}", "ERROR")
                break
            time.sleep(1)  # Small delay between steps
        
        # Summary
        self.log("\n" + "="*80, "INFO")
        self.log("📊 TEST RESULTS SUMMARY", "TEST")
        self.log("="*80, "INFO")
        
        all_passed = True
        for test_name, passed in self.test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"{test_name}: {status}", "INFO")
            if not passed:
                all_passed = False
        
        self.log("\n" + "="*80, "INFO")
        if all_passed:
            self.log("🎉 ALL TESTS PASSED! Frontend flow working correctly.", "SUCCESS")
        else:
            self.log("⚠️ SOME TESTS FAILED. See details above.", "WARNING")
            
        return all_passed
        
    def analyze_issues(self):
        """Analyze and report specific issues found"""
        issues = []
        
        if not self.test_results.get("greeting"):
            issues.append("Greeting not returning proper topic selection tools")
            
        if not self.test_results.get("topic_selection"):
            if "audio_present" in self.test_results:
                issues.append("Quiz generation missing audio")
            if "has_correct_answer" in self.test_results:
                issues.append("Quiz missing correct_answer field")
                
        if not self.test_results.get("quiz_answer"):
            issues.append("Continuous flow not triggering properly")
            if "has_audio" in self.test_results:
                issues.append("Continuous flow missing audio")
            if "has_feedback" in self.test_results:
                issues.append("Educational feedback not generated")
                
        if not self.test_results.get("flow_continuation"):
            issues.append("Flow not continuing after audio completion")
            
        if issues:
            self.log("\n🔧 IDENTIFIED ISSUES:", "WARNING")
            for i, issue in enumerate(issues, 1):
                self.log(f"  {i}. {issue}", "WARNING")
                
            self.log("\n📝 RECOMMENDED FIXES:", "INFO")
            if "audio" in str(issues).lower():
                self.log("  - Check TTS service configuration and fallback", "INFO")
            if "correct_answer" in str(issues).lower():
                self.log("  - Verify tool data structure in backend", "INFO")
            if "continuous flow" in str(issues).lower():
                self.log("  - Check template substitution in continuous flow", "INFO")
                self.log("  - Verify frontend is passing correct_answer properly", "INFO")

if __name__ == "__main__":
    tester = FrontendFlowTester()
    success = tester.run_complete_test()
    
    if not success:
        tester.analyze_issues()
        
    # Return exit code for CI/CD integration
    exit(0 if success else 1)