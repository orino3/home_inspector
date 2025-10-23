#!/usr/bin/env python3
"""
Test using the user's exact working code
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from environment
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

print(f"Testing API key: {api_key[:15]}...{api_key[-10:]}\n")

def is_api_key_valid():
    try:
        # Make a simple test request (listing models)
        client.models.list()
    except Exception as e:
        print(f"API call error: {e}")
        return False
    else:
        return True

# Test your API key
print("API key is valid:", is_api_key_valid())
