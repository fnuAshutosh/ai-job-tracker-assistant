#!/usr/bin/env python3
"""
Fix for Gmail OAuth hanging issue in Streamlit
This creates a streamlit-safe OAuth flow
"""

import streamlit as st
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

def get_gmail_service_streamlit_safe():
    """
    Streamlit-safe version of Gmail authentication
    Returns service if already authenticated, otherwise shows OAuth instructions
    """
    
    # Check if we already have valid credentials
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            if creds and creds.valid:
                return build('gmail', 'v1', credentials=creds)
            elif creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                # Save refreshed credentials
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            st.error(f"Error with existing credentials: {e}")
    
    # No valid credentials - show OAuth instructions
    st.error("🔐 **Gmail Authentication Required**")
    st.markdown("""
    **To fetch emails from Gmail, you need to complete OAuth authentication:**
    
    1. **Run OAuth setup** in a separate terminal/command prompt:
       ```bash
       python -c "
       from gmail_utils import get_gmail_service
       try:
           service = get_gmail_service()
           print('[SUCCESS] Gmail authentication completed!')
       except Exception as e:
           print(f'[ERROR] {e}')
       "
       ```
    
    2. **Complete the OAuth flow** in your browser
    3. **Refresh this page** after authentication is complete
    
    **Alternative**: Use demo data instead of real Gmail integration.
    """)
    
    return None

def safe_fetch_interview_emails(service, max_results=50):
    """
    Safe wrapper for fetching emails that won't hang Streamlit
    """
    if not service:
        st.warning("Gmail service not available. Please complete authentication first.")
        return []
    
    try:
        with st.spinner("Fetching emails from Gmail..."):
            # Import the original function
            from gmail_utils import fetch_interview_emails
            return fetch_interview_emails(service, max_results)
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        st.info("💡 **Tip**: Make sure you've completed Gmail OAuth authentication in a separate terminal first.")
        return []

if __name__ == "__main__":
    st.title("🧪 Gmail OAuth Test")
    
    st.markdown("### Test Gmail Authentication")
    
    if st.button("Test Gmail Connection"):
        service = get_gmail_service_streamlit_safe()
        
        if service:
            st.success("✅ Gmail service authenticated successfully!")
            
            if st.button("Fetch Sample Emails"):
                emails = safe_fetch_interview_emails(service, max_results=5)
                st.write(f"Fetched {len(emails)} emails")
        else:
            st.error("❌ Gmail authentication required")