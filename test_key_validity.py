#!/usr/bin/env python3
"""
Test API key validity using the user's suggested method
"""

import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

# Load API key from .env
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

print("="*60)
print("API KEY VALIDITY TEST")
print("="*60)
print(f"Testing key: {api_key[:15]}...{api_key[-10:]}")
print()

def is_api_key_valid():
    try:
        # Make a simple test request (listing models)
        models = client.models.list()
        print(f"✅ Successfully connected to OpenAI API")
        print(f"   Found {len(list(models))} available models")
    except Exception as e:
        print(f"API call error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    else:
        return True

# Test your API key
result = is_api_key_valid()
print()
print("="*60)
print(f"API key is valid: {result}")
print("="*60)

if result:
    print("\n✅ SUCCESS! API key works!")
    print("We can proceed with the POC test.")
else:
    print("\n❌ FAILED! API key doesn't work.")
    print("Please check your OpenAI account billing settings.")
