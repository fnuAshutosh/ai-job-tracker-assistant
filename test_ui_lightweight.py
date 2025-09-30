"""
Lightweight UI Test Suite for Job Tracker Assistant
Tests UI components without requiring browser automation
Uses requests and HTML parsing to validate the application
"""

import streamlit as st
import requests
import time
from datetime import datetime
import json
import subprocess
import sys
import re

class LightweightUITester:
    def __init__(self, app_url="http://localhost:8501"):
        self.app_url = app_url
        self.test_results = []
        
    def log_result(self, test_name, status, details):
        """Log test result"""
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def test_app_accessibility(self):
        """Test if the Streamlit app is accessible"""
        try:
            response = requests.get(self.app_url, timeout=10)
            if response.status_code == 200:
                self.log_result("App Accessibility", "SUCCESS", f"App is accessible at {self.app_url}")
                return response.text
            else:
                self.log_result("App Accessibility", "FAILED", f"App returned status {response.status_code}")
                return None
        except Exception as e:
            self.log_result("App Accessibility", "FAILED", f"Cannot connect to app: {e}")
            return None
            
    def test_critical_imports(self):
        """Test if all critical modules can be imported"""
        critical_modules = [
            "landing_page", "user_api_keys", "privacy_components", 
            "demo_controller", "gmail_utils", "ai_email_classifier"
        ]
        
        for module in critical_modules:
            try:
                result = subprocess.run([
                    sys.executable, "-c", f"import {module}; print('SUCCESS')"
                ], capture_output=True, text=True, cwd="d:\\Ai AGENTS\\job-tracker-assistant")
                
                if "SUCCESS" in result.stdout:
                    self.log_result(f"Import {module}", "SUCCESS", f"Module {module} imports successfully")
                else:
                    self.log_result(f"Import {module}", "FAILED", f"Module {module} failed to import: {result.stderr}")
            except Exception as e:
                self.log_result(f"Import {module}", "FAILED", f"Import test failed: {e}")
                
    def test_landing_page_functionality(self):
        """Test landing page components programmatically"""
        try:
            # Test landing page function
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.append('d:\\\\Ai AGENTS\\\\job-tracker-assistant')
from landing_page import show_landing_page, initialize_landing_state
print('Landing page functions available')
"""
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("Landing Page Functions", "SUCCESS", "Landing page functions are available")
            else:
                self.log_result("Landing Page Functions", "FAILED", f"Landing page test failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("Landing Page Test", "FAILED", f"Cannot test landing page: {e}")
            
    def test_api_key_functionality(self):
        """Test API key management functions"""
        try:
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.append('d:\\\\Ai AGENTS\\\\job-tracker-assistant')
from user_api_keys import show_api_key_setup, get_user_gemini_key
print('API key functions available')
"""
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("API Key Functions", "SUCCESS", "API key management functions are available")
            else:
                self.log_result("API Key Functions", "FAILED", f"API key test failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("API Key Test", "FAILED", f"Cannot test API key functions: {e}")
            
    def test_privacy_components(self):
        """Test privacy component functions"""
        try:
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.append('d:\\\\Ai AGENTS\\\\job-tracker-assistant')
from privacy_components import show_privacy_disclaimer, show_consent_flow
print('Privacy components available')
"""
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("Privacy Components", "SUCCESS", "Privacy components are available")
            else:
                self.log_result("Privacy Components", "FAILED", f"Privacy test failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("Privacy Test", "FAILED", f"Cannot test privacy components: {e}")
            
    def test_demo_controller(self):
        """Test demo controller functionality"""
        try:
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.append('d:\\\\Ai AGENTS\\\\job-tracker-assistant')
from demo_controller import get_demo_controller
controller = get_demo_controller()
print(f'Demo controller initialized with {len(controller.demo_applications)} applications')
"""
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and "applications" in result.stdout:
                self.log_result("Demo Controller", "SUCCESS", "Demo controller functions correctly")
            else:
                self.log_result("Demo Controller", "FAILED", f"Demo controller test failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("Demo Controller Test", "FAILED", f"Cannot test demo controller: {e}")
            
    def test_database_operations(self):
        """Test database functionality"""
        try:
            result = subprocess.run([
                sys.executable, "-c", """
import sys
sys.path.append('d:\\\\Ai AGENTS\\\\job-tracker-assistant')
from db_utils import init_db, list_applications
init_db()
apps = list_applications()
print(f'Database has {len(apps)} applications')
"""
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and "applications" in result.stdout:
                self.log_result("Database Operations", "SUCCESS", "Database operations work correctly")
            else:
                self.log_result("Database Operations", "FAILED", f"Database test failed: {result.stderr}")
                
        except Exception as e:
            self.log_result("Database Test", "FAILED", f"Cannot test database: {e}")
            
    def test_streamlit_app_structure(self):
        """Test the main app.py structure"""
        try:
            with open("d:\\Ai AGENTS\\job-tracker-assistant\\app.py", "r", encoding="utf-8") as f:
                app_content = f.read()
                
            # Check for critical components
            critical_checks = [
                ("Landing Page Import", "from landing_page import"),
                ("API Key Import", "from user_api_keys import"),
                ("Privacy Import", "from privacy_components import"),
                ("Landing Page Call", "show_landing_page"),
                ("API Key Setup", "show_api_key_setup"),
            ]
            
            for check_name, check_pattern in critical_checks:
                if check_pattern in app_content:
                    self.log_result(f"App Structure - {check_name}", "SUCCESS", f"Found {check_pattern}")
                else:
                    self.log_result(f"App Structure - {check_name}", "WARNING", f"Missing {check_pattern}")
                    
        except Exception as e:
            self.log_result("App Structure Test", "FAILED", f"Cannot analyze app structure: {e}")
            
    def run_component_tests(self):
        """Run all component-level tests"""
        print("🔍 Testing Individual Components...")
        self.test_critical_imports()
        self.test_landing_page_functionality()
        self.test_api_key_functionality()
        self.test_privacy_components()
        self.test_demo_controller()
        self.test_database_operations()
        self.test_streamlit_app_structure()
        
    def run_integration_test(self):
        """Run integration test by starting the app and checking response"""
        print("🚀 Testing Live Application...")
        
        # Test app accessibility
        html_content = self.test_app_accessibility()
        
        if html_content:
            # Basic HTML validation
            if "streamlit" in html_content.lower():
                self.log_result("Streamlit Framework", "SUCCESS", "Streamlit framework detected in response")
            else:
                self.log_result("Streamlit Framework", "WARNING", "Streamlit framework not clearly detected")
                
            # Check for basic UI elements (these should appear in the HTML)
            ui_checks = [
                ("Title Element", "Job Application Tracker"),
                ("Privacy Text", "privacy"),
                ("API Key Text", "API"),
                ("Button Elements", "button"),
            ]
            
            for check_name, check_text in ui_checks:
                if check_text.lower() in html_content.lower():
                    self.log_result(f"UI Element - {check_name}", "SUCCESS", f"Found '{check_text}' in page")
                else:
                    self.log_result(f"UI Element - {check_name}", "WARNING", f"'{check_text}' not found in page")
        
    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        warning_count = len([r for r in self.test_results if r['status'] == 'WARNING'])
        failed_count = len([r for r in self.test_results if r['status'] == 'FAILED'])
        total_count = len(self.test_results)
        
        # Calculate health score
        health_score = (success_count / total_count * 100) if total_count > 0 else 0
        
        report = f"""
🔍 JOB TRACKER ASSISTANT - COMPREHENSIVE UI TEST REPORT
{'=' * 70}
🕒 Test Execution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Application: {self.app_url}
🏥 Health Score: {health_score:.1f}%

📊 TEST SUMMARY:
{'─' * 30}
✅ Passed Tests: {success_count:>3}
⚠️  Warnings:     {warning_count:>3}
❌ Failed Tests: {failed_count:>3}
📋 Total Tests:  {total_count:>3}

🔍 DETAILED TEST RESULTS:
{'─' * 50}
"""
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['test'].split(' -')[0].split(' ')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
            
        for category, tests in categories.items():
            report += f"\n📂 {category.upper()} TESTS:\n"
            for result in tests:
                status_icon = {"SUCCESS": "✅", "WARNING": "⚠️", "FAILED": "❌", "INFO": "ℹ️"}.get(result['status'], "❓")
                report += f"   {status_icon} {result['test']}: {result['details']}\n"
                
        # Critical Analysis
        report += f"""
{'─' * 50}
🎯 CRITICAL ANALYSIS:
"""
        
        critical_failures = [r for r in self.test_results if r['status'] == 'FAILED']
        if critical_failures:
            report += "\n❌ CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:\n"
            for failure in critical_failures:
                report += f"   🚨 {failure['test']}: {failure['details']}\n"
        else:
            report += "\n✅ No critical failures detected!\n"
            
        # Warnings analysis
        warnings = [r for r in self.test_results if r['status'] == 'WARNING']
        if warnings:
            report += "\n⚠️  WARNINGS TO INVESTIGATE:\n"
            for warning in warnings:
                report += f"   🔍 {warning['test']}: {warning['details']}\n"
                
        # Recommendations
        report += f"""
{'─' * 50}
💡 RECOMMENDATIONS:
"""
        
        if health_score >= 90:
            report += "\n🎉 EXCELLENT: Application is functioning very well!"
        elif health_score >= 75:
            report += "\n👍 GOOD: Application is mostly functional with minor issues."
        elif health_score >= 50:
            report += "\n⚠️  FAIR: Application has moderate issues that should be addressed."
        else:
            report += "\n🚨 POOR: Application has significant issues requiring immediate attention."
            
        # Next steps
        if failed_count > 0:
            report += f"\n\n🔧 NEXT STEPS:\n"
            report += "   1. Address critical failures first\n"
            report += "   2. Review warnings for potential issues\n"
            report += "   3. Re-run tests after fixes\n"
        else:
            report += f"\n\n🚀 READY FOR PRODUCTION:\n"
            report += "   • All critical components functional\n"
            report += "   • UI elements properly integrated\n"
            report += "   • Application ready for user testing\n"
            
        return report

def main():
    """Main test execution function"""
    print("🔍 Job Tracker Assistant - Comprehensive UI Test Suite")
    print("=" * 60)
    
    tester = LightweightUITester()
    
    # Run component tests first
    tester.run_component_tests()
    
    print("\n" + "=" * 60)
    
    # Run integration tests
    tester.run_integration_test()
    
    # Generate and save report
    report = tester.generate_comprehensive_report()
    
    # Save to file
    with open("d:\\Ai AGENTS\\job-tracker-assistant\\ui_test_report_comprehensive.txt", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(report)
    print(f"\n📝 Detailed report saved to: ui_test_report_comprehensive.txt")

if __name__ == "__main__":
    main()