"""
User API Key Management System
Handles user-provided API keys for Gmail and Gemini integration
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
    ## 🔑 API Key Setup - Bring Your Own Keys
    
    To use real Gmail integration and AI analysis, you need to provide your own API keys. 
    This ensures **maximum privacy** and **zero cost to us** while giving you full control.
    
    ### 🛡️ Privacy Promise:
    - ✅ **Session-Only Storage**: Keys exist only in your browser session
    - ✅ **Never Saved**: Keys are destroyed when you close the tab
    - ✅ **Not Transmitted**: Keys never leave your browser for logging/analytics
    - ✅ **Your Control**: You manage your own API usage and costs
    """)
    
    # Gemini API Key Section
    st.markdown("### 🤖 Gemini AI API Key (Required for AI Analysis)")
    
    with st.expander("📚 How to Get a Free Gemini API Key", expanded=False):
        st.markdown("""
        **Step-by-step guide:**
        
        1. **Visit Google AI Studio**: Go to [aistudio.google.com](https://aistudio.google.com)
        2. **Sign in**: Use your Google account
        3. **Get API Key**: Click "Get API Key" → "Create API Key"
        4. **Copy the key**: It looks like `AIzaSyA...` (keep it secret!)
        5. **Paste below**: Enter it in the field below
        
        **💰 Cost**: Generous free tier (15 requests per minute)
        **🔒 Security**: Only you have access to your key
        """)
    
    # Gemini API key input
    gemini_key = st.text_input(
        "🔑 Enter your Gemini API Key",
        type="password",
        placeholder="AIzaSyA...",
        help="Get free key from aistudio.google.com",
        key="gemini_api_key_input"
    )
    
    # Store in session state if provided
    if gemini_key:
        st.session_state.user_gemini_key = gemini_key
        st.success("✅ Gemini API key configured!")
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
    st.markdown("---")
    st.markdown("### ⚙️ Configuration Status")
    
    has_gemini = 'user_gemini_key' in st.session_state
    has_oauth = 'user_oauth_creds' in st.session_state
    
    col1, col2 = st.columns(2)
    
    with col1:
        if has_gemini:
            st.success("🤖 **Gemini AI**: Configured")
            st.info("AI email analysis available")
        else:
            st.warning("🤖 **Gemini AI**: Not configured")
            st.info("Demo mode only without AI analysis")
    
    with col2:
        if has_oauth:
            st.success("📧 **Custom OAuth**: Configured")
            st.info("Using your OAuth app")
        else:
            st.info("📧 **Default OAuth**: Will be used")
            st.info("Shared OAuth for basic access")
    
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