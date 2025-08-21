import json
import random

class LLMService:
    def __init__(self):
        # For demo purposes, we'll use mock responses
        pass
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a mock response for demo purposes"""
        # Mock responses for demo
        responses = [
            "안녕하세요! 만나서 반가워요.",
            "오늘은 어떤 것을 배우고 싶으신가요?", 
            "정말 흥미로운 질문이네요!",
            "함께 차근차근 풀어보죠.",
            "좋은 시도였어요. 다시 한 번 해볼까요?"
        ]
        
        emotions = ["neutral", "happy", "excited", "thoughtful"]
        
        return json.dumps({
            "character": "Demo Character",
            "dialogue": random.choice(responses),
            "emotion": random.choice(emotions),
            "speed": round(random.uniform(0.9, 1.1), 1)
        })