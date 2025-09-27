"""
Job Application Kanban Board - Concept Design
Interactive Jira-style board for tracking job applications through different stages.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import json

# Define board stages/columns
BOARD_STAGES = {
    'backlog': {'name': '📋 Backlog', 'color': '#f0f0f0', 'description': 'Jobs to apply to'},
    'applied': {'name': '📤 Applied', 'color': '#e3f2fd', 'description': 'Application submitted'},
    'screening': {'name': '📞 Screening', 'color': '#fff3e0', 'description': 'Phone/initial screening'},
    'interview': {'name': '🎯 Interview', 'color': '#f3e5f5', 'description': 'Technical/behavioral interviews'},
    'final': {'name': '✅ Final', 'color': '#e8f5e8', 'description': 'Final interview/decision pending'},
    'closed': {'name': '📊 Closed', 'color': '#ffebee', 'description': 'Final outcomes (Offer/Rejected)'}
}

# Define card priority levels
PRIORITY_LEVELS = {
    'high': {'name': '🔴 High', 'color': '#ffcdd2'},
    'medium': {'name': '🟡 Medium', 'color': '#fff9c4'},
    'low': {'name': '🟢 Low', 'color': '#c8e6c9'}
}

def create_application_card(app_data: Dict, stage: str) -> None:
    """Create a visual application card for the Kanban board"""
    
    with st.container():
        # Card header with company and role
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 12px; 
            margin: 8px 0; 
            background-color: {BOARD_STAGES[stage]['color']};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: between; align-items: center;">
                <h4 style="margin: 0; color: #333;">{app_data.get('company', 'Unknown Company')}</h4>
                <small style="color: #666;">#{app_data.get('id', '000')}</small>
            </div>
            <p style="margin: 4px 0; font-weight: 500; color: #555;">
                {app_data.get('role', 'Unknown Role')}
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                <small style="color: #888;">
                    📅 {app_data.get('applied_date', 'Unknown')}
                </small>
                <span style="
                    background: #007bff; 
                    color: white; 
                    padding: 2px 8px; 
                    border-radius: 12px; 
                    font-size: 11px;
                ">
                    {app_data.get('days_in_stage', 0)} days
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_kanban_board_mockup():
    """Create a mockup of the Kanban board layout"""
    
    st.title("🎯 Job Application Kanban Board")
    st.markdown("*Jira-style visual tracking for your job applications*")
    
    # Board controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.selectbox("🔍 Filter by", ["All Applications", "This Week", "High Priority", "Specific Company"])
    with col2:
        if st.button("➕ Add Application"):
            st.info("Would open 'Create New Application' modal")
    with col3:
        if st.button("📊 Analytics"):
            st.info("Would show pipeline metrics and analytics")
    
    st.markdown("---")
    
    # Create columns for each stage
    columns = st.columns(len(BOARD_STAGES))
    
    # Sample data for demonstration
    sample_applications = [
        {'id': 1, 'company': 'Google', 'role': 'Senior Software Engineer', 'stage': 'applied', 'applied_date': '2025-09-25', 'days_in_stage': 2},
        {'id': 2, 'company': 'Microsoft', 'role': 'Cloud Engineer', 'stage': 'screening', 'applied_date': '2025-09-20', 'days_in_stage': 7},
        {'id': 3, 'company': 'Amazon', 'role': 'Data Scientist', 'stage': 'interview', 'applied_date': '2025-09-15', 'days_in_stage': 12},
        {'id': 4, 'company': 'Meta', 'role': 'Full Stack Developer', 'stage': 'final', 'applied_date': '2025-09-10', 'days_in_stage': 17},
        {'id': 5, 'company': 'Netflix', 'role': 'Backend Engineer', 'stage': 'applied', 'applied_date': '2025-09-24', 'days_in_stage': 3},
        {'id': 6, 'company': 'Tesla', 'role': 'Software Engineer', 'stage': 'backlog', 'applied_date': '', 'days_in_stage': 0},
    ]
    
    # Render each column with applications
    for i, (stage_key, stage_info) in enumerate(BOARD_STAGES.items()):
        with columns[i]:
            # Column header
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px;
                border-radius: 8px 8px 0 0;
                text-align: center;
                font-weight: bold;
            ">
                {stage_info['name']}
            </div>
            """, unsafe_allow_html=True)
            
            # Application cards in this stage
            stage_apps = [app for app in sample_applications if app['stage'] == stage_key]
            
            if stage_apps:
                for app in stage_apps:
                    create_application_card(app, stage_key)
                    
                    # Action buttons for each card
                    col_move, col_edit, col_view = st.columns(3)
                    with col_move:
                        if st.button(f"→", key=f"move_{app['id']}", help="Move to next stage"):
                            st.success(f"Moving {app['company']} to next stage")
                    with col_edit:
                        if st.button(f"✏️", key=f"edit_{app['id']}", help="Edit application"):
                            st.info(f"Edit {app['company']} details")
                    with col_view:
                        if st.button(f"👁️", key=f"view_{app['id']}", help="View details"):
                            show_application_details(app)
            else:
                st.markdown(f"""
                <div style="
                    padding: 20px;
                    text-align: center;
                    color: #999;
                    border: 2px dashed #ddd;
                    border-radius: 8px;
                    margin: 10px 0;
                ">
                    No applications in {stage_info['name'].lower()}
                </div>
                """, unsafe_allow_html=True)
            
            # Add application button for backlog
            if stage_key == 'backlog':
                if st.button(f"➕ Add to {stage_info['name']}", key=f"add_{stage_key}"):
                    st.info("Would open 'Add New Job' form")

def show_application_details(app_data: Dict):
    """Show detailed view of an application (like Jira ticket view)"""
    
    st.markdown("---")
    st.markdown(f"### 🎫 Application Details - {app_data['company']}")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📞 Interviews", "📝 Notes", "📄 Documents"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Company:**", app_data['company'])
            st.write("**Role:**", app_data['role'])
            st.write("**Status:**", app_data['stage'].title())
        with col2:
            st.write("**Applied Date:**", app_data.get('applied_date', 'N/A'))
            st.write("**Days in Stage:**", app_data.get('days_in_stage', 0))
            st.write("**Priority:**", "🟡 Medium")
    
    with tab2:
        st.markdown("#### Upcoming Interviews")
        st.info("📅 Technical Interview - Oct 2, 2025 at 2:00 PM")
        st.markdown("#### Interview History")
        st.success("✅ Phone Screen - Sep 28, 2025 (Passed)")
    
    with tab3:
        st.text_area("Application Notes", 
                    value="Initial conversation went well. They're looking for someone with React and Node.js experience.",
                    height=100)
        if st.button("💾 Save Notes"):
            st.success("Notes saved!")
    
    with tab4:
        st.markdown("#### Attached Documents")
        st.markdown("- 📄 Resume_Google_2025.pdf")
        st.markdown("- 📄 Cover_Letter_Google.pdf")
        if st.button("📎 Add Document"):
            st.info("Would open file upload dialog")

def show_board_analytics():
    """Show analytics and metrics for the job application pipeline"""
    
    st.markdown("### 📊 Pipeline Analytics")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", "25", delta="3 this week")
    with col2:
        st.metric("Response Rate", "68%", delta="5%")
    with col3:
        st.metric("Interview Rate", "24%", delta="2%")
    with col4:
        st.metric("Offer Rate", "8%", delta="1%")
    
    # Pipeline visualization
    st.markdown("#### Application Flow")
    pipeline_data = pd.DataFrame({
        'Stage': ['Applied', 'Screening', 'Interview', 'Final', 'Offer'],
        'Count': [25, 17, 8, 3, 2],
        'Conversion_Rate': [100, 68, 32, 12, 8]
    })
    
    st.bar_chart(pipeline_data.set_index('Stage')['Count'])

if __name__ == "__main__":
    # Main app
    create_kanban_board_mockup()
    
    # Sidebar for additional controls
    with st.sidebar:
        st.markdown("### 🎛️ Board Controls")
        
        if st.button("📊 Show Analytics"):
            show_board_analytics()
        
        st.markdown("### 🔧 Quick Actions")
        if st.button("🔄 Sync Emails"):
            st.info("Would trigger Gmail sync with AI classification")
        
        if st.button("📅 Schedule Interview"):
            st.info("Would open calendar integration")
        
        if st.button("📧 Send Follow-up"):
            st.info("Would open email template selector")
        
        st.markdown("### ⚙️ Settings")
        st.checkbox("Auto-move based on emails", value=True)
        st.selectbox("Default view", ["All Stages", "My Applications", "This Week"])
        
        st.markdown("---")
        st.markdown("*💡 Drag & drop functionality would be implemented with custom JavaScript or Streamlit components*")