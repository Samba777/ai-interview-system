"""
Question Generator Module
Generates interview questions using Gemini AI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.gemini_config import GeminiConfig
import json


def generate_interview_questions(user_profile):
    """
    Generate 5 interview questions based on user profile
    
    Args:
        user_profile: dict with user info (role, domain, skills, experience)
    
    Returns:
        list of question dicts or None if failed
    """
    
    # Create prompt for Gemini
    prompt = f"""
You are an expert interviewer. Generate exactly 5 interview questions for a candidate with this profile:
Role: {user_profile['role']}
Domain: {user_profile['domain']}
Skills: {user_profile['skills']}
Experience: {user_profile['experience']} years

Guidelines:
- Questions 1-2: Conceptual/theory questions (Easy to Medium)
- Questions 3-4: Practical/scenario-based questions (Medium)
- Question 5: Problem-solving or coding explanation (Medium to Hard)
- Match difficulty to experience level (easier for freshers)
- Focus on the skills they listed
- Make questions realistic for actual interviews

Return ONLY a JSON array with this exact format (no extra text):
[
    {{
        "question_number": 1,
        "question_text": "Your question here",
        "reference_answer": "Brief 2-3 sentence answer",
        "expected_keywords": ["keyword1", "keyword2", "keyword3"],
        "difficulty_level": "Easy"
    }},
    ...
]
"""
    
    try:
        # Get Gemini instance
        gemini = GeminiConfig()
        # Generate content
        response = gemini.generate_content(prompt)
        if not response:
            return None
        # Parse JSON response
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]  # Remove ```json
        if response.startswith('```'):
            response = response[3:]  # Remove ```
        if response.endswith('```'):
            response = response[:-3]  # Remove ```
        response = response.strip()
        # Parse JSON
        questions = json.loads(response)
        return questions
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Response was: {response[:200]}")
        return None
    
    except Exception as e:
        print(f"❌ Error generating questions: {e}")
        return None


def save_questions_to_database(user_id, questions):
    """
    Save generated questions to database
    Creates interview session and saves all questions
    
    Returns interview_id or None
    """
    from config.database import DatabaseSession
    from models.database_models import Interview, Question
    from datetime import datetime
    
    try:
        with DatabaseSession() as session:
            # Create new interview
            interview = Interview(
                user_id=user_id,
                status='in_progress',
                started_at=datetime.utcnow()
            )
            session.add(interview)
            session.flush()  # Get interview_id
            
            print(f"✅ Created interview ID: {interview.id}")
            
            # Save all questions
            for q in questions:
                question = Question(
                    interview_id=interview.id,
                    question_number=q['question_number'],
                    question_text=q['question_text'],
                    reference_answer=q['reference_answer'],
                    expected_keywords=q['expected_keywords'],
                    difficulty_level=q['difficulty_level']
                )
                session.add(question)
            
            # Auto commit when context exits
            print(f"✅ Saved {len(questions)} questions to interview {interview.id}")
            # Auto commit when context exits
            print(f"✅ Saved interview ID: {interview.id}")
            print(f"✅ Saved {len(questions)} questions")
            return interview.id
    
    except Exception as e:
        print(f"❌ Error saving questions: {e}")
        import traceback
        traceback.print_exc()
        return None


# Test function
if __name__ == "__main__":
    test_profile = {
        'role': 'Data Scientist',
        'domain': 'Machine Learning',
        'skills': 'Python, Pandas, Scikit-learn',
        'experience': 0
    }
    print("Generating questions...")
    questions = generate_interview_questions(test_profile)
    if questions:
        print(f"\n✅ Generated {len(questions)} questions:")
        for q in questions:
            print(f"\n{q['question_number']}. {q['question_text']}")
            print(f"   Difficulty: {q['difficulty_level']}")
    else:
        print("❌ Failed to generate questions")
