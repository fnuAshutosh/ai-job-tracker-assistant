"""
Enhanced Database Schema for Kanban Board
Adds support for board stages, priorities, transitions, and timeline tracking.
"""

import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Optional

# Enhanced board stages with metadata
BOARD_STAGES = {
    'backlog': {'order': 0, 'name': 'Backlog', 'type': 'planning'},
    'applied': {'order': 1, 'name': 'Applied', 'type': 'active'},
    'screening': {'order': 2, 'name': 'Screening', 'type': 'active'},
    'interview': {'order': 3, 'name': 'Interview', 'type': 'active'},
    'final': {'order': 4, 'name': 'Final', 'type': 'active'},
    'closed': {'order': 5, 'name': 'Closed', 'type': 'completed'}
}

def upgrade_database_for_kanban():
    """Upgrade the existing database schema to support Kanban board features"""
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        # Add new columns to applications table
        new_columns = [
            ('board_stage', 'TEXT DEFAULT "applied"'),
            ('priority', 'TEXT DEFAULT "medium"'),  # high, medium, low
            ('stage_position', 'INTEGER DEFAULT 0'),  # Position within the stage
            ('days_in_current_stage', 'INTEGER DEFAULT 0'),
            ('stage_entered_date', 'TEXT DEFAULT CURRENT_TIMESTAMP'),
            ('total_pipeline_days', 'INTEGER DEFAULT 0'),
            ('tags', 'TEXT DEFAULT "[]"'),  # JSON array of tags
            ('contact_info', 'TEXT DEFAULT "{}"'),  # JSON object for contacts
            ('documents', 'TEXT DEFAULT "[]"'),  # JSON array of document references
            ('follow_up_date', 'TEXT'),
            ('salary_expectation', 'TEXT'),
            ('application_link', 'TEXT'),
            ('referral_source', 'TEXT')
        ]
        
        # Check existing columns first
        cursor.execute("PRAGMA table_info(applications)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE applications ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"⚠️ Error adding column {column_name}: {e}")
        
        # Create stage transitions tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stage_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                from_stage TEXT,
                to_stage TEXT NOT NULL,
                transition_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                automated BOOLEAN DEFAULT FALSE,  -- TRUE if moved by AI/email processing
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        # Create interview rounds tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                round_type TEXT NOT NULL,  -- phone_screen, technical, behavioral, onsite, final
                scheduled_date TEXT,
                completed_date TEXT,
                interviewer_name TEXT,
                interviewer_email TEXT,
                interview_link TEXT,
                notes TEXT,
                outcome TEXT,  -- passed, failed, pending
                feedback TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        # Create application notes/comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                note_type TEXT DEFAULT 'general',  -- general, interview, follow_up, research
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        # Create indexes for better performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_board_stage ON applications(board_stage)',
            'CREATE INDEX IF NOT EXISTS idx_stage_position ON applications(stage_position)',
            'CREATE INDEX IF NOT EXISTS idx_priority ON applications(priority)',
            'CREATE INDEX IF NOT EXISTS idx_follow_up_date ON applications(follow_up_date)',
            'CREATE INDEX IF NOT EXISTS idx_transitions_app_id ON stage_transitions(application_id)',
            'CREATE INDEX IF NOT EXISTS idx_interview_rounds_app_id ON interview_rounds(application_id)',
            'CREATE INDEX IF NOT EXISTS idx_notes_app_id ON application_notes(application_id)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Update existing applications to have proper board_stage if they don't
        cursor.execute('''
            UPDATE applications 
            SET board_stage = CASE 
                WHEN status = 'applied' THEN 'applied'
                WHEN status LIKE '%interview%' THEN 'interview'
                WHEN status = 'offer' THEN 'final'
                WHEN status = 'rejected' THEN 'closed'
                WHEN status = 'accepted' THEN 'closed'
                ELSE 'applied'
            END
            WHERE board_stage IS NULL OR board_stage = ''
        ''')
        
        conn.commit()
        print("🎉 Database successfully upgraded for Kanban board functionality!")
        
        # Show summary of what was added
        cursor.execute("SELECT COUNT(*) FROM applications")
        app_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM stage_transitions")
        transition_count = cursor.fetchone()[0]
        
        print(f"📊 Database Summary:")
        print(f"   • Applications: {app_count}")
        print(f"   • Stage Transitions: {transition_count}")
        print(f"   • Enhanced with Kanban board support")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error upgrading database: {e}")
        raise
    finally:
        conn.close()

def move_application_to_stage(app_id: int, new_stage: str, notes: str = "", automated: bool = False):
    """Move an application to a different board stage"""
    
    if new_stage not in BOARD_STAGES:
        raise ValueError(f"Invalid stage: {new_stage}")
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        # Get current stage
        cursor.execute("SELECT board_stage FROM applications WHERE id = ?", (app_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"Application {app_id} not found")
        
        old_stage = result[0]
        
        if old_stage == new_stage:
            print(f"Application {app_id} already in stage {new_stage}")
            return
        
        # Update application stage
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE applications 
            SET board_stage = ?, 
                stage_entered_date = ?,
                days_in_current_stage = 0,
                updated_at = ?
            WHERE id = ?
        ''', (new_stage, now, now, app_id))
        
        # Record the transition
        cursor.execute('''
            INSERT INTO stage_transitions 
            (application_id, from_stage, to_stage, notes, automated)
            VALUES (?, ?, ?, ?, ?)
        ''', (app_id, old_stage, new_stage, notes, automated))
        
        conn.commit()
        print(f"✅ Moved application {app_id} from {old_stage} to {new_stage}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error moving application: {e}")
        raise
    finally:
        conn.close()

def get_board_data():
    """Get all applications organized by board stage"""
    
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get applications with calculated days in stage
        cursor.execute('''
            SELECT 
                *,
                CASE 
                    WHEN stage_entered_date IS NOT NULL 
                    THEN CAST((julianday('now') - julianday(stage_entered_date)) AS INTEGER)
                    ELSE 0 
                END as calculated_days_in_stage
            FROM applications 
            ORDER BY board_stage, stage_position, id
        ''')
        
        applications = cursor.fetchall()
        
        # Organize by stage
        board_data = {}
        for stage in BOARD_STAGES.keys():
            board_data[stage] = []
        
        for app in applications:
            stage = app['board_stage'] or 'applied'
            if stage in board_data:
                app_dict = dict(app)
                app_dict['days_in_stage'] = app_dict['calculated_days_in_stage']
                board_data[stage].append(app_dict)
            else:
                # Handle applications with invalid stages
                board_data['applied'].append(dict(app))
        
        return board_data
        
    finally:
        conn.close()

def add_application_note(app_id: int, content: str, note_type: str = 'general'):
    """Add a note/comment to an application"""
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO application_notes (application_id, note_type, content)
            VALUES (?, ?, ?)
        ''', (app_id, note_type, content))
        
        conn.commit()
        print(f"✅ Added note to application {app_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error adding note: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Upgrading database for Kanban board functionality...")
    upgrade_database_for_kanban()
    
    print("\n📊 Testing board data retrieval...")
    board_data = get_board_data()
    
    for stage, apps in board_data.items():
        print(f"{BOARD_STAGES[stage]['name']}: {len(apps)} applications")