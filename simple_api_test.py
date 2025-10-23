#!/usr/bin/env python3
"""
Simple OpenAI API Test - Minimal working example
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

print("="*60)
print("SIMPLE OPENAI API TEST")
print("="*60)
print(f"\nAPI Key: {api_key[:15]}...{api_key[-10:]}")
print(f"Length: {len(api_key)} characters")

# Test with OpenAI client
try:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    print("\n1. Testing simple chat completion...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Say 'API works!' in exactly 2 words"}
        ],
        max_tokens=10
    )

    result = response.choices[0].message.content
    print(f"✅ SUCCESS!")
    print(f"   Response: {result}")
    print(f"   Model: gpt-3.5-turbo")
    print(f"   Tokens used: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ FAILED!")
    print(f"   Error: {e}")
    print(f"   Type: {type(e).__name__}")

    # Check common issues
    print("\n" + "="*60)
    print("TROUBLESHOOTING")
    print("="*60)

    if "401" in str(e) or "Unauthorized" in str(e):
        print("❌ Invalid API key")
        print("   → Regenerate at: https://platform.openai.com/api-keys")

    elif "403" in str(e) or "Access denied" in str(e) or "PermissionDeniedError" in str(type(e).__name__):
        print("❌ Billing not set up or account not active")
        print("   → Set up billing: https://platform.openai.com/settings/organization/billing")
        print("   → Add payment method")
        print("   → Set monthly limit ($10 minimum)")
        print("   → Wait 5-10 minutes after setup")

    elif "429" in str(e) or "rate_limit" in str(e).lower():
        print("❌ Rate limit exceeded")
        print("   → Wait a few minutes and try again")
        print("   → Check usage: https://platform.openai.com/usage")

    elif "quota" in str(e).lower():
        print("❌ Quota exceeded")
        print("   → Add more credits to your account")
        print("   → Check usage: https://platform.openai.com/usage")

    else:
        print(f"❌ Unknown error: {e}")
        print("   → Check OpenAI status: https://status.openai.com/")

print("\n" + "="*60)
