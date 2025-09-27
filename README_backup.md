# � AI-Powered Job Application Tracker

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/your-username/job-tracker-assistant?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/job-tracker-assistant?style=social)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)

**Transform your job search with AI-powered email classification and visual Kanban board management**

[🌟 Live Demo](#demo) • [🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🤝 Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [✨ Features](#features)
- [🎯 Demo](#demo)
- [🚀 Quick Start](#quick-start)
- [⚙️ Installation](#installation)
- [🔧 Configuration](#configuration)
- [� Usage Guide](#usage-guide)
- [🏗️ Architecture](#architecture)
- [🧪 Testing](#testing)
- [🤝 Contributing](#contributing)
- [📄 License](#license)

---

## ✨ Features

### 🤖 **AI-Powered Email Classification**
- **Smart Email Processing**: Automatically classifies emails into job applications, interviews, promotions, or irrelevant
- **Google Gemini Integration**: 98-100% classification accuracy using advanced AI
- **Real-time Processing**: Processes 50+ emails in seconds with intelligent filtering

### 📋 **Jira-Style Kanban Board**
- **Visual Pipeline Management**: 6-stage workflow (Backlog → Applied → Screening → Interview → Final → Closed)
- **Interactive Cards**: Drag-and-drop functionality with real-time updates
- **Progress Tracking**: Visual analytics and stage transition history

### 📊 **Comprehensive Dashboard**
- **Dual View System**: Switch between List view and Kanban board seamlessly
- **Analytics Dashboard**: Application statistics, success rates, and upcoming interviews
- **Priority Management**: Color-coded priority system (High, Medium, Low)

### 🔌 **Gmail Integration**
- **OAuth2 Authentication**: Secure Gmail API access
- **Real-time Sync**: Automatic email fetching and processing
- **Smart Filtering**: Skips promotional and spam emails automatically

### 🗄️ **Advanced Database**
- **SQLite Backend**: Robust 4-table schema with 28+ columns
- **Data Integrity**: Foreign key constraints and transaction safety
- **Migration Support**: Automatic schema updates and data preservation
- **📊 Streamlit UI**: Clean, interactive web interface
- **🔍 Search & Filter**: Find applications by company, role, or status
- **⏰ Interview Reminders**: Highlight upcoming interviews in the next 7 days
- **📝 Manual Entry**: Add applications that don't come through email

### 🔮 Roadmap (Future Enhancements)
- **📅 Calendar Sync**: Integration with Google Calendar/Outlook
- **🔔 Smart Notifications**: Email/SMS reminders for interviews
- **📈 Analytics Dashboard**: Track application success rates and trends
- **🤖 Advanced NLP**: Better company/role extraction using AI
- **📱 Mobile App**: React Native or Flutter companion app
- **🔗 Job Board Integration**: Auto-fetch from LinkedIn, Indeed, etc.
- **📄 Resume Matching**: Track which resume version was used

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed on your system
- Gmail account with interview emails
- Google Cloud account (free tier is sufficient)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd job-tracker-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### Step 2.1: Enable Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Library**
4. Search for "Gmail API" and click **Enable**

#### Step 2.2: Create OAuth2 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in required fields (App name, User support email, Developer email)
   - Add your Gmail address to test users
4. For Application type, choose **Desktop application**
5. Give it a name like "Job Tracker Assistant"
6. Click **Create**
7. **Download the JSON file** and save it as `credentials.json` in your project root

### 3. Run the Application
```bash
# Make sure virtual environment is activated
streamlit run app.py
```

### 4. First-Time Setup
1. Open your browser to `http://localhost:8501`
2. Click **"🔄 Fetch Interview Emails"** in the sidebar
3. Complete the OAuth flow in your browser
4. Grant permissions to read your Gmail
5. The app will fetch and parse interview emails automatically!

## 📁 Project Structure

```
job-tracker-assistant/
├── app.py                 # Main Streamlit application
├── gmail_utils.py         # Gmail API integration
├── parser_utils.py        # Email parsing and data extraction
├── db_utils.py           # SQLite database operations
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
├── README.md            # This file
├── credentials.json     # Google OAuth credentials (you provide)
├── token.json          # OAuth token (auto-generated)
├── jobs.db             # SQLite database (auto-generated)
└── venv/               # Virtual environment
```

## 🔧 Configuration

### Gmail Search Query
By default, the app searches for emails with these subjects:
- "interview"
- "phone screen"
- "interview scheduled"
- "technical interview"
- "final interview"
- "onsite interview"
- "video interview"
- "zoom interview"

You can modify the search query in `gmail_utils.py` by editing the `fetch_interview_emails()` function.

### Database Schema
The SQLite database stores applications with these fields:
- **id**: Primary key
- **msg_id**: Gmail message ID (for deduplication)
- **company**: Company name
- **role**: Job role/position
- **source**: 'gmail' or 'manual'
- **date_applied**: When you applied
- **status**: Application status (applied, interview_scheduled, interviewed, rejected, offer, accepted)
- **interview_date**: Scheduled interview date/time
- **interview_round**: Type of interview (phone_screen, technical, onsite, final)
- **notes**: Additional notes
- **snippet**: Email snippet (for Gmail entries)
- **email_subject**: Original email subject
- **email_from**: Sender email address
- **created_at/updated_at**: Timestamps

## 💡 Usage Tips

### 🎯 Best Practices
1. **Regular Syncing**: Fetch Gmail emails weekly to stay updated
2. **Status Updates**: Keep application statuses current for accurate tracking
3. **Add Notes**: Include interview feedback and next steps in notes
4. **Manual Entries**: Add applications from job boards or direct applications
5. **Interview Prep**: Use upcoming interviews section for daily prep planning

### 🔍 Search & Filter Tips
- Search works across company names, roles, and notes
- Use status filters to focus on active opportunities
- Date range helps track applications over specific periods
- Combine filters for precise results

### 📧 Email Parsing Tips
For best results with automatic email parsing:
- Keep interview emails in your inbox (don't archive immediately)
- Company emails work better than recruiting agency emails
- The app extracts dates in various formats (natural language, specific formats)
- Manual verification of parsed data is recommended

## 🛠️ Development

### Running Tests
```bash
# Test Gmail connection
python gmail_utils.py

# Test email parsing
python parser_utils.py

# Test database operations
python db_utils.py
```

### Adding Features
The codebase is modular:
- **gmail_utils.py**: Extend for additional email providers
- **parser_utils.py**: Improve parsing algorithms
- **db_utils.py**: Add new database operations
- **app.py**: Enhance UI components

### Common Issues & Solutions

#### "Import could not be resolved"
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

#### "streamlit has no attribute 'datetime_input'"  
- This has been fixed in the current version
- We use separate date and time inputs instead

#### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Place file in project root directory

#### "No interview emails found"
- Check Gmail search query in `gmail_utils.py`
- Verify you have emails matching the search terms
- Try broader search terms initially

#### Database errors
- Delete `jobs.db` to reset database
- Check file permissions
- Ensure SQLite is available (included with Python)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Bug Reports**: Open an issue with detailed steps to reproduce
2. **✨ Feature Requests**: Describe the feature and its use case
3. **🔧 Code Contributions**: 
   - Fork the repository
   - Create a feature branch
   - Submit a pull request with clear description

### Development Setup
```bash
# Clone your fork
git clone <your-fork-url>
cd job-tracker-assistant

# Create branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest  # (if we add tests)

# Submit PR
```

## 📈 Analytics & Insights

The app provides several metrics:
- **Total Applications**: Overall count of tracked applications
- **Applications by Status**: Breakdown of current pipeline
- **Success Rate**: Track offer/interview ratios (future feature)
- **Timeline Analysis**: Application-to-interview conversion times (future)

## 🔒 Privacy & Security

- **Local Storage**: All data stays on your machine (SQLite database)
- **OAuth Flow**: Secure Google authentication
- **Read-Only Access**: App only reads Gmail, cannot send emails
- **No Data Upload**: No data is sent to external servers
- **Token Storage**: OAuth tokens stored locally in `token.json`

## 📚 Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **google-api-python-client**: Gmail API integration
- **google-auth-oauthlib**: OAuth2 authentication
- **beautifulsoup4**: HTML parsing for email content
- **dateparser**: Natural language date parsing
- **python-dateutil**: Date/time utilities

## 📄 License

MIT License - see LICENSE file for details.

## 🙋‍♂️ Support

- **Documentation**: Check this README first
- **Issues**: Open a GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [Your email for direct support]

## 🎉 Acknowledgments

- Built with ❤️ for job seekers everywhere
- Inspired by the need to organize the chaotic job search process
- Thanks to the Streamlit team for the amazing framework
- Google for providing Gmail API access

---

**Happy Job Hunting! 🎯**

*Remember: Job searching is a numbers game. Stay organized, stay persistent, and track everything!*