"""
Comprehensive UI Test Suite for Job Tracker Assistant
Tests all UI components, buttons, forms, and workflows programmatically
"""

import streamlit as st
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import sys
from datetime import datetime

class JobTrackerUITester:
    def __init__(self, app_url="http://localhost:8501"):
        self.app_url = app_url
        self.test_results = []
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver in headless mode"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Try to use Chrome directly without webdriver-manager
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            self.log_result("Driver Setup", "SUCCESS", "Chrome headless driver initialized")
        except Exception as e:
            self.log_result("Driver Setup", "FAILED", f"Could not initialize driver: {e}")
            # Fallback: Create a mock testing interface
            self.driver = None
            
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
        
    def wait_for_streamlit_load(self):
        """Wait for Streamlit app to fully load"""
        try:
            # Wait for Streamlit's loading indicator to disappear
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # Additional wait for Streamlit components
            self.log_result("App Loading", "SUCCESS", "Streamlit app loaded successfully")
            return True
        except Exception as e:
            self.log_result("App Loading", "FAILED", f"App failed to load: {e}")
            return False
            
    def test_landing_page(self):
        """Test landing page components and flow"""
        try:
            self.driver.get(self.app_url)
            if not self.wait_for_streamlit_load():
                return False
                
            # Test 1: Check if privacy disclaimer is visible
            try:
                privacy_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Privacy Promise')]")
                self.log_result("Privacy Disclaimer", "SUCCESS", "Privacy disclaimer found on landing page")
            except:
                self.log_result("Privacy Disclaimer", "FAILED", "Privacy disclaimer not found")
                
            # Test 2: Check for consent checkbox/button
            try:
                consent_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'I understand') or contains(text(), 'consent') or contains(text(), 'agree')]")
                self.log_result("Consent Control", "SUCCESS", "Consent control found")
            except:
                self.log_result("Consent Control", "FAILED", "Consent control not found")
                
            # Test 3: Look for Demo vs Gmail buttons
            try:
                demo_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Demo') or contains(text(), 'Sample')]")
                self.log_result("Demo Button", "SUCCESS", "Demo mode button found")
            except:
                self.log_result("Demo Button", "FAILED", "Demo mode button not found")
                
            try:
                gmail_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Gmail') or contains(text(), 'Connect')]")
                self.log_result("Gmail Button", "SUCCESS", "Gmail connect button found")
            except:
                self.log_result("Gmail Button", "FAILED", "Gmail connect button not found")
                
            return True
        except Exception as e:
            self.log_result("Landing Page Test", "FAILED", f"Landing page test failed: {e}")
            return False
            
    def test_api_key_workflow(self):
        """Test API key input and management"""
        try:
            # Try to navigate to API key setup by clicking Gmail button
            try:
                gmail_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Connect My Gmail') or contains(text(), 'Gmail')]")
                gmail_button.click()
                time.sleep(3)  # Wait for navigation
                
                # Test 4: Check for API key input field
                try:
                    api_key_input = self.driver.find_element(By.XPATH, "//input[@type='password' or contains(@placeholder, 'AIzaSyA')]")
                    self.log_result("API Key Input Field", "SUCCESS", "Gemini API key input field found")
                    
                    # Test 5: Try typing in the API key field
                    test_key = "AIzaSyTestKey123456789"
                    api_key_input.clear()
                    api_key_input.send_keys(test_key)
                    time.sleep(1)
                    
                    # Check if the input was accepted
                    current_value = api_key_input.get_attribute("value")
                    if current_value == test_key:
                        self.log_result("API Key Input", "SUCCESS", "API key input accepts text correctly")
                    else:
                        self.log_result("API Key Input", "WARNING", f"Input value mismatch. Expected: {test_key}, Got: {current_value}")
                        
                except Exception as e:
                    self.log_result("API Key Input Field", "FAILED", f"API key input field not found: {e}")
                    
                # Test 6: Check for configuration status display
                try:
                    status_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Configuration Status') or contains(text(), 'Configured')]")
                    self.log_result("Configuration Status", "SUCCESS", "Configuration status section found")
                except:
                    self.log_result("Configuration Status", "FAILED", "Configuration status section not found")
                    
            except Exception as e:
                self.log_result("Gmail Navigation", "FAILED", f"Could not navigate to Gmail setup: {e}")
                
        except Exception as e:
            self.log_result("API Key Workflow", "FAILED", f"API key workflow test failed: {e}")
            
    def test_sidebar_controls(self):
        """Test sidebar buttons and controls"""
        try:
            # Test 7: Look for sidebar controls
            try:
                sidebar = self.driver.find_element(By.CLASS_NAME, "css-1d391kg")  # Streamlit sidebar class
                self.log_result("Sidebar", "SUCCESS", "Sidebar element found")
                
                # Test 8: Look for Reconfigure Keys button
                try:
                    reconfig_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Reconfigure') or contains(text(), 'Reset')]")
                    self.log_result("Reconfigure Button", "SUCCESS", "Reconfigure keys button found")
                    
                    # Try clicking it
                    reconfig_button.click()
                    time.sleep(2)
                    self.log_result("Reconfigure Click", "SUCCESS", "Reconfigure button clicked successfully")
                except Exception as e:
                    self.log_result("Reconfigure Button", "FAILED", f"Reconfigure button not found: {e}")
                    
                # Test 9: Look for Clear Keys button
                try:
                    clear_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Clear') or contains(text(), 'Delete')]")
                    self.log_result("Clear Button", "SUCCESS", "Clear keys button found")
                except Exception as e:
                    self.log_result("Clear Button", "FAILED", f"Clear button not found: {e}")
                    
            except Exception as e:
                self.log_result("Sidebar", "WARNING", f"Sidebar not found or different structure: {e}")
                
        except Exception as e:
            self.log_result("Sidebar Controls", "FAILED", f"Sidebar controls test failed: {e}")
            
    def test_demo_mode(self):
        """Test demo mode functionality"""
        try:
            # Navigate back to landing page
            self.driver.get(self.app_url)
            self.wait_for_streamlit_load()
            
            # Test 10: Try to activate demo mode
            try:
                demo_button = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Demo') or contains(text(), 'Sample')]")
                demo_button.click()
                time.sleep(3)
                
                # Test 11: Check for sample data or kanban board
                try:
                    # Look for job application data or kanban columns
                    kanban_element = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Applied') or contains(text(), 'Interview') or contains(text(), 'Applications')]")
                    self.log_result("Demo Data", "SUCCESS", "Demo mode shows sample data/kanban board")
                except:
                    self.log_result("Demo Data", "WARNING", "Demo data/kanban board not clearly visible")
                    
            except Exception as e:
                self.log_result("Demo Mode", "FAILED", f"Could not activate demo mode: {e}")
                
        except Exception as e:
            self.log_result("Demo Mode Test", "FAILED", f"Demo mode test failed: {e}")
            
    def test_app_responsiveness(self):
        """Test general app responsiveness and loading"""
        try:
            # Test 12: Check page load time
            start_time = time.time()
            self.driver.get(self.app_url)
            self.wait_for_streamlit_load()
            load_time = time.time() - start_time
            
            if load_time < 10:
                self.log_result("Page Load Speed", "SUCCESS", f"App loaded in {load_time:.2f} seconds")
            else:
                self.log_result("Page Load Speed", "WARNING", f"App loaded slowly in {load_time:.2f} seconds")
                
            # Test 13: Check for any JavaScript errors
            try:
                logs = self.driver.get_log('browser')
                error_count = len([log for log in logs if log['level'] == 'SEVERE'])
                if error_count == 0:
                    self.log_result("JavaScript Errors", "SUCCESS", "No severe JavaScript errors found")
                else:
                    self.log_result("JavaScript Errors", "WARNING", f"{error_count} JavaScript errors found")
            except:
                self.log_result("JavaScript Errors", "INFO", "Could not check JavaScript errors")
                
        except Exception as e:
            self.log_result("App Responsiveness", "FAILED", f"Responsiveness test failed: {e}")
            
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Job Tracker UI Test Suite...")
        print("=" * 60)
        
        if not self.driver:
            print("❌ Cannot run tests - WebDriver failed to initialize")
            return self.generate_report()
            
        try:
            # Run all test categories
            self.test_landing_page()
            self.test_api_key_workflow()
            self.test_sidebar_controls()
            self.test_demo_mode()
            self.test_app_responsiveness()
            
        finally:
            if self.driver:
                self.driver.quit()
                
        return self.generate_report()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        warning_count = len([r for r in self.test_results if r['status'] == 'WARNING'])
        failed_count = len([r for r in self.test_results if r['status'] == 'FAILED'])
        total_count = len(self.test_results)
        
        report = f"""
📊 JOB TRACKER UI TEST REPORT
{'=' * 50}
🕒 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 App URL: {self.app_url}

📈 SUMMARY:
✅ Passed: {success_count}
⚠️  Warnings: {warning_count}
❌ Failed: {failed_count}
📋 Total Tests: {total_count}

🔍 DETAILED RESULTS:
{'-' * 50}
"""
        
        for result in self.test_results:
            status_icon = {"SUCCESS": "✅", "WARNING": "⚠️", "FAILED": "❌", "INFO": "ℹ️"}.get(result['status'], "❓")
            report += f"{status_icon} [{result['timestamp']}] {result['test']}: {result['details']}\n"
            
        report += f"""
{'-' * 50}

🎯 CRITICAL FINDINGS:
"""
        
        # Analyze critical issues
        critical_issues = [r for r in self.test_results if r['status'] == 'FAILED']
        if critical_issues:
            report += "❌ CRITICAL ISSUES FOUND:\n"
            for issue in critical_issues:
                report += f"   • {issue['test']}: {issue['details']}\n"
        else:
            report += "✅ No critical failures detected!\n"
            
        # Analyze warnings
        warnings = [r for r in self.test_results if r['status'] == 'WARNING']
        if warnings:
            report += "\n⚠️  WARNINGS TO REVIEW:\n"
            for warning in warnings:
                report += f"   • {warning['test']}: {warning['details']}\n"
                
        # Overall assessment
        if failed_count == 0:
            report += f"\n🎉 OVERALL: UI is functioning well with {success_count} successful tests!"
        else:
            report += f"\n🔧 OVERALL: UI needs attention - {failed_count} critical issues found."
            
        return report

def main():
    """Main test execution"""
    print("🔍 Job Tracker Assistant - UI Test Suite")
    print("Checking if Streamlit app is running...")
    
    # Check if app is accessible
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit app is accessible at http://localhost:8501")
        else:
            print(f"⚠️  App returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        print("Make sure the app is running with: streamlit run app.py")
        return
        
    # Run the test suite
    tester = JobTrackerUITester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open("ui_test_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(report)
    print(f"\n📝 Report saved to: ui_test_report.txt")

if __name__ == "__main__":
    main()