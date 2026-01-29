#!/usr/bin/env python3
"""
Test script to verify custom OpenAI-compatible model configuration.
"""

import os
import sys
from dotenv import load_dotenv
import openai

def test_model_connection():
    """Test if the model endpoint is accessible and working."""
    load_dotenv()
    
    api_key = os.getenv("CHATGPT_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    
    print("=" * 60)
    print("PageIndex Custom Model Configuration Test")
    print("=" * 60)
    
    print("\n📋 Configuration:")
    print(f"  API Key: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"  Base URL: {base_url if base_url else 'Using default OpenAI endpoint'}")
    
    if not api_key:
        print("\n❌ Error: CHATGPT_API_KEY not found in .env file")
        print("Please create a .env file with your API key.")
        return False
    
    # Test model
    test_model = input("\n🤖 Enter model name to test (e.g., gpt-4o, qwen2.5:72b): ").strip()
    if not test_model:
        print("❌ No model specified")
        return False
    
    print(f"\n🔄 Testing connection to model: {test_model}...")
    
    try:
        # Create client
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = openai.OpenAI(**client_kwargs)
        
        # Test simple completion
        print("  Sending test message...")
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "user", "content": "Say 'Hello, PageIndex!' and nothing else."}
            ],
            temperature=0,
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"  Model response: {result}")
        
        print("\n✅ Success! Your model configuration is working correctly.")
        print("\n📝 You can now run PageIndex with this model:")
        print(f"   python3 run_pageindex.py --pdf_path your_document.pdf --model {test_model}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to model: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("  1. Check if your model service is running")
        print("  2. Verify OPENAI_API_BASE URL is correct (should end with /v1)")
        print("  3. Ensure the model name matches what's available in your service")
        print("  4. Check firewall settings and port accessibility")
        
        if base_url:
            print(f"\n  Try testing your endpoint directly:")
            print(f"  curl {base_url}/models")
        
        return False

if __name__ == "__main__":
    success = test_model_connection()
    sys.exit(0 if success else 1)
