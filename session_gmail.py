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
# REDIRECT_URI will be loaded from credentials.json

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
    
    # Try to load from credentials.json
    try:
        if os.path.exists('credentials.json'):
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                
            # Convert "installed" format to "web" format if needed
            if 'installed' in creds:
                return {
                    "web": {
                        "client_id": creds['installed']['client_id'],
                        "client_secret": creds['installed']['client_secret'],
                        "auth_uri": creds['installed']['auth_uri'],
                        "token_uri": creds['installed']['token_uri']
                    }
                }
            elif 'web' in creds:
                return creds
    except Exception as e:
        st.error(f"Error loading credentials.json: {e}")
    
    return DEFAULT_CLIENT_CONFIG

def start_gmail_oauth():
    """
    Start Gmail OAuth flow
    Returns authorization URL for user to visit
    """
    try:
        # Load credentials.json directly to get the correct redirect URI
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Get redirect URI from credentials.json
        redirect_uri = creds['installed']['redirect_uris'][0]
        
        # Create client config in the format Flow expects
        client_config = {
            "installed": {
                "client_id": creds['installed']['client_id'],
                "client_secret": creds['installed']['client_secret'],
                "auth_uri": creds['installed']['auth_uri'],
                "token_uri": creds['installed']['token_uri'],
                "redirect_uris": creds['installed']['redirect_uris']
            }
        }
        
        # Create flow with correct redirect URI
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
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
        st.error(f"Error details: {str(e)}")
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
    
    # Check if OAuth flow is already started
    if 'oauth_flow' in st.session_state:
        # Show the authentication steps
        st.markdown("### 📋 Complete Gmail Authentication")
        
        st.info("""
        **You started the Gmail connection process.**
        
        1. **Click the link below** to authenticate with Google
        2. **Grant permissions** in the popup/new tab
        3. **Copy the authorization code** you receive
        4. **Paste it below** and click Complete
        """)
        
        # Get the auth URL from the stored flow
        flow = st.session_state.oauth_flow
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Create a more prominent button-like link that opens in new tab
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{auth_url}" target="_blank" style="
                background-color: #4285f4;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                display: inline-block;
                font-size: 18px;
                box-shadow: 0 3px 6px rgba(0,0,0,0.2);
                transition: background-color 0.3s;
            " onmouseover="this.style.backgroundColor='#3367d6'" 
               onmouseout="this.style.backgroundColor='#4285f4'">
                🔐 Authenticate with Google
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Input for authorization code
        auth_code = st.text_input(
            "📝 **Enter the Authorization Code:**",
            placeholder="Paste the code from Google here...",
            key="gmail_auth_code",
            help="After clicking the link above and authenticating, you'll receive a code to paste here"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ **Complete Authentication**", type="primary") and auth_code:
                with st.spinner("🔄 Completing authentication..."):
                    if complete_gmail_oauth(auth_code):
                        st.success("🎉 **Gmail Connected Successfully!**")
                        st.balloons()  # Add celebration effect
                        st.rerun()
                    else:
                        st.error("❌ **Authentication failed.** Please try again.")
        
        with col2:
            if st.button("❌ **Cancel**"):
                del st.session_state.oauth_flow
                st.success("OAuth flow cancelled.")
                st.rerun()
    
    else:
        # Start OAuth flow
        st.markdown("### 🔐 Connect Your Gmail")
        
        if st.button("🚀 **Connect Gmail Account**", type="primary", use_container_width=True):
            auth_url = start_gmail_oauth()
            
            if auth_url:
                # Show immediate success message and instructions
                st.success("🎉 **OAuth flow started!** Opening Google authentication...")
                
                # Use Streamlit's native way to open links
                st.markdown(f"""
                ### 🚀 **Google Authentication Required**
                
                **Your authentication link is ready!**
                
                Click the button below to open Google OAuth in a new tab:
                """)
                
                # Streamlit-native approach - prominent link button
                st.markdown("### 🔐 **Click to Authenticate with Google**")
                
                # Use Streamlit's native link functionality with better UX
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
                ">
                    <h3 style="color: white; margin: 0 0 15px 0;">🚀 Ready to Connect!</h3>
                    <a href="{auth_url}" target="_blank" style="
                        background-color: white;
                        color: #4285f4;
                        padding: 15px 40px;
                        text-decoration: none;
                        border-radius: 50px;
                        font-weight: bold;
                        font-size: 18px;
                        display: inline-block;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        transition: all 0.3s ease;
                        border: 2px solid transparent;
                    " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 16px rgba(0,0,0,0.2)'" 
                      onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'">
                        � Authenticate with Google
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Add helpful instructions
                st.info("""
                **📋 Simple Steps:**
                1. **Click the blue button above** - it will open Google authentication in a new tab
                2. **Sign in** to your Google account if needed
                3. **Click "Allow"** to grant Gmail permissions  
                4. **Copy the code** from the success page
                5. **Come back here** and paste it below
                """)
                
                # Alternative text link for users who prefer it
                st.markdown(f"**Prefer a simple link?** [Click here to authenticate →]({auth_url})")
                
                st.markdown("---")
                
                st.info("""
                **After clicking the link above:**
                1. 🔐 **Authenticate** with your Google account
                2. 🔑 **Grant permissions** for Gmail access
                3. 📋 **Copy the authorization code** you receive
                4. 🔄 **Come back here** and paste it below
                """)
                
                st.rerun()  # Refresh to show the auth steps
    
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