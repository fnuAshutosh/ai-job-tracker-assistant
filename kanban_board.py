"""
Job Application Kanban Board - Full Implementation
Interactive Jira-style board integrated with the existing job tracker database.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
import json

# Import our existing utilities
from db_utils import get_db_connection, list_applications
from kanban_database import get_board_data, move_application_to_stage, add_application_note, BOARD_STAGES

def get_application_by_id(app_id: int) -> Dict:
    """Get a single application by ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        result = cursor.fetchone()
        return dict(result) if result else None
    finally:
        conn.close()

def create_kanban_card(app: Dict, stage: str):
    """Create an interactive application card for the Kanban board"""
    
    # Calculate days in current stage
    stage_entered = app.get('stage_entered_date')
    if stage_entered:
        try:
            entered_date = datetime.fromisoformat(stage_entered.replace('Z', '+00:00'))
            days_in_stage = (datetime.now() - entered_date).days
        except:
            days_in_stage = 0
    else:
        days_in_stage = 0
    
    # Determine card color based on priority and days in stage
    priority = app.get('priority', 'medium')
    if days_in_stage > 14:
        card_color = "#ffebee"  # Light red for stale applications
        border_color = "#f44336"
    elif priority == 'high':
        card_color = "#fff3e0"  # Light orange for high priority
        border_color = "#ff9800"
    elif priority == 'low':
        card_color = "#f1f8e9"  # Light green for low priority
        border_color = "#8bc34a"
    else:
        card_color = "#f5f5f5"  # Default gray
        border_color = "#9e9e9e"
    
    # Create the card
    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid {border_color}; 
            border-radius: 12px; 
            padding: 16px; 
            margin: 8px 0; 
            background-color: {card_color};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; color: #333; font-size: 16px;">
                    {app.get('company', 'Unknown Company')}
                </h4>
                <span style="
                    background: #1976d2; 
                    color: white; 
                    padding: 3px 8px; 
                    border-radius: 15px; 
                    font-size: 11px;
                    font-weight: bold;
                ">
                    #{app.get('id', '000')}
                </span>
            </div>
            
            <p style="margin: 4px 0 12px 0; font-weight: 500; color: #555; font-size: 14px;">
                📋 {app.get('role', 'Unknown Role')}
            </p>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <small style="color: #666;">
                    📅 Applied: {app.get('date_applied', 'Unknown')[:10] if app.get('date_applied') else 'Unknown'}
                </small>
                <small style="color: #666;">
                    ⏱️ {days_in_stage} days in stage
                </small>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="
                    background: {'#f44336' if priority == 'high' else '#ff9800' if priority == 'medium' else '#4caf50'}; 
                    color: white; 
                    padding: 2px 6px; 
                    border-radius: 10px; 
                    font-size: 10px;
                ">
                    {priority.upper()} PRIORITY
                </span>
                <small style="color: #888;">
                    📧 {app.get('source', 'manual').title()}
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➡️", key=f"move_{app['id']}", help="Move to next stage"):
            move_to_next_stage(app, stage)
    
    with col2:
        if st.button("✏️", key=f"edit_{app['id']}", help="Edit application"):
            st.session_state[f"edit_mode_{app['id']}"] = True
            st.rerun()
    
    with col3:
        if st.button("👁️", key=f"view_{app['id']}", help="View details"):
            st.session_state[f"show_details_{app['id']}"] = True
            st.rerun()
    
    with col4:
        if st.button("📝", key=f"note_{app['id']}", help="Add note"):
            st.session_state[f"add_note_{app['id']}"] = True
            st.rerun()
    
    # Handle different actions
    handle_card_actions(app)

def handle_card_actions(app: Dict):
    """Handle various actions on application cards"""
    
    app_id = app['id']
    
    # Show details modal
    if st.session_state.get(f"show_details_{app_id}"):
        show_application_details_modal(app)
    
    # Add note modal
    if st.session_state.get(f"add_note_{app_id}"):
        show_add_note_modal(app)
    
    # Edit mode (inline)
    if st.session_state.get(f"edit_mode_{app_id}"):
        show_edit_application_inline(app)

def move_to_next_stage(app: Dict, current_stage: str):
    """Move application to the next logical stage"""
    
    stage_order = ['backlog', 'applied', 'screening', 'interview', 'final', 'closed']
    
    try:
        current_idx = stage_order.index(current_stage)
        if current_idx < len(stage_order) - 1:
            next_stage = stage_order[current_idx + 1]
            move_application_to_stage(app['id'], next_stage, f"Auto-moved from {current_stage}")
            st.success(f"✅ Moved {app['company']} to {BOARD_STAGES[next_stage]['name']}")
            st.rerun()
        else:
            st.warning("Application is already in the final stage")
    except Exception as e:
        st.error(f"Error moving application: {e}")

def show_application_details_modal(app: Dict):
    """Show detailed application view in a modal-style expandable section"""
    
    with st.expander(f"🎫 Application Details - {app['company']}", expanded=True):
        
        # Close button
        if st.button("❌ Close", key=f"close_details_{app['id']}"):
            st.session_state[f"show_details_{app['id']}"] = False
            st.rerun()
        
        # Main details tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "📞 Interviews", "📝 Notes", "🔄 History", "📄 Documents"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Company:**", app.get('company', 'N/A'))
                st.write("**Role:**", app.get('role', 'N/A'))
                st.write("**Current Stage:**", BOARD_STAGES.get(app.get('board_stage', 'applied'), {}).get('name', 'Applied'))
                st.write("**Priority:**", app.get('priority', 'medium').title())
            
            with col2:
                st.write("**Applied Date:**", app.get('date_applied', 'N/A')[:10] if app.get('date_applied') else 'N/A')
                st.write("**Source:**", app.get('source', 'manual').title())
                st.write("**Status:**", app.get('status', 'applied').title())
                
                if app.get('interview_date'):
                    st.write("**Next Interview:**", app.get('interview_date')[:16])
            
            # Application notes
            if app.get('notes'):
                st.markdown("**Notes:**")
                st.text_area("", value=app['notes'], height=100, key=f"notes_display_{app['id']}", disabled=True)
        
        with tab2:
            st.markdown("#### Interview Schedule")
            if app.get('interview_date'):
                st.success(f"📅 Scheduled: {app['interview_date'][:16]}")
                st.write(f"**Round:** {app.get('interview_round', 'Unknown')}")
            else:
                st.info("No interviews scheduled")
            
            # Add interview scheduling
            if st.button(f"📅 Schedule Interview", key=f"schedule_{app['id']}"):
                st.success("Interview scheduling feature would open here")
        
        with tab3:
            # Display existing notes
            st.markdown("#### Application Notes")
            
            # Get notes from database
            notes = get_application_notes(app['id'])
            if notes:
                for note in notes:
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 12px; border-left: 4px solid #007bff; margin: 8px 0; border-radius: 4px;">
                        <small style="color: #666;">{note['created_at'][:16]} - {note['note_type'].title()}</small><br>
                        {note['content']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No notes yet")
        
        with tab4:
            st.markdown("#### Stage Transition History")
            
            # Get transition history
            transitions = get_stage_transitions(app['id'])
            if transitions:
                for trans in transitions:
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 8px; margin: 4px 0; border-radius: 4px;">
                        <strong>{trans['from_stage'] or 'New'} → {trans['to_stage']}</strong><br>
                        <small>{trans['transition_date'][:16]}</small>
                        {f"<br><em>{trans['notes']}</em>" if trans['notes'] else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transition history available")
        
        with tab5:
            st.markdown("#### Documents & Links")
            
            if app.get('application_link'):
                st.markdown(f"🔗 [Application Link]({app['application_link']})")
            
            st.info("Document management feature would be implemented here")

def show_add_note_modal(app: Dict):
    """Show add note modal"""
    
    with st.expander(f"📝 Add Note - {app['company']}", expanded=True):
        
        # Close button
        if st.button("❌ Cancel", key=f"cancel_note_{app['id']}"):
            st.session_state[f"add_note_{app['id']}"] = False
            st.rerun()
        
        # Note form
        note_type = st.selectbox("Note Type", ['general', 'interview', 'follow_up', 'research'], key=f"note_type_{app['id']}")
        note_content = st.text_area("Note Content", height=100, key=f"note_content_{app['id']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Note", key=f"save_note_{app['id']}"):
                if note_content.strip():
                    add_application_note(app['id'], note_content.strip(), note_type)
                    st.success("✅ Note saved!")
                    st.session_state[f"add_note_{app['id']}"] = False
                    st.rerun()
                else:
                    st.error("Please enter note content")
        with col2:
            if st.button("🗑️ Delete Application", key=f"delete_{app['id']}", type="secondary"):
                if st.confirm(f"Delete application to {app['company']}?"):
                    delete_application(app['id'])
                    st.success("Application deleted")
                    st.rerun()

def get_application_notes(app_id: int) -> List[Dict]:
    """Get notes for an application"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM application_notes 
            WHERE application_id = ? 
            ORDER BY created_at DESC
        """, (app_id,))
        return [dict(row) for row in cursor.fetchall()]
    except:
        return []
    finally:
        conn.close()

def get_stage_transitions(app_id: int) -> List[Dict]:
    """Get stage transition history for an application"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM stage_transitions 
            WHERE application_id = ? 
            ORDER BY transition_date DESC
        """, (app_id,))
        return [dict(row) for row in cursor.fetchall()]
    except:
        return []
    finally:
        conn.close()

def delete_application(app_id: int):
    """Delete an application and related data"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Delete related data first
        cursor.execute("DELETE FROM application_notes WHERE application_id = ?", (app_id,))
        cursor.execute("DELETE FROM stage_transitions WHERE application_id = ?", (app_id,))
        cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
    finally:
        conn.close()

def main_kanban_board():
    """Main Kanban board interface"""
    
    st.set_page_config(page_title="Job Application Kanban Board", layout="wide")
    
    st.title("🎯 Job Application Kanban Board")
    st.markdown("*Visual pipeline for tracking your job applications*")
    
    # Board controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        filter_option = st.selectbox("🔍 Filter Applications", 
                                   ["All Applications", "High Priority", "This Week", "Interview Stage", "Pending Follow-up"])
    
    with col2:
        if st.button("🔄 Refresh Board"):
            st.rerun()
    
    with col3:
        if st.button("➕ Add Application"):
            st.session_state['show_add_form'] = True
            st.rerun()
    
    with col4:
        if st.button("📊 Analytics"):
            st.session_state['show_analytics'] = True
            st.rerun()
    
    # Show add application form if requested
    if st.session_state.get('show_add_form'):
        show_add_application_form()
    
    # Show analytics if requested
    if st.session_state.get('show_analytics'):
        show_board_analytics()
    
    st.markdown("---")
    
    # Get board data
    try:
        board_data = get_board_data()
    except Exception as e:
        st.error(f"Error loading board data: {e}")
        return
    
    # Create columns for each stage
    columns = st.columns(len(BOARD_STAGES))
    
    # Render each column
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
                    create_kanban_card(app, stage_key)
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
                        No applications in<br>{stage_info['name'].lower()}
                    </p>
                </div>
                """, unsafe_allow_html=True)

def show_add_application_form():
    """Show form to add a new application"""
    
    with st.expander("➕ Add New Application", expanded=True):
        
        if st.button("❌ Cancel", key="cancel_add_form"):
            st.session_state['show_add_form'] = False
            st.rerun()
        
        with st.form("add_application_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company *", placeholder="e.g., Google")
                role = st.text_input("Role *", placeholder="e.g., Software Engineer")
                stage = st.selectbox("Initial Stage", list(BOARD_STAGES.keys()), 
                                   format_func=lambda x: BOARD_STAGES[x]['name'])
            
            with col2:
                priority = st.selectbox("Priority", ['high', 'medium', 'low'])
                application_link = st.text_input("Application Link", placeholder="https://...")
                date_applied = st.date_input("Application Date", value=datetime.now().date())
            
            notes = st.text_area("Notes", height=100, placeholder="Any additional information...")
            
            submitted = st.form_submit_button("💾 Add Application")
            
            if submitted:
                if company and role:
                    # Insert into database
                    conn = get_db_connection()
                    try:
                        cursor = conn.cursor()
                        now = datetime.now().isoformat()
                        
                        cursor.execute('''
                            INSERT INTO applications 
                            (company, role, board_stage, priority, date_applied, 
                             application_link, notes, source, stage_entered_date, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'manual', ?, ?, ?)
                        ''', (company, role, stage, priority, date_applied.isoformat(), 
                             application_link or None, notes or None, now, now, now))
                        
                        conn.commit()
                        st.success(f"✅ Added application to {company}!")
                        st.session_state['show_add_form'] = False
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error adding application: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("Please fill in Company and Role fields")

def show_board_analytics():
    """Show analytics dashboard"""
    
    with st.expander("📊 Board Analytics", expanded=True):
        
        if st.button("❌ Close Analytics", key="close_analytics"):
            st.session_state['show_analytics'] = False
            st.rerun()
        
        # Get analytics data
        board_data = get_board_data()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_apps = sum(len(apps) for apps in board_data.values())
        active_apps = sum(len(board_data.get(stage, [])) for stage in ['applied', 'screening', 'interview', 'final'])
        closed_apps = len(board_data.get('closed', []))
        
        with col1:
            st.metric("Total Applications", total_apps)
        with col2:
            st.metric("Active Applications", active_apps)
        with col3:
            st.metric("Closed Applications", closed_apps)
        with col4:
            success_rate = f"{(closed_apps/total_apps*100):.1f}%" if total_apps > 0 else "0%"
            st.metric("Pipeline Completion", success_rate)
        
        # Stage breakdown
        st.markdown("#### Applications by Stage")
        stage_data = []
        for stage_key, stage_info in BOARD_STAGES.items():
            count = len(board_data.get(stage_key, []))
            stage_data.append({"Stage": stage_info['name'], "Count": count})
        
        if stage_data:
            df = pd.DataFrame(stage_data)
            st.bar_chart(df.set_index('Stage'))

if __name__ == "__main__":
    main_kanban_board()