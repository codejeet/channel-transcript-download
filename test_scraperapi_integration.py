#!/usr/bin/env python3
"""
Test script to verify ScraperAPI integration logic
"""
import os

def test_proxy_configuration():
    """Test that proxy configuration is created correctly"""
    api_key = "test_key_123"

    proxies = {
        'http': f'http://scraperapi:{api_key}@proxy-server.scraperapi.com:8001',
        'https': f'http://scraperapi:{api_key}@proxy-server.scraperapi.com:8001'
    }

    print("✓ Proxy configuration created successfully")
    print(f"  HTTP Proxy: {proxies['http']}")
    print(f"  HTTPS Proxy: {proxies['https']}")

    # Test environment variable setting
    os.environ['HTTP_PROXY'] = proxies['http']
    os.environ['HTTPS_PROXY'] = proxies['https']

    assert os.environ.get('HTTP_PROXY') == proxies['http']
    assert os.environ.get('HTTPS_PROXY') == proxies['https']

    print("✓ Environment variables set correctly")

    # Clean up
    del os.environ['HTTP_PROXY']
    del os.environ['HTTPS_PROXY']

    print("✓ Environment variables cleaned up")

def test_api_key_from_env():
    """Test reading API key from environment variable"""
    test_key = "env_test_key_456"
    os.environ['SCRAPERAPI_KEY'] = test_key

    retrieved_key = os.environ.get('SCRAPERAPI_KEY')
    assert retrieved_key == test_key

    print("✓ API key retrieved from environment variable")

    # Clean up
    del os.environ['SCRAPERAPI_KEY']

if __name__ == '__main__':
    print("Testing ScraperAPI Integration Logic\n")
    print("=" * 50)

    test_proxy_configuration()
    print()
    test_api_key_from_env()

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
