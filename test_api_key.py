#!/usr/bin/env python3
"""
Test script to diagnose OpenAI API key issues
"""

import requests
import json

# Replace this with your actual API key
API_KEY = "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"

print("🔍 Testing OpenAI API Key...\n")

# Test 1: Check if key format is valid
print("1️⃣  Checking API key format...")
if API_KEY.startswith("sk-") and len(API_KEY) > 20:
    print("   ✅ API key format looks valid\n")
else:
    print("   ❌ API key format is invalid\n")

# Test 2: Try to list models (simple request that doesn't cost tokens)
print("2️⃣  Testing API authentication...")
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
    
    if response.status_code == 200:
        print("   ✅ API key is valid and authenticated\n")
    elif response.status_code == 401:
        print("   ❌ Invalid API key - authentication failed")
        print("   Action: Check that the API key is correct\n")
    elif response.status_code == 429:
        print("   ⏳ Rate limited - account might have quota issues")
        print("   Action: Check your account billing and usage limits\n")
    else:
        print(f"   ⚠️  Status code: {response.status_code}")
        print(f"   Response: {response.text}\n")
        
except Exception as e:
    print(f"   ❌ Connection error: {str(e)}\n")

# Test 3: Try a simple chat completion
print("3️⃣  Testing chat completion API...")
payload = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Say 'Hello' in one word"}
    ],
    "max_tokens": 5
}

try:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        print(f"   ✅ API works! Response: '{answer}'\n")
        print("🎉 Your API key is working perfectly!")
        
    elif response.status_code == 401:
        print("   ❌ Invalid API key")
        print("   Action: Verify your API key at https://platform.openai.com/account/api-keys\n")
        
    elif response.status_code == 429:
        print("   ⏳ Rate limited (429 error)")
        print("   This could mean:")
        print("   - Your account has no credits")
        print("   - Your account is new and needs verification")
        print("   - You've exceeded your usage quota")
        print("   Action: Check https://platform.openai.com/account/billing/overview\n")
        
    elif response.status_code == 403:
        print("   ❌ Permission denied")
        print("   Action: Your account might not have access to this API\n")
        
    else:
        print(f"   ⚠️  Status code: {response.status_code}")
        print(f"   Response: {response.text}\n")
        
except requests.exceptions.Timeout:
    print("   ⏱️  Request timed out\n")
except Exception as e:
    print(f"   ❌ Error: {str(e)}\n")

print("\n" + "="*50)
print("📋 Summary:")
print("="*50)
print("""
If you see:
- ✅ API works! → Your chatbot should work. Refresh the page.
- ❌ Invalid API key → Check your key at https://platform.openai.com/account/api-keys
- ⏳ Rate limited → Check billing at https://platform.openai.com/account/billing/overview
- ❌ Permission denied → Your account might need verification
""")

