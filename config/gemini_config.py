"""
Gemini AI Configuration
Singleton pattern for API client
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class GeminiConfig:
    """
    Singleton class for Gemini API
    Only one instance throughout the app
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Gemini API - only once!"""
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file!")
        
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel('models/gemini-2.5-flash')        
        print("✅ Gemini API connected!")
    
    def generate_content(self, prompt):
        """Generate content using Gemini"""
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return None


# Test function
if __name__ == "__main__":
    gemini = GeminiConfig()
    result = gemini.generate_content("Say hello!")
    print(result)