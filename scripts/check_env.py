#!/usr/bin/env python3
"""
Quick script to check if environment variables are set correctly.

Usage:
    python scripts/check_env.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Found .env file at: {env_path}")
else:
    print(f"⚠ No .env file found at: {env_path}")
    print("  You can create one by copying .env.example:")
    print("  cp .env.example .env")
    print()

print()
print("=" * 60)
print("Environment Variables Check")
print("=" * 60)
print()

# Check API Key
api_key = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
if api_key:
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✓ API Key: {masked_key}")
    if os.getenv("CHATGPT_API_KEY"):
        print("  (from CHATGPT_API_KEY)")
    else:
        print("  (from OPENAI_API_KEY)")
else:
    print("✗ API Key: Not set")
    print("  Please set CHATGPT_API_KEY or OPENAI_API_KEY in .env file")

print()

# Check API Base URL
api_base = os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL")
if api_base:
    print(f"✓ API Base URL: {api_base}")
    if os.getenv("OPENAI_API_BASE"):
        print("  (from OPENAI_API_BASE)")
    else:
        print("  (from OPENAI_BASE_URL)")
else:
    print("○ API Base URL: Not set (will use OpenAI default)")
    print("  Set OPENAI_API_BASE or OPENAI_BASE_URL to use custom endpoint")

print()
print("=" * 60)

# Final verdict
if api_key:
    print("✅ Configuration looks good!")
    print()
    print("Next steps:")
    print("  1. Test connection: python scripts/test_custom_model.py --model your_model")
    print("  2. Run PageIndex: python run_pageindex.py --pdf_path your_file.pdf --model your_model")
else:
    print("❌ Configuration incomplete!")
    print()
    print("Please set your API key:")
    print("  1. Copy .env.example to .env: cp .env.example .env")
    print("  2. Edit .env and set CHATGPT_API_KEY=your_key")
    print("  3. Run this script again to verify")
    sys.exit(1)

print()
