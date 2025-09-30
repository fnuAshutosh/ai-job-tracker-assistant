"""
Landing page for the Job Tracker Assistant
Provides initial user experience with privacy disclaimers and consent flo      # Import Gma    with col1:
        if st.button("🔗 **Connect Gmail Account**", type="primary", use_container_width=True):
            # Use the fixed OAuth solution that handles redirect URI properly
            try:
                from localhost_oauth_solution import show_localhost_oauth_solution
                return show_localhost_oauth_solution()
            except ImportError:
                # Fallback to original OAuth if new module isn't available
                st.error("❌ OAuth module not found. Please check your installation.")
                return FalseOAuth functionality
    from session_gmail import show_gmail_oauth_flow
    
    # Show Gmail OAuth flow
    gmail_connected = show_gmail_oauth_flow()
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.show_landing = True
            st.rerun()
    
    # Return True if Gmail is connected and user wants to proceed
    return gmail_connectedol1:
        if st.button("🔗 **Connect Gmail Account**", type="primary", use_container_width=True):
            return Trueith col1:
        if st.button("🔗 **Connect Gmail Account**", type="primary", use_container_width=True):
            return True"""

import streamlit as st
from privacy_components import (
    show_privacy_disclaimer,
    show_data_destruction_warning,
    show_consent_flow,
    show_session_status,
    show_privacy_footer
)
from user_api_keys import (
    show_api_key_setup,
    initialize_key_system,
    get_user_gemini_key
)

def show_landing_page():
    """
    Display the landing page with privacy information and consent flow
    Returns True if user is ready to proceed
    """
    # Add the exit warning script
    show_data_destruction_warning()
    
    # Show main privacy disclaimer
    show_privacy_disclaimer()
    
    # Get consent
    consent_given = show_consent_flow()
    
    if consent_given:
        st.markdown("---")
        
        # Show app options
        st.markdown("""
        ## 🚀 Choose Your Experience
        
        You can start with either mode and switch anytime:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📧 **Connect My Gmail**", use_container_width=True, type="primary"):
                st.session_state.user_choice = "gmail"
                st.session_state.show_landing = False
                st.rerun()
        
        with col2:
            if st.button("🎭 **Try Demo First**", use_container_width=True):
                st.session_state.user_choice = "demo"
                st.session_state.show_landing = False
                st.rerun()
        
        # Comparison table
        st.markdown("""
        ### 📊 Mode Comparison
        
        | Feature | Demo Mode | Gmail Mode |
        |---------|-----------|------------|
        | **Data Source** | Sample job data | Your real emails |
        | **Privacy** | No personal data | Session-only processing |
        | **Features** | All features available | All features available |
        | **Setup Time** | Instant | 30 seconds (OAuth) |
        | **Data Persistence** | None | None (deleted on exit) |
        """)
        
        return True
    
    return False

def show_gmail_onboarding():
    """
    Show Gmail connection onboarding flow with API key setup
    """
    st.markdown("""
    ## 📧 Connect Your Gmail Account
    
    To use real Gmail integration, you need to provide your own API keys. 
    This ensures maximum privacy and gives you full control over your data and costs.
    """)
    
    # API Key Setup
    has_gemini_key = show_api_key_setup()
    
    if not has_gemini_key:
        st.markdown("---")
        st.info("""
        👆 **Please enter your Gemini API key above** to continue with Gmail integration.
        
        Your API key enables AI-powered email analysis while keeping your data completely private.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Try Demo Mode Instead", use_container_width=True):
                st.session_state.user_choice = "demo"
                st.session_state.demo_mode = True
                st.rerun()
        with col2:
            if st.button("🔄 Refresh Page", use_container_width=True):
                st.rerun()
        
        return False
    
    # If API key is configured, proceed with Gmail setup
    st.markdown("---")
    st.success("🎉 **Step 1 Complete!** Your API key is configured.")
    st.markdown("## 🚀 Step 2: Connect Gmail")
    
    st.info("""
    **Next:** Click the button below to securely connect your Gmail account.
    
    • Google's official OAuth system (your password stays safe)
    • Read-only access to find job-related emails
    • All data deleted when you close this tab
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("� **Connect Gmail Account**", type="primary", use_container_width=True):
            return True
    
    with col2:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.show_landing = True
            st.rerun()
    
    # Additional info in expander
    with st.expander("🔒 Privacy & Security Details"):
        st.markdown("""
        **What happens when you connect:**
        1. **OAuth popup** opens (Google's secure login)
        2. **Grant permission** for read-only Gmail access
        3. **Email scan** finds job application emails
        4. **AI analysis** using your Gemini API key
        5. **Results display** in organized dashboard
        
        **Security promises:**
        - ✅ Official Google OAuth (your password never shared)
        - ✅ Read-only access (we can't send emails)
        - ✅ Session-only data (deleted when tab closes)
        - ✅ Your API costs (~$0.001 per email)
        
        **You can revoke access anytime** from your Google Account settings.
        """)
    
    return False

def show_demo_onboarding():
    """
    Show demo mode onboarding
    """
    st.markdown("""
    ## 🎭 Demo Mode
    
    ### What You'll See:
    ✅ **Sample Job Applications**: Realistic examples of job tracking  
    ✅ **Interview Scheduling**: See how upcoming interviews are organized  
    ✅ **AI Classification**: Experience our email categorization  
    ✅ **Full Functionality**: All features work with demo data  
    
    ### Privacy in Demo Mode:
    🔒 **No Personal Data**: Only pre-built sample data is used  
    🧹 **No Cleanup Needed**: Nothing personal to delete  
    📧 **Switch Anytime**: Connect Gmail later if you want real data  
    """)
    
    st.info("""
    💡 **Tip**: Demo mode is perfect for exploring features before 
    deciding to connect your Gmail account.
    """)
    
    if st.button("🚀 **Start Demo Experience**", type="primary", use_container_width=True):
        st.session_state.gmail_authenticated = False
        st.session_state.demo_mode = True
        return True
    
    if st.button("⬅️ Back to Options"):
        st.session_state.show_landing = True
        st.rerun()
    
    return False

def initialize_landing_state():
    """Initialize session state for landing page flow"""
    if 'show_landing' not in st.session_state:
        st.session_state.show_landing = True
    if 'user_choice' not in st.session_state:
        st.session_state.user_choice = None
    if 'gmail_authenticated' not in st.session_state:
        st.session_state.gmail_authenticated = False
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    
    # Initialize API key system
    initialize_key_system()