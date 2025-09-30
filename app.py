"""
Job Application Tracker - Streamlit UI
Main application interface for tracking job applications and interview emails.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import traceback
from typing import List, Dict, Any

# Import our utility modules
from gmail_utils import get_gmail_service, fetch_interview_emails
from parser_utils import parse_interview_email
from ai_email_classifier import GeminiEmailClassifier
from db_utils import (
    init_db, 
    upsert_application, 
    list_applications, 
    get_upcoming_interviews,
    update_application_status,
    delete_application,
    get_application_stats,
    search_applications
)
from init_demo_database import check_and_initialize_database

# Kanban board functions - defined early to avoid NameError
def main_kanban_view():
    """Kanban board view for visual pipeline management"""
    
    try:
        # Import Kanban functionality
        from kanban_database import get_board_data, move_application_to_stage, BOARD_STAGES
        
        st.markdown("### 🎯 Visual Pipeline - Drag & Drop Job Applications")
        st.info("💡 **Interactive Board**: Click the buttons below each application card to move between stages, add notes, or view details.")
        
        # Board controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            filter_option = st.selectbox("🔍 Filter Applications", 
                                       ["All Applications", "High Priority", "This Week", "Interview Stage"])
        
        with col2:
            if st.button("🔄 Refresh Board", help="Reload the board data"):
                st.rerun()
        
        with col3:
            if st.button("➕ Add Application", help="Add a new job application"):
                st.info("Use the sidebar form to add new applications, then refresh the board to see them here.")
        
        st.markdown("---")
        
        # Get board data
        board_data = get_board_data()
        
        # Create columns for each stage
        columns = st.columns(len(BOARD_STAGES))
        
        # Render each stage column
        for i, (stage_key, stage_info) in enumerate(BOARD_STAGES.items()):
            with columns[i]:
                # Column header
                stage_apps = board_data.get(stage_key, [])
                app_count = len(stage_apps)
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px;
                    border-radius: 12px 12px 0 0;
                    text-align: center;
                    font-weight: bold;
                    margin-bottom: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    {stage_info['name']} ({app_count})
                </div>
                """, unsafe_allow_html=True)
                
                # Applications in this stage
                if stage_apps:
                    for app in stage_apps:
                        create_simple_kanban_card(app, stage_key)
                else:
                    # Empty stage placeholder
                    st.markdown(f"""
                    <div style="
                        padding: 24px;
                        text-align: center;
                        color: #999;
                        border: 2px dashed #ddd;
                        border-radius: 12px;
                        margin: 8px 0;
                        background: #fafafa;
                    ">
                        <p style="margin: 0; font-style: italic;">
                            No applications<br>in {stage_info['name'].lower()}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Board analytics summary
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        total_apps = sum(len(apps) for apps in board_data.values())
        active_apps = sum(len(board_data.get(stage, [])) for stage in ['applied', 'screening', 'interview', 'final'])
        closed_apps = len(board_data.get('closed', []))
        
        with col1:
            st.metric("📊 Total Applications", total_apps)
        with col2:
            st.metric("🎯 Active Pipeline", active_apps)
        with col3:
            st.metric("✅ Completed", closed_apps)
        with col4:
            success_rate = f"{(closed_apps/total_apps*100):.1f}%" if total_apps > 0 else "0%"
            st.metric("📈 Completion Rate", success_rate)
        
    except Exception as e:
        st.error(f"Error loading Kanban board: {e}")
        st.info("💡 Make sure the database has been upgraded for Kanban functionality.")

def create_simple_kanban_card(app, stage):
    """Create a simplified Kanban card for the integrated view"""
    
    # Calculate days in current stage
    import datetime
    stage_entered = app.get('stage_entered_date')
    if stage_entered:
        try:
            entered_date = datetime.datetime.fromisoformat(stage_entered.replace('Z', '+00:00'))
            days_in_stage = (datetime.datetime.now() - entered_date).days
        except:
            days_in_stage = 0
    else:
        days_in_stage = 0
    
    # Determine card styling
    priority = app.get('priority', 'medium')
    if days_in_stage > 14:
        card_color = "#ffebee"
        border_color = "#f44336"
    elif priority == 'high':
        card_color = "#fff3e0"
        border_color = "#ff9800" 
    else:
        card_color = "#f5f5f5"
        border_color = "#9e9e9e"
    
    # Create the card
    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid {border_color}; 
            border-radius: 8px; 
            padding: 12px; 
            margin: 8px 0; 
            background-color: {card_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: #333;">
                    {app.get('company', 'Unknown')}
                </h5>
                <small style="color: #666;">#{app.get('id', '000')}</small>
            </div>
            <p style="margin: 4px 0 8px 0; color: #555; font-size: 13px;">
                {app.get('role', 'Unknown Role')[:30]}{'...' if len(str(app.get('role', ''))) > 30 else ''}
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <small style="color: #888;">
                    📅 {app.get('date_applied', 'Unknown')[:10] if app.get('date_applied') else 'Unknown'}
                </small>
                <small style="color: #888;">
                    ⏱️ {days_in_stage}d
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("➡️", key=f"simple_move_{app['id']}", help="Move to next stage"):
                move_to_next_stage_simple(app, stage)
        
        with col2:
            if st.button("✏️", key=f"simple_edit_{app['id']}", help="Edit details"):
                st.info(f"Editing {app['company']} - use the main list view for detailed editing")
        
        with col3:
            if st.button("👁️", key=f"simple_view_{app['id']}", help="View details"):
                show_simple_app_details(app)

def move_to_next_stage_simple(app, current_stage):
    """Simplified stage movement for integrated view"""
    from kanban_database import move_application_to_stage
    
    stage_order = ['backlog', 'applied', 'screening', 'interview', 'final', 'closed']
    
    try:
        current_idx = stage_order.index(current_stage)
        if current_idx < len(stage_order) - 1:
            next_stage = stage_order[current_idx + 1]
            move_application_to_stage(app['id'], next_stage, f"Moved via Kanban board")
            st.success(f"✅ Moved {app['company']} forward!")
            st.rerun()
        else:
            st.warning("Application is in the final stage")
    except Exception as e:
        st.error(f"Error: {e}")

def show_simple_app_details(app):
    """Show simple application details in an expander"""
    
    with st.expander(f"📋 {app['company']} - {app['role']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Company:**", app.get('company', 'N/A'))
            st.write("**Role:**", app.get('role', 'N/A'))
            st.write("**Priority:**", app.get('priority', 'medium').title())
            st.write("**Source:**", app.get('source', 'manual').title())
        
        with col2:
            st.write("**Applied:**", app.get('date_applied', 'N/A')[:10] if app.get('date_applied') else 'N/A')
            st.write("**Status:**", app.get('status', 'applied').title())
            if app.get('interview_date'):
                st.write("**Interview:**", app.get('interview_date')[:16])
        
        if app.get('notes'):
            st.markdown("**Notes:**")
            st.text(app['notes'])

# Page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database on app start with demo data if needed
if 'db_initialized' not in st.session_state:
    # Check and initialize database with demo data
    demo_created = check_and_initialize_database()
    init_db()  # Ensure all tables exist
    st.session_state.db_initialized = True
    
    if demo_created:
        st.success("🎭 Welcome! Demo database created with sample applications to explore the features.")

# Main title
st.title("💼 Job Application Tracker")

# Navigation selector in sidebar
view_mode = st.sidebar.radio("� View Mode", ["List View", "Kanban Board"], index=0)

if view_mode == "Kanban Board":
    main_kanban_view()
else:
    # Continue with original list view
    st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.header("🎯 Actions")
    
    # Gmail integration section
    st.subheader("📧 Gmail Integration")
    
    if st.button("🔄 Fetch Interview Emails", help="Fetch new interview emails from Gmail"):
        try:
            # Use safe Gmail service that won't hang Streamlit
            from gmail_streamlit_safe import get_gmail_service_streamlit_safe, safe_fetch_interview_emails
            
            service = get_gmail_service_streamlit_safe()
            
            if service:
                # Initialize AI classifier
                ai_classifier = GeminiEmailClassifier()
                
                # Fetch interview emails using safe method
                emails = safe_fetch_interview_emails(service, max_results=50)
                
                if emails:
                    st.success(f"Found {len(emails)} interview emails!")
                    
                    # Parse and store emails
                    processed_count = 0
                    for email in emails:
                        try:
                            # Parse email content
                            parsed_data = parse_interview_email(email)
                            
                            # Use AI-powered email classification
                            ai_classification = ai_classifier.classify_email(email)
                            
                            if ai_classification.category == 'promotional':
                                print(f"Skipping promotional email: {parsed_data['subject'][:50]}...")
                                continue
                            elif ai_classification.category == 'other':
                                print(f"Skipping non-job-related email: {parsed_data['subject'][:50]}...")
                                continue
                            
                            # Log what we're processing
                            print(f"Processing {ai_classification.category} email: {parsed_data['company']} - {parsed_data['role']}")
                            
                            # Use AI suggestion for status, with fallback to hardcoded logic
                            status = ai_classification.status_suggestion if ai_classification.status_suggestion else 'applied'
                            email_content_lower = f"{parsed_data['subject']} {parsed_data['body']}".lower()
                            
                            # Check for actual interview scheduling keywords
                            if any(keyword in email_content_lower for keyword in [
                                'interview scheduled', 'interview confirmed', 'interview invitation',
                                'please join', 'zoom link', 'meeting link', 'interview tomorrow',
                                'interview on', 'interview at', 'confirmed interview'
                            ]) and parsed_data['interview_dates']:
                                status = 'interview_scheduled'
                            elif any(keyword in email_content_lower for keyword in [
                                'congratulations', 'offer', 'selected', 'hired'
                            ]):
                                status = 'offer'
                            elif any(keyword in email_content_lower for keyword in [
                                'rejected', 'unfortunately', 'not selected', 'not moving forward'
                            ]):
                                status = 'rejected'
                            elif any(keyword in email_content_lower for keyword in [
                                'screening', 'phone screen', 'initial call'
                            ]):
                                status = 'interview_scheduled'
                            
                            # Prepare database record - prefer AI-extracted data when available
                            record = {
                                'msg_id': parsed_data['message_id'],
                                'company': ai_classification.company or parsed_data['company'],
                                'role': ai_classification.role or parsed_data['role'],
                                'source': 'gmail',
                                'status': status,
                                'snippet': parsed_data['snippet'],
                                'email_subject': parsed_data['subject'],
                                'email_from': parsed_data['from'],
                            }
                            
                            # Add interview date if found and status suggests interview scheduling
                            if (parsed_data['interview_dates'] and 
                                (ai_classification.interview_scheduled or status == 'interview_scheduled')):
                                record['interview_date'] = parsed_data['interview_dates'][0]
                                record['interview_round'] = 'unknown'
                            
                            # Store in database
                            upsert_application(record)
                            processed_count += 1
                            
                        except Exception as e:
                            st.error(f"Error processing email: {e}")
                            continue
                    
                    st.success(f"Processed {processed_count} emails successfully!")
                    st.rerun()  # Refresh the app to show new data
                    
                else:
                    st.info("No new interview emails found")
            else:
                # Service not available - instructions will be shown by get_gmail_service_streamlit_safe()
                pass
                    
        except FileNotFoundError:
            st.error("[ERROR] **Setup Required**: Please add your `credentials.json` file to the project directory. See README for setup instructions.")
        except Exception as e:
            st.error(f"Error fetching emails: {e}")
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

    st.markdown("---")
    
    # Manual entry section
    st.subheader("➕ Manual Entry")
    
    with st.form("add_application"):
        st.write("Add Application Manually")
        
        company = st.text_input("Company *", help="Company name")
        role = st.text_input("Job Role", help="Position title")
        
        col1, col2 = st.columns(2)
        with col1:
            date_applied = st.date_input("Date Applied", value=datetime.now().date())
        with col2:
            status = st.selectbox("Status", [
                "applied", "interview_scheduled", "interviewed", 
                "rejected", "offer", "accepted"
            ])
        
        # Interview date and time inputs
        col_date, col_time = st.columns(2)
        with col_date:
            interview_date = st.date_input("Interview Date (Optional)", value=None)
        with col_time:
            interview_time = st.time_input("Interview Time", value=None)
        
        interview_round = st.selectbox("Interview Round", [
            "", "phone_screen", "technical", "onsite", "final", "hr"
        ])
        
        notes = st.text_area("Notes", help="Additional notes about this application")
        
        submitted = st.form_submit_button("Add Application")
        
        if submitted:
            if company:  # Company is required
                record = {
                    'company': company,
                    'role': role,
                    'source': 'manual',
                    'date_applied': datetime.combine(date_applied, datetime.min.time()),
                    'status': status,
                    'notes': notes
                }
                
                if interview_date:
                    if interview_time:
                        # Combine date and time
                        record['interview_date'] = datetime.combine(interview_date, interview_time)
                    else:
                        # Use date with default time (9:00 AM)
                        record['interview_date'] = datetime.combine(interview_date, datetime.min.time().replace(hour=9))
                if interview_round:
                    record['interview_round'] = interview_round
                
                try:
                    app_id = upsert_application(record)
                    st.success(f"Added application (ID: {app_id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding application: {e}")
            else:
                st.error("Company name is required")

    st.markdown("---")
    
    # Statistics
    st.subheader("📊 Quick Stats")
    try:
        stats = get_application_stats()
        st.metric("Total Applications", stats.get('total_applications', 0))
        st.metric("Upcoming Interviews", stats.get('upcoming_interviews', 0))
        
        # Status breakdown
        if stats.get('by_status'):
            st.write("**By Status:**")
            for status, count in stats['by_status'].items():
                st.write(f"• {status.replace('_', ' ').title()}: {count}")
                
    except Exception as e:
        st.error(f"Error loading stats: {e}")

# Main content area
col1, col2 = st.columns([3, 1])

with col2:
    st.subheader("🔍 Search & Filter")
    
    # Search functionality
    search_query = st.text_input("Search applications", placeholder="Company, role, or notes...")
    
    # Status filter
    status_filter = st.multiselect("Filter by Status", [
        "applied", "interview_scheduled", "interviewed", 
        "rejected", "offer", "accepted"
    ])
    
    # Date range filter
    st.write("Date Range:")
    date_from = st.date_input("From", value=datetime.now().date() - timedelta(days=30))
    date_to = st.date_input("To", value=datetime.now().date() + timedelta(days=30))

with col1:
    # Main applications view
    st.subheader("📋 Applications")
    
    # Upcoming interviews section
    try:
        upcoming_interviews = get_upcoming_interviews(days_ahead=7)
        
        if not upcoming_interviews.empty:
            st.warning("[ALERT] **Upcoming Interviews (Next 7 Days)**")
            
            for _, interview in upcoming_interviews.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    with col_a:
                        st.write(f"**{interview['company']}** - {interview['role']}")
                    with col_b:
                        interview_dt = pd.to_datetime(interview['interview_date'])
                        if pd.notna(interview_dt):  # Check for NaT before strftime
                            st.write(f"[Date] {interview_dt.strftime('%B %d, %Y at %I:%M %p')}")
                        else:
                            st.write("[Date] TBD")
                    with col_c:
                        st.write(f"🎯 {interview.get('interview_round', 'Unknown')}")
                    
                    if interview.get('notes'):
                        st.caption(f"📝 {interview['notes']}")
                    
                    st.markdown("---")
    except Exception as e:
        st.error(f"Error loading upcoming interviews: {e}")

    # Applications table
    try:
        # Load applications
        if search_query:
            df = search_applications(search_query)
        else:
            df = list_applications()
        
        # Apply filters
        if status_filter:
            df = df[df['status'].isin(status_filter)]
        
        # Date filter (assuming date_applied column exists)
        if 'date_applied' in df.columns and not df.empty and len(df) > 0:
            # Convert to datetime and handle NaT values
            df['date_applied'] = pd.to_datetime(df['date_applied'], errors='coerce')
            
            # Create date range as datetime objects for proper comparison
            date_from_dt = pd.to_datetime(date_from)
            date_to_dt = pd.to_datetime(date_to) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)  # Include end of day
            
            # Filter by date range, handling NaT values (keep rows where date_applied is not null)
            mask = (df['date_applied'].notna()) & (df['date_applied'] >= date_from_dt) & (df['date_applied'] <= date_to_dt)
            df = df[mask]
        
        if not df.empty:
            st.write(f"**Showing {len(df)} applications**")
            
            # Display applications
            for idx, app in df.iterrows():
                with st.expander(f"**{app.get('company', 'Unknown')}** - {app.get('role', 'Unknown Role')} ({app.get('status', 'unknown').replace('_', ' ').title()})"):
                    
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        # Application details
                        if app.get('date_applied'):
                            date_applied = pd.to_datetime(app['date_applied'])
                            if pd.notna(date_applied):  # Check for NaT before strftime
                                st.write(f"[Date] **Applied:** {date_applied.strftime('%B %d, %Y')}")
                            else:
                                st.write("[Date] **Applied:** TBD")
                        
                        if app.get('interview_date'):
                            interview_dt = pd.to_datetime(app['interview_date'])
                            if pd.notna(interview_dt):  # Check for NaT before strftime
                                st.write(f"[Date] **Interview:** {interview_dt.strftime('%B %d, %Y at %I:%M %p')}")
                            else:
                                st.write("[Date] **Interview:** TBD")
                            
                            if app.get('interview_round'):
                                st.write(f"**Round:** {app['interview_round'].replace('_', ' ').title()}")
                        
                        if app.get('source') == 'gmail':
                            st.write(f"📧 **From:** {app.get('email_from', 'Unknown')}")
                            if app.get('email_subject'):
                                st.write(f"**Subject:** {app['email_subject']}")
                        
                        if app.get('notes'):
                            st.write(f"📝 **Notes:** {app['notes']}")
                    
                    with col_actions:
                        # Action buttons
                        new_status = st.selectbox(
                            "Update Status",
                            ["applied", "interview_scheduled", "interviewed", "rejected", "offer", "accepted"],
                            index=["applied", "interview_scheduled", "interviewed", "rejected", "offer", "accepted"].index(app.get('status', 'applied')),
                            key=f"status_{app['id']}"
                        )
                        
                        if st.button("Update", key=f"update_{app['id']}"):
                            try:
                                update_application_status(app['id'], new_status)
                                st.success("Updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        
                        if st.button("🗑️ Delete", key=f"delete_{app['id']}"):
                            try:
                                delete_application(app['id'])
                                st.success("Deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        else:
            st.info("No applications found. Try fetching from Gmail or adding manually!")
            
    except Exception as e:
        st.error(f"Error loading applications: {e}")
        with st.expander("Error Details"):
            st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("**Job Application Tracker** - Built with ❤️ using Streamlit")

# Instructions for first-time users
if st.sidebar.button("📖 Setup Instructions"):
    with st.sidebar:
        st.markdown("""
        ### 🚀 First Time Setup
        
        1. **Google Cloud Setup:**
           - Go to [Google Cloud Console](https://console.cloud.google.com)
           - Create a new project or select existing
           - Enable Gmail API
           - Create OAuth2 credentials
           - Download `credentials.json`
        
        2. **File Placement:**
           - Place `credentials.json` in project root
           - Run the app and click "Fetch Interview Emails"
           - Complete OAuth flow in browser
        
        3. **Usage:**
           - Fetch emails automatically finds interview-related emails
           - Manual entry for other applications
           - Update statuses as you progress
           
        📚 See README.md for detailed instructions
        """)


if __name__ == "__main__":
    # This won't be called when running with streamlit run
    # But useful for testing imports
    print("Job Application Tracker - Streamlit App")
    print("Run with: streamlit run app.py")