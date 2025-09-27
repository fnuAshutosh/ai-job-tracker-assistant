"""
Comprehensive Test Suite for Job Application Tracker
Tests all functionality including AI classification, database operations, and Kanban board.
"""

import sqlite3
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import sys
import os

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
try:
    from ai_email_classifier import GeminiEmailClassifier, EmailClassification
    from db_utils import (
        init_db, get_db_connection, upsert_application, list_applications,
        get_upcoming_interviews, update_application_status, delete_application,
        get_application_stats, search_applications
    )
    from kanban_database import (
        get_board_data, move_application_to_stage, add_application_note,
        BOARD_STAGES
    )
    from gmail_utils import get_gmail_service, fetch_interview_emails
    from parser_utils import parse_interview_email
    from smart_spam_detection import classify_email, is_job_board_spam
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project directory with venv activated")
    sys.exit(1)

class JobTrackerTester:
    """Comprehensive testing class for all job tracker functionality"""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.test_app_id = None
        print("🧪 Job Application Tracker - Comprehensive Test Suite")
        print("=" * 60)
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   💬 {message}")
        
        if passed:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
    
    def test_database_initialization(self):
        """Test database initialization and connection"""
        print("\n🗄️ Testing Database Functionality")
        print("-" * 40)
        
        try:
            # Test database initialization
            init_db()
            self.log_test("Database Initialization", True, "Database initialized successfully")
            
            # Test database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            required_tables = ['applications', 'stage_transitions', 'interview_rounds', 'application_notes']
            existing_tables = [table[0] for table in tables]
            
            for table in required_tables:
                if table in existing_tables:
                    self.log_test(f"Table '{table}' exists", True)
                else:
                    self.log_test(f"Table '{table}' exists", False, f"Missing table: {table}")
            
        except Exception as e:
            self.log_test("Database Initialization", False, str(e))
    
    def test_application_crud_operations(self):
        """Test Create, Read, Update, Delete operations for applications"""
        print("\n📝 Testing Application CRUD Operations")
        print("-" * 40)
        
        try:
            # Test CREATE - Insert a test application
            test_app = {
                'company': 'TestCorp',
                'role': 'Senior Test Engineer',
                'source': 'manual',
                'status': 'applied',
                'date_applied': datetime.now().isoformat(),
                'notes': 'Test application for automated testing',
                'board_stage': 'applied',
                'priority': 'high'
            }
            
            # Insert application
            app_id = upsert_application(test_app)
            self.test_app_id = app_id
            self.log_test("Create Application", app_id is not None, f"Created application with ID: {app_id}")
            
            # Test READ - List applications
            applications = list_applications()
            test_app_found = any(app['id'] == app_id for app in applications if app_id)
            self.log_test("Read Applications", test_app_found, f"Found {len(applications)} total applications")
            
            # Test UPDATE - Update application status
            if app_id:
                update_success = update_application_status(app_id, 'interview_scheduled')
                self.log_test("Update Application Status", update_success, "Status updated to interview_scheduled")
            
            # Test search functionality
            search_results = search_applications('TestCorp')
            search_found = len(search_results) > 0
            self.log_test("Search Applications", search_found, f"Found {len(search_results)} matching applications")
            
        except Exception as e:
            self.log_test("Application CRUD Operations", False, str(e))
    
    def test_kanban_board_functionality(self):
        """Test Kanban board operations"""
        print("\n🎯 Testing Kanban Board Functionality")
        print("-" * 40)
        
        try:
            # Test board data retrieval
            board_data = get_board_data()
            board_loaded = isinstance(board_data, dict) and len(BOARD_STAGES) == len(board_data.keys())
            self.log_test("Load Board Data", board_loaded, f"Loaded {len(board_data)} board stages")
            
            # Test stage definitions
            for stage_key, stage_info in BOARD_STAGES.items():
                stage_valid = 'name' in stage_info and 'order' in stage_info
                self.log_test(f"Stage '{stage_key}' definition", stage_valid, stage_info.get('name', 'Unknown'))
            
            # Test application stage movement (if test app exists)
            if self.test_app_id:
                # Move to screening stage
                move_success = True
                try:
                    move_application_to_stage(self.test_app_id, 'screening', 'Automated test movement')
                    self.log_test("Move Application Stage", True, "Moved from applied to screening")
                except Exception as e:
                    self.log_test("Move Application Stage", False, str(e))
                
                # Test adding notes
                try:
                    add_application_note(self.test_app_id, 'This is a test note for automated testing', 'general')
                    self.log_test("Add Application Note", True, "Added test note")
                except Exception as e:
                    self.log_test("Add Application Note", False, str(e))
            
        except Exception as e:
            self.log_test("Kanban Board Functionality", False, str(e))
    
    def test_ai_email_classifier(self):
        """Test AI email classification functionality"""
        print("\n🤖 Testing AI Email Classification")
        print("-" * 40)
        
        try:
            # Test classifier initialization
            classifier = GeminiEmailClassifier()
            self.log_test("AI Classifier Initialization", True, "Gemini classifier initialized")
            
            # Test email classifications with sample data
            test_emails = [
                {
                    'subject': 'Interview Invitation - Software Engineer at Google',
                    'from': 'recruiter@google.com',
                    'body': 'We would like to invite you for an interview for the Software Engineer position.',
                    'expected_category': 'job_interview'
                },
                {
                    'subject': 'Job Alert: 1000+ Developer Jobs Available',
                    'from': 'alerts@jobboard.com',
                    'body': 'Dear Job Seeker, we found many jobs for you. Click here to apply.',
                    'expected_category': 'promotional'
                },
                {
                    'subject': 'Application Status Update - Data Scientist Role',
                    'from': 'hr@startup.com',
                    'body': 'Thank you for your application. We are reviewing it and will get back to you soon.',
                    'expected_category': 'job_application'
                }
            ]
            
            for i, email in enumerate(test_emails, 1):
                try:
                    classification = classifier.classify_email(email)
                    category_correct = classification.category == email['expected_category']
                    confidence_valid = 0 <= classification.confidence <= 1
                    
                    self.log_test(f"AI Classification Test {i}", category_correct and confidence_valid, 
                                f"Category: {classification.category}, Confidence: {classification.confidence:.2f}")
                    
                    if not category_correct:
                        print(f"     Expected: {email['expected_category']}, Got: {classification.category}")
                    
                except Exception as e:
                    self.log_test(f"AI Classification Test {i}", False, f"Error: {str(e)}")
            
        except Exception as e:
            self.log_test("AI Email Classifier", False, str(e))
    
    def test_email_parsing(self):
        """Test email parsing functionality"""
        print("\n📧 Testing Email Parsing")
        print("-" * 40)
        
        try:
            # Test basic email parsing
            sample_email = {
                'subject': 'Interview Invitation - Senior Developer at TechCorp',
                'from': 'hr@techcorp.com',
                'body': 'Dear Candidate, we would like to schedule an interview for the Senior Developer position at TechCorp.',
                'snippet': 'Interview invitation for Senior Developer position'
            }
            
            parsed_data = parse_interview_email(sample_email)
            
            # Check if parsing extracted basic information
            company_extracted = parsed_data.get('company') is not None
            role_extracted = parsed_data.get('role') is not None
            subject_preserved = parsed_data.get('subject') == sample_email['subject']
            
            self.log_test("Email Parsing - Company", company_extracted, f"Company: {parsed_data.get('company', 'None')}")
            self.log_test("Email Parsing - Role", role_extracted, f"Role: {parsed_data.get('role', 'None')}")
            self.log_test("Email Parsing - Subject", subject_preserved, "Subject preserved correctly")
            
        except Exception as e:
            self.log_test("Email Parsing", False, str(e))
    
    def test_legacy_spam_detection(self):
        """Test legacy spam detection system"""
        print("\n🛡️ Testing Legacy Spam Detection")
        print("-" * 40)
        
        try:
            # Test legitimate email
            legit_email = {
                'subject': 'Interview Invitation - Software Engineer',
                'from': 'recruiter@google.com',
                'body': 'We would like to schedule an interview'
            }
            
            legit_parsed = parse_interview_email(legit_email)
            legit_classification = classify_email(legit_email, legit_parsed)
            
            self.log_test("Spam Detection - Legitimate Email", legit_classification != 'promotional', 
                         f"Classified as: {legit_classification}")
            
            # Test promotional email
            promo_email = {
                'subject': 'Job Alert: 1000+ Jobs Available Now!',
                'from': 'alerts@naukri.com',
                'body': 'Dear Job Seeker, we found 1000+ jobs for you'
            }
            
            promo_parsed = parse_interview_email(promo_email)
            promo_classification = classify_email(promo_email, promo_parsed)
            
            self.log_test("Spam Detection - Promotional Email", promo_classification == 'promotional',
                         f"Classified as: {promo_classification}")
            
            # Test job board spam detection
            is_spam = is_job_board_spam('Naukri', 'alerts@naukri.com')
            self.log_test("Job Board Spam Detection", is_spam, "Naukri alerts correctly identified as spam")
            
        except Exception as e:
            self.log_test("Legacy Spam Detection", False, str(e))
    
    def test_gmail_integration(self):
        """Test Gmail API integration (without actually fetching emails)"""
        print("\n📬 Testing Gmail Integration")
        print("-" * 40)
        
        try:
            # Test if Gmail service can be initialized (may fail if no credentials)
            try:
                service = get_gmail_service()
                if service:
                    self.log_test("Gmail Service Initialization", True, "Gmail service initialized successfully")
                else:
                    self.log_test("Gmail Service Initialization", False, "Service returned None")
            except FileNotFoundError:
                self.log_test("Gmail Service Initialization", False, "credentials.json not found (expected in testing)")
            except Exception as e:
                if "credentials" in str(e).lower():
                    self.log_test("Gmail Service Initialization", False, "Credentials issue (expected in testing)")
                else:
                    raise e
            
        except Exception as e:
            self.log_test("Gmail Integration", False, str(e))
    
    def test_database_analytics(self):
        """Test database analytics and statistics"""
        print("\n📊 Testing Database Analytics")
        print("-" * 40)
        
        try:
            # Test application statistics
            stats = get_application_stats()
            stats_valid = isinstance(stats, dict) and 'total_applications' in stats
            self.log_test("Application Statistics", stats_valid, f"Stats: {stats}")
            
            # Test upcoming interviews
            upcoming = get_upcoming_interviews()
            upcoming_valid = isinstance(upcoming, list)
            self.log_test("Upcoming Interviews", upcoming_valid, f"Found {len(upcoming)} upcoming interviews")
            
        except Exception as e:
            self.log_test("Database Analytics", False, str(e))
    
    def test_database_schema_integrity(self):
        """Test database schema integrity"""
        print("\n🏗️ Testing Database Schema Integrity")
        print("-" * 40)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check applications table structure
            cursor.execute("PRAGMA table_info(applications)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = [
                'id', 'company', 'role', 'status', 'board_stage', 'priority',
                'stage_entered_date', 'date_applied', 'created_at', 'updated_at'
            ]
            
            for col in required_columns:
                has_column = col in column_names
                self.log_test(f"Column '{col}' exists", has_column)
            
            conn.close()
            
        except Exception as e:
            self.log_test("Database Schema Integrity", False, str(e))
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data")
        print("-" * 40)
        
        try:
            if self.test_app_id:
                success = delete_application(self.test_app_id)
                self.log_test("Cleanup Test Application", success, f"Deleted test application {self.test_app_id}")
        except Exception as e:
            self.log_test("Cleanup Test Data", False, str(e))
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting comprehensive test suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing all job tracker functionality...\n")
        
        # Run all test suites
        self.test_database_initialization()
        self.test_database_schema_integrity()
        self.test_application_crud_operations()
        self.test_kanban_board_functionality()
        self.test_ai_email_classifier()
        self.test_email_parsing()
        self.test_legacy_spam_detection()
        self.test_gmail_integration()
        self.test_database_analytics()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed']
        pass_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        
        if self.test_results['failed'] > 0:
            print(f"\n⚠️ FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        print("\n🎯 FUNCTIONALITY STATUS:")
        print("-" * 30)
        
        # Categorize test results
        categories = {
            'Database Operations': ['Database', 'Application', 'Schema'],
            'Kanban Board System': ['Kanban', 'Board', 'Stage', 'Move', 'Note'],
            'AI Classification': ['AI', 'Classification'],
            'Email Processing': ['Email', 'Parsing', 'Spam'],
            'Gmail Integration': ['Gmail'],
            'Analytics & Stats': ['Statistics', 'Analytics', 'Interviews']
        }
        
        for category, keywords in categories.items():
            category_tests = [error for error in self.test_results['errors'] 
                            if any(keyword in error for keyword in keywords)]
            
            if category_tests:
                print(f"⚠️  {category}: {len(category_tests)} issues")
                for test in category_tests[:2]:  # Show first 2 issues
                    print(f"     - {test.split(':')[0]}")
            else:
                print(f"✅ {category}: All tests passed")
        
        print(f"\n🏁 Test Suite Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if pass_rate >= 90:
            print("🎉 EXCELLENT! Your job tracker is working perfectly!")
        elif pass_rate >= 75:
            print("👍 GOOD! Most functionality is working correctly.")
        elif pass_rate >= 50:
            print("⚠️ MODERATE: Some issues need attention.")
        else:
            print("🔧 NEEDS WORK: Several components require fixes.")
        
        print("=" * 60)

def main():
    """Main test execution"""
    print("Job Application Tracker - Comprehensive Test Suite")
    print("Testing all components: Database, AI, Kanban, Email Processing, Gmail Integration")
    print()
    
    # Verify we're in the right directory
    if not os.path.exists('jobs.db'):
        print("⚠️ Warning: jobs.db not found. Some tests may fail.")
        print("Make sure you're running from the project directory.")
    
    # Create and run tester
    tester = JobTrackerTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()