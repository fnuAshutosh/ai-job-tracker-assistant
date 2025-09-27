"""
Database utilities for SQLite operations in job application tracker.
Handles database initialization, CRUD operations, and data management.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json


DATABASE_PATH = 'jobs.db'


def get_db_connection():
    """
    Get SQLite database connection with row factory for dict-like access.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn


def init_db():
    """
    Initialize the database with required tables.
    Creates the applications table if it doesn't exist.
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_id TEXT UNIQUE,  -- Gmail message ID (for deduplication)
                company TEXT,
                role TEXT,
                source TEXT DEFAULT 'manual',  -- 'gmail' or 'manual'
                date_applied TEXT,  -- ISO format date
                status TEXT DEFAULT 'applied',  -- applied, interview_scheduled, interviewed, rejected, offer, accepted
                interview_date TEXT,  -- ISO format datetime
                interview_round TEXT,  -- phone_screen, technical, onsite, final, etc.
                notes TEXT,
                snippet TEXT,  -- Email snippet for Gmail entries
                email_subject TEXT,  -- Original email subject
                email_from TEXT,  -- Original email from header
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index on msg_id for faster lookups
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_msg_id ON applications(msg_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON applications(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON applications(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interview_date ON applications(interview_date)')
        
        conn.commit()
        print("Database initialized successfully")
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def upsert_application(record: Dict[str, Any]) -> int:
    """
    Insert or update application record based on msg_id.
    
    Args:
        record: Application data dictionary
        
    Returns:
        int: Record ID
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        # Convert datetime objects to ISO strings
        if 'date_applied' in record and isinstance(record['date_applied'], datetime):
            record['date_applied'] = record['date_applied'].isoformat()
        if 'interview_date' in record and isinstance(record['interview_date'], datetime):
            record['interview_date'] = record['interview_date'].isoformat()
        
        # Set updated timestamp
        record['updated_at'] = datetime.now().isoformat()
        
        # Check if record exists (by msg_id if provided)
        if record.get('msg_id'):
            cursor.execute('SELECT id FROM applications WHERE msg_id = ?', (record['msg_id'],))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                update_fields = []
                update_values = []
                
                for key, value in record.items():
                    if key != 'id':  # Don't update ID
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                update_values.append(record['msg_id'])
                
                query = f'''
                    UPDATE applications 
                    SET {', '.join(update_fields)}
                    WHERE msg_id = ?
                '''
                
                cursor.execute(query, update_values)
                record_id = existing['id']
                print(f"Updated application record (ID: {record_id})")
            else:
                # Insert new record
                record_id = _insert_new_record(cursor, record)
        else:
            # Insert new record without msg_id (manual entry)
            record_id = _insert_new_record(cursor, record)
        
        conn.commit()
        return record_id
        
    except sqlite3.Error as e:
        print(f"Error upserting application: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def _insert_new_record(cursor, record: Dict[str, Any]) -> int:
    """
    Insert a new application record.
    
    Args:
        cursor: Database cursor
        record: Application data
        
    Returns:
        int: New record ID
    """
    # Get column names and values
    columns = list(record.keys())
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    values = list(record.values())
    
    query = f'''
        INSERT INTO applications ({column_names})
        VALUES ({placeholders})
    '''
    
    cursor.execute(query, values)
    record_id = cursor.lastrowid
    print(f"Inserted new application record (ID: {record_id})")
    return record_id


def list_applications(limit: Optional[int] = None) -> pd.DataFrame:
    """
    Retrieve all applications as a pandas DataFrame.
    
    Args:
        limit: Maximum number of records to return
        
    Returns:
        pd.DataFrame: Applications data
    """
    conn = get_db_connection()
    
    try:
        query = '''
            SELECT 
                id,
                company,
                role,
                source,
                date_applied,
                status,
                interview_date,
                interview_round,
                notes,
                email_subject,
                email_from,
                created_at,
                updated_at
            FROM applications
            ORDER BY created_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        df = pd.read_sql_query(query, conn)
        
        # Convert date strings back to datetime objects for display
        if not df.empty:
            df['date_applied'] = pd.to_datetime(df['date_applied'], errors='coerce')
            df['interview_date'] = pd.to_datetime(df['interview_date'], errors='coerce')
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
        
        return df
        
    except sqlite3.Error as e:
        print(f"Error listing applications: {e}")
        raise
    finally:
        conn.close()


def get_upcoming_interviews(days_ahead: int = 7) -> pd.DataFrame:
    """
    Get applications with upcoming interviews within specified days.
    
    Args:
        days_ahead: Number of days to look ahead
        
    Returns:
        pd.DataFrame: Upcoming interviews
    """
    conn = get_db_connection()
    
    try:
        cutoff_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        current_date = datetime.now().isoformat()
        
        query = '''
            SELECT 
                id,
                company,
                role,
                interview_date,
                interview_round,
                notes,
                email_subject,
                status
            FROM applications
            WHERE interview_date IS NOT NULL 
              AND interview_date >= ?
              AND interview_date <= ?
            ORDER BY interview_date ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=(current_date, cutoff_date))
        
        if not df.empty:
            df['interview_date'] = pd.to_datetime(df['interview_date'])
        
        return df
        
    except sqlite3.Error as e:
        print(f"Error getting upcoming interviews: {e}")
        raise
    finally:
        conn.close()


def update_application_status(app_id: int, new_status: str, notes: Optional[str] = None) -> bool:
    """
    Update application status.
    
    Args:
        app_id: Application ID
        new_status: New status value
        notes: Optional notes to add
        
    Returns:
        bool: Success status
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        update_fields = ['status = ?', 'updated_at = ?']
        update_values = [new_status, datetime.now().isoformat()]
        
        if notes:
            update_fields.append('notes = ?')
            update_values.append(notes)
        
        update_values.append(app_id)
        
        query = f'''
            UPDATE applications 
            SET {', '.join(update_fields)}
            WHERE id = ?
        '''
        
        cursor.execute(query, update_values)
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Updated application {app_id} status to {new_status}")
            return True
        else:
            print(f"No application found with ID {app_id}")
            return False
            
    except sqlite3.Error as e:
        print(f"Error updating application status: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_application(app_id: int) -> bool:
    """
    Delete an application record.
    
    Args:
        app_id: Application ID to delete
        
    Returns:
        bool: Success status
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM applications WHERE id = ?', (app_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Deleted application {app_id}")
            return True
        else:
            print(f"No application found with ID {app_id}")
            return False
            
    except sqlite3.Error as e:
        print(f"Error deleting application: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def get_application_stats() -> Dict[str, Any]:
    """
    Get summary statistics about applications.
    
    Returns:
        Dict: Statistics summary
    """
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        
        stats = {}
        
        # Total applications
        cursor.execute('SELECT COUNT(*) FROM applications')
        stats['total_applications'] = cursor.fetchone()[0]
        
        # Applications by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM applications 
            GROUP BY status
        ''')
        stats['by_status'] = dict(cursor.fetchall())
        
        # Applications by source
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM applications 
            GROUP BY source
        ''')
        stats['by_source'] = dict(cursor.fetchall())
        
        # Upcoming interviews count
        cutoff_date = (datetime.now() + timedelta(days=7)).isoformat()
        current_date = datetime.now().isoformat()
        cursor.execute('''
            SELECT COUNT(*) FROM applications
            WHERE interview_date IS NOT NULL 
              AND interview_date >= ?
              AND interview_date <= ?
        ''', (current_date, cutoff_date))
        stats['upcoming_interviews'] = cursor.fetchone()[0]
        
        return stats
        
    except sqlite3.Error as e:
        print(f"Error getting application stats: {e}")
        raise
    finally:
        conn.close()


def search_applications(query: str, field: str = 'all') -> pd.DataFrame:
    """
    Search applications by company, role, or notes.
    
    Args:
        query: Search query
        field: Field to search ('company', 'role', 'notes', 'all')
        
    Returns:
        pd.DataFrame: Search results
    """
    conn = get_db_connection()
    
    try:
        if field == 'all':
            sql_query = '''
                SELECT * FROM applications
                WHERE company LIKE ? OR role LIKE ? OR notes LIKE ?
                ORDER BY updated_at DESC
            '''
            params = [f'%{query}%', f'%{query}%', f'%{query}%']
        else:
            sql_query = f'''
                SELECT * FROM applications
                WHERE {field} LIKE ?
                ORDER BY updated_at DESC
            '''
            params = [f'%{query}%']
        
        df = pd.read_sql_query(sql_query, conn, params=params)
        
        if not df.empty:
            df['date_applied'] = pd.to_datetime(df['date_applied'], errors='coerce')
            df['interview_date'] = pd.to_datetime(df['interview_date'], errors='coerce')
        
        return df
        
    except sqlite3.Error as e:
        print(f"Error searching applications: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Test database operations
    print("Initializing database...")
    init_db()
    
    print("Testing record insertion...")
    test_record = {
        'msg_id': 'test123',
        'company': 'Google',
        'role': 'Software Engineer',
        'source': 'gmail',
        'date_applied': datetime.now() - timedelta(days=5),
        'status': 'interview_scheduled',
        'interview_date': datetime.now() + timedelta(days=2),
        'interview_round': 'technical',
        'notes': 'Technical interview scheduled',
        'email_subject': 'Interview Invitation - Software Engineer',
        'email_from': 'recruiter@google.com'
    }
    
    app_id = upsert_application(test_record)
    print(f"Inserted record with ID: {app_id}")
    
    print("Listing all applications:")
    df = list_applications()
    print(df)
    
    print("Getting upcoming interviews:")
    upcoming = get_upcoming_interviews()
    print(upcoming)
    
    print("Getting application stats:")
    stats = get_application_stats()
    print(stats)