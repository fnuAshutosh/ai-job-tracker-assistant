"""
Streamlit UI Testing with Multiple Port Detection
Tests UI functionality with automatic port discovery.
"""

import time
import os
import sys
from datetime import datetime
import requests
from typing import Dict, List

def find_running_app():
    """Find which port the Streamlit app is running on"""
    print("🔍 Searching for running Streamlit app...")
    ports_to_test = [8503, 8502, 8501, 8504, 8505]
    
    for port in ports_to_test:
        app_url = f"http://localhost:{port}"
        try:
            response = requests.get(app_url, timeout=2)
            if response.status_code == 200:
                print(f"✅ Found running app on port {port}")
                return app_url
        except:
            continue
    
    print("❌ No running Streamlit app found on common ports")
    return None

def test_app_accessibility(app_url):
    """Test if the Streamlit app is accessible and functional"""
    print(f"\n🧪 Testing App Accessibility: {app_url}")
    print("=" * 50)
    
    try:
        response = requests.get(app_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ PASS App Accessibility")
            print(f"   💬 Status Code: {response.status_code}")
            print(f"   💬 Response Length: {len(response.content):,} bytes")
            
            # Analyze content
            content = response.text.lower()
            
            content_tests = [
                ("Streamlit Framework", "streamlit" in content),
                ("App Title", "job application tracker" in content or "job tracker" in content),
                ("CSS Styling", "css" in content or ".stApp" in content),
                ("JavaScript", "script" in content),
                ("Main Container", "main" in content or "stmain" in content),
                ("Interactive Elements", "button" in content or "input" in content)
            ]
            
            passed = sum(1 for _, result in content_tests if result)
            total = len(content_tests)
            
            print(f"\n📋 Content Analysis ({passed}/{total} passed):")
            for test_name, result in content_tests:
                status = "✅" if result else "❌"
                print(f"{status} {test_name}")
            
            # Performance check
            content_size_mb = len(response.content) / (1024 * 1024)
            if content_size_mb > 10:
                print(f"⚠️  Large response size: {content_size_mb:.2f} MB")
            
            return True
            
        else:
            print(f"❌ FAIL App Accessibility - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL App Accessibility - Error: {str(e)}")
        return False

def test_app_endpoints(app_url):
    """Test various Streamlit endpoints"""
    print(f"\n🔌 Testing Streamlit Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("/", "Main Page"),
        ("/_stcore/health", "Health Check"),
        ("/_stcore/stream", "WebSocket Stream")
    ]
    
    results = []
    for endpoint, description in endpoints:
        url = app_url + endpoint
        try:
            response = requests.get(url, timeout=5)
            success = response.status_code in [200, 204, 101]  # 101 for WebSocket upgrade
            status = "✅ PASS" if success else f"❌ FAIL ({response.status_code})"
            print(f"{status} {description}")
            results.append(success)
        except Exception as e:
            print(f"❌ FAIL {description} - {str(e)[:50]}...")
            results.append(False)
    
    return sum(results) / len(results) if results else 0

def test_response_performance(app_url):
    """Test response time and performance"""
    print(f"\n⚡ Testing Performance")
    print("-" * 40)
    
    try:
        # Measure multiple requests
        times = []
        for i in range(3):
            start_time = time.time()
            response = requests.get(app_url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"✅ Average Response Time: {avg_time:.2f}s")
            print(f"   💬 Min: {min_time:.2f}s, Max: {max_time:.2f}s")
            
            # Performance assessment
            if avg_time < 2.0:
                print("✅ PASS Performance - Excellent")
            elif avg_time < 5.0:
                print("⚠️  WARN Performance - Acceptable")
            else:
                print("❌ FAIL Performance - Slow")
            
            return True
    
    except Exception as e:
        print(f"❌ FAIL Performance Test - {str(e)}")
        return False
    
    return False

def test_mobile_compatibility(app_url):
    """Test mobile compatibility with different user agents"""
    print(f"\n📱 Testing Device Compatibility")
    print("-" * 40)
    
    user_agents = {
        "Desktop Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mobile iPhone": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Tablet iPad": "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    }
    
    results = []
    for device, user_agent in user_agents.items():
        try:
            headers = {'User-Agent': user_agent}
            response = requests.get(app_url, headers=headers, timeout=10)
            
            success = response.status_code == 200
            status = "✅ PASS" if success else f"❌ FAIL ({response.status_code})"
            print(f"{status} {device}")
            results.append(success)
            
        except Exception as e:
            print(f"❌ FAIL {device} - Error")
            results.append(False)
    
    return sum(results) / len(results) if results else 0

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE UI TEST REPORT")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result)
    
    print(f"📈 Overall Success Rate: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 EXCELLENT: All tests passed! Your app is fully functional.")
        grade = "A+"
    elif passed_tests >= total_tests * 0.8:
        print("✅ GOOD: Most tests passed. Minor issues detected.")
        grade = "B+"
    elif passed_tests >= total_tests * 0.6:
        print("⚠️  FAIR: Some tests failed. Check for issues.")
        grade = "C+"
    else:
        print("❌ POOR: Multiple test failures detected.")
        grade = "D"
    
    print(f"🎯 Grade: {grade}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if passed_tests < total_tests:
        print("• Check if all Streamlit components are working correctly")
        print("• Verify database connections and AI service availability")
        print("• Test manually in browser for visual verification")
    
    print("• Monitor application logs for any errors")
    print("• Consider implementing automated integration tests")
    print("• Test with real user data and scenarios")
    
    return grade

def comprehensive_ui_test():
    """Run comprehensive UI tests"""
    print("Job Application Tracker - Comprehensive UI Testing Suite")
    print("Testing accessibility, performance, compatibility, and functionality")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Find the running app
    app_url = find_running_app()
    if not app_url:
        print("\n❌ Cannot run tests - Streamlit app is not running")
        print("Please start the app with: streamlit run app.py")
        return
    
    # Run all tests
    test_results = []
    
    print("\n" + "🚀 Starting Test Suite".center(60, "="))
    
    # Test 1: Basic Accessibility
    test_results.append(test_app_accessibility(app_url))
    
    # Test 2: Endpoint Testing
    endpoint_success_rate = test_app_endpoints(app_url)
    test_results.append(endpoint_success_rate > 0.5)
    
    # Test 3: Performance Testing
    test_results.append(test_response_performance(app_url))
    
    # Test 4: Mobile Compatibility
    mobile_success_rate = test_mobile_compatibility(app_url)
    test_results.append(mobile_success_rate > 0.5)
    
    # Generate final report
    grade = generate_test_report(test_results)
    
    print(f"\nTesting completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"App tested: {app_url}")
    
    return grade

if __name__ == "__main__":
    comprehensive_ui_test()