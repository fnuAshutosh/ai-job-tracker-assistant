"""
Interview Intelligence Database Schema Extension
Extends existing job tracker database with interview intelligence features.
"""

INTERVIEW_INTELLIGENCE_SCHEMA = {
    # Company intelligence data
    'company_intelligence': '''
        CREATE TABLE IF NOT EXISTS company_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            domain TEXT,  -- normalized company domain (e.g., google.com)
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            intelligence_data TEXT,  -- JSON blob with all scraped data
            data_sources TEXT,  -- JSON array of sources used
            confidence_score REAL DEFAULT 0.0,  -- 0.0 to 1.0
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name)
        )
    ''',
    
    # Role-specific intelligence
    'role_intelligence': '''
        CREATE TABLE IF NOT EXISTS role_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_intelligence_id INTEGER NOT NULL,
            role_title TEXT NOT NULL,
            role_level TEXT,  -- junior, mid, senior, staff, principal
            interview_process TEXT,  -- JSON structure of interview rounds
            technical_topics TEXT,  -- JSON array of technical areas
            behavioral_themes TEXT,  -- JSON array of behavioral patterns
            difficulty_rating REAL,  -- 1.0 to 5.0
            recent_changes TEXT,  -- JSON of recent process changes
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_intelligence_id) REFERENCES company_intelligence (id),
            UNIQUE(company_intelligence_id, role_title, role_level)
        )
    ''',
    
    # Interview intelligence reports generated for users
    'intelligence_reports': '''
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            role_title TEXT,
            report_data TEXT,  -- JSON with complete intelligence report
            prep_plan TEXT,  -- JSON with personalized preparation plan
            confidence_score REAL DEFAULT 0.0,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,  -- when this report should be refreshed
            FOREIGN KEY (application_id) REFERENCES applications (id),
            UNIQUE(application_id)
        )
    ''',
    
    # Web scraping sources and their data
    'intelligence_sources': '''
        CREATE TABLE IF NOT EXISTS intelligence_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,  -- glassdoor, blind, reddit, linkedin
            source_url TEXT,
            company_name TEXT,
            scraped_data TEXT,  -- JSON of raw scraped data
            relevance_score REAL DEFAULT 0.0,  -- AI-determined relevance
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            processed BOOLEAN DEFAULT FALSE,
            INDEX(company_name, scraped_at)
        )
    ''',
    
    # User's interview preparation sessions
    'prep_sessions': '''
        CREATE TABLE IF NOT EXISTS prep_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            session_type TEXT,  -- technical, behavioral, system_design
            company_specific_data TEXT,  -- JSON with company-tailored content
            questions_practiced TEXT,  -- JSON array of questions
            performance_metrics TEXT,  -- JSON with scoring and feedback
            duration_minutes INTEGER,
            completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''',
    
    # Interview pattern analysis
    'interview_patterns': '''
        CREATE TABLE IF NOT EXISTS interview_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role_category TEXT,  -- swe, pm, ds, etc
            pattern_type TEXT,  -- process_change, question_trend, difficulty_shift
            pattern_data TEXT,  -- JSON with pattern details
            confidence REAL DEFAULT 0.0,
            detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
            validated BOOLEAN DEFAULT FALSE,
            INDEX(company_name, pattern_type)
        )
    '''
}

def create_intelligence_tables():
    """Create all interview intelligence tables"""
    import sqlite3
    
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    try:
        for table_name, schema in INTERVIEW_INTELLIGENCE_SCHEMA.items():
            cursor.execute(schema)
            print(f"✅ Created/verified table: {table_name}")
        
        conn.commit()
        print("🎉 Interview intelligence database schema ready!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_intelligence_tables()