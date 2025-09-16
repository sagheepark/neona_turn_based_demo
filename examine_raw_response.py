#!/usr/bin/env python3
"""
Examine the exact raw response to see what the LLM is actually generating
"""

import os
import json
import asyncio
from openai import AsyncOpenAI

async def examine_raw_response():
    """Examine the exact raw response bytes"""
    
    # Simple prompt focusing just on the format issue
    simple_prompt = """Generate a JSON response with multiple sentences in the dialogue field.

CRITICAL: Use literal \\n characters (backslash + n) inside the JSON string values for sentence separation.
Do NOT use actual newline characters inside JSON strings.

Example of correct format:
{"dialogue": "First sentence.\\nSecond sentence."}

Generate a response about Korean history with 2-3 sentences in the dialogue field."""

    client = AsyncOpenAI(
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )
    
    print("🔬 EXAMINING RAW RESPONSE BYTES")
    print("=" * 60)
    print("Simple prompt:")
    print(simple_prompt)
    print("=" * 60)
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini"),
            messages=[
                {"role": "user", "content": simple_prompt}
            ],
            max_tokens=200,
            temperature=0.3,
        )
        
        raw_response = response.choices[0].message.content.strip()
        
        print("📝 RAW RESPONSE (as string):")
        print(repr(raw_response))  # This shows escape sequences
        print()
        
        print("📝 RAW RESPONSE (as displayed):")
        print(raw_response)
        print()
        
        print("🔍 BYTE ANALYSIS:")
        for i, char in enumerate(raw_response):
            if char in ['\n', '\\']:
                print(f"Position {i}: {repr(char)} (ord: {ord(char)})")
        
        print()
        print("🧪 PARSING TEST:")
        try:
            parsed = json.loads(raw_response)
            dialogue = parsed.get('dialogue', '')
            print(f"Parsed dialogue: {repr(dialogue)}")
            has_literal_newline = '\\n' in dialogue
            has_actual_newline = chr(10) in dialogue
            print(f"Contains literal \\n: {has_literal_newline}")
            print(f"Contains actual newline: {has_actual_newline}")
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(examine_raw_response())
