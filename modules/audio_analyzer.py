"""
Audio Analyzer Module
Analyzes transcript for sentiment, keywords, and grammar
"""

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
import re


class AudioAnalyzer:
    """
    Singleton class for audio analysis
    """
    
    _instance = None
    _sentiment_analyzer = None
    _similarity_model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioAnalyzer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize analyzers - only once"""
        print("Loading audio analysis models...")
        self._sentiment_analyzer = SentimentIntensityAnalyzer()
        self._similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Audio analysis models loaded!")
    
    def analyze_sentiment(self, transcript):
        """
        Analyze sentiment using VADER
        
        Returns:
            dict with sentiment_score and sentiment_label
        """
        try:
            scores = self._sentiment_analyzer.polarity_scores(transcript)
            compound = scores['compound']
            
            # Determine label
            if compound >= 0.05:
                label = "Positive"
            elif compound <= -0.05:
                label = "Negative"
            else:
                label = "Neutral"
            
            return {
                'sentiment_score': compound,
                'sentiment_label': label
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {'sentiment_score': 0.0, 'sentiment_label': 'Neutral'}
    
    def check_grammar(self, transcript):
        """
        Basic grammar check using TextBlob
        
        Returns:
            grammar_score (0-100)
        """
        try:
            blob = TextBlob(transcript)
            
            # Check for basic issues
            words = len(transcript.split())
            if words == 0:
                return 0.0
            
            # Corrected text
            corrected = str(blob.correct())
            
            # Calculate similarity (how much was corrected)
            if transcript == corrected:
                score = 100.0  # Perfect grammar
            else:
                # Simple ratio of unchanged words
                original_words = set(transcript.lower().split())
                corrected_words = set(corrected.lower().split())
                unchanged = len(original_words & corrected_words)
                score = (unchanged / words) * 100
            
            return round(score, 2)
        
        except Exception as e:
            print(f"Error in grammar check: {e}")
            return 75.0  # Default average score
    
    def match_keywords(self, user_transcript, reference_answer, expected_keywords):
        """
        Match keywords and calculate similarity
        
        Returns:
            dict with keyword_match_score, matched_keywords, semantic_similarity
        """
        try:
            user_lower = user_transcript.lower()
            
            # Check which expected keywords are mentioned
            matched = []
            for keyword in expected_keywords:
                if keyword.lower() in user_lower:
                    matched.append(keyword)
            
            # Keyword match percentage
            if len(expected_keywords) > 0:
                keyword_match = (len(matched) / len(expected_keywords)) * 100
            else:
                keyword_match = 50.0
            
            # Semantic similarity using sentence transformers
            user_embedding = self._similarity_model.encode(user_transcript, convert_to_tensor=True)
            ref_embedding = self._similarity_model.encode(reference_answer, convert_to_tensor=True)
            similarity = util.cos_sim(user_embedding, ref_embedding).item()
            
            # Convert to percentage
            semantic_score = round(similarity * 100, 2)
            
            return {
                'keyword_match_score': round(keyword_match, 2),
                'matched_keywords': matched,
                'semantic_similarity': semantic_score
            }
        
        except Exception as e:
            print(f"Error in keyword matching: {e}")
            return {
                'keyword_match_score': 0.0,
                'matched_keywords': [],
                'semantic_similarity': 0.0
            }
    
    def analyze_complete(self, transcript, reference_answer, expected_keywords):
        """
        Complete analysis of transcript
        
        Returns:
            dict with all metrics
        """
        sentiment = self.analyze_sentiment(transcript)
        grammar = self.check_grammar(transcript)
        keywords = self.match_keywords(transcript, reference_answer, expected_keywords)
        
        return {
            'sentiment_score': sentiment['sentiment_score'],
            'sentiment_label': sentiment['sentiment_label'],
            'grammar_score': grammar,
            'keyword_match_score': keywords['keyword_match_score'],
            'matched_keywords': keywords['matched_keywords'],
            'semantic_similarity': keywords['semantic_similarity']
        }


# Test function
if __name__ == "__main__":
    analyzer = AudioAnalyzer()
    
    test_transcript = "Machine learning is a subset of artificial intelligence that uses algorithms to learn from data."
    test_reference = "Machine learning is part of AI that enables systems to learn and improve from experience."
    test_keywords = ["machine learning", "AI", "algorithms", "data"]
    
    results = analyzer.analyze_complete(test_transcript, test_reference, test_keywords)
    
    print("\n=== Analysis Results ===")
    print(f"Sentiment: {results['sentiment_label']} ({results['sentiment_score']})")
    print(f"Grammar Score: {results['grammar_score']}%")
    print(f"Keyword Match: {results['keyword_match_score']}%")
    print(f"Matched Keywords: {results['matched_keywords']}")
    print(f"Semantic Similarity: {results['semantic_similarity']}%")