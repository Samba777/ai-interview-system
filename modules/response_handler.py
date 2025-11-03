"""
Response Handler Module
Saves user responses to database
"""

from config.database import DatabaseSession
from models.database_models import Response
from datetime import datetime


def save_response(interview_id, question_id, transcript, audio_metrics=None, video_metrics=None):
    """
    Save user's response to database
    
    Args:
        interview_id: ID of current interview
        question_id: ID of the question being answered
        transcript: User's answer text (from audio or typed)
        audio_metrics: Dictionary with audio analysis metrics
        video_metrics: Dictionary with video analysis metrics
    
    Returns:
        response_id if success, None if failed
    """
    try:
        with DatabaseSession() as session:
            # Create Response object
            response = Response(
                interview_id=interview_id,
                question_id=question_id,
                transcript=transcript
            )
            
            # Add audio metrics if available
            if audio_metrics:
                response.sentiment_score = audio_metrics.get('sentiment_score')
                response.sentiment_label = audio_metrics.get('sentiment_label')
                response.keyword_match_score = audio_metrics.get('keyword_match_score')
                response.matched_keywords = audio_metrics.get('matched_keywords')
                response.grammar_score = audio_metrics.get('grammar_score')
            
            # Add video metrics if available
            if video_metrics:
                response.eye_contact_score = video_metrics.get('eye_contact_score')
                response.gaze_violations = video_metrics.get('gaze_violations')
                response.violation_timestamps = video_metrics.get('violation_details')
            
            # Save to database
            session.add(response)
            session.flush()
            
            return response.id
    
    except Exception as e:
        print(f"❌ Error saving response: {e}")
        return None