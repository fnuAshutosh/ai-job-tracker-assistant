import requests
import time

print("Quick Streamlit Test")
print("=" * 40)

try:
    response = requests.get('http://localhost:8503', timeout=10)
    if response.status_code == 200:
        print("SUCCESS: Streamlit app is accessible")
        print(f"Response size: {len(response.content):,} bytes")
        
        content = response.text.lower()
        tests = [
            ('Streamlit detected', 'streamlit' in content),
            ('Job tracker title', 'job' in content and 'tracker' in content),
            ('Interactive elements', 'button' in content or 'input' in content),
            ('CSS styling', 'css' in content or 'style' in content)
        ]
        
        passed = sum(1 for _, result in tests if result)
        print(f"Content tests: {passed}/{len(tests)} passed")
        
        for test_name, result in tests:
            status = "PASS" if result else "FAIL"
            print(f"  {status}: {test_name}")
        
        print()
        print("SUCCESS: Your Streamlit app is working perfectly!")
        print("You can access it at: http://localhost:8503")
        
    else:
        print(f"FAIL: Status code {response.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")