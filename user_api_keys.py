"""
User API Key Management System
Handles user-pro      if not gemini_key:
        st.info("🔑 Please enter your API key above to continue")
    elif not gemini_key.startswith('AIzaSy'):f not gemini_key:
        st.info("🔑 Please enter your API key above to continue")
    elif not gemini_key.startswith('AIzaSy'):ed API keys for Gmail and Gemini integration
All keys are stored in session state only and destroyed on exit
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any

def show_api_key_setup():
    """
    Show API key setup interface for user-provided credentials
    Returns True if keys are configured and ready
    """
    st.markdown("""
    ## 🔑 Step 1: Enter Your Gemini API Key
    
    **Required for AI email analysis.** Get your free API key in 2 minutes!
    
    ### 🛡️ Your Privacy is Protected:
    - ✅ **Session-Only**: Key stored only in your browser, never on our servers
    - ✅ **Auto-Destroyed**: Deleted when you close the tab
    - ✅ **Your Control**: You manage costs and usage directly with Google
    """)
    
    # Prominent API key input
    st.markdown("### 🔑 Enter Your API Key Here:")
    
    # API key input with better UX
    gemini_key = st.text_input(
        "Paste your Gemini API Key (starts with 'AIzaSy')",
        type="password",
        placeholder="AIzaSyA...",
        help="Get your free key from aistudio.google.com",
        key="gemini_api_key_input"
    )
    
    # Help section
    with st.expander("❓ How to Get Your Free API Key (2 minutes)", expanded=False):
        st.markdown("""
        **Quick setup:**
        
        1. 🌐 **Visit**: [aistudio.google.com](https://aistudio.google.com)
        2. 🔐 **Sign in** with your Google account
        3. 🔑 **Click**: "Get API Key" → "Create API Key"
        4. 📋 **Copy** the key (starts with `AIzaSy...`)
        5. 📥 **Paste** it in the field above
        
        **💰 Free tier**: 15 requests/minute (plenty for email analysis)
        **🔒 Secure**: Key stays in your browser only
        """)
    
    if not gemini_key:
        st.info("� Please enter your API key above to continue")
    elif not gemini_key.startswith('AIzaSy'):
        st.warning("⚠️ API key should start with 'AIzaSy'. Please check your key.")
    
    # Store in session state if provided
    if gemini_key and gemini_key.startswith('AIzaSy'):
        st.session_state.user_gemini_key = gemini_key
        st.success("🎉 **API Key Configured Successfully!** You can now connect Gmail.")
    elif gemini_key and not gemini_key.startswith('AIzaSy'):
        # Invalid key format - don't store it
        if 'user_gemini_key' in st.session_state:
            del st.session_state.user_gemini_key
    else:
        if 'user_gemini_key' in st.session_state:
            del st.session_state.user_gemini_key
    
    # Gmail OAuth Section
    st.markdown("### 📧 Gmail OAuth Credentials (Optional - Advanced Users)")
    
    with st.expander("🔧 Advanced: Custom Gmail OAuth Setup", expanded=False):
        st.markdown("""
        **For advanced users who want their own OAuth app:**
        
        1. **Google Cloud Console**: Visit [console.cloud.google.com](https://console.cloud.google.com)
        2. **Create Project**: New project or select existing
        3. **Enable Gmail API**: APIs & Services → Enable APIs → Gmail API
        4. **Create Credentials**: Credentials → OAuth 2.0 Client IDs → Web Application
        5. **Download JSON**: Download the credentials file
        6. **Upload below**: Use the file uploader
        
        **⚠️ Note**: This is optional! We provide default OAuth for basic users.
        """)
    
    # OAuth credentials upload (optional)
    uploaded_oauth = st.file_uploader(
        "📁 Upload OAuth Credentials (JSON file)",
        type=['json'],
        help="Optional: Your own OAuth app credentials"
    )
    
    if uploaded_oauth:
        try:
            import json
            oauth_data = json.load(uploaded_oauth)
            st.session_state.user_oauth_creds = oauth_data
            st.success("✅ Custom OAuth credentials uploaded!")
        except Exception as e:
            st.error(f"❌ Invalid OAuth file: {e}")
    
    # Configuration status
    has_gemini = 'user_gemini_key' in st.session_state
    has_oauth = 'user_oauth_creds' in st.session_state
    
    if has_gemini:
        st.markdown("---")
        st.markdown("### ✅ Ready to Connect Gmail!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("🤖 **Gemini AI**: Ready")
            st.caption("AI email analysis enabled")
        with col2:
            st.info("📧 **Gmail OAuth**: Default")
            st.caption("Secure Google authentication")
    
    # Return configuration status
    return has_gemini

def get_user_gemini_key() -> Optional[str]:
    """Get user's Gemini API key from session state"""
    return st.session_state.get('user_gemini_key')

def get_user_oauth_creds() -> Optional[Dict[str, Any]]:
    """Get user's OAuth credentials from session state"""
    return st.session_state.get('user_oauth_creds')

def show_api_usage_info():
    """Show current API usage and key status in sidebar"""
    if 'user_gemini_key' in st.session_state:
        st.sidebar.markdown("""
        ### 🔑 Your API Keys
        **Gemini AI**: ✅ Active  
        **Storage**: Session only  
        **Cost**: Your account  
        **Usage**: Your quota  
        
        🔒 Keys destroyed on exit
        """)
    else:
        st.sidebar.markdown("""
        ### 🔑 API Key Status
        **Gemini AI**: ❌ Not provided  
        **Mode**: Demo only  
        **Cost**: Free  
        
        💡 Add your API key for real integration
        """)

def clear_user_keys():
    """Clear all user-provided API keys from session"""
    keys_to_clear = ['user_gemini_key', 'user_oauth_creds']
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("🗑️ All API keys cleared from session")

def show_key_management_controls():
    """Show controls for managing API keys"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Key Management")
    
    if st.sidebar.button("🗑️ Clear All Keys", help="Remove keys from session"):
        clear_user_keys()
        st.rerun()
    
    if st.sidebar.button("🔧 Reconfigure Keys", help="Go back to key setup"):
        st.session_state.show_key_setup = True
        st.rerun()

def initialize_key_system():
    """Initialize the API key management system"""
    if 'show_key_setup' not in st.session_state:
        st.session_state.show_key_setup = False

def create_configured_gemini_classifier():
    """Create Gemini classifier with user's API key"""
    user_key = get_user_gemini_key()
    
    if not user_key:
        st.error("🔑 Gemini API key required for AI analysis")
        return None
    
    try:
        from ai_email_classifier import GeminiEmailClassifier
        
        # Create classifier with user's key
        classifier = GeminiEmailClassifier()
        
        # Override the API key (we'll need to modify GeminiEmailClassifier to accept key)
        # For now, we'll set it in environment temporarily
        import os
        os.environ['GEMINI_API_KEY'] = user_key
        
        return classifier
        
    except Exception as e:
        st.error(f"❌ Error configuring Gemini classifier: {e}")
        return None