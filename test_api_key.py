#!/usr/bin/env python3
"""
Test OpenAI API key to diagnose access issues
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {api_key[:20]}...{api_key[-10:]} (length: {len(api_key)})")

client = OpenAI(api_key=api_key)

# Test 1: List models
print("\n" + "="*80)
print("TEST 1: Listing available models")
print("="*80)
try:
    models = client.models.list()
    print("✅ Success! Available models:")
    for model in list(models)[:5]:
        print(f"   - {model.id}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    print(f"   Details: {str(e)}")

# Test 2: Simple chat completion
print("\n" + "="*80)
print("TEST 2: Simple chat completion")
print("="*80)
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in 3 words"}],
        max_tokens=10
    )
    print(f"✅ Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    print(f"   Details: {str(e)}")

# Test 3: Vision API (with simple image)
print("\n" + "="*80)
print("TEST 3: Vision API with base64 image")
print("="*80)
try:
    import base64

    # Read one of our synthetic photos
    with open("sample_data/photos/photo1_ceiling_stain.jpg", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image in one sentence."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }],
        max_tokens=50
    )
    print(f"✅ Success! Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Type: {type(e).__name__}")
    print(f"   Details: {str(e)}")
    if hasattr(e, 'response'):
        print(f"   Response: {e.response}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
