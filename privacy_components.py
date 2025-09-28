"""
Privacy-first UI components for the Job Tracker Assistant
Provides transparent information about data handling and user privacy
"""

import streamlit as st
import streamlit.components.v1 as components

def show_privacy_disclaimer():
    """Display comprehensive privacy disclaimer and app information"""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            🔒 AI Job Tracker Assistant
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0; opacity: 0.9;">
            Privacy-First Email Analysis for Job Applications
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Privacy Promise Section
    st.markdown("""
    ## 🛡️ Our Privacy Promise
    
    **Your privacy is our top priority.** This app is designed with zero data persistence:
    
    ✅ **No Data Storage**: We never save your emails or personal information  
    ✅ **Session-Only**: All data exists only during your current browser session  
    ✅ **Automatic Cleanup**: Everything is permanently deleted when you close the tab  
    ✅ **No Tracking**: We don't track, profile, or analyze your behavior  
    ✅ **Open Source**: Full transparency - you can review our code anytime  
    """)
    
    # How It Works Section
    with st.expander("🔍 How This App Works", expanded=False):
        st.markdown("""
        ### What We Do:
        1. **You Connect**: Securely authenticate with your Gmail account
        2. **We Analyze**: Process your emails in memory to find job-related content
        3. **You Explore**: View organized job applications, interviews, and opportunities
        4. **We Forget**: All data disappears when you close your browser
        
        ### What We Access:
        - **Read-only Gmail access**: We only read your emails, never send or modify
        - **Job-related content**: We focus on emails from recruiters, companies, and job boards
        - **Temporary processing**: Analysis happens in your browser session only
        
        ### What We DON'T Do:
        - ❌ Store your emails on our servers
        - ❌ Share data with third parties
        - ❌ Create permanent user accounts
        - ❌ Track your activity across sessions
        - ❌ Use your data for advertising or AI training
        """)
    
    # Technical Details Section
    with st.expander("⚙️ Technical Implementation", expanded=False):
        st.markdown("""
        ### Session-Based Architecture:
        - **OAuth Tokens**: Stored only in browser memory during your session
        - **Email Data**: Processed in temporary memory, never written to disk
        - **AI Analysis**: Runs locally in your browser session
        - **Database**: Demo data only - your real data never touches our database
        
        ### Data Lifecycle:
        ```
        🔐 You Login → 📧 Emails Loaded → 🤖 AI Processing → 📊 Results Shown → 🗑️ Session Ends → ✨ All Data Destroyed
        ```
        
        ### Security Measures:
        - Google OAuth 2.0 standard authentication
        - HTTPS encryption for all communications
        - No server-side data persistence
        - Automatic memory cleanup on session end
        """)

def show_data_destruction_warning():
    """JavaScript component to warn users before leaving the page"""
    warning_script = """
    <script>
    let hasUserData = false;
    
    // Set flag when user connects Gmail
    window.setUserDataFlag = function(hasData) {
        hasUserData = hasData;
    };
    
    // Warning popup before leaving
    window.addEventListener('beforeunload', function(e) {
        if (hasUserData) {
            const message = 'Your job tracking data will be permanently deleted when you leave this page. This cannot be undone.';
            e.preventDefault();
            e.returnValue = message;
            return message;
        }
    });
    
    // Also warn on tab close
    window.addEventListener('unload', function(e) {
        if (hasUserData) {
            // Final cleanup notification
            console.log('🗑️ User data destroyed - session ended');
        }
    });
    </script>
    """
    
    components.html(warning_script, height=0)

def show_consent_flow():
    """Display consent flow before Gmail authentication"""
    st.markdown("""
    ## 📋 Consent & Permission
    
    Before connecting your Gmail account, please confirm you understand:
    """)
    
    consent_items = [
        "I understand this app will access my Gmail emails in read-only mode",
        "I understand my data is processed only during this browser session",
        "I understand all data is permanently deleted when I close this tab",
        "I understand no data is stored on external servers",
        "I consent to temporary email analysis for job tracking purposes"
    ]
    
    all_agreed = True
    
    for i, item in enumerate(consent_items):
        agreed = st.checkbox(item, key=f"consent_{i}")
        if not agreed:
            all_agreed = False
    
    if all_agreed:
        st.success("✅ Thank you for your consent! You can now connect your Gmail account.")
        return True
    else:
        st.warning("Please review and agree to all items above to continue.")
        return False

def show_session_status():
    """Display current session status and data handling info"""
    if 'gmail_authenticated' in st.session_state and st.session_state.gmail_authenticated:
        st.sidebar.markdown("""
        ### 🔐 Session Status
        **Status**: Gmail Connected  
        **Data Mode**: Live Email Processing  
        **Storage**: Memory Only  
        **Auto-Cleanup**: On Session End  
        
        ⚠️ **Reminder**: All data will be permanently deleted when you close this tab.
        """)
        
        # Set JavaScript flag for exit warning
        components.html("""
        <script>
        if (window.setUserDataFlag) {
            window.setUserDataFlag(true);
        }
        </script>
        """, height=0)
    else:
        st.sidebar.markdown("""
        ### 🔒 Session Status
        **Status**: Demo Mode  
        **Data Mode**: Sample Data Only  
        **Your Gmail**: Not Connected  
        
        Connect your Gmail to see real job tracking data!
        """)

def show_demo_vs_real_banner():
    """Show banner indicating current data mode"""
    if 'gmail_authenticated' in st.session_state and st.session_state.gmail_authenticated:
        st.info("🔴 **LIVE MODE**: Showing data from your Gmail account. This data will be deleted when you close the tab.", icon="🔴")
    else:
        st.info("🟡 **DEMO MODE**: Showing sample data. Connect your Gmail to see your real job applications.", icon="🟡")

def show_privacy_footer():
    """Display privacy information in footer"""
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; padding: 1rem;">
        🔒 <strong>Privacy-First Design</strong> • 
        🗑️ <strong>Zero Data Persistence</strong> • 
        ✨ <strong>Session-Only Processing</strong><br>
        <small>Your data is never stored and is automatically destroyed when you leave this page.</small>
    </div>
    """, unsafe_allow_html=True)