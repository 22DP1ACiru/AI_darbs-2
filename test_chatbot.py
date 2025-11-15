#!/usr/bin/env python
"""
Test script to diagnose chatbot issues
Run this to check if everything is set up correctly
"""

import os
import sys

print("=" * 60)
print("CHATBOT DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Check Python path
print("\n[1] Python Path:")
print(f"   Current directory: {os.getcwd()}")
print(f"   Python path: {sys.path[0]}")

# Test 2: Check .env file
print("\n[2] Environment File Check:")
if os.path.exists(".env"):
    print("   ✓ .env file exists")
    with open(".env", "r") as f:
        content = f.read()
        if "HUGGINGFACE_API_KEY" in content:
            print("   ✓ HUGGINGFACE_API_KEY found in .env")
        else:
            print("   ✗ HUGGINGFACE_API_KEY NOT found in .env")
else:
    print("   ✗ .env file NOT found")

# Test 3: Check directory structure
print("\n[3] Directory Structure:")
if os.path.exists("chatbot_integration"):
    print("   ✓ chatbot_integration/ directory exists")
    
    if os.path.exists("chatbot_integration/__init__.py"):
        print("   ✓ chatbot_integration/__init__.py exists")
    else:
        print("   ✗ chatbot_integration/__init__.py MISSING!")
        print("   → Create it: touch chatbot_integration/__init__.py")
    
    if os.path.exists("chatbot_integration/chatbot_service.py"):
        print("   ✓ chatbot_integration/chatbot_service.py exists")
    else:
        print("   ✗ chatbot_integration/chatbot_service.py MISSING!")
else:
    print("   ✗ chatbot_integration/ directory NOT found")

# Test 4: Try loading .env
print("\n[4] Testing dotenv Loading:")
try:
    from dotenv import load_dotenv
    print("   ✓ python-dotenv imported")
    load_dotenv()
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if api_key:
        print(f"   ✓ API Key loaded: {api_key[:10]}...")
    else:
        print("   ✗ API Key is None or empty")
except ImportError:
    print("   ✗ python-dotenv not installed")
    print("   → Run: pip install python-dotenv")

# Test 5: Try importing ChatbotService
print("\n[5] Testing ChatbotService Import:")
try:
    from chatbot_integration.chatbot_service import ChatbotService
    print("   ✓ ChatbotService imported successfully")
    
    # Try initializing
    try:
        service = ChatbotService()
        print("   ✓ ChatbotService initialized successfully")
        
        # Try a simple call
        try:
            response = service.get_chatbot_response(
                user_message="Hello",
                chat_history=[],
                product_info="Test product: $10"
            )
            if response.get('success'):
                print("   ✓ Test API call successful!")
                print(f"   Response: {response['response'][:50]}...")
            else:
                print(f"   ⚠ API call returned success=False")
                print(f"   Error: {response.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   ✗ Test API call failed: {e}")
            
    except Exception as e:
        print(f"   ✗ ChatbotService initialization failed: {e}")
        
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    print("\n   Possible fixes:")
    print("   1. Make sure chatbot_integration/__init__.py exists")
    print("   2. Make sure chatbot_service.py is in chatbot_integration/")
    print("   3. Check for syntax errors in chatbot_service.py")

# Test 6: Check OpenAI package
print("\n[6] Testing OpenAI Package:")
try:
    from openai import OpenAI
    print("   ✓ openai package imported")
except ImportError:
    print("   ✗ openai package not installed")
    print("   → Run: pip install openai==1.3.7")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

# Summary
print("\n📋 SUMMARY:")
if os.path.exists("chatbot_integration/__init__.py") and os.path.exists(".env"):
    print("✓ Basic structure looks good")
    print("→ If still having issues, check Flask terminal for specific error")
else:
    print("✗ Some files are missing. Fix the issues above and try again.")

print("\n💡 Next steps:")
print("1. Fix any ✗ issues shown above")
print("2. Restart Flask: python app.py")
print("3. Test the chatbot")
print("4. If error persists, copy the Flask terminal error here")