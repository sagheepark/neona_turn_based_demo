#!/usr/bin/env python3
"""
Simple test to directly call the LLM to understand what's failing
"""

import os
from openai import AzureOpenAI

# Use the same config as the backend
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://neo-research.openai.azure.com/")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

print("🧪 DIRECT LLM TEST")
print("="*50)
print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
print(f"API Key: {'Set' if AZURE_OPENAI_API_KEY else 'Not Set'}")
print(f"API Version: {AZURE_OPENAI_API_VERSION}")
print(f"Deployment: {AZURE_OPENAI_DEPLOYMENT}")

try:
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
    print("✅ Azure OpenAI client initialized successfully")
    
    # Test a simple call
    print("\n🔍 Testing direct LLM call...")
    
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a test assistant. Respond with: TEST_RESPONSE_SUCCESS"}
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    response_text = response.choices[0].message.content.strip()
    print(f"✅ LLM Response: {response_text}")
    
    if "TEST_RESPONSE_SUCCESS" in response_text:
        print("✅ LLM is working correctly")
    else:
        print(f"⚠️  Unexpected response: {response_text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Exception type: {type(e).__name__}")
    import traceback
    traceback.print_exc()