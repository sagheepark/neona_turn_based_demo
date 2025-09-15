"""
Optimized Prompt Builder Service
Implements 3-tier prompt structure for improved token efficiency and LLM attention:
1. STABLE (front): Character identity + Instructions + Cached knowledge
2. DYNAMIC (middle): Conversation history  
3. CURRENT (last): User input for optimal attention
"""

from typing import List, Dict


class OptimizedPromptBuilder:
    """
    3-Tier prompt structure builder:
    1. STABLE (front): Character identity + Instructions + Cached knowledge
    2. DYNAMIC (middle): Conversation history  
    3. CURRENT (last): User input for optimal attention
    """
    
    def build_llm_prompt(self, character_prompt: str, cached_knowledge: List[Dict], 
                        conversation_history: List[Dict], current_user_input: str, character_id: str = None) -> str:
        """
        Build optimized prompt structure:
        1. STABLE ELEMENTS (front) - character, instructions, knowledge
        2. DYNAMIC HISTORY (middle) - conversation context  
        3. CURRENT INPUT (last) - immediate user message
        """
        
        # 1. STABLE FRONT SECTION (cached, rarely changes)
        stable_section = self.build_stable_section(character_prompt, cached_knowledge, character_id)
        
        # 2. DYNAMIC HISTORY SECTION (changes each message)
        history_section = self.build_history_section(conversation_history)
        
        # 3. CURRENT INPUT SECTION (always last)
        current_section = self.build_current_input_section(current_user_input)
        
        return f"{stable_section}\n\n{history_section}\n\n{current_section}"
    
    def build_stable_section(self, character_prompt: str, cached_knowledge: List[Dict], character_id: str = None) -> str:
        """Build stable prompt elements that don't change often"""
        
        # Character identity and instructions (most stable)
        character_section = f"""CHARACTER IDENTITY:
{character_prompt}

OUTPUT FORMAT:
- Respond only with valid JSON: {{"character": "name", "dialogue": "text", "emotion": "emotion", "speed": number}}
- Emotion must be: normal, happy, sad, angry, surprised, fearful, disgusted, excited
- Speed must be between 0.8 and 1.2
- Keep responses 2-3 sentences maximum
- Use natural Korean conversation style"""

        # Knowledge base (semi-stable, changes per topic cluster)
        knowledge_section = ""
        if cached_knowledge:
            knowledge_items = []
            for item in cached_knowledge:
                knowledge_items.append(
                    f"- {item.get('title', 'Knowledge')}: {item.get('content', '')}"
                )
            
            knowledge_section = f"""

AVAILABLE KNOWLEDGE:
{chr(10).join(knowledge_items)}

KNOWLEDGE USAGE:
- Reference relevant knowledge naturally in your responses
- Don't mention "according to my knowledge base" - speak as the character
- Combine multiple knowledge items when relevant
- If no relevant knowledge, rely on character personality"""

        # Add character-specific instructions
        character_specific_section = ""
        if character_id == "seol_min_seok_quiz":
            character_specific_section = """

🎯 QUIZ CHARACTER SPECIAL INSTRUCTIONS:
When the user requests a quiz or asks you to create questions:
- ALWAYS format quiz questions in this EXACT structure: "Question? A) Option1 B) Option2 C) Option3 D) Option4"
- Include exactly 4 options labeled with A), B), C), D)
- Make sure there is a clear question ending with "?"
- Choose historically accurate correct answers based on your knowledge
- Focus on Korean history topics (조선시대, 고려시대, etc.)
- Examples:
  * "다음 중 세종대왕의 업적은? A) 한글 창제 B) 불교 장려 C) 몽골 침입 D) 일제강점"
  * "고려를 건국한 인물은? A) 왕건 B) 이성계 C) 박혁거세 D) 온조"

CRITICAL: This A/B/C/D format is required for the quiz UI to work properly!"""
        elif character_id == "dr_genie_science_quiz":
            character_specific_section = """

🎯 SCIENCE QUIZ CHARACTER SPECIAL INSTRUCTIONS:
When the user requests a quiz or asks you to create questions:
- ALWAYS format quiz questions in this EXACT structure: "Question? A) Option1 B) Option2 C) Option3 D) Option4"
- Include exactly 4 options labeled with A), B), C), D)
- Make sure there is a clear question ending with "?"
- Choose scientifically accurate correct answers based on your knowledge
- Focus on science topics (물리학, 화학, 생물학, etc.)
- Examples:
  * "다음 중 힘의 단위는? A) 뉴턴 B) 파스칼 C) 줄 D) 와트"
  * "물의 화학식은? A) H2O B) CO2 C) NaCl D) CH4"

CRITICAL: This A/B/C/D format is required for the quiz UI to work properly!"""

        return f"{character_section}{knowledge_section}{character_specific_section}"
    
    def build_history_section(self, conversation_history: List[Dict]) -> str:
        """Build conversation history section"""
        
        if not conversation_history:
            return "CONVERSATION HISTORY:\n(This is the start of our conversation)"
        
        # Format recent history (last 10 messages for context)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        
        formatted_history = []
        for msg in recent_history:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            formatted_history.append(f"{role}: {content}")
        
        history_text = "\n".join(formatted_history)
        
        return f"""CONVERSATION HISTORY:
{history_text}"""
    
    def build_current_input_section(self, user_input: str) -> str:
        """Build current user input section - always last for optimal attention"""
        
        return f"""CURRENT USER MESSAGE:
{user_input}

RESPOND NOW AS THE CHARACTER:"""