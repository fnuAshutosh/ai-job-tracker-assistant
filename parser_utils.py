"""
Email parsing utilities for extracting company names and dates from interview emails.
Uses various heuristics to identify relevant information from email content.
"""

import re
import email.utils
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import dateparser
from dateutil import parser as dateutil_parser


def extract_dates(text: str, reference_date: Optional[datetime] = None) -> List[datetime]:
    """
    Extract interview dates and times from email text.
    
    Args:
        text: Email body or subject text
        reference_date: Reference date for relative parsing (defaults to now)
        
    Returns:
        List[datetime]: List of detected dates/times
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    dates = []
    
    # Common date/time patterns in interview emails
    patterns = [
        # Explicit dates: "Monday, January 15th at 2:00 PM"
        r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?\s+at\s+\d{1,2}:\d{2}\s*(?:am|pm)',
        
        # Dates with time: "January 15, 2024 at 2:00 PM"
        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s*(?:am|pm)',
        
        # Short format: "Jan 15 at 2:00 PM"
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}\s+at\s+\d{1,2}:\d{2}\s*(?:am|pm)',
        
        # Relative dates: "tomorrow at", "next Monday at"
        r'(?:tomorrow|next\s+(?:monday|tuesday|wednesday|thursday|friday))\s+at\s+\d{1,2}:\d{2}\s*(?:am|pm)',
        
        # Time ranges: "between 2:00-3:00 PM on January 15"
        r'between\s+\d{1,2}:\d{2}\s*(?:am|pm)?\s*-\s*\d{1,2}:\d{2}\s*(?:am|pm)\s+on\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
        
        # ISO format: "2024-01-15T14:00:00"
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
    ]
    
    text_lower = text.lower()
    
    # Extract potential date strings using patterns
    potential_dates = []
    for pattern in patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            potential_dates.append(match.group())
    
    # Also look for standalone date-like strings
    # This catches more natural language dates
    words = text.split()
    for i, word in enumerate(words):
        if any(month in word.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
            # Take the word and a few surrounding words as potential date string
            context_start = max(0, i - 3)
            context_end = min(len(words), i + 4)
            potential_date = ' '.join(words[context_start:context_end])
            potential_dates.append(potential_date)
    
    # Parse each potential date string
    for date_str in potential_dates:
        try:
            # Try dateparser first (handles natural language)
            parsed_date = dateparser.parse(
                date_str,
                settings={
                    'RELATIVE_BASE': reference_date,
                    'PREFER_DATES_FROM': 'future',
                    'RETURN_AS_TIMEZONE_AWARE': False
                }
            )
            
            if parsed_date and parsed_date > reference_date - timedelta(days=1):  # Only future dates (with small buffer)
                dates.append(parsed_date)
                
        except (ValueError, TypeError):
            # Try dateutil as fallback
            try:
                parsed_date = dateutil_parser.parse(date_str, fuzzy=True)
                if parsed_date and parsed_date > reference_date - timedelta(days=1):
                    dates.append(parsed_date)
            except (ValueError, TypeError):
                continue
    
    # Remove duplicates and sort
    unique_dates = list(set(dates))
    unique_dates.sort()
    
    return unique_dates


def extract_company_from_email(from_header: str) -> Optional[str]:
    """
    Extract company name from email 'From' header.
    
    Args:
        from_header: Email From header (e.g., "John Doe <john@company.com>")
        
    Returns:
        str: Extracted company name or None
    """
    if not from_header:
        return None
    
    # Parse email address
    try:
        parsed = email.utils.parseaddr(from_header)
        email_address = parsed[1] if parsed[1] else from_header
        
        # Extract domain
        domain = email_address.split('@')[-1] if '@' in email_address else email_address
        
        # Remove common email providers
        common_providers = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
            'aol.com', 'icloud.com', 'protonmail.com', 'zoho.com'
        }
        
        if domain.lower() in common_providers:
            return None
        
        # Clean up domain to get company name
        # Remove www, .com, etc.
        company = domain.lower()
        company = re.sub(r'^www\.', '', company)
        company = re.sub(r'\.(com|org|net|edu|gov|co\.uk|co|io|ai|tech)$', '', company)
        
        # Capitalize properly
        return company.replace('_', ' ').replace('-', ' ').title()
        
    except Exception:
        return None


def extract_company_from_text(subject: str, body: str) -> Optional[str]:
    """
    Extract company name from email subject and body using pattern matching.
    
    Args:
        subject: Email subject line
        body: Email body text
        
    Returns:
        str: Extracted company name or None
    """
    full_text = f"{subject} {body}".lower()
    
    # Patterns to look for company mentions
    patterns = [
        r'interview\s+(?:with|at)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+team|\s+for|\s+on|\s+scheduled|\.|\n|$)',
        r'(?:from|at)\s+([A-Z][a-zA-Z\s&]+?)\s+(?:team|company|corporation|inc|llc)',
        r'([A-Z][a-zA-Z\s&]+?)\s+interview\s+(?:invitation|scheduled|confirmation)',
        r'position\s+at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+for|\s+in|\s+as|\.|\n|$)',
        r'opportunity\s+at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+for|\s+in|\s+as|\.|\n|$)',
        r'role\s+at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+for|\s+in|\s+as|\.|\n|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            company = match.group(1).strip()
            
            # Clean up the company name
            company = re.sub(r'\s+', ' ', company)  # Multiple spaces to single space
            company = company.title()
            
            # Filter out common false positives
            false_positives = {
                'The', 'A', 'An', 'This', 'That', 'Your', 'Our', 'My', 'His', 'Her',
                'Team', 'Interview', 'Phone', 'Video', 'Zoom', 'Call', 'Meeting',
                'Position', 'Role', 'Opportunity', 'Job', 'Application'
            }
            
            if company not in false_positives and len(company) > 2:
                return company
    
    return None


def extract_company(from_header: str, subject: str, body: str) -> Optional[str]:
    """
    Extract company name using multiple strategies.
    
    Args:
        from_header: Email From header
        subject: Email subject line
        body: Email body text
        
    Returns:
        str: Best guess company name or None
    """
    # Strategy 1: Extract from email domain
    company_from_email = extract_company_from_email(from_header)
    if company_from_email:
        return company_from_email
    
    # Strategy 2: Extract from email content
    company_from_text = extract_company_from_text(subject, body)
    if company_from_text:
        return company_from_text
    
    # Strategy 3: Fallback to domain extraction even from common providers
    if from_header and '@' in from_header:
        try:
            parsed = email.utils.parseaddr(from_header)
            email_address = parsed[1] if parsed[1] else from_header
            domain = email_address.split('@')[-1]
            
            # For common providers, try to find company in display name
            if domain.lower() in ['gmail.com', 'yahoo.com', 'outlook.com']:
                display_name = parsed[0] if parsed[0] else ''
                # Look for company mentions in display name
                if 'recruiter' in display_name.lower():
                    # Extract company before "recruiter"
                    parts = display_name.lower().split('recruiter')[0].strip()
                    if parts:
                        return parts.title()
            else:
                # Use domain as fallback
                company = domain.lower()
                company = re.sub(r'^www\.', '', company)
                company = re.sub(r'\.(com|org|net|edu|gov|co\.uk|co|io)$', '', company)
                return company.replace('_', ' ').replace('-', ' ').title()
                
        except Exception:
            pass
    
    return None


def extract_job_role(subject: str, body: str) -> Optional[str]:
    """
    Extract job role/position from email content.
    
    Args:
        subject: Email subject line
        body: Email body text
        
    Returns:
        str: Extracted job role or None
    """
    full_text = f"{subject} {body}".lower()
    
    # Patterns for role extraction
    patterns = [
        r'(?:for\s+the\s+|for\s+)([a-zA-Z\s]+?)(?:\s+position|\s+role|\s+interview)',
        r'(?:software|senior|junior|principal|lead|staff)\s+([a-zA-Z\s]+?)(?:\s+position|\s+role|\s+interview)',
        r'position:\s*([a-zA-Z\s]+?)(?:\n|$|\.)',
        r'role:\s*([a-zA-Z\s]+?)(?:\n|$|\.)',
        r'([a-zA-Z\s]+?)(?:\s+engineer|\s+developer|\s+analyst|\s+manager|\s+director)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            role = match.group(1).strip()
            role = re.sub(r'\s+', ' ', role)  # Clean up spaces
            role = role.title()
            
            # Filter out noise words
            if len(role) > 2 and role.lower() not in ['the', 'this', 'your', 'our']:
                return role
    
    return None


def parse_interview_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse interview email and extract relevant information.
    
    Args:
        email_data: Email data from Gmail API
        
    Returns:
        Dict: Parsed interview information
    """
    parsed = {
        'message_id': email_data.get('message_id'),
        'subject': email_data.get('subject', ''),
        'from': email_data.get('from', ''),
        'date_received': email_data.get('date', ''),
        'snippet': email_data.get('snippet', ''),
        'body': email_data.get('body', ''),
        'company': None,
        'role': None,
        'interview_dates': [],
        'source': 'gmail'
    }
    
    # Extract company
    parsed['company'] = extract_company(
        email_data.get('from', ''),
        email_data.get('subject', ''),
        email_data.get('body', '')
    )
    
    # Extract job role
    parsed['role'] = extract_job_role(
        email_data.get('subject', ''),
        email_data.get('body', '')
    )
    
    # Extract interview dates
    text_content = f"{email_data.get('subject', '')} {email_data.get('body', '')}"
    parsed['interview_dates'] = extract_dates(text_content)
    
    return parsed


if __name__ == "__main__":
    # Test the parsing functions
    test_email = {
        'message_id': 'test123',
        'subject': 'Interview with Google - Software Engineer Position',
        'from': 'John Recruiter <john@google.com>',
        'date': '2024-01-10',
        'snippet': 'We would like to schedule an interview...',
        'body': 'Hi there! We would like to schedule a technical interview for the Senior Software Engineer position at Google. Are you available on Monday, January 15th at 2:00 PM? Please let us know your availability.'
    }
    
    result = parse_interview_email(test_email)
    
    print("Parsed Interview Email:")
    print(f"Company: {result['company']}")
    print(f"Role: {result['role']}")
    print(f"Interview Dates: {result['interview_dates']}")
    print(f"From: {result['from']}")
    print(f"Subject: {result['subject']}")