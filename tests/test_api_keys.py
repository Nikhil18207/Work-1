"""
Quick test to check if API keys are loaded correctly
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("API KEY CHECK")
print("=" * 80)

serper_key = os.getenv('SERPER_API_KEY', '')
google_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
google_cx = os.getenv('GOOGLE_SEARCH_CX', '')

print(f"\nSERPER_API_KEY:")
if serper_key:
    print(f"  ✅ Found: {serper_key[:20]}... (length: {len(serper_key)})")
else:
    print(f"  ❌ Not found")

print(f"\nGOOGLE_SEARCH_API_KEY:")
if google_key:
    print(f"  ✅ Found: {google_key[:20]}... (length: {len(google_key)})")
else:
    print(f"  ❌ Not found")

print(f"\nGOOGLE_SEARCH_CX:")
if google_cx:
    print(f"  ✅ Found: {google_cx[:20]}... (length: {len(google_cx)})")
else:
    print(f"  ❌ Not found")

print("\n" + "=" * 80)

# Test which provider will be used
if serper_key:
    print("✅ Will use: SERPER API")
elif google_key and google_cx:
    print("✅ Will use: GOOGLE CUSTOM SEARCH")
else:
    print("❌ No search provider configured")

print("=" * 80)
