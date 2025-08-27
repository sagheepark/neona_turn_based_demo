"""
Test Suite for OptimizedPromptBuilder
Following TDD: Red → Green → Refactor
Testing 3-tier prompt structure for improved token efficiency and LLM attention
"""

import pytest
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.optimized_prompt_builder import OptimizedPromptBuilder


class TestOptimizedPromptBuilder:
    """Test suite for optimized prompt building system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.builder = OptimizedPromptBuilder()
        self.test_character_prompt = """You are 설민석, a Korean history teacher.
Personality: Enthusiastic, knowledgeable about Korean history
Speaking style: Engaging and educational"""
        
        self.test_knowledge = [
            {
                "title": "3·1 운동 개요",
                "content": "1919년 3월 1일에 시작된 일제강점기 최대 규모의 독립운동",
                "relevance_score": 0.9
            },
            {
                "title": "유관순 활동",
                "content": "유관순은 3·1 운동의 대표적인 학생 독립운동가",
                "relevance_score": 0.7
            }
        ]
        
        self.test_history = [
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요, 역사 여행 가이드 설민석입니다!"},
            {"role": "user", "content": "3·1 운동에 대해 알고 싶어요"}
        ]
        
    def test_builder_initialization(self):
        """Test 1: Builder should initialize correctly"""
        # Given: A new builder instance
        # When: Checking initialization
        # Then: Should have proper structure
        assert self.builder is not None
        assert hasattr(self.builder, 'build_llm_prompt')
        assert hasattr(self.builder, 'build_stable_section')
        assert hasattr(self.builder, 'build_history_section')
        assert hasattr(self.builder, 'build_current_input_section')
        
    def test_stable_section_structure(self):
        """Test 2: Stable section should have proper structure"""
        # Given: Character prompt and knowledge
        # When: Building stable section
        stable_section = self.builder.build_stable_section(
            self.test_character_prompt,
            self.test_knowledge
        )
        
        # Then: Should contain character identity and knowledge
        assert "CHARACTER IDENTITY:" in stable_section
        assert "설민석" in stable_section
        assert "OUTPUT FORMAT:" in stable_section
        assert "AVAILABLE KNOWLEDGE:" in stable_section
        assert "3·1 운동 개요" in stable_section
        assert "KNOWLEDGE USAGE:" in stable_section
        
    def test_stable_section_without_knowledge(self):
        """Test 3: Stable section should work without knowledge"""
        # Given: Character prompt but no knowledge
        # When: Building stable section without knowledge
        stable_section = self.builder.build_stable_section(
            self.test_character_prompt,
            []
        )
        
        # Then: Should contain character but no knowledge section
        assert "CHARACTER IDENTITY:" in stable_section
        assert "설민석" in stable_section
        assert "OUTPUT FORMAT:" in stable_section
        assert "AVAILABLE KNOWLEDGE:" not in stable_section
        
    def test_history_section_with_messages(self):
        """Test 4: History section should format messages properly"""
        # Given: Conversation history
        # When: Building history section
        history_section = self.builder.build_history_section(self.test_history)
        
        # Then: Should format conversations properly
        assert "CONVERSATION HISTORY:" in history_section
        assert "User: 안녕하세요" in history_section
        assert "Assistant: 안녕하세요, 역사 여행 가이드 설민석입니다!" in history_section
        assert "User: 3·1 운동에 대해 알고 싶어요" in history_section
        
    def test_history_section_empty(self):
        """Test 5: History section should handle empty history"""
        # Given: No conversation history
        # When: Building history section with empty history
        history_section = self.builder.build_history_section([])
        
        # Then: Should indicate start of conversation
        assert "CONVERSATION HISTORY:" in history_section
        assert "This is the start of our conversation" in history_section
        
    def test_history_section_truncation(self):
        """Test 6: History section should limit to last 10 messages"""
        # Given: Long conversation history (15 messages)
        long_history = []
        for i in range(15):
            long_history.append({"role": "user", "content": f"Message {i}"})
            
        # When: Building history section
        history_section = self.builder.build_history_section(long_history)
        
        # Then: Should only include last 10 messages
        assert "Message 5" in history_section  # Message 5 should be included (from index 5-14)
        assert "Message 4" not in history_section  # Message 4 should be truncated
        assert "Message 14" in history_section  # Latest message should be included
        
    def test_current_input_section(self):
        """Test 7: Current input section should format user message"""
        # Given: Current user message
        user_input = "언제 3·1 운동이 일어났나요?"
        
        # When: Building current input section
        current_section = self.builder.build_current_input_section(user_input)
        
        # Then: Should format properly with call to action
        assert "CURRENT USER MESSAGE:" in current_section
        assert "언제 3·1 운동이 일어났나요?" in current_section
        assert "RESPOND NOW AS THE CHARACTER:" in current_section
        
    def test_complete_prompt_structure(self):
        """Test 8: Complete prompt should follow 3-tier structure"""
        # Given: All prompt components
        current_input = "3·1 운동은 언제 일어났나요?"
        
        # When: Building complete LLM prompt
        complete_prompt = self.builder.build_llm_prompt(
            self.test_character_prompt,
            self.test_knowledge,
            self.test_history,
            current_input
        )
        
        # Then: Should follow proper order
        lines = complete_prompt.split('\n')
        
        # Find section positions
        character_pos = next(i for i, line in enumerate(lines) if "CHARACTER IDENTITY:" in line)
        history_pos = next(i for i, line in enumerate(lines) if "CONVERSATION HISTORY:" in line)
        current_pos = next(i for i, line in enumerate(lines) if "CURRENT USER MESSAGE:" in line)
        
        # Verify order: Stable → History → Current
        assert character_pos < history_pos < current_pos
        
    def test_json_format_specification(self):
        """Test 9: Stable section should specify correct JSON format"""
        # Given: Any character prompt
        # When: Building stable section
        stable_section = self.builder.build_stable_section(self.test_character_prompt, [])
        
        # Then: Should specify proper JSON format
        assert '{"character": "name"' in stable_section
        assert '"dialogue": "text"' in stable_section
        assert '"emotion": "emotion"' in stable_section
        assert '"speed": number' in stable_section
        
    def test_emotion_constraints(self):
        """Test 10: Should specify valid emotions"""
        # Given: Character prompt
        # When: Building stable section
        stable_section = self.builder.build_stable_section(self.test_character_prompt, [])
        
        # Then: Should list valid emotions
        assert "normal, happy, sad, angry, surprised, fearful, disgusted, excited" in stable_section
        
    def test_knowledge_integration_instructions(self):
        """Test 11: Should provide knowledge usage instructions"""
        # Given: Character prompt with knowledge
        # When: Building stable section with knowledge
        stable_section = self.builder.build_stable_section(
            self.test_character_prompt,
            self.test_knowledge
        )
        
        # Then: Should provide usage instructions
        assert "Reference relevant knowledge naturally" in stable_section
        assert "don't mention \"according to my knowledge base\"" in stable_section.lower()
        assert "Combine multiple knowledge items when relevant" in stable_section
        
    def test_token_efficiency(self):
        """Test 12: Complete prompt should be reasonably sized"""
        # Given: Typical prompt components
        current_input = "3·1 운동에 대해 자세히 알려주세요"
        
        # When: Building complete prompt
        complete_prompt = self.builder.build_llm_prompt(
            self.test_character_prompt,
            self.test_knowledge,
            self.test_history,
            current_input
        )
        
        # Then: Should be within reasonable token limits
        # Rough estimate: ~3-4 chars per token in Korean
        estimated_tokens = len(complete_prompt) / 3.5
        assert estimated_tokens < 1500  # Should be under 1500 tokens
        assert estimated_tokens > 100   # But not empty
        assert len(complete_prompt) > 0  # Basic sanity check
        
    def test_section_separation(self):
        """Test 13: Sections should be properly separated"""
        # Given: All components
        current_input = "역사에 대해 궁금해요"
        
        # When: Building complete prompt
        complete_prompt = self.builder.build_llm_prompt(
            self.test_character_prompt,
            self.test_knowledge,
            self.test_history,
            current_input
        )
        
        # Then: Sections should be separated by double newlines
        sections = complete_prompt.split('\n\n')
        assert len(sections) >= 3  # At least 3 major sections
        
    def test_korean_content_handling(self):
        """Test 14: Should properly handle Korean content"""
        # Given: Korean character prompt and messages
        korean_prompt = "당신은 한국사 교사 설민석입니다. 한국어로 대답하세요."
        korean_history = [
            {"role": "user", "content": "한국사에 대해 질문이 있어요"},
            {"role": "assistant", "content": "네, 무엇이든 물어보세요!"}
        ]
        korean_input = "조선시대는 언제부터 언제까지인가요?"
        
        # When: Building prompt with Korean content
        prompt = self.builder.build_llm_prompt(
            korean_prompt,
            [],
            korean_history,
            korean_input
        )
        
        # Then: Should preserve Korean characters properly
        assert "설민석" in prompt
        assert "한국사에 대해 질문이 있어요" in prompt
        assert "조선시대는 언제부터 언제까지인가요?" in prompt


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])