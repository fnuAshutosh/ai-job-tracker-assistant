#!/usr/bin/env python3
"""
Database cleanup script to fix inaccurate job application data
"""

import sys
import os
import sqlite3

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_utils import get_db_connection

def cleanup_database():
    """Clean up inaccurate job application entries"""
    print("🧹 Starting database cleanup...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Delete entries from promotional/spam sources
        spam_companies = [
            'Naukri', 'Shine', 'Monster', 'Indeed', 'LinkedIn', 'Calendly',
            'Geeksforgeeks', 'Hackerearth', 'Codechef', 'Interviewbit',
            'Glassdoor', 'Angelco', 'Instahyre', 'Cutshort', 'Jobs.Shine'
        ]
        
        placeholders = ','.join(['?' for _ in spam_companies])
        delete_query = f"DELETE FROM applications WHERE company IN ({placeholders})"
        cursor.execute(delete_query, spam_companies)
        deleted_spam = cursor.rowcount
        print(f"📧 Deleted {deleted_spam} promotional/spam entries")
        
        # 2. Delete entries without proper company AND role information
        cursor.execute("""
            DELETE FROM applications 
            WHERE (company IS NULL OR company = '') 
            AND (role IS NULL OR role = '' OR role LIKE '%None%')
        """)
        deleted_incomplete = cursor.rowcount
        print(f"🗑️ Deleted {deleted_incomplete} incomplete entries")
        
        # 3. Update status for remaining entries that don't have interview dates
        cursor.execute("""
            UPDATE applications 
            SET status = 'applied' 
            WHERE status = 'interview_scheduled' 
            AND (interview_date IS NULL OR interview_date = '')
        """)
        updated_status = cursor.rowcount
        print(f"📝 Updated status to 'applied' for {updated_status} entries without interview dates")
        
        # 4. Show remaining data
        cursor.execute("SELECT COUNT(*) FROM applications")
        remaining_count = cursor.fetchone()[0]
        print(f"✅ Cleanup complete! {remaining_count} entries remaining")
        
        # Show sample of cleaned data
        cursor.execute("""
            SELECT company, role, status, email_subject 
            FROM applications 
            WHERE company IS NOT NULL AND company != ''
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print("\n📊 Sample of cleaned data:")
        for row in cursor.fetchall():
            company, role, status, subject = row
            print(f"• {company} - {role or 'No role'} [{status}]")
            if subject:
                print(f"  Subject: {subject[:60]}...")
        
        conn.commit()
        print("\n🎉 Database cleanup successful!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_database()