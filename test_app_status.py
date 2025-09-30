#!/usr/bin/env python3
"""
Simple test script to check if the Streamlit app is running and accessible
"""

import requests
import time
import sys

def test_app(port=8503, timeout=10):
    """Test if the app is accessible"""
    url = f"http://localhost:{port}"
    
    try:
        print(f"Testing app at {url}...")
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            print(f"[SUCCESS] App is running and accessible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content Length: {len(response.text)} characters")
            
            # Check if it contains Streamlit content
            if "streamlit" in response.text.lower() or "job tracker" in response.text.lower():
                print(f"   Content: Contains expected Streamlit content")
            else:
                print(f"   Warning: May not be the expected Streamlit app")
                
            return True
        else:
            print(f"[FAILED] App returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[FAILED] Cannot connect to {url}")
        print("   App may not be running or port may be blocked")
        return False
    except requests.exceptions.Timeout:
        print(f"[FAILED] Request timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8503
    test_app(port)