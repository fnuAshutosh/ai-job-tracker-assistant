"""
Demo Mode Logic and Controls for AI Job Tracker
Handles guided walkthrough, reset functionality, and multiple demo experiences
"""

import streamlit as st
import sqlite3
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# Load demo data
def load_demo_data():
    """Load sample data from JSON files"""
    try:
        with open('demo_data/sample_data.json', 'r') as f:
            sample_data = json.load(f)
        
        with open('demo_data/company_intelligence.json', 'r') as f:
            company_intel = json.load(f)
            
        return sample_data, company_intel
    except FileNotFoundError:
        st.error("Demo data files not found. Please check demo_data directory.")
        return {}, {}

class DemoController:
    """Controls demo modes, walkthrough, and reset functionality"""
    
    def __init__(self):
        self.initialize_demo_session()
    
    def initialize_demo_session(self):
        """Initialize demo session state"""
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = True
            st.session_state.demo_experience = "welcome"  # welcome, guided, full, sandbox
            st.session_state.walkthrough_step = 0
            st.session_state.demo_user_id = f"demo_{random.randint(1000, 9999)}"
            st.session_state.applications_added = []
            st.session_state.emails_processed = []
    
    def render_demo_controls(self):
        """Render demo control panel in sidebar"""
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🎭 Demo Experience")
            
            # Demo mode selector
            demo_modes = {
                "🚀 Quick Overview": "full",
                "🎯 Guided Walkthrough": "guided", 
                "🔄 Start Fresh": "fresh",
                "🎮 Sandbox Mode": "sandbox"
            }
            
            selected_mode = st.selectbox(
                "Choose your experience:",
                options=list(demo_modes.keys()),
                index=1 if st.session_state.get('demo_experience', 'welcome') == "guided" else 0
            )
            
            if st.button("🎬 Switch Experience"):
                st.session_state.demo_experience = demo_modes[selected_mode]
                if demo_modes[selected_mode] == "fresh":
                    self.reset_demo()
                elif demo_modes[selected_mode] == "full":
                    self.load_full_demo()
                elif demo_modes[selected_mode] == "guided":
                    self.start_guided_walkthrough()
                st.rerun()
            
            # Reset controls
            st.markdown("#### 🔄 Demo Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🆕 Reset", help="Start completely over"):
                    self.reset_demo()
                    st.success("Demo reset!")
                    st.rerun()
            
            with col2:
                if st.button("⚡ Skip", help="Jump to full demo"):
                    self.load_full_demo()
                    st.success("Loaded full demo!")
                    st.rerun()
            
            # Scenario selector for fresh starts
            if st.session_state.get('demo_experience', 'welcome') in ["fresh", "guided"]:
                st.markdown("#### 🎲 Try a Scenario")
                sample_data, _ = load_demo_data()
                scenarios = sample_data.get('demo_scenarios', {})
                
                scenario_names = [f"{scenario['name']}" for scenario in scenarios.values()]
                selected_scenario = st.selectbox("Pick a scenario:", ["Choose...", *scenario_names])
                
                if selected_scenario != "Choose..." and st.button("🎬 Load Scenario"):
                    self.load_scenario(selected_scenario, scenarios)
                    st.rerun()
    
    def reset_demo(self):
        """Reset demo to clean state"""
        # Clear demo session state
        demo_keys = [key for key in st.session_state.keys() if key.startswith('demo_') or key.startswith('walkthrough_')]
        for key in demo_keys:
            del st.session_state[key]
        
        # Reset demo state
        st.session_state.demo_mode = True
        st.session_state.demo_experience = "fresh"
        st.session_state.walkthrough_step = 0
        st.session_state.demo_user_id = f"demo_{random.randint(1000, 9999)}"
        st.session_state.applications_added = []
        st.session_state.emails_processed = []
        
        # Create clean demo database
        self.create_clean_demo_database()
        
        st.balloons()
    
    def create_clean_demo_database(self):
        """Create empty database for fresh demo experience"""
        try:
            # Import database initialization
            from db_utils import init_db
            
            # Create clean demo database
            demo_user_id = st.session_state.get('demo_user_id', f"demo_{random.randint(1000, 9999)}")
            demo_db_path = f"demo_{demo_user_id}.db"
            
            # Initialize empty database
            conn = sqlite3.connect(demo_db_path)
            conn.close()
            
            # Initialize with schema but no data
            init_db()  # This will create tables in jobs.db
            
        except Exception as e:
            st.error(f"Error creating demo database: {e}")
    
    def load_full_demo(self):
        """Load full demo with all sample data"""
        st.session_state.demo_experience = "full"
        sample_data, _ = load_demo_data()
        
        # Load all sample applications
        try:
            from db_utils import upsert_application
            
            for app_data in sample_data.get('sample_applications', []):
                upsert_application(
                    msg_id=f"demo_{app_data['company']}_{random.randint(100, 999)}",
                    company=app_data['company'],
                    role=app_data['role'],
                    status=app_data['status'],
                    date_applied=app_data['date_applied'],
                    interview_date=app_data.get('interview_date'),
                    interview_round=app_data.get('interview_round'),
                    notes=app_data.get('notes', ''),
                    source='demo'
                )
            
        except Exception as e:
            st.error(f"Error loading demo data: {e}")
    
    def start_guided_walkthrough(self):
        """Start the guided walkthrough experience"""
        st.session_state.demo_experience = "guided"
        st.session_state.walkthrough_step = 0
        self.create_clean_demo_database()
    
    def render_walkthrough(self):
        """Render the guided walkthrough experience"""
        if st.session_state.get('demo_experience', 'welcome') != "guided":
            return False
            
        step = st.session_state.get('walkthrough_step', 0)
        
        if step == 0:
            return self.walkthrough_welcome()
        elif step == 1:
            return self.walkthrough_add_application()
        elif step == 2:
            return self.walkthrough_email_simulation()
        elif step == 3:
            return self.walkthrough_ai_classification()
        elif step == 4:
            return self.walkthrough_intelligence_generation()
        elif step == 5:
            return self.walkthrough_complete()
        
        return False
    
    def walkthrough_welcome(self):
        """Step 0: Welcome and introduction"""
        st.markdown("# 🎯 Welcome to Your AI Job Tracker!")
        
        st.markdown("""
        ### Experience the magic from day 1 of your job hunt!
        
        Right now your board is empty - just like when you start looking for jobs.
        Let's walk through how this AI-powered system transforms your job search.
        
        **What you'll experience:**
        - ✅ Add your first job application
        - 📧 See AI classify job emails intelligently  
        - 🧠 Generate company-specific interview intelligence
        - 📊 Watch your dashboard come to life
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start My Job Hunt Journey", size="large"):
                st.session_state.walkthrough_step = 1
                st.rerun()
        
        return True
    
    def walkthrough_add_application(self):
        """Step 1: Add first job application"""
        st.markdown("### 📝 Step 1: Add Your First Job Application")
        
        st.info("Every job hunt starts with applying to companies. Let's add your first application!")
        
        with st.form("first_application"):
            st.markdown("**Pick a company you'd like to apply to:**")
            
            col1, col2 = st.columns(2)
            with col1:
                company = st.selectbox("Company:", ["Google", "Microsoft", "Meta", "Amazon", "Netflix"])
            with col2:
                role = st.selectbox("Role:", ["Software Engineer", "Product Manager", "Data Scientist", "DevOps Engineer"])
            
            if st.form_submit_button("🎯 Apply to This Job!", use_container_width=True):
                # Add application to database
                try:
                    from db_utils import upsert_application
                    
                    app_id = upsert_application(
                        msg_id=f"demo_{company}_{random.randint(100, 999)}",
                        company=company,
                        role=role,
                        status='applied',
                        date_applied=datetime.now().strftime('%Y-%m-%d'),
                        source='demo'
                    )
                    
                    st.session_state.applications_added.append({
                        'company': company, 
                        'role': role,
                        'app_id': app_id
                    })
                    st.session_state.last_application = {'company': company, 'role': role}
                    
                    st.success(f"🎉 Congratulations! You applied to {company} for {role}!")
                    time.sleep(2)  # Let user see the success message
                    st.session_state.walkthrough_step = 2
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error adding application: {e}")
        
        return True
    
    def walkthrough_email_simulation(self):
        """Step 2: Simulate receiving an email"""
        last_app = st.session_state.get('last_application', {})
        company = last_app.get('company', 'Google')
        
        st.markdown("### 📧 Step 2: You Got an Email Response!")
        
        st.markdown(f"**Great news! You received an email from {company}:**")
        
        # Simulate email content
        sample_emails = {
            "Google": "Subject: Interview Invitation - Software Engineer Position\nFrom: sarah.chen@google.com\n\nHi! We'd like to schedule a phone screen for the Software Engineer position. Are you available next week?",
            "Microsoft": "Subject: Next Steps - Product Manager Role\nFrom: recruiter@microsoft.com\n\nThank you for your interest! We'd love to chat about the Product Manager opportunity.",
            "Meta": "Subject: Interview Scheduling - Data Scientist\nFrom: hiring@meta.com\n\nCongratulations! We'd like to move forward with an interview for the Data Scientist role.",
            "Amazon": "Subject: Interview Opportunity - DevOps Engineer\nFrom: talent@amazon.com\n\nWe're impressed with your background and would like to schedule an interview.",
            "Netflix": "Subject: Technical Interview - Software Engineer\nFrom: engineering@netflix.com\n\nWe're excited to learn more about you through a technical interview."
        }
        
        email_content = sample_emails.get(company, sample_emails["Google"])
        
        st.text_area("Email Content:", email_content, height=100, disabled=True)
        
        st.info("💡 **This is where AI magic happens!** Let's see how our AI classifies this email.")
        
        if st.button("🤖 Let AI Analyze This Email", use_container_width=True):
            st.session_state.current_email = email_content
            st.session_state.walkthrough_step = 3
            st.rerun()
        
        return True
    
    def walkthrough_ai_classification(self):
        """Step 3: Show AI email classification in action"""
        st.markdown("### 🤖 Step 3: AI Email Classification in Action")
        
        # Show AI processing with realistic delay
        with st.spinner("🧠 AI analyzing email content..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)  # Total 2 seconds
                progress_bar.progress(i + 1)
        
        # Show classification results
        st.success("✅ **AI Classification Complete!**")
        
        last_app = st.session_state.get('last_application', {})
        company = last_app.get('company', 'Google')
        
        classification_result = {
            "category": "job_interview",
            "confidence": 0.96,
            "company": company,
            "reasoning": "Email contains interview scheduling language and recruiter contact information",
            "action_suggested": "Schedule interview, prepare for phone screen",
            "priority": "High"
        }
        
        st.json(classification_result)
        
        st.markdown("**🎯 What the AI found:**")
        st.markdown(f"- 📊 **Category:** Job Interview ({classification_result['confidence']*100:.0f}% confidence)")
        st.markdown(f"- 🏢 **Company:** {company}")
        st.markdown(f"- 💡 **Next Action:** {classification_result['action_suggested']}")
        st.markdown(f"- ⚡ **Priority:** {classification_result['priority']}")
        
        st.info("🚀 **Ready for the next level?** Let's generate company-specific interview intelligence!")
        
        if st.button("🧠 Generate Interview Intelligence", use_container_width=True):
            st.session_state.walkthrough_step = 4
            st.rerun()
        
        return True
    
    def walkthrough_intelligence_generation(self):
        """Step 4: Generate company-specific interview intelligence"""
        last_app = st.session_state.get('last_application', {})
        company = last_app.get('company', 'Google')
        
        st.markdown("### 🧠 Step 4: Generating Interview Intelligence")
        
        st.markdown(f"**Now the AI researches {company}'s interview process for you...**")
        
        # Show research process with realistic delays
        research_steps = [
            "🔍 Analyzing recent interview experiences...",
            "📊 Processing company interview patterns...",
            "🎯 Generating personalized preparation plan...",
            "✨ Compiling intelligence report..."
        ]
        
        progress_container = st.empty()
        
        for i, step in enumerate(research_steps):
            with progress_container:
                st.info(step)
            time.sleep(1.5)
        
        progress_container.empty()
        st.success("🎉 **Interview Intelligence Generated!**")
        
        # Show intelligence report
        _, company_intel = load_demo_data()
        intel_data = company_intel.get(company, {})
        
        if intel_data:
            st.markdown(f"### 📋 {company} Interview Intelligence Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Confidence Score", f"{intel_data.get('confidence_score', 0.85)*100:.0f}%")
                st.metric("Difficulty Rating", f"{intel_data.get('difficulty_rating', 4.0)}/5.0")
            
            with col2:
                st.metric("Interview Rounds", len(intel_data.get('interview_process', {}).get('structure', [])))
                st.metric("Success Tips", len(intel_data.get('success_tips', [])))
            
            with st.expander("📊 Interview Process", expanded=True):
                for round_info in intel_data.get('interview_process', {}).get('structure', []):
                    st.markdown(f"**Round {round_info['round']}: {round_info['type']}**")
                    st.markdown(f"- Duration: {round_info['duration']}")
                    st.markdown(f"- Focus: {round_info['focus']}")
            
            with st.expander("🎯 Success Tips"):
                for tip in intel_data.get('success_tips', []):
                    st.markdown(f"- {tip}")
            
            with st.expander("🔄 Recent Changes"):
                st.markdown(intel_data.get('recent_changes', 'No recent changes noted.'))
        
        if st.button("🎊 Complete the Experience!", use_container_width=True):
            st.session_state.walkthrough_step = 5
            st.rerun()
        
        return True
    
    def walkthrough_complete(self):
        """Step 5: Walkthrough complete"""
        st.balloons()
        
        st.markdown("# 🎉 Congratulations! Experience Complete!")
        
        st.markdown("""
        ### You just experienced the full AI Job Tracker workflow:
        
        ✅ **Added your job application** - The foundation of tracking  
        ✅ **AI classified incoming email** - Smart automation at work  
        ✅ **Generated interview intelligence** - Company-specific insights  
        ✅ **Saw the complete system** - From application to preparation  
        
        ### 🚀 What's next?
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Try Different Company", use_container_width=True):
                st.session_state.walkthrough_step = 1
                st.rerun()
        
        with col2:
            if st.button("📊 Explore Full Demo", use_container_width=True):
                self.load_full_demo()
                st.rerun()
        
        with col3:
            if st.button("🆕 Start Over", use_container_width=True):
                self.reset_demo()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 💡 **Ready to use this for real?**")
        st.info("This demo showed sample data. To use with your real Gmail and job applications, clone the repository and follow the setup instructions in the README!")
        
        return True
    
    def load_scenario(self, scenario_name: str, scenarios: Dict):
        """Load a specific demo scenario"""
        # Find matching scenario
        scenario_data = None
        for scenario in scenarios.values():
            if scenario['name'] == scenario_name:
                scenario_data = scenario
                break
        
        if not scenario_data:
            st.error("Scenario not found!")
            return
        
        # Reset demo first
        self.reset_demo()
        
        # Load scenario applications
        try:
            from db_utils import upsert_application
            
            for app_data in scenario_data.get('applications', []):
                upsert_application(
                    msg_id=f"demo_scenario_{app_data['company']}_{random.randint(100, 999)}",
                    company=app_data['company'],
                    role=app_data['role'], 
                    status=app_data['status'],
                    date_applied=datetime.now().strftime('%Y-%m-%d'),
                    source='demo_scenario'
                )
            
            st.session_state.demo_experience = "full"
            st.success(f"Loaded scenario: {scenario_name}")
            
        except Exception as e:
            st.error(f"Error loading scenario: {e}")
    
    def render_demo_banner(self):
        """Render demo mode banner"""
        if st.session_state.get('demo_mode', False):
            demo_type = st.session_state.get('demo_experience', 'full')
            
            if demo_type == "guided":
                step = st.session_state.get('walkthrough_step', 0)
                st.info(f"🎭 **Guided Demo Mode** - Step {step + 1}/6 - Experience the AI job tracker journey!")
            elif demo_type == "full":
                st.info("🎭 **Demo Mode** - Exploring with sample data. All features functional! Try the reset button to start fresh.")
            elif demo_type == "fresh":
                st.info("🎭 **Fresh Start Mode** - Clean slate ready for your first application!")
            else:
                st.info("🎭 **Demo Mode** - Interactive experience with sample data.")

# Global demo controller instance
demo_controller = DemoController()

def get_demo_controller():
    """Get the global demo controller instance"""
    return demo_controller