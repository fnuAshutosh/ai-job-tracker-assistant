#!/usr/bin/env python3
"""
Quick UI Test for Streamlit App
"""

import requests
import time
from datetime import datetime

def main():
    print("🧪 Quick Streamlit App Test")
    print("=" * 40)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    
    app_url = "http://localhost:8503"
    
    try:
        print(f"\n🎯 Testing: {app_url}")
        
        # Wait a moment for app to be ready
        time.sleep(2)
        
        response = requests.get(app_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS!")
            print(f"   Status: {response.status_code}")
            print(f"   Size: {len(response.content):,} bytes")
            
            # Basic content checks
            content = response.text.lower()
            
            checks = [
                ("App Framework", "streamlit" in content),
                ("Job Tracker", "job" in content and "tracker" in content),
                ("Main Content", len(content) > 1000),
                ("CSS Loaded", "css" in content or "style" in content),
                ("Interactive Elements", "button" in content or "input" in content)
            ]
            
            print(f"\n📋 Content Verification:")
            passed = 0
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if result:
                    passed += 1
            
            success_rate = passed / len(checks) * 100
            print(f"\n📊 Overall: {passed}/{len(checks)} checks passed ({success_rate:.1f}%)")
            
            if success_rate >= 80:
                print("🎉 EXCELLENT: App is working great!")
            elif success_rate >= 60:
                print("✅ GOOD: App is functional with minor issues")
            else:
                print("⚠️  FAIR: App has some issues but is running")
        
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Connection refused - app not running")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    print(f"\nCompleted: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()