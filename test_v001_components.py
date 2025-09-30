#!/usr/bin/env python3
"""
Test Version 0.0.1 functionality
Quick verification that all components are working
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("Testing Version 0.0.1 imports...")
    
    try:
        import streamlit as st
        print("✓ Streamlit: OK")
    except ImportError as e:
        print(f"✗ Streamlit: FAIL - {e}")
        return False
    
    try:
        from gmail_utils import get_gmail_service, fetch_interview_emails
        print("✓ Gmail Utils: OK")
    except ImportError as e:
        print(f"✗ Gmail Utils: FAIL - {e}")
        return False
    
    try:
        from ai_email_classifier import GeminiEmailClassifier
        print("✓ AI Email Classifier: OK")
    except ImportError as e:
        print(f"? AI Email Classifier: WARNING - {e}")
        print("  (May need google-generativeai package)")
    
    try:
        from db_utils import init_db, list_applications
        print("✓ Database Utils: OK")
    except ImportError as e:
        print(f"✗ Database Utils: FAIL - {e}")
        return False
    
    try:
        from kanban_database import get_board_data, BOARD_STAGES
        print("✓ Kanban Database: OK")
    except ImportError as e:
        print(f"✗ Kanban Database: FAIL - {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from init_demo_database import check_and_initialize_database
        result = check_and_initialize_database()
        print(f"✓ Database check: {'Demo created' if result else 'Already exists'}")
        return True
    except Exception as e:
        print(f"✗ Database test: FAIL - {e}")
        return False

def test_credentials():
    """Test OAuth credentials"""
    print("\nTesting credentials...")
    
    if os.path.exists('credentials.json'):
        print("✓ credentials.json: EXISTS")
        try:
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            if 'installed' in creds:
                print("✓ OAuth format: VALID")
                return True
            else:
                print("? OAuth format: Unexpected format")
                return False
        except Exception as e:
            print(f"✗ credentials.json: READ ERROR - {e}")
            return False
    else:
        print("✗ credentials.json: MISSING")
        return False

def main():
    print("🧪 Version 0.0.1 Component Test")
    print("=" * 40)
    
    import_test = test_imports()
    db_test = test_database()
    creds_test = test_credentials()
    
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY:")
    print(f"  Imports: {'✓ PASS' if import_test else '✗ FAIL'}")
    print(f"  Database: {'✓ PASS' if db_test else '✗ FAIL'}")
    print(f"  Credentials: {'✓ PASS' if creds_test else '✗ FAIL'}")
    
    if import_test and db_test and creds_test:
        print("\n🎉 Version 0.0.1 is ready to use!")
        print("📱 Access at: http://localhost:8507")
    else:
        print("\n⚠️  Some components need attention")
        
    return import_test and db_test and creds_test

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)