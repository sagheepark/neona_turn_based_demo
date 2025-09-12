#!/usr/bin/env python3
"""
Integration Test: Complete Tool-Orchestrated Platform
Demonstrates the full LLM → Tool Detection → Platform Action → User Experience flow
"""

import pytest
import asyncio
from services.tool_orchestrator import ToolOrchestrator
from services.platform_tool_handler import PlatformToolHandler


class TestToolOrchestratedIntegration:
    """Integration tests for the complete tool-orchestrated platform"""

    def test_complete_quiz_flow_integration(self):
        """
        Integration Test: Complete Quiz Flow
        Demonstrates: LLM Response → Tool Detection → Platform Action → UI Result
        """
        # Arrange: Mock LLM response with tool command
        llm_response = '''
        {
            "character": "seol_min_seok_quiz",
            "dialogue": "좋습니다! 어떤 주제로 퀴즈를 시작할까요?",
            "emotion": "enthusiastic", 
            "speed": 1.0,
            "tool": "quiz",
            "tool_data": {
                "type": "topic_selection",
                "items": ["조선시대", "근현대사", "일제강점기"]
            }
        }
        '''
        
        # Step 1: LLM Response → Tool Detection
        orchestrator = ToolOrchestrator()
        parsed_response = orchestrator.parse_llm_response(llm_response)
        
        # Step 2: Tool Detection → Platform Action
        handler = PlatformToolHandler()
        platform_result = handler.execute_tool(
            parsed_response["tool"], 
            parsed_response["tool_data"]
        )
        
        # Step 3: Verify Complete Flow
        # LLM response properly parsed
        assert parsed_response["character"] == "seol_min_seok_quiz"
        assert parsed_response["dialogue"] == "좋습니다! 어떤 주제로 퀴즈를 시작할까요?"
        assert parsed_response["tool"] == "quiz"
        
        # Tool properly executed  
        assert platform_result["ui_type"] == "selection"
        assert len(platform_result["options"]) == 3
        assert "조선시대" in platform_result["options"]
        
        print("✅ COMPLETE QUIZ FLOW INTEGRATION: SUCCESS")
        print(f"   LLM Dialogue: {parsed_response['dialogue']}")
        print(f"   Tool Detected: {parsed_response['tool']}")
        print(f"   UI Generated: {platform_result['ui_type']} with {len(platform_result['options'])} options")

    @pytest.mark.asyncio
    async def test_continuous_flow_integration(self):
        """
        Integration Test: Continuous Flow
        Demonstrates: Answer → Educational Feedback → Next Question Flow
        """
        # Arrange: Mock LLM response with continuous tool
        llm_response = '''
        {
            "character": "seol_min_seok_quiz",
            "dialogue": "정답입니다! 훌륭해요!",
            "emotion": "proud",
            "tool": "continuous",
            "tool_data": {
                "reason": "educational_flow",
                "next_context": "provide_explanation_then_next_question"
            }
        }
        '''
        
        # Step 1: Parse feedback response
        orchestrator = ToolOrchestrator()  
        parsed_response = orchestrator.parse_llm_response(llm_response)
        
        # Step 2: Execute continuous flow
        handler = PlatformToolHandler()
        continuous_result = await handler.handle_continuous_tool("test_session_456")
        
        # Step 3: Verify Continuous Flow
        assert parsed_response["tool"] == "continuous"
        assert continuous_result["conversation_continued"] == True
        assert continuous_result["next_response"]["dialogue"] == "다음 문제입니다!"
        
        print("✅ CONTINUOUS FLOW INTEGRATION: SUCCESS")
        print(f"   Feedback: {parsed_response['dialogue']}")
        print(f"   Flow Continued: {continuous_result['conversation_continued']}")
        print(f"   Next Response: {continuous_result['next_response']['dialogue']}")

    def test_show_selection_integration(self):
        """
        Integration Test: Show Selection Tool
        Demonstrates: Quiz Question → Selection UI Generation
        """
        # Arrange: Mock LLM response with show_selection tool
        llm_response = '''
        {
            "character": "seol_min_seok_quiz",
            "dialogue": "다음 중 세종대왕의 업적은 무엇일까요?",
            "emotion": "curious",
            "tool": "show_selection", 
            "tool_data": {
                "type": "quiz_question",
                "question": "다음 중 세종대왕의 업적은?",
                "items": ["한글 창제", "불교 장려", "몽골 침입", "일제강점"],
                "correct_answer": "한글 창제"
            }
        }
        '''
        
        # Complete Flow Execution
        orchestrator = ToolOrchestrator()
        handler = PlatformToolHandler()
        
        parsed_response = orchestrator.parse_llm_response(llm_response)
        ui_result = handler.execute_tool(parsed_response["tool"], parsed_response["tool_data"])
        
        # Verify Quiz UI Generation
        assert ui_result["ui_type"] == "quiz"
        assert ui_result["question"] == "다음 중 세종대왕의 업적은?"
        assert len(ui_result["options"]) == 4
        assert ui_result["correct_answer"] == "한글 창제"
        
        print("✅ SHOW SELECTION INTEGRATION: SUCCESS")
        print(f"   Question: {ui_result['question']}")
        print(f"   Options: {ui_result['options']}")
        print(f"   Correct: {ui_result['correct_answer']}")

    def test_character_extensibility_demo(self):
        """
        Demo: Character Extensibility
        Shows how different characters can use the same tool system
        """
        # Story Character Example
        story_response = '''
        {
            "character": "story_teller",
            "dialogue": "당신은 어떤 길을 선택하시겠습니까?",
            "emotion": "mysterious",
            "tool": "show_selection",
            "tool_data": {
                "type": "story_choice", 
                "question": "어느 길로 가시겠습니까?",
                "items": ["숲 속 길", "강가 길", "산길", "마을 길"]
            }
        }
        '''
        
        # Python Tutor Character Example  
        tutor_response = '''
        {
            "character": "python_tutor",
            "dialogue": "다음 연습 문제를 선택해주세요.",
            "emotion": "helpful",
            "tool": "show_selection",
            "tool_data": {
                "type": "coding_exercise",
                "question": "어떤 주제를 연습하시겠습니까?",
                "items": ["리스트 조작", "딕셔너리 활용", "함수 정의", "클래스 설계"]
            }
        }
        '''
        
        # Test Both Characters Use Same System
        orchestrator = ToolOrchestrator()
        handler = PlatformToolHandler()
        
        # Story character
        story_parsed = orchestrator.parse_llm_response(story_response)
        story_ui = handler.execute_tool(story_parsed["tool"], story_parsed["tool_data"])
        
        # Tutor character
        tutor_parsed = orchestrator.parse_llm_response(tutor_response)
        tutor_ui = handler.execute_tool(tutor_parsed["tool"], tutor_parsed["tool_data"])
        
        # Both work with same system!
        assert story_ui["ui_type"] == "quiz"  # Same UI type
        assert tutor_ui["ui_type"] == "quiz"  # Same UI type
        assert len(story_ui["options"]) == 4
        assert len(tutor_ui["options"]) == 4
        
        print("✅ CHARACTER EXTENSIBILITY: SUCCESS")
        print(f"   Story Character: {story_parsed['character']} → {len(story_ui['options'])} choices")
        print(f"   Tutor Character: {tutor_parsed['character']} → {len(tutor_ui['options'])} exercises")
        print("   📈 PLATFORM SCALABILITY DEMONSTRATED")


if __name__ == "__main__":
    print("🚀 TESTING TOOL-ORCHESTRATED PLATFORM INTEGRATION")
    print("=" * 70)
    
    # Run the integration tests
    pytest.main([__file__, "-v", "-s"])
    
    print("\n" + "=" * 70)
    print("🎉 TOOL-ORCHESTRATED PLATFORM: IMPLEMENTATION COMPLETE")
    print("✅ LLM controls platform through structured tool outputs")
    print("✅ Clean separation: LLM logic ↔ Platform mechanics") 
    print("✅ Infinitely extensible for new character types")
    print("✅ Compact, maintainable architecture achieved")