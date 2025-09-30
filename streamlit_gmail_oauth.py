"""
Streamlit-friendly Gmail OAuth implementation
Addresses popup limitations with a better user experience
"""

import streamlit as st
import json
import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64

def get_oauth_config():
    """Load OAuth configuration from credentials.json"""
    try:
        with open('credentials.json', 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        st.error(f"❌ **Error loading credentials:** {str(e)}")
        return None

def create_streamlit_friendly_oauth():
    """
    Create OAuth flow that works well with Streamlit limitations
    """
    config = get_oauth_config()
    if not config:
        return None
        
    try:
        # Create flow - use the redirect URI from credentials.json
        redirect_uri = config['installed']['redirect_uris'][0]  # Use configured redirect URI
        flow = Flow.from_client_config(
            config,
            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            redirect_uri=redirect_uri
        )
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return flow, auth_url
        
    except Exception as e:
        st.error(f"❌ **OAuth setup error:** {str(e)}")
        return None, None

def show_streamlit_oauth_interface():
    """
    Show a Streamlit-friendly OAuth interface that works around popup limitations
    """
    
    st.markdown("## 🔐 **Gmail Authentication**")
    
    # Step 1: Create the OAuth flow
    if 'gmail_oauth_flow' not in st.session_state:
        flow, auth_url = create_streamlit_friendly_oauth()
        if flow and auth_url:
            st.session_state.gmail_oauth_flow = flow
            st.session_state.gmail_auth_url = auth_url
        else:
            st.error("❌ **Failed to initialize OAuth flow**")
            return False
    
    # Step 2: Display authentication options
    auth_url = st.session_state.gmail_auth_url
    
    # Create a prominent, easy-to-use interface
    st.markdown("### 🚀 **Ready to Connect Your Gmail**")
    
    # Option 1: Direct link button (most reliable)
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <a href="{auth_url}" target="_blank" style="
            background-color: #4285f4;
            color: white;
            padding: 18px 36px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            display: inline-block;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        ">🔗 Open Google Authentication</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Option 2: Copy-paste URL for users who prefer it
    with st.expander("🔧 **Alternative: Copy & Paste URL**"):
        st.text_area(
            "Copy this URL and paste in a new browser tab:",
            value=auth_url,
            height=100,
            key="oauth_url_copy"
        )
    
    # Step 3: Instructions
    st.markdown("---")
    st.info("""
    **📋 After clicking the link above:**
    
    1. **🔐 Sign in** to your Google account
    2. **🔑 Click "Allow"** to grant Gmail permissions  
    3. **📋 Copy the authorization code** from the result page
    4. **🔄 Return here** and paste the code below
    """)
    
    # Step 4: Code input
    st.markdown("### 📝 **Enter Authorization Code**")
    
    auth_code = st.text_input(
        "Paste the code from Google:",
        placeholder="4/0AX4XfWj...",
        key="gmail_auth_code_input",
        help="After authenticating with Google, you'll see a code to copy and paste here"
    )
    
    # Step 5: Complete authentication
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("✅ **Complete Authentication**", type="primary", use_container_width=True):
            if auth_code:
                if complete_streamlit_oauth(auth_code):
                    st.success("🎉 **Gmail Connected Successfully!**")
                    st.balloons()
                    
                    # Clean up session state
                    del st.session_state.gmail_oauth_flow
                    del st.session_state.gmail_auth_url
                    
                    st.rerun()
                else:
                    st.error("❌ **Authentication failed.** Please check your code and try again.")
            else:
                st.warning("⚠️ **Please enter the authorization code first.**")
    
    # Cancel option
    if st.button("❌ Cancel OAuth"):
        del st.session_state.gmail_oauth_flow
        del st.session_state.gmail_auth_url
        st.info("OAuth flow cancelled.")
        st.rerun()
    
    return True

def complete_streamlit_oauth(auth_code):
    """
    Complete the OAuth flow with the authorization code
    """
    try:
        flow = st.session_state.gmail_oauth_flow
        
        # Exchange code for credentials
        flow.fetch_token(code=auth_code)
        
        # Store credentials in session
        credentials = flow.credentials
        st.session_state.gmail_authenticated = True
        st.session_state.gmail_credentials = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        return True
        
    except Exception as e:
        st.error(f"❌ **OAuth completion error:** {str(e)}")
        return False

def is_gmail_authenticated():
    """Check if Gmail is authenticated"""
    return st.session_state.get('gmail_authenticated', False)

def get_gmail_credentials():
    """Get stored Gmail credentials"""
    if is_gmail_authenticated():
        creds_dict = st.session_state.get('gmail_credentials')
        if creds_dict:
            return Credentials(
                token=creds_dict['token'],
                refresh_token=creds_dict['refresh_token'],
                token_uri=creds_dict['token_uri'],
                client_id=creds_dict['client_id'],
                client_secret=creds_dict['client_secret'],
                scopes=creds_dict['scopes']
            )
    return None

def show_gmail_status():
    """Show current Gmail authentication status"""
    if is_gmail_authenticated():
        st.success("✅ **Gmail Connected**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Your Gmail account is successfully connected!")
        with col2:
            if st.button("🔌 Disconnect"):
                disconnect_gmail()
                st.rerun()
    else:
        st.warning("⚠️ **Gmail Not Connected**")
        if st.button("🔗 Connect Gmail", type="primary"):
            return show_streamlit_oauth_interface()
    
    return is_gmail_authenticated()

def disconnect_gmail():
    """Disconnect Gmail and clear credentials"""
    keys_to_remove = [
        'gmail_authenticated',
        'gmail_credentials',
        'gmail_oauth_flow', 
        'gmail_auth_url',
        'gmail_auth_code_input'
    ]
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("🔌 **Gmail disconnected**")

# Main interface function
def streamlit_gmail_oauth():
    """
    Main function to handle Gmail OAuth in Streamlit
    Returns True if authenticated, False otherwise
    """
    
    if is_gmail_authenticated():
        return show_gmail_status()
    else:
        return show_streamlit_oauth_interface()

if __name__ == "__main__":
    # Test the OAuth interface
    st.title("🧪 **Gmail OAuth Test**")
    streamlit_gmail_oauth()