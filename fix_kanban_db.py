"""
Fix Kanban Database Schema
Properly add missing columns for Kanban functionality.
"""

import sqlite3
from datetime import datetime

def fix_kanban_database():
    """Fix the database schema for Kanban board functionality"""
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        print("🔧 Fixing Kanban database schema...")
        
        # Check existing columns first
        cursor.execute("PRAGMA table_info(applications)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Found existing columns: {len(existing_columns)}")
        
        # Define columns that need to be added
        columns_to_add = [
            ('board_stage', 'TEXT DEFAULT "applied"'),
            ('priority', 'TEXT DEFAULT "medium"'),
            ('stage_position', 'INTEGER DEFAULT 0'),
            ('days_in_current_stage', 'INTEGER DEFAULT 0'),
            ('stage_entered_date', 'TEXT'),  # Remove DEFAULT CURRENT_TIMESTAMP
            ('total_pipeline_days', 'INTEGER DEFAULT 0'),
            ('tags', 'TEXT DEFAULT "[]"'),
            ('contact_info', 'TEXT DEFAULT "{}"'),
            ('documents', 'TEXT DEFAULT "[]"'),
            ('follow_up_date', 'TEXT'),
            ('salary_expectation', 'TEXT'),
            ('application_link', 'TEXT'),
            ('referral_source', 'TEXT')
        ]
        
        # Add missing columns one by one
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE applications ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ Warning adding {column_name}: {e}")
            else:
                print(f"ℹ️ Column {column_name} already exists")
        
        # Update stage_entered_date for existing records that don't have it
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE applications 
            SET stage_entered_date = ? 
            WHERE stage_entered_date IS NULL OR stage_entered_date = ''
        """, (now,))
        
        updated_rows = cursor.rowcount
        print(f"📅 Updated stage_entered_date for {updated_rows} existing records")
        
        # Ensure board_stage is set for existing applications
        cursor.execute("""
            UPDATE applications 
            SET board_stage = CASE 
                WHEN status = 'applied' THEN 'applied'
                WHEN status LIKE '%interview%' OR status = 'interview_scheduled' THEN 'interview'
                WHEN status = 'offer' THEN 'final'
                WHEN status = 'rejected' THEN 'closed'
                WHEN status = 'accepted' THEN 'closed'
                ELSE 'applied'
            END
            WHERE board_stage IS NULL OR board_stage = ''
        """)
        
        board_updates = cursor.rowcount
        print(f"🎯 Updated board_stage for {board_updates} existing records")
        
        # Create additional tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stage_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                from_stage TEXT,
                to_stage TEXT NOT NULL,
                transition_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                automated BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        print("✅ Created/verified stage_transitions table")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                round_type TEXT NOT NULL,
                scheduled_date TEXT,
                completed_date TEXT,
                interviewer_name TEXT,
                interviewer_email TEXT,
                interview_link TEXT,
                notes TEXT,
                outcome TEXT,
                feedback TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        print("✅ Created/verified interview_rounds table")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER NOT NULL,
                note_type TEXT DEFAULT 'general',
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        print("✅ Created/verified application_notes table")
        
        # Create indexes for better performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_board_stage ON applications(board_stage)',
            'CREATE INDEX IF NOT EXISTS idx_stage_position ON applications(stage_position)',
            'CREATE INDEX IF NOT EXISTS idx_priority ON applications(priority)',
            'CREATE INDEX IF NOT EXISTS idx_stage_entered_date ON applications(stage_entered_date)',
            'CREATE INDEX IF NOT EXISTS idx_transitions_app_id ON stage_transitions(application_id)',
            'CREATE INDEX IF NOT EXISTS idx_interview_rounds_app_id ON interview_rounds(application_id)',
            'CREATE INDEX IF NOT EXISTS idx_notes_app_id ON application_notes(application_id)'
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError:
                pass  # Index might already exist
        
        print("✅ Created/verified database indexes")
        
        conn.commit()
        
        # Verify the fix by checking the updated schema
        cursor.execute("PRAGMA table_info(applications)")
        final_columns = [column[1] for column in cursor.fetchall()]
        
        print(f"\n🎉 Database schema update complete!")
        print(f"📊 Total columns: {len(final_columns)}")
        print(f"🔍 New columns added for Kanban functionality")
        
        # Test the Kanban query
        cursor.execute("""
            SELECT id, company, role, board_stage, stage_entered_date, priority
            FROM applications 
            LIMIT 3
        """)
        
        test_results = cursor.fetchall()
        print(f"\n✅ Schema verification: Successfully queried {len(test_results)} test records")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error fixing database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_kanban_database()