"""
Session-based Gmail integration
Handles Gmail OAuth and email fetching with session-only storage
"""

import streamlit as st
import os
import json
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# OAuth 2.0 configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'  # For installed app flow

# Default OAuth credentials (you can replace with your own)
DEFAULT_CLIENT_CONFIG = {
    "web": {
        "client_id": "your-default-client-id.apps.googleusercontent.com",
        "client_secret": "your-default-client-secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

def get_oauth_config():
    """Get OAuth configuration (user's or default)"""
    user_creds = st.session_state.get('user_oauth_creds')
    if user_creds:
        return user_creds
    return DEFAULT_CLIENT_CONFIG

def start_gmail_oauth():
    """
    Start Gmail OAuth flow
    Returns authorization URL for user to visit
    """
    try:
        client_config = get_oauth_config()
        
        # Create flow
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store flow in session for later use
        st.session_state.oauth_flow = flow
        
        return auth_url
        
    except Exception as e:
        st.error(f"❌ OAuth setup failed: {e}")
        return None

def complete_gmail_oauth(auth_code: str):
    """
    Complete OAuth flow with authorization code
    Returns True if successful
    """
    try:
        if 'oauth_flow' not in st.session_state:
            st.error("❌ OAuth flow not found. Please restart the process.")
            return False
        
        flow = st.session_state.oauth_flow
        
        # Exchange authorization code for credentials
        flow.fetch_token(code=auth_code)
        
        # Store credentials in session
        credentials = flow.credentials
        st.session_state.gmail_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Mark as authenticated
        st.session_state.gmail_authenticated = True
        
        # Clean up flow
        del st.session_state.oauth_flow
        
        return True
        
    except Exception as e:
        st.error(f"❌ OAuth completion failed: {e}")
        return False

def get_gmail_service():
    """
    Get authenticated Gmail service
    Returns Gmail API service object
    """
    if not st.session_state.get('gmail_authenticated', False):
        return None
    
    creds_data = st.session_state.get('gmail_credentials')
    if not creds_data:
        return None
    
    try:
        # Create credentials from session data
        credentials = Credentials.from_authorized_user_info(creds_data, SCOPES)
        
        # Refresh token if needed
        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update session with new token
                st.session_state.gmail_credentials.update({
                    'token': credentials.token
                })
            else:
                st.error("❌ Gmail credentials expired. Please re-authenticate.")
                st.session_state.gmail_authenticated = False
                return None
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        return service
        
    except Exception as e:
        st.error(f"❌ Gmail service creation failed: {e}")
        st.session_state.gmail_authenticated = False
        return None

def show_gmail_oauth_flow():
    """
    Show Gmail OAuth authentication flow
    Returns True if successfully authenticated
    """
    if st.session_state.get('gmail_authenticated', False):
        st.success("✅ **Gmail Connected!** You can now fetch your emails.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 **Start Fetching Emails**", type="primary"):
                return True
        
        with col2:
            if st.button("🔒 **Disconnect Gmail**"):
                disconnect_gmail()
                st.rerun()
        
        return False
    
    # Start OAuth flow
    st.markdown("### 🔐 Gmail Authentication")
    
    if st.button("🚀 **Start Gmail Authentication**", type="primary"):
        auth_url = start_gmail_oauth()
        
        if auth_url:
            st.markdown(f"""
            ### 📋 Authentication Steps:
            
            1. **Click the link below** to open Gmail authentication:
            
            🔗 **[Authenticate with Gmail]({auth_url})**
            
            2. **Grant permissions** in the popup window
            3. **Copy the authorization code** you receive
            4. **Paste it below** and click Complete
            """)
            
            # Input for authorization code
            auth_code = st.text_input(
                "📝 Enter Authorization Code:",
                placeholder="Paste the code from Google here...",
                key="gmail_auth_code"
            )
            
            if st.button("✅ **Complete Authentication**") and auth_code:
                if complete_gmail_oauth(auth_code):
                    st.success("🎉 **Gmail Connected Successfully!**")
                    st.rerun()
    
    return False

def disconnect_gmail():
    """Disconnect Gmail and clear session data"""
    # Clear Gmail-related session data
    gmail_keys = [
        'gmail_authenticated',
        'gmail_credentials', 
        'oauth_flow',
        'gmail_auth_code'
    ]
    
    for key in gmail_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("🔒 Gmail disconnected. All authentication data cleared from session.")

def fetch_session_emails(max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail using session credentials
    Returns list of email data
    """
    service = get_gmail_service()
    if not service:
        st.error("❌ Gmail not connected. Please authenticate first.")
        return []
    
    try:
        # Search for job-related emails
        query = 'subject:(interview OR application OR position OR job OR hiring OR recruiter)'
        
        # Get message list
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            st.info("📧 No job-related emails found with current search criteria.")
            return []
        
        # Fetch full message details
        emails = []
        for message in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            emails.append(msg_data)
        
        return emails
        
    except Exception as e:
        st.error(f"❌ Error fetching emails: {e}")
        return []