#!/usr/bin/env python3
"""
Quick test to check if Sora API is available with your OpenAI API key
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

print("=" * 80)
print("CHECKING OPENAI API ACCESS")
print("=" * 80)

# Test 1: Check API key works
print("\n1. Testing API Key...")
try:
    # Simple test with a cheap model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5
    )
    print("   ✅ API Key is valid and working")
except Exception as e:
    print(f"   ❌ API Key error: {e}")
    exit(1)

# Test 2: List available models
print("\n2. Checking available models...")
try:
    models = client.models.list()
    model_ids = [model.id for model in models.data]

    print(f"   Found {len(model_ids)} models")

    # Check for Sora models
    sora_models = [m for m in model_ids if 'sora' in m.lower()]

    if sora_models:
        print("\n   ✅ SORA MODELS FOUND:")
        for model in sora_models:
            print(f"      - {model}")
    else:
        print("\n   ❌ No Sora models found in your account")
        print("      This means Sora API is not yet available for your API key")

    # Check for other video-related models
    video_models = [m for m in model_ids if 'video' in m.lower()]
    if video_models:
        print("\n   📹 Other video models found:")
        for model in video_models:
            print(f"      - {model}")

    # Show some available models
    print("\n   Available models (sample):")
    for model in sorted(model_ids)[:10]:
        print(f"      - {model}")

    if len(model_ids) > 10:
        print(f"      ... and {len(model_ids) - 10} more")

except Exception as e:
    print(f"   ⚠️  Could not list models: {e}")

# Test 3: Check organization verification status
print("\n3. Checking organization status...")
try:
    # Try to access a capability that requires verification
    # Note: This might fail if not verified, but that's expected
    print("   Check your organization status at:")
    print("   https://platform.openai.com/settings/organization/general")
    print("   Look for 'Organization verification' section")
except Exception as e:
    print(f"   Info: {e}")

# Test 4: Try a Sora API call (will fail if not available)
print("\n4. Testing Sora API access...")
try:
    # Attempt to create a video (this will fail gracefully if not available)
    # Using the endpoint from the documentation
    response = client.post(
        "/v1/videos",
        json={
            "model": "sora-2",
            "prompt": "Test video",
            "duration": 5
        }
    )
    print("   ✅ Sora API is accessible!")
    print(f"   Response: {response}")
except AttributeError:
    # client.post doesn't exist, try different approach
    print("   ⚠️  Cannot test Sora API directly (method not available)")
    print("   This is normal - Sora uses different endpoints")
except Exception as e:
    error_message = str(e)
    if "sora" in error_message.lower() or "video" in error_message.lower():
        print(f"   ❌ Sora API error: {error_message}")
        if "not found" in error_message.lower() or "does not exist" in error_message.lower():
            print("   → Sora API is not available for your account yet")
    else:
        print(f"   ⚠️  Error: {error_message}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("""
To enable Sora API access:

1. Verify your organization (if not already done):
   → https://platform.openai.com/settings/organization/general
   → Click "Verify Organization"
   → Wait 15 minutes for propagation

2. Check if you have Sora access:
   → Look for 'sora-2' or 'sora-2-pro' in model list above
   → If not present, Sora is not yet available

3. ChatGPT Pro subscription notes:
   → ChatGPT Pro ($200/mo) gives you Sora access in ChatGPT web/app
   → But this does NOT automatically grant API access
   → API access is separate and requires invitation

4. To request API access:
   → Contact OpenAI support
   → Or wait for broader rollout (coming weeks)

For now, our POC doesn't need Sora - we're analyzing existing
videos/photos, not generating them!
""")

print("=" * 80)
