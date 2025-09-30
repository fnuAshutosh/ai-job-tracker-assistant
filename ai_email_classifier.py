"""
AI-powered email classification using Google Gemini API
Intelligent detection of job-related emails vs promotional/spam content
"""

import os
import json
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Install with: pip install google-generativeai")


@dataclass
class EmailClassification:
    """Results of email classification"""
    category: str  # 'job_interview', 'job_application', 'promotional', 'irrelevant'
    confidence: float  # 0.0 to 1.0
    reasoning: str
    company: Optional[str] = None
    role: Optional[str] = None
    interview_scheduled: bool = False
    status_suggestion: str = 'applied'


class GeminiEmailClassifier:
    """AI-powered email classifier using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini classifier with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if not self.api_key:
            print("Warning: No Gemini API key found. Set GEMINI_API_KEY environment variable or pass api_key parameter")
            print("Get your API key from: https://makersuite.google.com/app/apikey")
            return
            
        if not GEMINI_AVAILABLE:
            print("Error: google-generativeai package not installed")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            # Use the current stable model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("Gemini AI classifier initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.model = None
    
    def classify_email(self, email_data: Dict[str, Any]) -> EmailClassification:
        """
        Classify email using AI
        
        Args:
            email_data: Dict containing 'subject', 'from', 'body', 'snippet'
            
        Returns:
            EmailClassification: Classification results
        """
        if not self.model:
            # Fallback to rule-based classification
            return self._fallback_classification(email_data)
        
        try:
            # Prepare email content for AI analysis
            email_content = self._prepare_email_content(email_data)
            
            # Create AI prompt
            prompt = self._create_classification_prompt(email_content)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            print(f"AI classification failed: {e}")
            print("🔄 Falling back to rule-based classification")
            return self._fallback_classification(email_data)
    
    def _prepare_email_content(self, email_data: Dict[str, Any]) -> str:
        """Prepare email content for AI analysis"""
        subject = email_data.get('subject', '')
        from_email = email_data.get('from', '')
        body = email_data.get('body', '')
        snippet = email_data.get('snippet', '')
        
        # Use body if available, otherwise use snippet
        content = body if body and len(body) > len(snippet) else snippet
        
        # Limit content length to avoid token limits
        if len(content) > 2000:
            content = content[:2000] + "... [truncated]"
        
        return f"""
Email Analysis Request:

From: {from_email}
Subject: {subject}
Content: {content}
        """.strip()
    
    def _create_classification_prompt(self, email_content: str) -> str:
        """Create detailed prompt for AI classification"""
        return f"""
You are an expert email classifier for a job application tracking system. Analyze the following email and provide a detailed classification.

{email_content}

Please analyze this email and respond with a JSON object containing:

1. "category": One of:
   - "job_interview": Email is scheduling/confirming an actual job interview
   - "job_application": Email is about a job application (confirmation, status update)
   - "promotional": Email is promotional/marketing from job boards, recruiting agencies
   - "irrelevant": Email is not related to job searching

2. "confidence": Float between 0.0 and 1.0 indicating your confidence in the classification

3. "reasoning": Brief explanation of your classification decision

4. "company": The actual company name (not job board) if identifiable, or null

5. "role": The job role/position if mentioned, or null

6. "interview_scheduled": Boolean - true if this email is scheduling a specific interview

7. "status_suggestion": One of "applied", "interview_scheduled", "interviewed", "rejected", "offer", "accepted"

Focus on:
- Is this from an actual company or a job board/recruiting platform?
- Does it contain specific interview scheduling details?
- Is the language personalized or generic/mass-marketing?
- Are there specific company names, roles, interview times mentioned?

Respond ONLY with valid JSON, no other text.
        """
    
    def _parse_ai_response(self, response_text: str) -> EmailClassification:
        """Parse AI response into EmailClassification object"""
        try:
            # Clean up response text (remove markdown formatting if present)
            clean_response = response_text.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response.replace('```json', '').replace('```', '').strip()
            elif clean_response.startswith('```'):
                clean_response = clean_response.replace('```', '').strip()
            
            # Parse JSON
            result = json.loads(clean_response)
            
            return EmailClassification(
                category=result.get('category', 'irrelevant'),
                confidence=float(result.get('confidence', 0.5)),
                reasoning=result.get('reasoning', 'AI classification'),
                company=result.get('company'),
                role=result.get('role'),
                interview_scheduled=bool(result.get('interview_scheduled', False)),
                status_suggestion=result.get('status_suggestion', 'applied')
            )
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response was: {response_text[:200]}...")
            return self._create_fallback_classification("AI parsing error")
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._create_fallback_classification("AI response error")
    
    def _fallback_classification(self, email_data: Dict[str, Any]) -> EmailClassification:
        """Rule-based fallback classification when AI is not available"""
        subject = email_data.get('subject', '').lower()
        from_email = email_data.get('from', '').lower()
        content = (email_data.get('body', '') or email_data.get('snippet', '')).lower()
        
        # Simple rule-based classification
        full_content = f"{subject} {content}"
        
        # Check for obvious promotional indicators
        promotional_indicators = [
            'job alert', 'job recommendation', 'unsubscribe', 'click here to apply',
            'thousands of jobs', 'job match', 'career newsletter', 'job digest'
        ]
        
        if any(indicator in full_content for indicator in promotional_indicators):
            return EmailClassification(
                category='promotional',
                confidence=0.8,
                reasoning='Rule-based: Contains promotional keywords',
                status_suggestion='applied'
            )
        
        # Check for interview scheduling
        interview_indicators = [
            'interview scheduled', 'interview confirmed', 'please join',
            'zoom link', 'meeting link', 'interview invitation'
        ]
        
        if any(indicator in full_content for indicator in interview_indicators):
            return EmailClassification(
                category='job_interview',
                confidence=0.7,
                reasoning='Rule-based: Contains interview scheduling keywords',
                interview_scheduled=True,
                status_suggestion='interview_scheduled'
            )
        
        # Default to job application related
        return EmailClassification(
            category='job_application',
            confidence=0.6,
            reasoning='Rule-based: Appears job-related but unclear type',
            status_suggestion='applied'
        )
    
    def _create_fallback_classification(self, reason: str) -> EmailClassification:
        """Create a fallback classification when AI fails"""
        return EmailClassification(
            category='irrelevant',
            confidence=0.3,
            reasoning=f'Fallback classification: {reason}',
            status_suggestion='applied'
        )


def setup_gemini_api_key():
    """Interactive setup for Gemini API key"""
    print("🔑 Gemini API Key Setup")
    print("-" * 30)
    print("To use AI-powered email classification, you need a Gemini API key.")
    print("Get your free API key from: https://makersuite.google.com/app/apikey")
    print()
    
    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Save to environment file
        env_file = '.env'
        with open(env_file, 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print(f"API key saved to {env_file}")
        os.environ['GEMINI_API_KEY'] = api_key
        return api_key
    else:
        print("Skipping API key setup. Will use rule-based classification.")
        return None


# Global classifier instance
_classifier_instance = None

def get_email_classifier() -> GeminiEmailClassifier:
    """Get or create the global email classifier instance"""
    global _classifier_instance
    
    if _classifier_instance is None:
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("[INFO] No Gemini API key found in environment")
            setup_response = input("Would you like to set up Gemini API key now? (y/n): ").lower()
            if setup_response == 'y':
                api_key = setup_gemini_api_key()
        
        _classifier_instance = GeminiEmailClassifier(api_key)
    
    return _classifier_instance


if __name__ == "__main__":
    # Test the AI classifier
    print("🧪 Testing AI Email Classifier")
    print("=" * 40)
    
    # Test cases
    test_emails = [
        {
            'subject': 'Interview Invitation - Senior Software Engineer at Google',
            'from': 'recruiter@google.com',
            'body': 'Hi John, Thank you for your interest in the Senior Software Engineer position at Google. We would like to schedule a technical interview with you for this Tuesday, October 1st at 2:00 PM PST. Please confirm your availability. The interview will be conducted via Google Meet and will focus on system design and coding problems. Best regards, Sarah Chen, Technical Recruiter',
            'snippet': 'Interview invitation for Tuesday at 2 PM'
        },
        {
            'subject': 'Job Alert: 1000+ Software Developer Jobs Available Now!',
            'from': 'alerts@naukri.com',
            'body': 'Dear Job Seeker, We have found 1000+ new software developer jobs matching your profile! Click here to apply now. Get instant job alerts. Unsubscribe here if you no longer wish to receive these alerts.',
            'snippet': 'Job alert with 1000+ jobs available'
        },
        {
            'subject': 'Application Status Update - Data Scientist Role',
            'from': 'hr@startup.ai',
            'body': 'Hello, Thank you for applying to our Data Scientist position. Your application is currently under review by our hiring team. We will get back to you within 5-7 business days with next steps.',
            'snippet': 'Application under review, will hear back in 5-7 days'
        }
    ]
    
    classifier = get_email_classifier()
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Test Email {i}:")
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        
        result = classifier.classify_email(email)
        
        print(f"🤖 AI Classification:")
        print(f"   Category: {result.category}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Reasoning: {result.reasoning}")
        print(f"   Company: {result.company}")
        print(f"   Role: {result.role}")
        print(f"   Interview Scheduled: {result.interview_scheduled}")
        print(f"   Status Suggestion: {result.status_suggestion}")