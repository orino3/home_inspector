#!/usr/bin/env python3
"""
Comprehensive API Access Diagnostic
Tests what models and features are available to your API key
"""

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print("="*80)
print("OPENAI API ACCESS DIAGNOSTIC")
print("="*80)
print(f"\nAPI Key: {api_key[:15]}...{api_key[-10:]}")
print(f"Length: {len(api_key)} characters")
print(f"Format: {'✅ Valid' if api_key.startswith('sk-') else '❌ Invalid'}")

from openai import OpenAI
client = OpenAI(api_key=api_key)

# Test 1: List available models
print("\n" + "-"*80)
print("TEST 1: List Available Models")
print("-"*80)
try:
    models_response = client.models.list()
    models = [m.id for m in models_response]

    print(f"✅ Success! Found {len(models)} models")

    # Check for key models we need
    key_models = {
        'gpt-4o': 'GPT-4o (for reasoning/correlation)',
        'gpt-4o-mini': 'GPT-4o Mini (cheaper alternative)',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo (basic chat)',
        'whisper-1': 'Whisper (audio transcription)',
    }

    print("\nModels we need for the project:")
    for model_id, description in key_models.items():
        if model_id in models:
            print(f"   ✅ {model_id} - {description}")
        else:
            print(f"   ❌ {model_id} - {description} (NOT AVAILABLE)")

    print(f"\nAll available models:")
    for model in sorted(models)[:20]:  # Show first 20
        print(f"   - {model}")
    if len(models) > 20:
        print(f"   ... and {len(models) - 20} more")

except Exception as e:
    print(f"❌ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test 2: Simple text completion with cheapest model
print("\n" + "-"*80)
print("TEST 2: Simple Text Completion (gpt-3.5-turbo)")
print("-"*80)
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Reply with just: OK"}],
        max_tokens=5
    )

    result = response.choices[0].message.content
    print(f"✅ Success!")
    print(f"   Response: {result}")
    print(f"   Tokens: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test 3: GPT-4o text completion
print("\n" + "-"*80)
print("TEST 3: GPT-4o Text Completion")
print("-"*80)
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Reply with just: OK"}],
        max_tokens=5
    )

    result = response.choices[0].message.content
    print(f"✅ Success!")
    print(f"   Response: {result}")
    print(f"   Tokens: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    if "gpt-4o" in str(e).lower() or "model" in str(e).lower():
        print(f"   Note: Your account may not have access to GPT-4o")
        print(f"   We can use gpt-4o-mini or gpt-3.5-turbo instead")

# Test 4: GPT-4o Vision (this is what we really need)
print("\n" + "-"*80)
print("TEST 4: GPT-4o Vision API (CRITICAL FOR OUR PROJECT)")
print("-"*80)
try:
    # Create a tiny test image in base64
    import base64

    # Use our synthetic photo
    with open("sample_data/photos/photo1_ceiling_stain.jpg", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you see? Reply in 5 words or less."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
            ]
        }],
        max_tokens=20
    )

    result = response.choices[0].message.content
    print(f"✅ Success! Vision API works!")
    print(f"   Response: {result}")
    print(f"   Tokens: {response.usage.total_tokens}")
    print(f"\n   🎉 THIS IS THE KEY API WE NEED - IT WORKS!")

except Exception as e:
    print(f"❌ Failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"\n   ⚠️  This is critical - we need Vision API for photo analysis")

# Test 5: Check account/organization info
print("\n" + "-"*80)
print("TEST 5: Account Information")
print("-"*80)
try:
    # Try to get organization info indirectly
    response = client.models.retrieve("gpt-3.5-turbo")
    print(f"✅ Can access model info")
    print(f"   Model ID: {response.id}")
    print(f"   Owned by: {response.owned_by}")

except Exception as e:
    print(f"❌ Failed: {e}")

print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)

print("""
For our Home Inspection AI project, we need:

1. ✅ GPT-4o or GPT-4o-mini (text reasoning)
2. ✅ GPT-4o Vision (photo analysis) - MOST CRITICAL
3. ✅ Whisper (audio transcription) - optional, can skip in testing

If any of these failed above:
- Check if you're logged into the correct OpenAI account
- Verify the API key is from the account with the balance
- Some keys may be restricted to specific models
- Try regenerating the API key at: https://platform.openai.com/api-keys

If billing/access issues persist:
- Check organization settings: https://platform.openai.com/settings/organization/general
- Verify API key permissions: https://platform.openai.com/api-keys
- Check usage limits: https://platform.openai.com/settings/organization/limits
""")

print("="*80)
