# Required Dependencies for Interview Intelligence Features

## 🔧 **Current Dependencies (Already Available)**
```
google-api-python-client==2.108.0  # Gmail integration
google-auth-httplib2==0.1.1        # Gmail auth
google-auth-oauthlib==1.1.0         # Gmail auth
beautifulsoup4==4.12.2              # Basic HTML parsing
streamlit==1.28.1                   # UI framework
pandas==2.1.3                       # Data manipulation
dateparser==1.1.8                   # Date parsing
python-dateutil==2.8.2              # Date utilities
```

## 📦 **New Dependencies to Add**

### **Stage 1: MVP - Basic Intelligence (Week 1-2)**
```
# Web scraping and data collection
requests==2.31.0                    # HTTP requests for web scraping
selenium==4.15.0                    # Dynamic content scraping (Glassdoor, LinkedIn)
webdriver-manager==4.0.1            # Auto-manage browser drivers
lxml==4.9.3                         # Fast XML/HTML parsing
fake-useragent==1.4.0               # Rotate user agents for scraping

# AI and text processing (beyond existing Gemini)
google-generativeai>=0.3.0          # Latest Gemini API (upgrade existing)
openai==1.3.5                       # Backup AI option (optional)
nltk==3.8.1                         # Natural language processing
spacy==3.7.2                        # Advanced NLP for text analysis
textblob==0.17.1                    # Sentiment analysis and text processing

# Data processing and analysis
numpy==1.24.3                       # Numerical computations
scikit-learn==1.3.2                 # Machine learning for pattern analysis
python-dotenv==1.0.0                # Environment variable management
```

### **Stage 2: Enhanced Intelligence (Week 3-4)**
```
# Advanced web scraping and data sources
scrapy==2.11.0                      # Industrial-strength web scraping
playwright==1.40.0                  # Modern browser automation (faster than Selenium)
aiohttp==3.9.0                      # Async HTTP requests for faster scraping
asyncio-throttle==1.0.2             # Rate limiting for async requests

# Data storage and caching
redis==5.0.1                        # Fast caching for scraped data
cachetools==5.3.2                   # Memory caching utilities
sqlalchemy==2.0.23                  # Advanced database operations (optional upgrade)

# Text analysis and intelligence
transformers==4.35.0                # Pre-trained models for text analysis
sentence-transformers==2.2.2        # Semantic text similarity
wordcloud==1.9.2                    # Text visualization
pyLDAvis==3.4.0                     # Topic modeling visualization
```

### **Stage 3: AI Practice Sessions (Week 5-6)**
```
# Speech processing for interview simulation
speech-recognition==3.10.0          # Speech-to-text for verbal practice
pyttsx3==2.90                       # Text-to-speech for AI responses
pyaudio==0.2.11                     # Audio processing
sounddevice==0.4.6                  # Audio recording/playback

# Advanced AI for interactive sessions
langchain==0.0.340                  # AI workflow orchestration
tiktoken==0.5.1                     # Token counting for AI APIs
anthropic==0.7.7                    # Claude API (alternative to Gemini)

# Performance tracking and analytics
matplotlib==3.8.0                   # Basic plotting for progress charts
plotly==5.17.0                      # Interactive charts for analytics
seaborn==0.12.2                     # Statistical data visualization
```

### **Stage 4: Advanced Features (Week 7-8)**
```
# LinkedIn and social media APIs
linkedin-api==2.2.0                 # LinkedIn data access (unofficial)
tweepy==4.14.0                      # Twitter API for company sentiment
facebook-sdk==3.1.0                 # Facebook API for company data

# Advanced machine learning
xgboost==2.0.1                      # Gradient boosting for outcome prediction
lightgbm==4.1.0                     # Fast gradient boosting
joblib==1.3.2                       # Model persistence and parallel processing

# Workflow and scheduling
celery==5.3.4                       # Background task processing
schedule==1.2.0                     # Task scheduling
apscheduler==3.10.4                 # Advanced scheduling

# Monitoring and logging
loguru==0.7.2                       # Advanced logging
prometheus-client==0.19.0           # Metrics collection
structlog==23.2.0                   # Structured logging
```

---

## 📋 **Updated requirements.txt**

```txt
# Existing dependencies
google-api-python-client==2.108.0
google-auth-httplib2==0.1.1
google-auth-oauthlib==1.1.0
beautifulsoup4==4.12.2
streamlit==1.28.1
pandas==2.1.3
dateparser==1.1.8
python-dateutil==2.8.2

# Stage 1: MVP Intelligence Features
requests==2.31.0
selenium==4.15.0
webdriver-manager==4.0.1
lxml==4.9.3
fake-useragent==1.4.0
google-generativeai>=0.3.0
nltk==3.8.1
textblob==0.17.1
numpy==1.24.3
python-dotenv==1.0.0
cachetools==5.3.2

# Stage 2: Enhanced Intelligence (add when needed)
# scrapy==2.11.0
# playwright==1.40.0
# aiohttp==3.9.0
# asyncio-throttle==1.0.2
# redis==5.0.1
# transformers==4.35.0
# sentence-transformers==2.2.2

# Stage 3: AI Practice Sessions (add when needed)
# speech-recognition==3.10.0
# pyttsx3==2.90
# langchain==0.0.340
# matplotlib==3.8.0
# plotly==5.17.0

# Stage 4: Advanced Features (add when needed)
# xgboost==2.0.1
# celery==5.3.4
# schedule==1.2.0
# loguru==0.7.2
```

---

## ⚡ **Installation Strategy**

### **Immediate Setup (Stage 1):**
```bash
pip install requests selenium webdriver-manager lxml fake-useragent nltk textblob numpy python-dotenv cachetools
pip install --upgrade google-generativeai
```

### **Progressive Installation:**
- Install dependencies only when implementing each stage
- Avoid dependency bloat early in development
- Test each stage thoroughly before adding more dependencies

### **Optional Dependencies:**
```bash
# For better performance (optional)
pip install uvloop  # Faster event loop for async operations
pip install orjson  # Faster JSON processing
pip install httpx   # Modern HTTP client (alternative to requests)
```

---

## 🔒 **Security and Environment Setup**

### **Environment Variables Needed:**
```bash
# Existing
GEMINI_API_KEY=your_gemini_api_key

# New for Stage 1
SCRAPING_USER_AGENT=your_custom_user_agent
SCRAPING_DELAY_MIN=1
SCRAPING_DELAY_MAX=3
CACHE_TTL_SECONDS=3600

# Optional for advanced features
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
LINKEDIN_USERNAME=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
```

### **Development Environment Setup:**
```bash
# Create virtual environment
python -m venv interview_intelligence_env
source interview_intelligence_env/bin/activate  # Linux/Mac
# or
interview_intelligence_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Download required models
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 🎯 **Dependency Management Strategy**

### **Stage-Based Installation:**
1. **Week 1:** Install only Stage 1 dependencies
2. **Week 3:** Add Stage 2 dependencies when implementing enhanced features
3. **Week 5:** Add Stage 3 dependencies for practice sessions
4. **Week 7:** Add Stage 4 dependencies for advanced features

### **Performance Considerations:**
- Use `cachetools` for in-memory caching (Stage 1)
- Add `redis` for persistent caching (Stage 2)
- Use `asyncio` for concurrent scraping (Stage 2)
- Implement proper rate limiting to avoid being blocked

### **Fallback Strategy:**
- If Gemini API fails → Use OpenAI as backup
- If Selenium fails → Use requests + BeautifulSoup
- If advanced NLP fails → Use simple text processing
- Always have graceful degradation

---

## 🚀 **Ready to Start Implementation**

**Next Steps:**
1. Update requirements.txt with Stage 1 dependencies
2. Install new packages in development environment
3. Create basic intelligence_engine.py
4. Test web scraping with simple examples
5. Integrate with existing Kanban board

**Would you like me to start implementing Stage 1 with these dependencies?**