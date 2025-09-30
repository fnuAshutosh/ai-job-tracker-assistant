"""
Database Initialization with Demo Data
Creates a fresh database with sample applications for demonstration purposes.
This runs automatically when the app starts if no database exists.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Generate realistic demo data for the application"""
    
    # Demo companies - avoiding real company names to prevent any issues
    companies = [
        "TechCorp Solutions", "InnovateSoft Inc", "DataFlow Systems", 
        "CloudMesh Technologies", "AI Dynamics Ltd", "NextGen Solutions",
        "DevOps Masters", "ScaleUp Technologies", "CodeCraft Inc",
        "DigitalEdge Systems", "SmartCode Solutions", "TechPioneer Labs",
        "ByteForge Technologies", "CloudNinja Inc", "DataVault Systems",
        "AgileWorks Tech", "TechSphere Solutions", "DevStream Inc",
        "CodeFactory Tech", "DigitalCraft Systems", "TechVision Labs",
        "InnovateCode Inc", "SmartTech Solutions", "CloudForge Systems",
        "DataWorks Technologies", "TechMaster Labs", "DevCraft Inc",
        "QuantumSoft Solutions", "CyberFlow Technologies", "NeuralNet Inc"
    ]
    
    # Job roles
    roles = [
        "Senior Software Engineer", "Frontend Developer", "Backend Developer",
        "Full Stack Developer", "DevOps Engineer", "Data Scientist",
        "Machine Learning Engineer", "Product Manager", "Technical Lead", 
        "Software Architect", "UI/UX Designer", "QA Engineer",
        "Site Reliability Engineer", "Cloud Engineer", "Python Developer",
        "React Developer", "Java Developer", "Database Administrator",
        "Security Engineer", "Platform Engineer", "Mobile Developer",
        "Data Engineer", "Analytics Engineer", "Solutions Architect"
    ]
    
    # Application statuses and corresponding board stages
    status_stage_map = {
        'applied': 'applied',
        'interview_scheduled': 'screening', 
        'interviewed': 'interview',
        'offer': 'final',
        'rejected': 'closed'
    }
    
    priorities = ['high', 'medium', 'low']
    sources = ['Company Website', 'LinkedIn', 'Job Board', 'Referral', 'Direct Contact']
    
    demo_applications = []
    
    # Generate 20 demo applications
    for i in range(20):
        company = random.choice(companies)
        role = random.choice(roles)
        status = random.choice(list(status_stage_map.keys()))
        board_stage = status_stage_map[status]
        priority = random.choice(priorities)
        source = random.choice(sources)
        
        # Generate realistic dates
        days_ago = random.randint(1, 90)
        date_applied = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        stage_entered_date = date_applied
        
        # Generate interview date if applicable
        interview_date = None
        if status in ['interview_scheduled', 'interviewed']:
            interview_days = random.randint(5, 30)
            interview_date = (datetime.now() + timedelta(days=interview_days)).strftime('%Y-%m-%d %H:%M')
        
        # Create demo email addresses
        company_domain = company.lower().replace(' ', '').replace('.', '').replace(',', '')[:15]
        email_from = f"careers@{company_domain}-demo.com"
        
        # Generate realistic notes
        notes_options = [
            f"Applied for {role} position. Waiting for response.",
            f"Completed initial application for {role} role.",
            f"Phone screening scheduled. Technical round pending.",
            f"Great company culture. Excited about this opportunity.",
            f"Salary range: $80k-120k. Remote work available.",
            f"Technical assessment completed. Awaiting feedback.",
            f"Final round interview. Team seems amazing!",
            f"Offer received! Negotiating terms.",
            f"Unfortunately didn't move forward. Great experience though."
        ]
        
        notes = random.choice(notes_options) if random.random() > 0.3 else None
        
        # Email subject based on status
        subject_templates = {
            'applied': f"Application Received - {role}",
            'interview_scheduled': f"Interview Invitation - {role}",
            'interviewed': f"Thank you for interviewing - {role}",
            'offer': f"Job Offer - {role}",
            'rejected': f"Application Update - {role}"
        }
        
        email_subject = subject_templates.get(status, f"Regarding {role} Position")
        
        application = {
            'msg_id': f'demo-msg-{i+1:03d}',
            'company': company,
            'role': role,
            'source': source,
            'date_applied': date_applied,
            'status': status,
            'interview_date': interview_date,
            'interview_round': '1' if interview_date else None,
            'notes': notes,
            'snippet': f"Join our team as a {role} at {company}. We're looking for talented individuals...",
            'email_subject': email_subject,
            'email_from': email_from,
            'board_stage': board_stage,
            'priority': priority,
            'stage_position': random.randint(1, 5),
            'days_in_current_stage': random.randint(1, 30),
            'total_pipeline_days': random.randint(5, 90),
            'tags': random.choice(['remote', 'on-site', 'hybrid', 'contract', 'full-time']),
            'contact_info': 'Contact via company careers page',
            'documents': 'Resume, Cover Letter',
            'follow_up_date': None,
            'salary_expectation': f"${random.randint(70, 150)}k - ${random.randint(80, 200)}k",
            'application_link': f"https://{company_domain}-demo.com/careers",
            'referral_source': source,
            'stage_entered_date': stage_entered_date
        }
        
        demo_applications.append(application)
    
    return demo_applications

def initialize_demo_database():
    """Initialize database with demo data"""
    print("[INIT] Initializing demo database...")
    print("=" * 40)
    
    # Import database utilities
    from db_utils import init_db
    from kanban_database import upgrade_database_for_kanban
    
    # Initialize the database schema
    print("[SCHEMA] Creating database schema...")
    init_db()
    upgrade_database_for_kanban()  # Add Kanban-specific columns
    
    # Generate demo data
    print("[DATA] Generating demo applications...")
    demo_apps = create_demo_data()
    
    # Insert demo data
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    for app in demo_apps:
        cursor.execute("""
            INSERT INTO applications (
                msg_id, company, role, source, date_applied, status,
                interview_date, interview_round, notes, snippet, email_subject,
                email_from, created_at, updated_at, board_stage, priority,
                stage_position, days_in_current_stage, total_pipeline_days,
                tags, contact_info, documents, follow_up_date, salary_expectation,
                application_link, referral_source, stage_entered_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app['msg_id'], app['company'], app['role'], app['source'], 
            app['date_applied'], app['status'], app['interview_date'], 
            app['interview_round'], app['notes'], app['snippet'], 
            app['email_subject'], app['email_from'], 
            datetime.now().isoformat(), datetime.now().isoformat(),
            app['board_stage'], app['priority'], app['stage_position'],
            app['days_in_current_stage'], app['total_pipeline_days'],
            app['tags'], app['contact_info'], app['documents'],
            app['follow_up_date'], app['salary_expectation'],
            app['application_link'], app['referral_source'], app['stage_entered_date']
        ))
    
    # Note: Additional tables (stage_transitions, interview_rounds, application_notes) 
    # will be created automatically when the app starts if needed
    
    conn.commit()
    conn.close()
    
    print(f"[SUCCESS] Created {len(demo_apps)} demo applications")
    print("[SUCCESS] Demo database initialization complete!")
    print("\n🎯 This demo data includes:")
    print("   • Realistic company names (all fictional)")
    print("   • Various job roles and application statuses")
    print("   • Sample interview scheduling and notes")
    print("   • Complete Kanban board pipeline data")
    print("   • No personal or sensitive information")
    
    return True

def check_and_initialize_database():
    """Check if database exists, create with demo data if not"""
    if not os.path.exists('jobs.db'):
        print("[INIT] No database found. Initializing with demo data...")
        initialize_demo_database()
        return True
    else:
        # Check if database is empty
        conn = sqlite3.connect('jobs.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM applications")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                print("[EMPTY] Database exists but is empty. Adding demo data...")
                initialize_demo_database()
                return True
            else:
                print(f"[OK] Database exists with {count} applications")
                return False
        except sqlite3.OperationalError:
            # Table doesn't exist, reinitialize
            conn.close()
            print("[REPAIR] Database schema missing. Reinitializing...")
            initialize_demo_database()
            return True

if __name__ == "__main__":
    print("[DEMO] Job Tracker - Demo Database Initialization")
    print("=" * 60)
    print("This script creates a sample database with demo data.")
    print("Perfect for testing and demonstrating the application!")
    print("-" * 60)
    
    initialize_demo_database()
    
    print("\n🎉 Ready to go!")
    print("Run 'streamlit run app.py' to start the application")