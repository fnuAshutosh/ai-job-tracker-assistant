#!/usr/bin/env python3
"""
Simple OAuth test script to verify Gmail API authentication works
"""

import sys
import os

# Add current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_oauth():
    """Test Gmail OAuth authentication"""
    print("🔍 Testing Gmail OAuth authentication...")
    
    try:
        from gmail_utils import get_gmail_service
        
        print("📧 Attempting to connect to Gmail API...")
        service = get_gmail_service()
        
        print("✅ Successfully authenticated with Gmail!")
        
        # Test basic profile access
        profile = service.users().getProfile(userId='me').execute()
        print(f"📬 Connected to: {profile.get('emailAddress')}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 0)}")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = test_oauth()
    if success:
        print("\n🎉 OAuth test successful! Ready to use Gmail integration.")
    else:
        print("\n💡 Please:")
        print("1. Add your email as a test user in Google Cloud Console")
        print("2. Or publish your OAuth app")
        print("3. Make sure credentials.json is for Desktop application")