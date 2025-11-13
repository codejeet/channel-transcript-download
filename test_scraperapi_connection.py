#!/usr/bin/env python3
"""
Test script to verify your ScraperAPI key works correctly.

Usage:
  python test_scraperapi_connection.py YOUR_API_KEY

Or set environment variable:
  export SCRAPERAPI_KEY=YOUR_API_KEY
  python test_scraperapi_connection.py
"""
import sys
import os

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install it with: pip install requests")
    sys.exit(1)


def test_scraperapi_connection(api_key):
    """Test ScraperAPI connection using API endpoint method"""
    print(f"Testing ScraperAPI connection...")
    print(f"API Key: {api_key[:8]}..." if len(api_key) > 8 else api_key)
    print()

    # Test with httpbin.org as shown in ScraperAPI docs
    payload = {
        'api_key': api_key,
        'url': 'https://httpbin.org/ip'
    }

    try:
        print("Making test request to httpbin.org via ScraperAPI...")
        r = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)

        if r.status_code == 200:
            print("✓ Connection successful!")
            print(f"✓ Status Code: {r.status_code}")
            print(f"✓ Response length: {len(r.text)} bytes")
            print(f"\nResponse preview:")
            print("-" * 50)
            print(r.text[:500])
            print("-" * 50)
            return True
        else:
            print(f"✗ Request failed with status code: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print("✗ Request timed out. ScraperAPI may be slow or unavailable.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False


def main():
    # Get API key from command line or environment variable
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get('SCRAPERAPI_KEY')

    if not api_key:
        print("Error: No API key provided")
        print()
        print("Usage:")
        print("  python test_scraperapi_connection.py YOUR_API_KEY")
        print()
        print("Or set environment variable:")
        print("  export SCRAPERAPI_KEY=YOUR_API_KEY")
        print("  python test_scraperapi_connection.py")
        sys.exit(1)

    success = test_scraperapi_connection(api_key)

    if success:
        print("\n✓ Your ScraperAPI key is working correctly!")
        print("You can now use it with the transcript downloader:")
        print(f'  export SCRAPERAPI_KEY={api_key}')
        print('  python youtube_transcript_downloader.py "https://www.youtube.com/@username"')
    else:
        print("\n✗ ScraperAPI test failed. Please check:")
        print("  1. Your API key is correct")
        print("  2. You have available API credits")
        print("  3. Your internet connection is working")
        print("  4. ScraperAPI service is operational")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
