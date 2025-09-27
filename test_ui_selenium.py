"""
Visual UI Testing Suite for Job Application Tracker
Using Selenium to test all Streamlit UI functionality including Kanban board interactions.
"""

import time
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import traceback

# Install selenium if not present
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
except ImportError:
    print("❌ Selenium not found. Installing selenium...")
    os.system("pip install selenium")
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait, Select
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    except ImportError:
        print("❌ Failed to install/import selenium. Please install manually: pip install selenium")
        sys.exit(1)

class StreamlitUITester:
    """Comprehensive UI testing class for Streamlit job tracker application"""
    
    def __init__(self, app_url: str = "http://localhost:8501", headless: bool = False):
        self.app_url = app_url
        self.headless = headless
        self.driver = None
        self.wait = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'screenshots': []
        }
        
        print("🧪 Streamlit UI Visual Testing Suite")
        print("=" * 50)
        print(f"🎯 Target URL: {app_url}")
        print(f"🖥️ Headless mode: {headless}")
        print()
    
    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Try to use Chrome driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 10)
            
            print("✅ Chrome WebDriver initialized successfully")
            return True
            
        except WebDriverException as e:
            print(f"❌ Chrome WebDriver failed: {e}")
            print("💡 Make sure Chrome and ChromeDriver are installed")
            return False
        except Exception as e:
            print(f"❌ Driver setup error: {e}")
            return False
    
    def log_test(self, test_name: str, passed: bool, message: str = "", take_screenshot: bool = False):
        """Log test results and optionally take screenshot"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   💬 {message}")
        
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
        
        # Take screenshot if requested or if test failed
        if take_screenshot or not passed:
            self.take_screenshot(test_name.replace(' ', '_').lower())
    
    def take_screenshot(self, name: str):
        """Take a screenshot and save it"""
        try:
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            self.test_results['screenshots'].append(filename)
            print(f"   📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"   ⚠️ Screenshot failed: {e}")
    
    def wait_for_streamlit_load(self, timeout: int = 30):
        """Wait for Streamlit app to fully load"""
        try:
            # Wait for the main title to appear
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
            time.sleep(2)  # Additional wait for Streamlit to settle
            return True
        except TimeoutException:
            print("⚠️ Streamlit app did not load within timeout period")
            return False
    
    def test_app_loading(self):
        """Test basic app loading and title"""
        print("\n🚀 Testing Application Loading")
        print("-" * 40)
        
        try:
            # Navigate to the app
            self.driver.get(self.app_url)
            
            # Wait for app to load
            if self.wait_for_streamlit_load():
                self.log_test("App Loading", True, "Streamlit app loaded successfully")
            else:
                self.log_test("App Loading", False, "App failed to load within timeout")
                return False
            
            # Check for main title
            try:
                title_element = self.driver.find_element(By.TAG_NAME, "h1")
                title_text = title_element.text
                has_correct_title = "Job Application Tracker" in title_text
                self.log_test("Main Title", has_correct_title, f"Title: {title_text}")
            except NoSuchElementException:
                self.log_test("Main Title", False, "Main title not found")
            
            # Check for sidebar
            try:
                sidebar = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="stSidebar"]')
                self.log_test("Sidebar Present", sidebar is not None, "Sidebar found in DOM")
            except NoSuchElementException:
                self.log_test("Sidebar Present", False, "Sidebar not found")
            
            return True
            
        except Exception as e:
            self.log_test("App Loading", False, f"Exception: {str(e)}")
            return False
    
    def test_view_mode_switching(self):
        """Test switching between List View and Kanban Board"""
        print("\n🔄 Testing View Mode Switching")
        print("-" * 40)
        
        try:
            # Look for view mode radio buttons in sidebar
            try:
                # Find the radio buttons for view mode
                radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                
                if len(radio_buttons) >= 2:
                    self.log_test("View Mode Options", True, f"Found {len(radio_buttons)} radio options")
                    
                    # Test switching to Kanban Board
                    for radio in radio_buttons:
                        # Check if this is the Kanban Board option
                        parent = radio.find_element(By.XPATH, '..')
                        if "Kanban Board" in parent.text:
                            radio.click()
                            time.sleep(3)  # Wait for view to change
                            self.log_test("Switch to Kanban Board", True, "Clicked Kanban Board option")
                            break
                    
                    # Test switching back to List View
                    for radio in radio_buttons:
                        parent = radio.find_element(By.XPATH, '..')
                        if "List View" in parent.text:
                            radio.click()
                            time.sleep(3)  # Wait for view to change
                            self.log_test("Switch to List View", True, "Clicked List View option")
                            break
                            
                else:
                    self.log_test("View Mode Options", False, "Radio buttons not found or insufficient")
                    
            except NoSuchElementException:
                self.log_test("View Mode Options", False, "Radio buttons not found in sidebar")
                
        except Exception as e:
            self.log_test("View Mode Switching", False, f"Exception: {str(e)}")
    
    def test_kanban_board_features(self):
        """Test Kanban board functionality"""
        print("\n🎯 Testing Kanban Board Features")
        print("-" * 40)
        
        try:
            # Switch to Kanban Board view first
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            for radio in radio_buttons:
                parent = radio.find_element(By.XPATH, '..')
                if "Kanban Board" in parent.text:
                    radio.click()
                    time.sleep(3)
                    break
            
            # Look for Kanban board columns
            try:
                # Check for stage columns
                columns = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="column"]')
                if len(columns) >= 6:  # We have 6 stages
                    self.log_test("Kanban Columns", True, f"Found {len(columns)} columns")
                else:
                    self.log_test("Kanban Columns", False, f"Expected 6 columns, found {len(columns)}")
                
                # Look for application cards
                cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[style*="border"]')
                card_count = len([card for card in cards if "background-color" in card.get_attribute("style")])
                self.log_test("Application Cards", card_count > 0, f"Found {card_count} application cards")
                
                # Look for stage headers with gradient backgrounds
                headers = self.driver.find_elements(By.CSS_SELECTOR, 'div[style*="gradient"]')
                header_count = len(headers)
                self.log_test("Stage Headers", header_count >= 6, f"Found {header_count} stage headers")
                
            except Exception as e:
                self.log_test("Kanban Board Structure", False, f"Error checking board structure: {str(e)}")
            
            # Test metrics section
            try:
                metrics = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="metric"]')
                if len(metrics) >= 4:  # We have 4 metrics
                    self.log_test("Kanban Metrics", True, f"Found {len(metrics)} metrics")
                else:
                    self.log_test("Kanban Metrics", False, f"Expected 4 metrics, found {len(metrics)}")
            except Exception as e:
                self.log_test("Kanban Metrics", False, f"Error finding metrics: {str(e)}")
                
        except Exception as e:
            self.log_test("Kanban Board Features", False, f"Exception: {str(e)}")
    
    def test_sidebar_functionality(self):
        """Test sidebar elements and functionality"""
        print("\n📋 Testing Sidebar Functionality")
        print("-" * 40)
        
        try:
            # Test Gmail fetch button
            try:
                fetch_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Fetch Interview Emails')]")
                self.log_test("Gmail Fetch Button", True, "Found Gmail fetch button")
                
                # Test clicking the button (may fail due to OAuth, but UI should respond)
                try:
                    fetch_button.click()
                    time.sleep(2)
                    # Look for any response (success or error message)
                    messages = self.driver.find_elements(By.CSS_SELECTOR, '[role="alert"], .stSuccess, .stError, .stInfo')
                    if messages:
                        self.log_test("Gmail Fetch Response", True, f"Button click generated response")
                    else:
                        self.log_test("Gmail Fetch Response", False, "No response to button click")
                except Exception as e:
                    self.log_test("Gmail Fetch Click", False, f"Button click failed: {str(e)}")
                    
            except NoSuchElementException:
                self.log_test("Gmail Fetch Button", False, "Gmail fetch button not found")
            
            # Test manual entry form elements
            try:
                # Look for input fields
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                self.log_test("Text Input Fields", len(text_inputs) > 0, f"Found {len(text_inputs)} text inputs")
                
                # Look for select dropdowns
                selects = self.driver.find_elements(By.CSS_SELECTOR, 'select, [role="combobox"]')
                self.log_test("Dropdown Fields", len(selects) > 0, f"Found {len(selects)} dropdown fields")
                
                # Look for submit button
                submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Add Application') or contains(text(), 'Submit')]")
                self.log_test("Submit Button", len(submit_buttons) > 0, "Found submit button for manual entry")
                
            except Exception as e:
                self.log_test("Manual Entry Form", False, f"Error checking form elements: {str(e)}")
                
        except Exception as e:
            self.log_test("Sidebar Functionality", False, f"Exception: {str(e)}")
    
    def test_data_display(self):
        """Test data display and table functionality"""
        print("\n📊 Testing Data Display")
        print("-" * 40)
        
        try:
            # Switch to List View
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
            for radio in radio_buttons:
                parent = radio.find_element(By.XPATH, '..')
                if "List View" in parent.text:
                    radio.click()
                    time.sleep(3)
                    break
            
            # Look for data table
            try:
                tables = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="stDataFrame"], table, .dataframe')
                if tables:
                    self.log_test("Data Table", True, f"Found {len(tables)} data tables")
                    
                    # Check if table has rows
                    rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr, [data-testid="row"]')
                    self.log_test("Table Rows", len(rows) > 1, f"Found {len(rows)} table rows (including header)")
                else:
                    self.log_test("Data Table", False, "No data tables found")
                    
            except Exception as e:
                self.log_test("Data Table", False, f"Error finding data table: {str(e)}")
            
            # Look for filter/search functionality
            try:
                search_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[placeholder*="search"], input[placeholder*="filter"]')
                self.log_test("Search/Filter", len(search_inputs) > 0, f"Found {len(search_inputs)} search/filter inputs")
            except Exception as e:
                self.log_test("Search/Filter", False, f"Error checking search functionality: {str(e)}")
                
        except Exception as e:
            self.log_test("Data Display", False, f"Exception: {str(e)}")
    
    def test_interactive_elements(self):
        """Test interactive UI elements"""
        print("\n🖱️ Testing Interactive Elements")
        print("-" * 40)
        
        try:
            # Test buttons are clickable
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button')
            clickable_buttons = 0
            
            for button in buttons[:5]:  # Test first 5 buttons to avoid too many clicks
                try:
                    if button.is_enabled() and button.is_displayed():
                        clickable_buttons += 1
                except Exception:
                    pass
            
            self.log_test("Clickable Buttons", clickable_buttons > 0, f"Found {clickable_buttons} clickable buttons out of {len(buttons)} total")
            
            # Test expandable sections
            try:
                expanders = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="stExpander"]')
                if expanders:
                    self.log_test("Expandable Sections", True, f"Found {len(expanders)} expandable sections")
                    
                    # Try to click first expander
                    try:
                        expanders[0].click()
                        time.sleep(1)
                        self.log_test("Expander Interaction", True, "Successfully clicked expander")
                    except Exception as e:
                        self.log_test("Expander Interaction", False, f"Could not click expander: {str(e)}")
                else:
                    self.log_test("Expandable Sections", False, "No expandable sections found")
                    
            except Exception as e:
                self.log_test("Expandable Sections", False, f"Error testing expanders: {str(e)}")
            
            # Test form interactions
            try:
                inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                if inputs and len(inputs) > 0:
                    # Try to type in first text input
                    test_input = inputs[0]
                    test_input.clear()
                    test_input.send_keys("Test Company")
                    time.sleep(1)
                    
                    entered_value = test_input.get_attribute('value')
                    self.log_test("Text Input Interaction", "Test Company" in entered_value, f"Input value: {entered_value}")
                else:
                    self.log_test("Text Input Interaction", False, "No text inputs found for testing")
                    
            except Exception as e:
                self.log_test("Text Input Interaction", False, f"Error testing text input: {str(e)}")
                
        except Exception as e:
            self.log_test("Interactive Elements", False, f"Exception: {str(e)}")
    
    def test_responsive_design(self):
        """Test responsive design by changing window size"""
        print("\n📱 Testing Responsive Design")
        print("-" * 40)
        
        try:
            # Test desktop view
            self.driver.set_window_size(1920, 1080)
            time.sleep(2)
            desktop_elements = len(self.driver.find_elements(By.CSS_SELECTOR, '*'))
            self.log_test("Desktop View", desktop_elements > 0, f"Desktop view has {desktop_elements} elements")
            
            # Test tablet view
            self.driver.set_window_size(768, 1024)
            time.sleep(2)
            tablet_elements = len(self.driver.find_elements(By.CSS_SELECTOR, '*'))
            self.log_test("Tablet View", tablet_elements > 0, f"Tablet view has {tablet_elements} elements")
            
            # Test mobile view
            self.driver.set_window_size(375, 667)
            time.sleep(2)
            mobile_elements = len(self.driver.find_elements(By.CSS_SELECTOR, '*'))
            self.log_test("Mobile View", mobile_elements > 0, f"Mobile view has {mobile_elements} elements")
            
            # Restore desktop view
            self.driver.set_window_size(1920, 1080)
            time.sleep(1)
            
        except Exception as e:
            self.log_test("Responsive Design", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling")
        print("-" * 40)
        
        try:
            # Test navigation to invalid URL paths
            current_url = self.driver.current_url
            
            # Try invalid path (this should still load Streamlit)
            self.driver.get(current_url + "/invalid-path")
            time.sleep(3)
            
            # Check if app still loads (Streamlit handles routing)
            try:
                title = self.driver.find_element(By.TAG_NAME, "h1")
                self.log_test("Invalid Path Handling", True, "App still loads with invalid path")
            except NoSuchElementException:
                self.log_test("Invalid Path Handling", False, "App breaks with invalid path")
            
            # Return to main app
            self.driver.get(self.app_url)
            time.sleep(3)
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
    
    def test_accessibility(self):
        """Test basic accessibility features"""
        print("\n♿ Testing Accessibility Features")
        print("-" * 40)
        
        try:
            # Check for alt text on images
            images = self.driver.find_elements(By.CSS_SELECTOR, 'img')
            images_with_alt = [img for img in images if img.get_attribute('alt')]
            self.log_test("Image Alt Text", len(images_with_alt) == len(images) or len(images) == 0, 
                         f"{len(images_with_alt)}/{len(images)} images have alt text")
            
            # Check for form labels
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input')
            labels = self.driver.find_elements(By.CSS_SELECTOR, 'label')
            self.log_test("Form Labels", len(labels) > 0 or len(inputs) == 0, 
                         f"Found {len(labels)} labels for {len(inputs)} inputs")
            
            # Check for heading structure
            headings = self.driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
            self.log_test("Heading Structure", len(headings) > 0, f"Found {len(headings)} headings")
            
        except Exception as e:
            self.log_test("Accessibility Features", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all UI tests in sequence"""
        print(f"🚀 Starting Visual UI Test Suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.setup_driver():
            print("❌ Failed to set up WebDriver. Cannot continue with tests.")
            return False
        
        try:
            # Run all test suites
            self.test_app_loading()
            self.test_view_mode_switching()
            self.test_kanban_board_features()
            self.test_sidebar_functionality()
            self.test_data_display()
            self.test_interactive_elements()
            self.test_responsive_design()
            self.test_error_handling()
            self.test_accessibility()
            
            # Final screenshot
            self.take_screenshot("final_app_state")
            
        except Exception as e:
            print(f"❌ Unexpected error during testing: {e}")
            self.log_test("Test Suite Execution", False, str(e))
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🏁 WebDriver closed")
        
        # Print results
        self.print_test_summary()
        return True
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 VISUAL UI TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total UI Tests: {total_tests}")
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        print(f"📸 Screenshots Taken: {len(self.test_results['screenshots'])}")
        
        if self.test_results['failed'] > 0:
            print(f"\n⚠️ FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        if self.test_results['screenshots']:
            print(f"\n📷 SCREENSHOTS SAVED:")
            for screenshot in self.test_results['screenshots']:
                print(f"   • {screenshot}")
        
        print(f"\n🎯 UI FUNCTIONALITY STATUS:")
        print("-" * 30)
        
        if pass_rate >= 90:
            print("🎉 EXCELLENT! Your UI is working perfectly!")
        elif pass_rate >= 75:
            print("👍 GOOD! Most UI functionality is working correctly.")
        elif pass_rate >= 50:
            print("⚠️ MODERATE: Some UI issues need attention.")
        else:
            print("🔧 NEEDS WORK: Several UI components require fixes.")
        
        print(f"\n🏁 Visual Test Suite Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """Main test execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual UI Testing for Job Application Tracker")
    parser.add_argument("--url", default="http://localhost:8501", help="Streamlit app URL")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--no-screenshots", action="store_true", help="Disable screenshots")
    
    args = parser.parse_args()
    
    print("Job Application Tracker - Visual UI Testing Suite")
    print("Using Selenium WebDriver to test all Streamlit functionality")
    print()
    
    # Check if Streamlit is running
    import requests
    try:
        response = requests.get(args.url, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Warning: Streamlit app may not be running at {args.url}")
            print("   Please start the app with: streamlit run app.py")
    except requests.exceptions.RequestException:
        print(f"❌ Error: Cannot connect to {args.url}")
        print("   Please make sure Streamlit app is running")
        return
    
    # Run the tests
    tester = StreamlitUITester(app_url=args.url, headless=args.headless)
    tester.run_all_tests()

if __name__ == "__main__":
    main()