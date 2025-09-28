"""
Landing page for the Job Tracker Assistant
Provides initial user experience with privacy disclaimers and consent flow
"""

import streamlit as st
from privacy_components import (
    show_privacy_disclaimer,
    show_data_destruction_warning,
    show_consent_flow,
    show_session_status,
    show_privacy_footer
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
    Show Gmail connection onboarding flow
    """
    st.markdown("""
    ## 📧 Connect Your Gmail Account
    
    ### What Happens Next:
    1. **OAuth Login**: Secure Google authentication popup
    2. **Permission Grant**: You'll grant read-only access to your Gmail
    3. **Email Analysis**: We'll scan for job-related emails in memory
    4. **Results Display**: See your organized job applications and interviews
    5. **Automatic Cleanup**: All data destroyed when you close the tab
    """)
    
    # Security reassurance
    st.success("""
    🔒 **Security Promise**: We use Google's official OAuth 2.0 system. 
    Your Gmail password is never shared with us. You can revoke access anytime 
    from your Google Account settings.
    """)
    
    # Warning about data destruction
    st.warning("""
    ⚠️ **Important**: Your data will be permanently deleted when you:
    - Close this browser tab
    - Navigate to a different website  
    - Your session times out
    - You manually disconnect Gmail
    
    This cannot be undone and is by design for your privacy.
    """)
    
    if st.button("🔗 **I Understand - Connect Gmail**", type="primary", use_container_width=True):
        return True
    
    if st.button("⬅️ Back to Options"):
        st.session_state.show_landing = True
        st.rerun()
    
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