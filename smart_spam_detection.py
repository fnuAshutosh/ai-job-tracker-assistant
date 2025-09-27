"""
Intelligent spam detection for job-related emails
"""

import re
from typing import Dict, Any, List

def is_promotional_email(email_data: Dict[str, Any]) -> bool:
    """
    Determine if an email is promotional/spam vs legitimate interview email.
    
    Args:
        email_data: Parsed email data
        
    Returns:
        bool: True if email is likely promotional/spam
    """
    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    from_email = email_data.get('from', '').lower()
    
    # Strong spam indicators
    spam_indicators = [
        # Mass marketing phrases
        'unsubscribe', 'click here to apply', 'apply now', 'thousands of jobs',
        'job alert', 'job recommendation', 'similar jobs', 'job match',
        'career opportunities', 'new job openings', 'job search',
        
        # Promotional language
        'walk-in interview', 'walk in interview', 'mass hiring', 'bulk hiring',
        'immediate hiring', 'urgent hiring', 'hiring drive',
        
        # Generic templates
        'dear candidate', 'dear job seeker', 'dear applicant',
        'congratulations! you are eligible', 'your profile matches',
        
        # Newsletter/update indicators
        'newsletter', 'weekly update', 'job digest', 'career newsletter'
    ]
    
    # Count spam indicators
    spam_score = 0
    content = f"{subject} {body}"
    
    for indicator in spam_indicators:
        if indicator in content:
            spam_score += 1
    
    # Strong legitimate indicators
    legitimate_indicators = [
        # Personal communication
        'dear ' + extract_name_from_email(from_email), 'hi there', 'hello',
        'thank you for applying', 'thank you for your interest',
        'we would like to schedule', 'please confirm your availability',
        'looking forward to speaking with you',
        
        # Specific scheduling
        'zoom link', 'meeting link', 'calendar invite', 'interview scheduled for',
        'please join us at', 'interview confirmation',
        
        # Company-specific communication
        'from our hr team', 'hiring manager', 'recruiting team'
    ]
    
    legitimate_score = 0
    for indicator in legitimate_indicators:
        if indicator in content:
            legitimate_score += 1
    
    # Decision logic
    if spam_score >= 3:  # Multiple spam indicators
        return True
    if legitimate_score >= 2:  # Multiple legitimate indicators
        return False
    if spam_score > legitimate_score:
        return True
    
    return False

def extract_name_from_email(email: str) -> str:
    """Extract name from email for personalization check"""
    if '@' in email:
        local_part = email.split('@')[0]
        return local_part.replace('.', ' ').replace('_', ' ')
    return ''

def is_job_board_spam(company: str, from_email: str) -> bool:
    """
    Check if email is from job board promotional campaigns
    vs legitimate company communications
    """
    if not company:
        return False
        
    company_lower = company.lower()
    from_lower = from_email.lower()
    
    # Known job board domains (these are promotional)
    job_board_domains = [
        'naukri.com', 'shine.com', 'monster.com', 'timesjobs.com',
        'foundit.in', 'glassdoor.com', 'indeed.com'
    ]
    
    # If company matches job board name AND email is from that domain
    job_board_names = ['naukri', 'shine', 'monster', 'timesjobs', 'foundit', 'glassdoor', 'indeed']
    
    if company_lower in job_board_names:
        for domain in job_board_domains:
            if domain in from_lower:
                return True  # This is a job board promotional email
    
    return False

def has_actual_interview_details(email_data: Dict[str, Any], parsed_data: Dict[str, Any]) -> bool:
    """
    Check if email contains actual interview scheduling details
    vs generic promotional content
    """
    content = f"{email_data.get('subject', '')} {email_data.get('body', '')}".lower()
    
    # Specific interview details
    specific_details = [
        # Time/date specifics
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
        'tomorrow', 'next week', 'this week',
        'am', 'pm', ':', 'zoom', 'teams', 'meet', 'call',
        
        # Interview process specifics
        'technical round', 'hr round', 'final round', 'phone screen',
        'coding interview', 'system design', 'behavioral interview',
        
        # Scheduling language
        'please confirm', 'available on', 'reschedule', 'calendar'
    ]
    
    detail_count = sum(1 for detail in specific_details if detail in content)
    
    # Check if we found actual dates
    has_dates = len(parsed_data.get('interview_dates', [])) > 0
    
    # Legitimate if has specific details AND dates
    return detail_count >= 3 or has_dates

def classify_email(email_data: Dict[str, Any], parsed_data: Dict[str, Any]) -> str:
    """
    Classify email as: 'legitimate', 'promotional', or 'uncertain'
    """
    # Check various spam indicators
    is_promo = is_promotional_email(email_data)
    is_job_board = is_job_board_spam(parsed_data.get('company', ''), email_data.get('from', ''))
    has_details = has_actual_interview_details(email_data, parsed_data)
    
    if is_job_board or is_promo:
        return 'promotional'
    elif has_details:
        return 'legitimate'
    else:
        return 'uncertain'

if __name__ == "__main__":
    # Test cases
    test_emails = [
        {
            'subject': 'Interview Invitation - Software Engineer at Google',
            'body': 'Hi John, Thank you for applying to Google. We would like to schedule a technical interview for tomorrow at 2:00 PM. Please confirm your availability.',
            'from': 'recruiter@google.com'
        },
        {
            'subject': 'Job Alert: 500+ Software Developer Jobs',  
            'body': 'Dear Job Seeker, Check out thousands of jobs. Click here to apply now! Unsubscribe here.',
            'from': 'alerts@naukri.com'
        }
    ]
    
    for i, email in enumerate(test_emails, 1):
        classification = classify_email(email, {'company': 'Google', 'interview_dates': []})
        print(f"Email {i}: {classification}")
        print(f"Subject: {email['subject'][:50]}...")
        print()