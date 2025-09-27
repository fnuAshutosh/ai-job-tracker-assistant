"""
Compare AI Classification vs Old Hardcoded Rules
Demonstrates the improvement of AI-powered email classification over rule-based approach.
"""

from ai_email_classifier import GeminiEmailClassifier
from smart_spam_detection import classify_email, is_job_board_spam
from parser_utils import parse_interview_email

def compare_classification_approaches():
    """Compare AI vs rule-based classification on sample emails"""
    
    # Initialize AI classifier
    print("🤖 Initializing AI Classifier...")
    ai_classifier = GeminiEmailClassifier()
    
    # Test emails
    test_emails = [
        {
            'subject': 'Interview Invitation - Senior Software Engineer at Google',
            'from': 'recruiter@google.com',
            'body': '''Hi John,

I hope this email finds you well. We were impressed with your application for the Senior Software Engineer position at Google.

We would like to invite you for a technical interview. Are you available Tuesday, October 1st at 2:00 PM PST for a video call via Google Meet?

Please confirm your availability.

Best regards,
Sarah Chen
Technical Recruiter, Google'''
        },
        {
            'subject': 'Job Alert: 1000+ Software Developer Jobs Available Now!',
            'from': 'alerts@naukri.com',
            'body': '''Dear Job Seeker,

Great news! We found 1000+ jobs matching your profile:

🎯 Software Developer - Multiple Companies
🎯 Full Stack Engineer - Remote Options
🎯 DevOps Engineer - Top Startups

Click here to apply now!
Get instant job alerts on your phone.

Unsubscribe | Update Preferences'''
        },
        {
            'subject': 'Application Status Update - Data Scientist Role',
            'from': 'hr@startup.ai',
            'body': '''Hello,

Thank you for your interest in the Data Scientist position at StartupAI.

Your application is currently under review by our technical team. We will update you on the next steps within 2-3 business days.

Best regards,
HR Team
StartupAI'''
        }
    ]
    
    print("\n" + "="*80)
    print("📊 CLASSIFICATION COMPARISON")
    print("="*80)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Test Email {i}:")
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Body preview: {email['body'][:100]}...")
        
        # Old approach - parse then classify
        parsed_data = parse_interview_email(email)
        old_classification = classify_email(email, parsed_data)
        is_spam = is_job_board_spam(parsed_data.get('company', ''), email.get('from', ''))
        
        # New AI approach
        ai_result = ai_classifier.classify_email(email)
        
        print(f"\n🔧 OLD RULE-BASED APPROACH:")
        print(f"   Classification: {old_classification}")
        print(f"   Is Job Board Spam: {is_spam}")
        print(f"   Parsed Company: {parsed_data.get('company', 'None')}")
        print(f"   Parsed Role: {parsed_data.get('role', 'None')}")
        
        print(f"\n🤖 NEW AI APPROACH:")
        print(f"   Category: {ai_result.category}")
        print(f"   Confidence: {ai_result.confidence:.2f}")
        print(f"   Company: {ai_result.company or 'None'}")
        print(f"   Role: {ai_result.role or 'None'}")
        print(f"   Interview Scheduled: {ai_result.interview_scheduled}")
        print(f"   Status Suggestion: {ai_result.status_suggestion}")
        print(f"   Reasoning: {ai_result.reasoning[:100]}...")
        
        print("-" * 50)
    
    print(f"\n✅ Comparison Complete!")
    print(f"💡 Key Benefits of AI Approach:")
    print(f"   • More accurate category classification")
    print(f"   • Better company and role extraction") 
    print(f"   • Confidence scoring for reliability")
    print(f"   • Context-aware reasoning")
    print(f"   • Adaptable to new email patterns")

if __name__ == "__main__":
    compare_classification_approaches()