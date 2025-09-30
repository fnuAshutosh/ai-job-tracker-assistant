"""
Streamlit-native OAuth flow implementation
Better approach that works within Streamlit's limitations
"""

import streamlit as st
import webbrowser
import threading
import time
from urllib.parse import urlparse, parse_qs

def show_streamlit_native_oauth(auth_url):
    """
    Streamlit-native OAuth implementation that works better with browser limitations
    """
    
    st.markdown("### 🔐 **Google Authentication Required**")
    
    # Create three columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Primary authentication button
        if st.button("🚀 **Open Google Authentication**", type="primary", use_container_width=True):
            # Show the URL in an expandable section
            with st.expander("🔗 **Authentication URL** (click to expand)", expanded=True):
                st.code(auth_url, language="text")
                st.markdown(f"[🔐 **Click here to authenticate →**]({auth_url})")
    
    # Show instructions in a nice format
    st.markdown("---")
    
    # Create tabs for different approaches
    tab1, tab2, tab3 = st.tabs(["📱 **Quick Steps**", "🖥️ **Desktop Users**", "📋 **Manual Copy**"])
    
    with tab1:
        st.markdown("""
        ### 📱 **Mobile/Quick Method:**
        1. **Tap the authentication button** above
        2. **Tap the link** in the expandable section  
        3. **Complete Google sign-in**
        4. **Copy the code** and return here
        """)
        
    with tab2:
        st.markdown(f"""
        ### 🖥️ **Desktop Users:**
        1. **Right-click** [this link]({auth_url}) and select "Open in new tab"
        2. **Complete authentication** in the new tab
        3. **Copy the authorization code**
        4. **Return to this tab** and paste below
        """)
        
    with tab3:
        st.markdown("""
        ### 📋 **Manual Copy Method:**
        1. **Click the button above** to reveal the URL
        2. **Copy the URL** from the code box
        3. **Paste in new browser tab** and navigate
        4. **Complete authentication** and copy code
        """)
    
    return True

def show_qr_code_oauth(auth_url):
    """
    Alternative: Show QR code for mobile users
    """
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(auth_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        st.markdown("### 📱 **QR Code Alternative**")
        st.markdown(f'<img src="data:image/png;base64,{img_str}" width="200">', unsafe_allow_html=True)
        st.markdown("**Scan with your phone** to open OAuth in mobile browser")
        
        return True
        
    except ImportError:
        st.info("💡 **Tip:** Install `qrcode` package for QR code authentication option")
        return False

def create_oauth_instructions():
    """
    Create comprehensive OAuth instructions
    """
    
    st.markdown("### 🎯 **How OAuth Works Here**")
    
    st.info("""
    **Due to Streamlit's security model, we can't open popups automatically.**
    
    But don't worry! The process is still simple:
    """)
    
    # Create visual steps
    steps = [
        ("1️⃣", "**Click Authentication Button**", "Opens the OAuth URL in an expandable section"),
        ("2️⃣", "**Open in New Tab**", "Click/copy the link to open Google authentication"),
        ("3️⃣", "**Authorize Access**", "Sign in and grant Gmail permissions"),  
        ("4️⃣", "**Copy Code**", "Google will show you an authorization code"),
        ("5️⃣", "**Paste & Complete**", "Return here and paste the code below")
    ]
    
    for emoji, title, desc in steps:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"## {emoji}")
        with col2:
            st.markdown(f"**{title}**")
            st.markdown(desc)
    
    st.success("✨ **This approach works reliably across all browsers and devices!**")

def enhanced_oauth_flow(auth_url):
    """
    Enhanced OAuth flow with multiple options and better UX
    """
    
    # Header
    st.markdown("## 🔐 **Gmail Authentication**")
    
    # Show different options in tabs
    tab1, tab2, tab3 = st.tabs(["🚀 **Quick Auth**", "📱 **QR Code**", "ℹ️ **Help**"])
    
    with tab1:
        show_streamlit_native_oauth(auth_url)
        
    with tab2:
        if not show_qr_code_oauth(auth_url):
            st.markdown(f"**Manual link:** [Authenticate with Google]({auth_url})")
            
    with tab3:
        create_oauth_instructions()
    
    return True