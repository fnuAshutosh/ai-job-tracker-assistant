"""
Final OAuth solution - uses localhost redirect URI properly
"""

import streamlit as st
import json
from google_auth_oauthlib.flow import Flow
from urllib.parse import urlparse, parse_qs

def create_localhost_oauth_flow():
    """
    Create OAuth flow using the localhost redirect URI from credentials.json
    """
    try:
        with open('credentials.json', 'r') as f:
            client_config = json.load(f)
        
        # Use the configured redirect URI (should be http://localhost)
        redirect_uri = client_config['installed']['redirect_uris'][0]
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            redirect_uri=redirect_uri
        )
        
        return flow, redirect_uri
        
    except Exception as e:
        st.error(f"❌ OAuth setup error: {str(e)}")
        return None, None

def show_localhost_oauth_solution():
    """
    OAuth solution that works with localhost redirect URI
    """
    
    st.markdown("## 🔐 Gmail OAuth (Localhost Solution)")
    
    if 'localhost_oauth_flow' not in st.session_state:
        flow, redirect_uri = create_localhost_oauth_flow()
        
        if not flow:
            return False
            
        # Generate authorization URL
        try:
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            st.session_state.localhost_oauth_flow = flow
            st.session_state.localhost_auth_url = auth_url
            st.session_state.localhost_redirect_uri = redirect_uri
            
        except Exception as e:
            st.error(f"❌ Error generating auth URL: {str(e)}")
            return False
    
    # Display the OAuth interface
    auth_url = st.session_state.localhost_auth_url
    redirect_uri = st.session_state.localhost_redirect_uri
    
    st.success("✅ OAuth flow ready!")
    
    # Authentication instructions
    st.markdown("### 🚀 Authentication Steps")
    
    st.markdown(f"""
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4>🔗 Step 1: Click to Authenticate</h4>
        <a href="{auth_url}" target="_blank" style="
            background-color: #4285f4;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            display: inline-block;
            margin: 10px 0;
        ">🔐 Authenticate with Google</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Method selection
    method = st.radio(
        "**Choose your method:**",
        [
            "📋 I'll copy the authorization code (Recommended)",
            "🔗 I'll copy the full redirect URL"
        ],
        key="oauth_method"
    )
    
    if "authorization code" in method:
        st.info("""
        **After clicking the link above:**
        1. 🔐 Sign in to your Google account
        2. ✅ Grant Gmail permissions
        3. 📋 **Copy the authorization code** from the result page
        4. 📝 Paste it below
        """)
        
        auth_code = st.text_input(
            "📝 Authorization Code:",
            placeholder="4/0AX4XfWj...",
            key="localhost_auth_code",
            help="The code Google shows after you grant permissions"
        )
        
        if st.button("✅ Complete with Code", type="primary") and auth_code:
            if complete_localhost_oauth_with_code(auth_code):
                st.success("🎉 Gmail Connected!")
                st.balloons()
                cleanup_oauth_session()
                return True
            else:
                st.error("❌ Failed. Please check the code and try again.")
    
    else:
        st.info(f"""
        **After clicking the link above:**
        1. 🔐 Sign in to your Google account
        2. ✅ Grant Gmail permissions
        3. 🔗 **Copy the entire URL** from your browser address bar
        4. 📝 Paste it below
        
        The URL will start with: `{redirect_uri}?code=...`
        """)
        
        full_url = st.text_input(
            "🔗 Full Redirect URL:",
            placeholder=f"{redirect_uri}?code=4/0AX4XfWj...",
            key="localhost_full_url",
            help="Copy the complete URL from your browser after authentication"
        )
        
        if st.button("✅ Complete with URL", type="primary") and full_url:
            if complete_localhost_oauth_with_url(full_url):
                st.success("🎉 Gmail Connected!")
                st.balloons()
                cleanup_oauth_session()
                return True
            else:
                st.error("❌ Failed. Please check the URL and try again.")
    
    # Cancel option
    if st.button("❌ Cancel OAuth"):
        cleanup_oauth_session()
        st.info("OAuth cancelled.")
        st.rerun()
    
    return False

def complete_localhost_oauth_with_code(auth_code):
    """Complete OAuth using authorization code"""
    try:
        flow = st.session_state.localhost_oauth_flow
        flow.fetch_token(code=auth_code)
        store_gmail_credentials(flow.credentials)
        return True
    except Exception as e:
        st.error(f"Code authentication error: {str(e)}")
        return False

def complete_localhost_oauth_with_url(full_url):
    """Complete OAuth using full redirect URL"""
    try:
        # Parse the URL to extract the authorization code
        parsed_url = urlparse(full_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            st.error("❌ No authorization code found in URL")
            return False
        
        auth_code = query_params['code'][0]
        return complete_localhost_oauth_with_code(auth_code)
        
    except Exception as e:
        st.error(f"URL parsing error: {str(e)}")
        return False

def store_gmail_credentials(credentials):
    """Store Gmail credentials in session"""
    st.session_state.gmail_authenticated = True
    st.session_state.gmail_credentials = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def cleanup_oauth_session():
    """Clean up OAuth session variables"""
    keys = ['localhost_oauth_flow', 'localhost_auth_url', 'localhost_redirect_uri', 
            'localhost_auth_code', 'localhost_full_url']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

if __name__ == "__main__":
    st.title("🔧 Localhost OAuth Solution")
    show_localhost_oauth_solution()