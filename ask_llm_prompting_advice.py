#!/usr/bin/env python3
"""
Ask the LLM how to prompt for literal \n characters instead of actual newlines
"""

import os
import json
import asyncio
from openai import AsyncOpenAI

async def ask_llm_for_prompting_advice():
    """Ask the LLM how to prompt for literal \n characters"""
    
    # Initialize OpenAI client
    client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    # Meta-prompt asking for prompting advice
    meta_prompt = """You are an expert at prompt engineering for LLMs. I need your help with a specific prompting challenge.

PROBLEM:
I want an LLM to generate JSON responses where multi-sentence text fields contain literal \\n characters (the two-character sequence backslash-n) instead of actual newlines.

CURRENT SITUATION:
- When I ask for "use \\n as delimiter between sentences"
- The LLM generates actual newlines in JSON strings instead of literal \\n characters
- Example of what I'm getting:
```json
{
    "text": "First sentence.
Second sentence."
}
```

DESIRED OUTPUT:
- I want literal \\n characters in the JSON string values:
```json
{
    "text": "First sentence.\\nSecond sentence."
}
```

QUESTION:
What specific prompting techniques, instructions, or examples should I use to make the LLM generate literal \\n characters instead of actual newlines in JSON string values?

Please provide:
1. Specific prompt instructions that work
2. Example formats to include in the prompt
3. Any other techniques that help with this specific case

Be very specific and practical in your advice."""

    print("🤖 ASKING LLM FOR PROMPTING ADVICE")
    print("=" * 60)
    print("Meta-prompt:")
    print(meta_prompt)
    print("=" * 60)
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            messages=[
                {"role": "user", "content": meta_prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        
        advice = response.choices[0].message.content.strip()
        
        print("🎯 LLM'S PROMPTING ADVICE:")
        print("=" * 60)
        print(advice)
        print("=" * 60)
        
        return advice
        
    except Exception as e:
        print(f"❌ Error asking LLM: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(ask_llm_for_prompting_advice())
