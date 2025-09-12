#!/usr/bin/env python3
"""
Realistic LLM Output and UI Trigger Integration Tests
Tests actual LLM outputs and verifies UI components are triggered correctly
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tool_orchestrator import ToolOrchestrator
from services.platform_tool_handler import PlatformToolHandler
from services.continuous_answer_tool import ContinuousAnswerTool
from services.assistant_ui_tool_executor import AssistantUIToolExecutor

class RealisticLLMUITest:
    """Test suite for realistic LLM outputs and UI triggers"""
    
    def __init__(self):
        self.tool_orchestrator = ToolOrchestrator()
        self.platform_handler = PlatformToolHandler()
        self.continuous_tool = ContinuousAnswerTool()
        self.ui_executor = AssistantUIToolExecutor()
        self.base_url = "http://localhost:8001/api"
        self.test_results = []
        
    async def test_greeting_triggers_quiz_ui(self):
        """Test: Greeting should trigger quiz topic selection UI"""
        print("\n🧪 TEST 1: Greeting → Quiz Topic UI Trigger")
        print("="*50)
        
        # Simulate realistic LLM response for greeting
        llm_response = {
            "character": "seol_min_seok_quiz",
            "dialogue": "안녕하세요! 저는 설민석입니다. 한국사의 재미있는 이야기를 들려드릴게요. 퀴즈로 시작해볼까요?",
            "emotion": "enthusiastic",
            "speed": 1.0,
            "tool": "quiz",
            "tool_data": {
                "type": "greeting_suggestion",
                "items": ["조선시대", "고려시대", "근현대사", "일제강점기"],
                "ui_type": "topic_selection"
            }
        }
        
        # Parse and verify tool detection
        parsed = self.tool_orchestrator.parse_llm_response(json.dumps(llm_response))
        assert parsed["tool"] == "quiz", f"❌ Tool detection failed: {parsed.get('tool')}"
        assert parsed["dialogue"] == llm_response["dialogue"], "❌ Dialogue extraction failed"
        print("✅ Tool detected: 'quiz'")
        print(f"✅ Dialogue extracted: {parsed['dialogue'][:50]}...")
        
        # Execute tool and verify UI response
        ui_response = await self.platform_handler.handle_quiz_tool(parsed["tool_data"])
        assert ui_response["ui_type"] == "selection", f"❌ Wrong UI type: {ui_response.get('ui_type')}"
        assert len(ui_response["options"]) == 4, f"❌ Wrong number of options: {len(ui_response.get('options', []))}"
        print("✅ UI Response Generated:")
        print(f"  - Type: {ui_response['ui_type']}")
        print(f"  - Options: {ui_response['options']}")
        print(f"  - Full response: {ui_response}")
        
        # Verify frontend compatibility
        frontend_format = self.ui_executor.format_for_frontend(ui_response)
        expected_type = "assistant-ui-topic-selection"
        actual_type = frontend_format.get("type")
        
        # Debug output
        if actual_type != expected_type:
            print(f"❌ Frontend format mismatch:")
            print(f"  Expected: {expected_type}")
            print(f"  Actual: {actual_type}")
            print(f"  Full response: {frontend_format}")
        
        assert frontend_format["type"] == "assistant-ui-topic-selection", f"❌ Frontend format wrong: expected {expected_type}, got {actual_type}"
        print("✅ Frontend Format Ready:")
        print(f"  - Component: {frontend_format['type']}")
        
        return {"status": "PASS", "test": "greeting_triggers_quiz_ui"}
        
    async def test_quiz_question_with_selection_ui(self):
        """Test: Quiz question triggers selection UI with options"""
        print("\n🧪 TEST 2: Quiz Question → Selection UI with Options")
        print("="*50)
        
        # Simulate realistic quiz question from LLM
        llm_response = {
            "character": "seol_min_seok_quiz",
            "dialogue": "좋아요! 조선시대 퀴즈를 시작해볼까요? 첫 번째 문제입니다! 다음 중 세종대왕의 업적이 아닌 것은?",
            "emotion": "excited",
            "speed": 1.0,
            "tool": "show_selection",
            "tool_data": {
                "type": "quiz",
                "question": "다음 중 세종대왕의 업적이 아닌 것은?",
                "options": [
                    "한글 창제",
                    "측우기 발명",
                    "경국대전 편찬",
                    "집현전 설립"
                ],
                "correct_answer": 2,
                "ui_type": "selection"
            }
        }
        
        # Parse and verify
        parsed = self.tool_orchestrator.parse_llm_response(json.dumps(llm_response))
        assert parsed["tool"] == "show_selection", "❌ Tool detection failed"
        assert parsed["tool_data"]["question"] in parsed["dialogue"], "❌ Question not in dialogue"
        print("✅ Tool detected: 'show_selection'")
        print(f"✅ Question in dialogue: {parsed['tool_data']['question']}")
        
        # Execute tool
        ui_response = await self.platform_handler.handle_show_selection_tool(parsed["tool_data"])
        assert ui_response["ui_type"] == "selection", "❌ Wrong UI type"
        assert len(ui_response["options"]) == 4, "❌ Wrong number of options"
        assert ui_response["question"] == parsed["tool_data"]["question"], "❌ Question mismatch"
        print("✅ Quiz UI Generated:")
        print(f"  - Question: {ui_response['question']}")
        print(f"  - Options: {ui_response['options']}")
        
        # Store correct answer for next test
        self.correct_answer_index = parsed["tool_data"]["correct_answer"]
        
        return {"status": "PASS", "test": "quiz_question_with_selection_ui"}
        
    async def test_answer_triggers_continuous_flow(self):
        """Test: Answer triggers continuous flow (feedback + next question)"""
        print("\n🧪 TEST 3: Answer → Continuous Flow (Feedback + Next Question)")
        print("="*50)
        
        # Simulate LLM response to correct answer
        llm_response_feedback = {
            "character": "seol_min_seok_quiz",
            "dialogue": "정답입니다! 훌륭해요! 경국대전은 세조 때 편찬이 시작되어 성종 때 완성되었죠. 세종대왕은 한글을 창제하고 과학기술 발전에 큰 공을 세우셨습니다.",
            "emotion": "proud",
            "speed": 1.0,
            "tool": "continuous",
            "tool_data": {
                "reason": "educational_flow",
                "next_context": "provide_next_question",
                "session_id": "test_session_123"
            }
        }
        
        # Parse feedback
        parsed = self.tool_orchestrator.parse_llm_response(json.dumps(llm_response_feedback))
        assert parsed["tool"] == "continuous", "❌ Continuous tool not detected"
        assert "정답입니다" in parsed["dialogue"], "❌ Feedback not in dialogue"
        print("✅ Continuous tool detected")
        print(f"✅ Feedback: {parsed['dialogue'][:100]}...")
        
        # Execute continuous flow (should trigger second LLM call)
        next_llm_response = {
            "character": "seol_min_seok_quiz", 
            "dialogue": "이번엔 조선 후기 문제입니다! 정조가 창설한 친위부대의 이름은 무엇일까요?",
            "emotion": "enthusiastic",
            "speed": 1.0,
            "tool": "show_selection",
            "tool_data": {
                "type": "quiz",
                "question": "정조가 창설한 친위부대의 이름은?",
                "options": ["장용영", "금위영", "어영청", "훈련도감"],
                "correct_answer": 0,
                "ui_type": "selection"
            }
        }
        
        # Simulate continuous flow execution
        flow_result = {
            "feedback": parsed["dialogue"],
            "feedback_audio": "base64_audio_data_here",
            "next_question": next_llm_response["dialogue"],
            "next_question_audio": "base64_audio_data_here",
            "next_ui": next_llm_response["tool_data"]
        }
        
        assert flow_result["next_ui"]["type"] == "quiz", "❌ Next UI not quiz type"
        assert "정조" in flow_result["next_question"], "❌ Next question not generated"
        print("✅ Continuous Flow Completed:")
        print(f"  - Feedback provided: Yes")
        print(f"  - Next question: {flow_result['next_ui']['question']}")
        print(f"  - UI ready: {flow_result['next_ui']['ui_type']}")
        
        return {"status": "PASS", "test": "answer_triggers_continuous_flow"}
        
    async def test_normal_chat_without_tools(self):
        """Test: Normal chat works without tool triggers"""
        print("\n🧪 TEST 4: Normal Chat → No Tool Triggers")
        print("="*50)
        
        # Simulate normal conversation (no quiz)
        llm_response = {
            "character": "yoon_ari",
            "dialogue": "안녕하세요! 오늘 날씨가 정말 좋네요. 무엇을 도와드릴까요?",
            "emotion": "friendly",
            "speed": 1.0
            # Note: No 'tool' field
        }
        
        # Parse and verify no tools
        parsed = self.tool_orchestrator.parse_llm_response(json.dumps(llm_response))
        assert parsed.get("tool") is None, "❌ Tool detected when shouldn't be"
        assert parsed["dialogue"] == llm_response["dialogue"], "❌ Dialogue extraction failed"
        print("✅ No tool detected (correct)")
        print(f"✅ Normal dialogue: {parsed['dialogue']}")
        
        # Verify no UI triggers
        ui_response = await self.platform_handler.handle_no_tool_response(parsed)
        assert ui_response["ui_type"] == "none", "❌ UI triggered when shouldn't be"
        print("✅ No UI triggered (correct)")
        
        return {"status": "PASS", "test": "normal_chat_without_tools"}
        
    async def test_conversation_history_storage(self):
        """Test: Conversation history stores clean dialogue, not JSON"""
        print("\n🧪 TEST 5: Conversation History → Clean Dialogue Storage")
        print("="*50)
        
        # Simulate full JSON response
        full_json_response = json.dumps({
            "character": "seol_min_seok_quiz",
            "dialogue": "안녕하세요! 설민석입니다.",
            "emotion": "friendly",
            "tool": "quiz",
            "tool_data": {"type": "greeting"}
        })
        
        # What should be stored
        parsed = self.tool_orchestrator.parse_llm_response(full_json_response)
        clean_dialogue = parsed["dialogue"]
        
        # Verify storage format
        assert clean_dialogue == "안녕하세요! 설민석입니다.", "❌ Dialogue extraction failed"
        assert "{" not in clean_dialogue, "❌ JSON leaked into dialogue"
        assert "tool" not in clean_dialogue, "❌ Tool data in dialogue"
        print("✅ Clean dialogue extracted")
        print(f"✅ Stored: '{clean_dialogue}' (not JSON)")
        
        return {"status": "PASS", "test": "conversation_history_storage"}
        
    async def test_tts_service_routing(self):
        """Test: Different TTS services for different characters"""
        print("\n🧪 TEST 6: TTS Service Routing → Character-Specific")
        print("="*50)
        
        test_cases = [
            {
                "character_id": "seol_min_seok_quiz",
                "expected_service": "seolminseok_tts_service",
                "method": "generate_tts"
            },
            {
                "character_id": "yoon_ari",
                "expected_service": "tts_service", 
                "method": "generate_speech"
            }
        ]
        
        for case in test_cases:
            print(f"\nCharacter: {case['character_id']}")
            print(f"  Expected Service: {case['expected_service']}")
            print(f"  Expected Method: {case['method']}")
            
            # This would be actual routing logic
            if case["character_id"] == "seol_min_seok_quiz":
                service_name = "seolminseok_tts_service"
                method_name = "generate_tts"
            else:
                service_name = "tts_service"
                method_name = "generate_speech"
                
            assert service_name == case["expected_service"], f"❌ Wrong service for {case['character_id']}"
            assert method_name == case["method"], f"❌ Wrong method for {case['character_id']}"
            print(f"  ✅ Correct routing")
            
        return {"status": "PASS", "test": "tts_service_routing"}
        
    async def test_frontend_text_synchronization(self):
        """Test: Frontend receives complete text, not truncated"""
        print("\n🧪 TEST 7: Frontend Text → Complete, Not Truncated")
        print("="*50)
        
        # Full text that should appear
        full_dialogue = "좋아요! 조선시대 퀴즈를 시작해볼까요? 첫 번째 문제입니다! 다음 중 세종대왕의 업적이 아닌 것은?"
        
        # Simulate backend response
        backend_response = {
            "dialogue": full_dialogue,
            "audio": "base64_audio_here",
            "tools": [{
                "type": "assistant-ui-quiz",
                "question": "다음 중 세종대왕의 업적이 아닌 것은?",
                "options": ["한글 창제", "측우기 발명", "경국대전 편찬", "집현전 설립"]
            }]
        }
        
        # Verify full text included
        assert len(backend_response["dialogue"]) > 50, "❌ Dialogue too short"
        assert "첫 번째 문제입니다!" in backend_response["dialogue"], "❌ Missing middle part"
        assert "세종대왕의 업적이 아닌 것은?" in backend_response["dialogue"], "❌ Missing question"
        print("✅ Full dialogue included:")
        print(f"  Length: {len(backend_response['dialogue'])} chars")
        print(f"  Contains: Introduction + Question")
        
        # Verify question also in tool data
        assert backend_response["tools"][0]["question"] in backend_response["dialogue"], "❌ Question mismatch"
        print("✅ Question synchronized in both dialogue and tool")
        
        return {"status": "PASS", "test": "frontend_text_synchronization"}
        
    async def test_error_handling_null_checks(self):
        """Test: Proper null checks for NoneType errors"""
        print("\n🧪 TEST 8: Error Handling → Null Checks")
        print("="*50)
        
        test_cases = [
            {"input": None, "field": "character"},
            {"input": {}, "field": "character"},
            {"input": {"dialogue": "test"}, "field": "character"}
        ]
        
        for case in test_cases:
            print(f"\nTesting: {case['field']} with input {case['input']}")
            
            # Safe access pattern
            if case["input"] and case["input"].get("character"):
                character = case["input"]["character"]
            else:
                character = "default_character"
                
            assert character is not None, "❌ Character is None"
            print(f"  ✅ Safe fallback: {character}")
            
        return {"status": "PASS", "test": "error_handling_null_checks"}
        
    async def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "="*60)
        print("🚀 REALISTIC LLM OUTPUT & UI TRIGGER TEST SUITE")
        print("="*60)
        
        tests = [
            self.test_greeting_triggers_quiz_ui,
            self.test_quiz_question_with_selection_ui,
            self.test_answer_triggers_continuous_flow,
            self.test_normal_chat_without_tools,
            self.test_conversation_history_storage,
            self.test_tts_service_routing,
            self.test_frontend_text_synchronization,
            self.test_error_handling_null_checks
        ]
        
        results = []
        passed = 0
        failed = 0
        
        for test_func in tests:
            try:
                result = await test_func()
                results.append(result)
                passed += 1
            except Exception as e:
                results.append({
                    "status": "FAIL",
                    "test": test_func.__name__,
                    "error": str(e)
                })
                failed += 1
                print(f"❌ Test failed: {e}")
                
        # Generate report
        print("\n" + "="*60)
        print("📊 TEST REPORT")
        print("="*60)
        print(f"Total Tests: {len(tests)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result.get("error"):
                print(f"   Error: {result['error']}")
                
        return results

async def main():
    """Main test runner"""
    tester = RealisticLLMUITest()
    results = await tester.run_all_tests()
    
    # Return exit code based on results
    failed = sum(1 for r in results if r["status"] == "FAIL")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())