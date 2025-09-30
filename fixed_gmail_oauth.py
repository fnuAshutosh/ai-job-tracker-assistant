"""
Fixed Gmail OAuth implementation that properly handles redirect URIs
Addresses the "invalid_request" error by using correct OAuth flow
"""

import streamlit as st
import json
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

def get_redirect_uri_from_credentials():
    """
    Get the correct redirect URI from credentials.json
    """
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds and 'redirect_uris' in creds['installed']:
            redirect_uris = creds['installed']['redirect_uris']
            
            # Prefer localhost if available, otherwise use first URI
            for uri in redirect_uris:
                if 'localhost' in uri:
                    return uri
            
            return redirect_uris[0]
        
        return None
        
    except Exception as e:
        st.error(f"Error reading credentials.json: {e}")
        return None

def create_oauth_flow():
    """
    Create OAuth flow with proper configuration
    """
    try:
        with open('credentials.json', 'r') as f:
            client_config = json.load(f)
        
        redirect_uri = get_redirect_uri_from_credentials()
        
        if not redirect_uri:
            st.error("❌ No valid redirect URI found in credentials.json")
            return None
        
        # For localhost redirects, we need to handle this as a web flow
        if 'localhost' in redirect_uri:
            # Use out-of-band flow instead for Streamlit compatibility
            redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            redirect_uri=redirect_uri
        )
        
        return flow
        
    except Exception as e:
        st.error(f"❌ OAuth flow creation error: {str(e)}")
        return None

def show_fixed_oauth_flow():
    """
    Show OAuth flow with proper error handling and redirect URI management
    """
    
    st.markdown("## 🔐 Gmail Authentication (Fixed)")
    
    # Check if flow is already started
    if 'fixed_oauth_flow' not in st.session_state:
        
        # Create OAuth flow
        flow = create_oauth_flow()
        if not flow:
            st.error("❌ Failed to create OAuth flow. Please check credentials.json")
            return False
        
        # Generate authorization URL
        try:
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            st.session_state.fixed_oauth_flow = flow
            st.session_state.fixed_auth_url = auth_url
            
        except Exception as e:
            st.error(f"❌ Error generating auth URL: {str(e)}")
            return False
    
    # Display authentication interface
    auth_url = st.session_state.fixed_auth_url
    
    st.success("✅ OAuth flow created successfully!")
    
    # Show the authentication URL
    st.markdown("### 🚀 Step 1: Authenticate with Google")
    
    # Primary authentication link
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0; padding: 20px; background: #f0f8ff; border-radius: 10px;">
        <h4>🔗 Click to Authenticate:</h4>
        <a href="{auth_url}" target="_blank" style="
            background-color: #4285f4;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            display: inline-block;
            margin: 10px;
        ">🔐 Authenticate with Google</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Troubleshooting section
    with st.expander("🔧 Troubleshooting OAuth Errors"):
        st.markdown(f"""
        **If you see "invalid_request" error:**
        
        1. **Check the URL**: Make sure it starts with `https://accounts.google.com/o/oauth2/auth`
        2. **Verify credentials**: Your credentials.json should be for the correct project
        3. **Redirect URI**: Currently using out-of-band flow to avoid redirect issues
        
        **Current OAuth URL:**
        ```
        {auth_url[:100]}...
        ```
        
        **Configured redirect**: `urn:ietf:wg:oauth:2.0:oob` (out-of-band)
        """)
    
    # Step 2: Code input
    st.markdown("---")
    st.markdown("### 📝 Step 2: Enter Authorization Code")
    
    st.info("""
    **After clicking the link above:**
    1. Sign in to your Google account
    2. Grant Gmail read permissions
    3. Copy the authorization code shown
    4. Paste it below
    """)
    
    auth_code = st.text_input(
        "Authorization Code:",
        placeholder="Paste the code from Google here...",
        key="fixed_auth_code"
    )
    
    # Complete authentication
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Complete Authentication", type="primary") and auth_code:
            if complete_fixed_oauth(auth_code):
                st.success("🎉 Gmail Connected Successfully!")
                st.balloons()
                
                # Cleanup
                del st.session_state.fixed_oauth_flow
                del st.session_state.fixed_auth_url
                
                return True
            else:
                st.error("❌ Authentication failed. Please try again.")
    
    with col2:
        if st.button("❌ Cancel"):
            del st.session_state.fixed_oauth_flow
            del st.session_state.fixed_auth_url
            st.info("OAuth cancelled.")
            st.rerun()
    
    return False

def complete_fixed_oauth(auth_code):
    """
    Complete OAuth with the authorization code
    """
    try:
        flow = st.session_state.fixed_oauth_flow
        
        # Exchange code for credentials
        flow.fetch_token(code=auth_code)
        
        # Store credentials
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
        st.error(f"❌ OAuth completion error: {str(e)}")
        return False

def test_credentials_config():
    """
    Test and display current credentials configuration
    """
    st.markdown("## 🔍 Credentials Configuration Test")
    
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
            
            st.success("✅ credentials.json found")
            
            if 'installed' in creds:
                client_id = creds['installed']['client_id']
                redirect_uris = creds['installed'].get('redirect_uris', [])
                
                st.info(f"""
                **Configuration Details:**
                - Client ID: `{client_id[:20]}...`
                - Redirect URIs: `{redirect_uris}`
                - Project ID: `{creds['installed'].get('project_id', 'Not found')}`
                """)
                
                if redirect_uris:
                    for i, uri in enumerate(redirect_uris):
                        if 'localhost' in uri:
                            st.warning(f"⚠️ Redirect URI {i+1}: `{uri}` (localhost - may cause issues)")
                        else:
                            st.info(f"ℹ️ Redirect URI {i+1}: `{uri}`")
                else:
                    st.error("❌ No redirect URIs configured")
            else:
                st.error("❌ credentials.json not in 'installed' format")
                
        except Exception as e:
            st.error(f"❌ Error reading credentials.json: {e}")
    else:
        st.error("❌ credentials.json not found")

if __name__ == "__main__":
    st.title("🔧 Fixed Gmail OAuth Test")
    
    tab1, tab2 = st.tabs(["🔐 OAuth Flow", "🔍 Config Test"])
    
    with tab1:
        show_fixed_oauth_flow()
    
    with tab2:
        test_credentials_config()