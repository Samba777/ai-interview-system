"""
Feedback Generation Module
Calculates scores and generates AI feedback using Gemini
"""

from config.database import DatabaseSession
from models.database_models import Interview, Question, Response, Feedback
from config.gemini_config import GeminiConfig
import json


class FeedbackGenerator:
    """
    Generates comprehensive interview feedback
    """
    
    def __init__(self):
        self.gemini = GeminiConfig()
    
    def calculate_overall_score(self, interview_id):
        """
        Calculate overall interview score from all responses
        
        Args:
            interview_id: ID of interview
        
        Returns:
            dict with scores
        """
        with DatabaseSession() as session:
            responses = session.query(Response).filter_by(
                interview_id=interview_id
            ).all()
            
            if not responses:
                return None
            
            total_questions = len(responses)
            
            # Initialize totals
            total_audio_score = 0
            total_video_score = 0
            total_content_score = 0
            
            audio_count = 0
            video_count = 0
            content_count = 0
            
            # Calculate averages
            for response in responses:
                # Audio metrics (sentiment + grammar)
                if response.sentiment_score is not None and response.grammar_score is not None:
                    audio_score = (
                        response.sentiment_score * 0.5 +
                        response.grammar_score * 0.5
                    )
                    total_audio_score += audio_score
                    audio_count += 1
                
                # Video metrics
                if response.eye_contact_score is not None:
                    total_video_score += response.eye_contact_score
                    video_count += 1
                
                # Content metrics
                if response.keyword_match_score is not None:
                    total_content_score += response.keyword_match_score
                    content_count += 1
            
            # Calculate averages
            avg_audio = (total_audio_score / audio_count) if audio_count > 0 else 0
            avg_video = (total_video_score / video_count) if video_count > 0 else 0
            avg_content = (total_content_score / content_count) if content_count > 0 else 0
            
            # Overall score (weighted average)
            overall_score = (
                avg_content * 0.5 +   # Content most important
                avg_audio * 0.3 +     # Audio quality
                avg_video * 0.2       # Video presence
            )
            
            return {
                'overall_score': round(overall_score, 2),
                'content_score': round(avg_content, 2),
                'audio_score': round(avg_audio, 2),
                'video_score': round(avg_video, 2),
                'total_questions': total_questions
            }
    
    def get_question_wise_analysis(self, interview_id):
        """
        Get detailed analysis for each question
        
        Args:
            interview_id: ID of interview
        
        Returns:
            list of question analyses
        """
        with DatabaseSession() as session:
            responses = session.query(Response).filter_by(
                interview_id=interview_id
            ).all()
            
            analyses = []
            
            for response in responses:
                question = session.query(Question).filter_by(
                    id=response.question_id
                ).first()
                
                analysis = {
                    'question_number': question.question_number,
                    'question_text': question.question_text,
                    'user_answer': response.transcript,
                    'keyword_match': response.keyword_match_score or 0,
                    'sentiment': response.sentiment_label or 'N/A',
                    'grammar': response.grammar_score or 0,
                    'eye_contact': response.eye_contact_score or 0,
                    'matched_keywords': response.matched_keywords or []
                }
                
                analyses.append(analysis)
            
            return analyses
    
    def generate_ai_feedback(self, interview_id):
        """
        Generate personalized feedback using Gemini
        
        Args:
            interview_id: ID of interview
        
        Returns:
            dict with AI-generated feedback
        """
        # Get scores and analysis
        scores = self.calculate_overall_score(interview_id)
        question_analysis = self.get_question_wise_analysis(interview_id)
        
        if not scores:
            return None
        
        # Create prompt for Gemini
        prompt = f"""
You are an expert interview coach. Analyze this interview performance and provide constructive feedback.

Overall Scores:
- Content Knowledge: {scores['content_score']:.0f}%
- Communication Quality: {scores['audio_score']:.0f}%  
- Professional Presence: {scores['video_score']:.0f}%
- Overall Score: {scores['overall_score']:.0f}%

Question-wise Performance:
"""
        
        for q in question_analysis:
            prompt += f"""
Question {q['question_number']}: {q['question_text']}
- Keyword Match: {q['keyword_match']:.0f}%
- Sentiment: {q['sentiment']}
- Grammar: {q['grammar']:.0f}%
- Eye Contact: {q['eye_contact']:.0f}%
"""
        
        prompt += """

Provide feedback in this EXACT JSON format:
{
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["actionable tip 1", "actionable tip 2", "actionable tip 3"],
    "overall_comment": "2-3 sentence summary"
}

Be specific, encouraging, and actionable. Focus on concrete improvements.
"""
        
        # Generate feedback
        try:
            response = self.gemini.generate_content(prompt)
            
            # Handle different response types
            if hasattr(response, 'text'):
                feedback_text = response.text
            elif isinstance(response, str):
                feedback_text = response
            else:
                feedback_text = str(response)
            
            # Clean the response (remove markdown code blocks if present)
            feedback_text = feedback_text.strip()
            if feedback_text.startswith('```json'):
                feedback_text = feedback_text[7:]
            if feedback_text.startswith('```'):
                feedback_text = feedback_text[3:]
            if feedback_text.endswith('```'):
                feedback_text = feedback_text[:-3]
            feedback_text = feedback_text.strip()
            
            feedback_json = json.loads(feedback_text)
            
            return feedback_json
        
        except Exception as e:
            print(f"Error generating AI feedback: {e}")
            return {
                'strengths': ['Completed the interview', 'Answered all questions'],
                'weaknesses': ['Analysis could not be completed'],
                'recommendations': ['Try regenerating feedback', 'Review your answers manually'],
                'overall_comment': 'Feedback generation encountered an issue. Please try regenerating.'
            }
    
    def save_feedback(self, interview_id):
        """
        Calculate scores, generate feedback, and save to database
        
        Args:
            interview_id: ID of interview
        
        Returns:
            feedback_id if success, None if failed
        """
        try:
            # Calculate scores
            scores = self.calculate_overall_score(interview_id)
            if not scores:
                return None
            
            # Get question analysis
            question_analysis = self.get_question_wise_analysis(interview_id)
            
            # Generate AI feedback
            ai_feedback = self.generate_ai_feedback(interview_id)
            
            # Save to database
            with DatabaseSession() as session:
                # Check if feedback already exists
                existing = session.query(Feedback).filter_by(
                    interview_id=interview_id
                ).first()
                
                if existing:
                    # Update existing
                    existing.overall_score = scores['overall_score']
                    existing.content_score = scores['content_score']
                    existing.audio_score = scores['audio_score']
                    existing.video_score = scores['video_score']
                    existing.strengths = '\n'.join(ai_feedback.get('strengths', []))
                    existing.weaknesses = '\n'.join(ai_feedback.get('weaknesses', []))
                    existing.recommendations = '\n'.join(ai_feedback.get('recommendations', []))
                    existing.question_wise_analysis = question_analysis
                    
                    session.commit()
                    return existing.id
                
                else:
                    # Create new
                    feedback = Feedback(
                        interview_id=interview_id,
                        overall_score=scores['overall_score'],
                        content_score=scores['content_score'],
                        audio_score=scores['audio_score'],
                        video_score=scores['video_score'],
                        strengths='\n'.join(ai_feedback.get('strengths', [])),
                        weaknesses='\n'.join(ai_feedback.get('weaknesses', [])),
                        recommendations='\n'.join(ai_feedback.get('recommendations', [])),
                        question_wise_analysis=question_analysis
                    )
                    
                    session.add(feedback)
                    session.flush()
                    
                    return feedback.id
        
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return None