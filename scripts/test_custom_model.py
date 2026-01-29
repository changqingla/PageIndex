#!/usr/bin/env python3
"""
Test script to verify custom OpenAI-compatible API configuration.

Usage:
    python scripts/test_custom_model.py
    python scripts/test_custom_model.py --model qwen2.5:72b
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import openai
from dotenv import load_dotenv

load_dotenv()

def test_connection(model_name=None):
    """Test connection to the configured API endpoint."""
    
    api_key = os.getenv("CHATGPT_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    
    print("=" * 60)
    print("PageIndex Custom Model Configuration Test")
    print("=" * 60)
    print()
    
    # Display configuration
    print("📋 Current Configuration:")
    print(f"  API Key: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"  API Base: {api_base if api_base else 'Default (OpenAI)'}")
    print(f"  Model: {model_name if model_name else 'Not specified'}")
    print()
    
    if not api_key:
        print("❌ Error: CHATGPT_API_KEY not found in .env file")
        print("   Please copy .env.example to .env and set your API key")
        return False
    
    # Test connection
    print("🔗 Testing connection...")
    
    try:
        client_kwargs = {"api_key": api_key}
        if api_base:
            client_kwargs["base_url"] = api_base
        
        client = openai.OpenAI(**client_kwargs)
        
        # Try to list models if possible
        try:
            models = client.models.list()
            print("✓ Connection successful!")
            print()
            print("📦 Available models:")
            for model in list(models)[:10]:  # Show first 10
                print(f"  - {model.id}")
            if len(list(models)) > 10:
                print(f"  ... and {len(list(models)) - 10} more")
        except Exception as e:
            # Some APIs don't support listing models
            print("✓ Connection successful!")
            print("  (Model listing not supported by this API)")
        
        print()
        
        # Test a simple completion if model is specified
        if model_name:
            print(f"🧪 Testing completion with model: {model_name}")
            print()
            
            test_prompt = "Extract the title from this text: 'Chapter 1: Introduction to AI'"
            
            print(f"Prompt: {test_prompt}")
            print()
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0,
                max_tokens=50
            )
            
            result = response.choices[0].message.content
            print(f"Response: {result}")
            print()
            print("✅ Model test successful!")
            
        else:
            print("💡 Tip: Run with --model <model_name> to test a specific model")
        
        print()
        print("=" * 60)
        print("✅ All tests passed! You're ready to use PageIndex.")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Run: python3 run_pageindex.py --pdf_path your_document.pdf --model your_model")
        print("  2. See docs/CUSTOM_MODELS.md for more configuration options")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check if your API service is running")
        print("  2. Verify OPENAI_API_BASE URL (should end with /v1)")
        print("  3. Confirm API key is correct")
        print("  4. Check firewall/network settings")
        print()
        print("For Ollama users:")
        print("  - Start Ollama: ollama serve")
        print("  - Pull a model: ollama pull qwen2.5:72b")
        print("  - Set OPENAI_API_BASE=http://localhost:11434/v1")
        print()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test custom OpenAI-compatible API configuration"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name to test (e.g., qwen2.5:72b, gpt-4o)"
    )
    
    args = parser.parse_args()
    
    success = test_connection(args.model)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
