"""
Simple test version to verify API key interface
"""

import streamlit as st
from user_api_keys import show_api_key_setup

# Page config
st.set_page_config(
    page_title="API Key Test",
    page_icon="🔑"
)

st.title("🔑 API Key Setup Test")

# Test the API key setup interface directly
st.markdown("### Testing the API Key Setup Interface")

# Call the function directly to see if it displays
has_key = show_api_key_setup()

# Show the result
if has_key:
    st.success("✅ API key is configured!")
    
    # Show what's in session state
    st.markdown("### Session State Contents:")
    if 'user_gemini_key' in st.session_state:
        st.write("Gemini key length:", len(st.session_state.user_gemini_key))
        st.write("Key starts with:", st.session_state.user_gemini_key[:10] + "...")
    else:
        st.write("No Gemini key in session state")
        
else:
    st.info("💡 Please enter a Gemini API key above to test")

# Debug session state
st.markdown("---")
st.markdown("### Full Session State Debug")
st.json({k: f"{str(v)[:50]}..." if len(str(v)) > 50 else v for k, v in st.session_state.items()})