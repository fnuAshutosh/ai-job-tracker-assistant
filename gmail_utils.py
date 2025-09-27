"""
Gmail API integration utilities for job application tracker.
Handles OAuth2 authentication and email fetching for interview-related emails.
"""

import os
import base64
import re
from typing import List, Dict, Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup


# Gmail API scope for readonly access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_gmail_service():
    """
    Authenticate and return Gmail service object using OAuth2.
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated Gmail service
        
    Raises:
        FileNotFoundError: If credentials.json is not found
        Exception: If authentication fails
    """
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials available, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found. Please download it from Google Cloud Console "
                    "and place it in the project root directory."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            
            # Try different OAuth methods based on credentials type
            try:
                # First try the standard desktop flow
                print("🔐 Starting OAuth authentication...")
                print("📋 If browser doesn't open, copy the URL and paste it in your browser")
                creds = flow.run_local_server(
                    port=0,  # Let system choose available port
                    open_browser=True,
                    timeout_seconds=300,  # Give more time for user to authenticate
                    access_type='offline',
                    prompt='consent'  # Force consent screen to ensure we get refresh token
                )
                print("✅ Authentication successful!")
            except Exception as e:
                print(f"⚠️ Local server method failed: {e}")
                print("🔄 Trying alternative authentication method...")
                try:
                    # Fallback to console-based authentication
                    print("📝 Please complete authentication in your browser and paste the authorization code here:")
                    creds = flow.run_console()
                except Exception as e2:
                    print(f"❌ Console method also failed: {e2}")
                    print("\n💡 Troubleshooting:")
                    print("1. Make sure your OAuth consent screen is PUBLISHED (not in Testing)")
                    print("2. Check that Gmail API is enabled in your project")
                    print("3. Verify credentials.json is for Desktop application type")
                    raise Exception(f"OAuth authentication failed. Error: {e}")
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def decode_email_body(payload: Dict[str, Any]) -> str:
    """
    Extract and decode email body from Gmail message payload.
    
    Args:
        payload: Gmail message payload
        
    Returns:
        str: Decoded email body text
    """
    body_text = ""
    
    def extract_text_from_part(part: Dict[str, Any]) -> str:
        """Recursively extract text from email parts."""
        text = ""
        
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        elif part.get('mimeType') == 'text/html':
            data = part.get('body', {}).get('data', '')
            if data:
                html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                # Convert HTML to plain text
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
        elif 'parts' in part:
            # Handle multipart messages
            for subpart in part['parts']:
                text += extract_text_from_part(subpart)
                
        return text
    
    if 'parts' in payload:
        for part in payload['parts']:
            body_text += extract_text_from_part(part)
    else:
        body_text = extract_text_from_part(payload)
    
    return body_text.strip()


def get_header_value(headers: List[Dict[str, str]], name: str) -> str:
    """
    Extract header value from Gmail message headers.
    
    Args:
        headers: List of email headers
        name: Header name to find
        
    Returns:
        str: Header value or empty string if not found
    """
    for header in headers:
        if header.get('name', '').lower() == name.lower():
            return header.get('value', '')
    return ''


def fetch_interview_emails(service, query: str = None, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch interview-related emails from Gmail.
    
    Args:
        service: Authenticated Gmail service
        query: Gmail search query (default: interview-related keywords)
        max_results: Maximum number of emails to fetch
        
    Returns:
        List[Dict]: List of parsed email data
        
    Raises:
        HttpError: If Gmail API request fails
    """
    if query is None:
        # Broader query - let smart spam detection handle filtering
        query = 'subject:(interview OR "phone screen" OR "interview scheduled" OR "technical interview" OR "final interview" OR "onsite interview" OR "video interview" OR "zoom interview" OR "interview invitation" OR "interview confirmed")'
    
    try:
        # Search for messages matching the query
        results = service.users().messages().list(
            userId='me', 
            q=query, 
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print(f"No messages found matching query")
            return []
        
        print(f"Found {len(messages)} potential interview emails")
        
        # Fetch full message details
        interview_emails = []
        
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                payload = message['payload']
                headers = payload.get('headers', [])
                
                # Extract email details
                email_data = {
                    'message_id': msg['id'],
                    'subject': get_header_value(headers, 'Subject'),
                    'from': get_header_value(headers, 'From'),
                    'date': get_header_value(headers, 'Date'),
                    'snippet': message.get('snippet', ''),
                    'body': decode_email_body(payload)
                }
                
                interview_emails.append(email_data)
                
            except HttpError as error:
                print(f"Error fetching message {msg['id']}: {error}")
                continue
        
        print(f"Successfully fetched {len(interview_emails)} interview emails")
        return interview_emails
        
    except HttpError as error:
        print(f"Error searching for messages: {error}")
        raise


def test_gmail_connection():
    """
    Test Gmail API connection and print basic account info.
    """
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()
        print(f"Successfully connected to Gmail!")
        print(f"Email: {profile.get('emailAddress')}")
        print(f"Messages in inbox: {profile.get('messagesTotal', 0)}")
        return True
    except Exception as e:
        print(f"Failed to connect to Gmail: {e}")
        return False


if __name__ == "__main__":
    # Test the Gmail connection
    if test_gmail_connection():
        print("\n" + "="*50)
        print("Testing email fetch...")
        try:
            service = get_gmail_service()
            emails = fetch_interview_emails(service, max_results=5)
            
            print(f"\nFound {len(emails)} interview emails:")
            for i, email in enumerate(emails[:3], 1):  # Show first 3
                print(f"\n{i}. {email['subject']}")
                print(f"   From: {email['from']}")
                print(f"   Date: {email['date']}")
                print(f"   Snippet: {email['snippet'][:100]}...")
                
        except Exception as e:
            print(f"Error during email fetch test: {e}")