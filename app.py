"""
AI Interview Evaluation System
Main Streamlit Application
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig, test_connection

# Page configuration
st.set_page_config(
    page_title="AI Interview System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_domain' not in st.session_state:
        st.session_state.user_domain = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_skills' not in st.session_state:
        st.session_state.user_skills = None
    if 'user_experience' not in st.session_state:
        st.session_state.user_experience = None
    
    if 'interview_id' not in st.session_state:
        st.session_state.interview_id = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'questions_generated' not in st.session_state:
        st.session_state.questions_generated = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    
    if 'interview_completed' not in st.session_state:
        st.session_state.interview_completed = False
    if 'total_gaze_violations' not in st.session_state:
        st.session_state.total_gaze_violations = 0


def check_database_connection():
    """Check database connection"""
    try:
        db = DatabaseConfig()
        return True
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.info("Please check PostgreSQL is running")
        return False


def reset_interview():
    """Reset interview session to start new interview"""
    st.session_state.interview_id = None
    st.session_state.current_question = 0
    st.session_state.questions_generated = False
    st.session_state.questions = []
    st.session_state.interview_completed = False
    st.session_state.total_gaze_violations = 0


def main():
    """Main application"""
    
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-title">🎯 AI Interview Evaluation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Practice interviews with AI-powered feedback</p>', unsafe_allow_html=True)
    
    # Check database
    with st.spinner("Connecting to database..."):
        db_connected = check_database_connection()
    
    if not db_connected:
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📊 Interview Progress")
        
        if st.session_state.user_name:
            st.success(f"👤 Welcome, {st.session_state.user_name}!")
        else:
            st.info("👋 Please complete Personal Info")
        
        if st.session_state.interview_id:
            st.info(f"🔖 Interview ID: {st.session_state.interview_id}")
            progress = (st.session_state.current_question / 5) * 100
            st.progress(progress / 100)
            st.caption(f"Question {st.session_state.current_question}/5")
        
        st.markdown("---")
        st.markdown("### 🎓 How it works:")
        st.markdown("""
        1. **Enter details** - Tell us about yourself
        2. **Get 5 questions** - AI generates questions
        3. **Record answers** - Answer via audio + video
        4. **Get feedback** - Receive analysis and tips
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ System Status")
        st.success("✅ Database Connected")
        st.success("✅ Gemini AI Ready")
        st.success("✅ Speech-to-Text Ready")
        st.success("✅ Video Analysis Ready")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Personal Info",
        "❓ Domain Q&A",
        "🎥 Interview Session",
        "📊 Analysis",
        "🎯 Feedback",
        "📜 History"
    ])
    
    # Tab 1: Personal Info
    with tab1:
        st.markdown("## 📋 Personal Information")
        st.markdown("Tell us about yourself to get personalized questions")
        
        from ui.personal_info import render_personal_info_form, display_user_profile
        
        if st.session_state.user_id is None:
            render_personal_info_form()
        else:
            display_user_profile()
    
    # Tab 2: Domain Q&A
    with tab2:
        st.markdown("## ❓ Domain Q&A")
        
        if st.session_state.user_id is None:
            st.warning("⚠️ Please complete Personal Info first")
        
        elif not st.session_state.questions_generated:
            st.info("💡 We'll generate 5 personalized interview questions based on your profile")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🤖 Generate Questions", type="primary", use_container_width=True):
                    with st.spinner("✨ Gemini AI is generating your questions..."):
                        from modules.qa_generator import generate_interview_questions, save_questions_to_database
                        
                        user_profile = {
                            'role': st.session_state.user_role,
                            'domain': st.session_state.user_domain,
                            'skills': st.session_state.user_skills,
                            'experience': st.session_state.user_experience
                        }
                        
                        questions = generate_interview_questions(user_profile)
                        
                        if questions:
                            interview_id = save_questions_to_database(
                                st.session_state.user_id,
                                questions
                            )
                            
                            if interview_id:
                                st.session_state.questions = questions
                                st.session_state.interview_id = interview_id
                                st.session_state.questions_generated = True
                                st.success("✅ Questions generated and saved to database!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Failed to save questions to database")
                        else:
                            st.error("❌ Failed to generate questions. Please try again.")
        
        else:
            st.success("✅ Your personalized interview questions are ready!")
            st.markdown("---")
            
            st.markdown("### 📝 Your Interview Questions:")
            for q in st.session_state.questions:
                st.markdown(f"{q['question_number']}. {q['question_text']} *({q['difficulty_level']})*")
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Questions"):
                    st.session_state.questions_generated = False
                    st.session_state.interview_id = None
                    st.session_state.current_question = 0
                    st.rerun()
            with col2:
                st.info("👉 Go to **Interview Session** tab to start!")
    
    # Tab 3: Interview Session
    with tab3:
        st.markdown("## 🎥 Interview Session")
        
        if not st.session_state.questions_generated:
            st.warning("⚠️ Please generate questions first (Domain Q&A tab)")
        
        else:
            current_q = st.session_state.current_question
            total_q = len(st.session_state.questions)
            
            if current_q >= total_q:
                st.success("🎉 Interview Complete!")
                st.balloons()
                st.info("👉 Go to **Feedback** tab to see your results!")
            
            else:
                question = st.session_state.questions[current_q]
                
                st.progress((current_q + 1) / total_q)
                st.caption(f"Question {current_q + 1} of {total_q}")
                
                st.markdown("---")
                
                st.markdown(f"### Question {question['question_number']}")
                st.markdown(f"**{question['question_text']}**")
                st.caption(f"💡 Difficulty: {question['difficulty_level']}")
                
                st.markdown("---")
                
                # Check if already answered
                from config.database import DatabaseSession
                from models.database_models import Response, Question
                import json
                
                existing_response_data = None
                with DatabaseSession() as session:
                    db_question = session.query(Question).filter_by(
                        interview_id=st.session_state.interview_id,
                        question_number=question['question_number']
                    ).first()
                    
                    if db_question:
                        existing_response = session.query(Response).filter_by(
                            interview_id=st.session_state.interview_id,
                            question_id=db_question.id
                        ).first()
                        
                        # Load data INSIDE session
                        if existing_response:
                            existing_response_data = {
                                'transcript': existing_response.transcript,
                                'sentiment_score': existing_response.sentiment_score,
                                'sentiment_label': existing_response.sentiment_label,
                                'keyword_match_score': existing_response.keyword_match_score,
                                'grammar_score': existing_response.grammar_score,
                                'eye_contact_score': existing_response.eye_contact_score,
                                'gaze_violations': existing_response.gaze_violations
                            }
                
                if existing_response_data:
                    st.success("✅ You already answered this question")
                    
                    with st.expander("📝 View Your Previous Answer", expanded=True):
                        st.write("**Your Answer:**")
                        st.info(existing_response_data['transcript'])
                        
                        st.write("**Analysis Results:**")
                        
                        # Audio metrics
                        if existing_response_data['sentiment_score'] is not None:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Sentiment", existing_response_data['sentiment_label'] or 'N/A')
                            with col2:
                                st.metric("Keywords", f"{existing_response_data['keyword_match_score'] or 0:.0f}%")
                            with col3:
                                st.metric("Grammar", f"{existing_response_data['grammar_score'] or 0:.0f}%")
                        
                        # Video metrics
                        if existing_response_data['eye_contact_score'] is not None:
                            st.write("**Video Metrics:**")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Eye Contact", f"{existing_response_data['eye_contact_score']:.0f}%")
                            with col2:
                                st.metric("Gaze Issues", existing_response_data['gaze_violations'] or 0)
                    
                    st.divider()
                    st.info("💡 You cannot change your answer once submitted")
                
                st.markdown("---")
                
                # Recording interface
                st.markdown("### Record Your Answer")
                
                from audio_recorder_streamlit import audio_recorder
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Audio Recording:**")
                    audio_bytes = audio_recorder(
                        key=f"audio_{current_q}"
                    )
                    
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
                        st.success("Audio recorded!")
                
                with col2:
                    from modules.video_recorder import render_video_recorder
                    video_frames = render_video_recorder(key=f"video_{current_q}")
                
                st.markdown("---")
                
                st.markdown("**Or type your answer:**")
                answer = st.text_area(
                    "Type here (optional):",
                    height=100,
                    key=f"answer_{current_q}"
                )
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if current_q > 0:
                        if st.button("⬅️ Previous"):
                            st.session_state.current_question -= 1
                            st.rerun()
                
                with col3:
                    # Can only proceed if not already answered AND has new input
                    has_new_input = answer.strip() or audio_bytes or video_frames
                    can_proceed = has_new_input and not existing_response_data
                    
                    if can_proceed:
                        if st.button("Next ➡️", type="primary"):
                            from modules.response_handler import save_response
                            from modules.stt_module import WhisperSTT
                            from modules.audio_analyzer import AudioAnalyzer
                            from modules.video_analyzer import VideoAnalyzer
                            
                            question_obj = st.session_state.questions[current_q]
                            
                            # Process audio if recorded
                            final_transcript = answer
                            if audio_bytes and not answer.strip():
                                with st.spinner("🎤 Converting speech to text..."):
                                    whisper = WhisperSTT()
                                    transcript = whisper.transcribe_audio(audio_bytes)
                                    if transcript:
                                        final_transcript = transcript
                                        st.success(f"✅ Transcribed: {transcript[:100]}...")
                            
                            # Analyze transcript
                            analysis_metrics = None
                            if final_transcript.strip():
                                with st.spinner("🔍 Analyzing your answer..."):
                                    analyzer = AudioAnalyzer()
                                    
                                    reference_answer = question_obj.get('reference_answer', '')
                                    expected_keywords = question_obj.get('expected_keywords', [])
                                    
                                    analysis_metrics = analyzer.analyze_complete(
                                        final_transcript,
                                        reference_answer,
                                        expected_keywords
                                    )
                                    
                                    st.markdown("### 📊 Audio Analysis")
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Sentiment", 
                                                 analysis_metrics['sentiment_label'],
                                                 f"{analysis_metrics['sentiment_score']:.2f}")
                                    
                                    with col2:
                                        st.metric("Keyword Match", 
                                                 f"{analysis_metrics['keyword_match_score']:.1f}%")
                                    
                                    with col3:
                                        st.metric("Grammar Score", 
                                                 f"{analysis_metrics['grammar_score']:.1f}%")
                                    
                                    if analysis_metrics['matched_keywords']:
                                        st.success(f"✅ Matched keywords: {', '.join(analysis_metrics['matched_keywords'])}")
                            
                            # Analyze video if recorded
                            video_metrics = None
                            if video_frames:
                                with st.spinner("👁️ Analyzing video..."):
                                    video_analyzer = VideoAnalyzer()
                                    video_metrics = video_analyzer.analyze_video_frames(video_frames)
                                    
                                    if video_metrics:
                                        st.markdown("### 📹 Video Analysis")
                                        col1, col2, col3 = st.columns(3)
                                        
                                        with col1:
                                            st.metric("Face Detection", f"{video_metrics['face_detection_rate']:.0f}%")
                                        with col2:
                                            st.metric("Eye Contact", f"{video_metrics['eye_contact_score']:.0f}%")
                                        with col3:
                                            st.metric("Gaze Issues", video_metrics['gaze_violations'])
                                        
                                        #Track total violations
                                        st.session_state.total_gaze_violations += video_metrics['gaze_violations']

                                        #check is limit exceeded
                                        if st.session_state.total_gaze_violations >= 5:
                                            st.error("❌ **Interview Terminated!**")
                                            st.warning("⚠️ You looked away from the camera too many times (3+ violations).")
                                            st.info("💡 **Tip:** Maintain eye contact with the camera during interviews to show confidence and engagement.")

                                            #Mark interview as completed
                                            st.session_state.current_question = len(st.session_state.questions)
                                            st.stop()

                            # Save to database
                            with DatabaseSession() as session:
                                db_question = session.query(Question).filter_by(
                                    interview_id=st.session_state.interview_id,
                                    question_number=question_obj['question_number']
                                ).first()
                                
                                if db_question:
                                    response_id = save_response(
                                        st.session_state.interview_id,
                                        db_question.id,
                                        final_transcript,
                                        analysis_metrics,
                                        video_metrics
                                    )
                                    
                                    if response_id:
                                        st.success("✅ Answer saved!")
                                    else:
                                        st.warning("⚠️ Could not save answer, but continuing...")
                                else:
                                    st.error("❌ Question not found in database!")
                            
                            # Move to next question
                            st.session_state.current_question += 1
                            st.rerun()
                    
                    elif existing_response_data:
                        # Already answered - can skip to next
                        if st.button("Next ➡️", type="primary"):
                            st.session_state.current_question += 1
                            st.rerun()
                    
                    else:
                        st.button("Next ➡️", disabled=True, help="Please answer first")
    
    # Tab 4: Analysis
    with tab4:
        st.markdown("## 📊 Interview Analysis Dashboard")
        
        if not st.session_state.interview_id:
            st.warning("⚠️ Please complete an interview first")
        
        else:
            from config.database import DatabaseSession
            from models.database_models import Response, Question
            import json
            
            with DatabaseSession() as session:
                # Get all responses for this interview
                responses_db = session.query(Response).filter_by(
                    interview_id=st.session_state.interview_id
                ).all()
                
                total_questions = session.query(Question).filter_by(
                    interview_id=st.session_state.interview_id
                ).count()
                
                # Load all data into dicts INSIDE session
                responses = []
                for r in responses_db:
                    responses.append({
                        'question_id': r.question_id,
                        'keyword_match_score': r.keyword_match_score,
                        'grammar_score': r.grammar_score,
                        'sentiment_label': r.sentiment_label,
                        'sentiment_score': r.sentiment_score,
                        'eye_contact_score': r.eye_contact_score,
                        'matched_keywords': r.matched_keywords
                    })
                
                answered = len(responses)
            
            if answered == 0:
                st.info("📝 Answer questions in the Interview Session tab to see analysis")
            
            else:
                # Summary Stats
                st.markdown("### 📈 Overall Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Questions Answered", f"{answered}/{total_questions}")
                
                # Calculate averages
                avg_keyword = sum([r['keyword_match_score'] or 0 for r in responses]) / answered if answered > 0 else 0
                avg_grammar = sum([r['grammar_score'] or 0 for r in responses]) / answered if answered > 0 else 0
                avg_eye_contact = sum([r['eye_contact_score'] or 0 for r in responses if r['eye_contact_score']]) / len([r for r in responses if r['eye_contact_score']]) if any(r['eye_contact_score'] for r in responses) else 0
                
                with col2:
                    st.metric("Avg Content Score", f"{avg_keyword:.0f}%")
                
                with col3:
                    st.metric("Avg Grammar", f"{avg_grammar:.0f}%")
                
                with col4:
                    st.metric("Avg Eye Contact", f"{avg_eye_contact:.0f}%")
                
                # Sentiment Distribution
                st.markdown("---")
                st.markdown("### 😊 Sentiment Distribution")
                
                sentiments = [r['sentiment_label'] for r in responses if r['sentiment_label']]
                if sentiments:
                    from collections import Counter
                    sentiment_counts = Counter(sentiments)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Positive", sentiment_counts.get('POSITIVE', 0), "✅")
                    with col2:
                        st.metric("Neutral", sentiment_counts.get('NEUTRAL', 0), "😐")
                    with col3:
                        st.metric("Negative", sentiment_counts.get('NEGATIVE', 0), "⚠️")
                
                # Question-wise Performance Chart
                st.markdown("---")
                st.markdown("### 📊 Performance Across Questions")
                
                import plotly.graph_objects as go
                
                keyword_scores = [r['keyword_match_score'] or 0 for r in responses]
                grammar_scores = [r['grammar_score'] or 0 for r in responses]
                eye_contact_scores = [r['eye_contact_score'] or 0 for r in responses]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(responses) + 1)),
                    y=keyword_scores,
                    mode='lines+markers',
                    name='Content',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10)
                ))
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(responses) + 1)),
                    y=grammar_scores,
                    mode='lines+markers',
                    name='Grammar',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=10)
                ))
                
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(responses) + 1)),
                    y=eye_contact_scores,
                    mode='lines+markers',
                    name='Eye Contact',
                    line=dict(color='#2ca02c', width=3),
                    marker=dict(size=10)
                ))
                
                fig.update_layout(
                    xaxis_title="Question Number",
                    yaxis_title="Score (%)",
                    yaxis_range=[0, 100],
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Best & Worst Performance
                st.markdown("---")
                st.markdown("### 🏆 Performance Highlights")
                
                col1, col2 = st.columns(2)
                
                # Find best and worst
                if responses:
                    best_response = max(responses, key=lambda r: r['keyword_match_score'] or 0)
                    worst_response = min(responses, key=lambda r: r['keyword_match_score'] or 0)
                    
                    with col1:
                        st.success("**🌟 Best Performance**")
                        with DatabaseSession() as session:
                            best_q = session.query(Question).filter_by(id=best_response['question_id']).first()
                            if best_q:
                                st.write(f"**Question {best_q.question_number}:** {best_q.question_text[:60]}...")
                                st.metric("Content Score", f"{best_response['keyword_match_score'] or 0:.0f}%")
                    
                    with col2:
                        st.warning("**📚 Needs Improvement**")
                        with DatabaseSession() as session:
                            worst_q = session.query(Question).filter_by(id=worst_response['question_id']).first()
                            if worst_q:
                                st.write(f"**Question {worst_q.question_number}:** {worst_q.question_text[:60]}...")
                                st.metric("Content Score", f"{worst_response['keyword_match_score'] or 0:.0f}%")
                
                # Keyword Coverage
                st.markdown("---")
                st.markdown("### 🔑 Keyword Coverage")
                
                all_keywords = []
                for r in responses:
                    if r['matched_keywords']:
                        all_keywords.extend(r['matched_keywords'])
                
                if all_keywords:
                    from collections import Counter
                    keyword_freq = Counter(all_keywords).most_common(10)
                    
                    st.write("**Top 10 Most Used Keywords:**")
                    
                    keywords = [k[0] for k in keyword_freq]
                    counts = [k[1] for k in keyword_freq]
                    
                    fig = go.Figure(go.Bar(
                        x=counts,
                        y=keywords,
                        orientation='h',
                        marker_color='#1f77b4'
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Frequency",
                        yaxis_title="Keywords",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No keywords tracked yet")
                
                # Call to action
                if answered < total_questions:
                    st.markdown("---")
                    st.info(f"💡 Complete remaining {total_questions - answered} questions to see full analysis!")
    
    # Tab 5: Feedback
    with tab5:
        st.markdown("## 🎯 Interview Feedback")
        
        if not st.session_state.interview_id:
            st.warning("⚠️ Please complete an interview first")
        
        else:
            # Check if all questions answered
            from config.database import DatabaseSession
            from models.database_models import Response, Question, Feedback
            
            with DatabaseSession() as session:
                total_questions = session.query(Question).filter_by(
                    interview_id=st.session_state.interview_id
                ).count()
                
                answered_questions = session.query(Response).filter_by(
                    interview_id=st.session_state.interview_id
                ).count()
                
                # Check if feedback exists and load all data
                existing_feedback = session.query(Feedback).filter_by(
                    interview_id=st.session_state.interview_id
                ).first()
                
                # Load data into dict INSIDE session
                if existing_feedback:
                    feedback_data = {
                        'overall_score': existing_feedback.overall_score,
                        'content_score': existing_feedback.content_score,
                        'audio_score': existing_feedback.audio_score,
                        'video_score': existing_feedback.video_score,
                        'strengths': existing_feedback.strengths,
                        'weaknesses': existing_feedback.weaknesses,
                        'recommendations': existing_feedback.recommendations,
                        'question_wise_analysis': existing_feedback.question_wise_analysis
                    }
                else:
                    feedback_data = None
            
            # Now use feedback_data outside session
            if answered_questions < total_questions:
                st.warning(f"⚠️ Complete all questions to see feedback ({answered_questions}/{total_questions} answered)")
            
            else:
                # Generate feedback button
                if not feedback_data:
                    st.info("📊 All questions answered! Generate your feedback report.")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🤖 Generate Feedback", type="primary", use_container_width=True):
                            with st.spinner("✨ Analyzing your performance..."):
                                from modules.feedback_generator import FeedbackGenerator
                                
                                generator = FeedbackGenerator()
                                feedback_id = generator.save_feedback(st.session_state.interview_id)
                                
                                if feedback_id:
                                    st.success("✅ Feedback generated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate feedback")
                
                else:
                    # Display existing feedback
                    st.success("📊 Your Interview Feedback Report")
                    st.markdown("---")
                    
                    # Overall Scores
                    st.markdown("### 🎯 Overall Performance")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        score = feedback_data['overall_score']
                        delta = "🎉" if score >= 70 else "💪" if score >= 50 else "📚"
                        st.metric("Overall Score", f"{score:.0f}%", delta)
                    
                    with col2:
                        st.metric("Content", f"{feedback_data['content_score']:.0f}%")
                    
                    with col3:
                        st.metric("Communication", f"{feedback_data['audio_score']:.0f}%")
                    
                    with col4:
                        st.metric("Presence", f"{feedback_data['video_score']:.0f}%")
                    
                    # Performance Bar
                    st.markdown("---")
                    st.markdown("### 📊 Score Breakdown")
                    
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    
                    categories = ['Content', 'Communication', 'Presence']
                    scores = [
                        feedback_data['content_score'],
                        feedback_data['audio_score'],
                        feedback_data['video_score']
                    ]
                    
                    fig.add_trace(go.Bar(
                        x=categories,
                        y=scores,
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                        text=[f"{s:.0f}%" for s in scores],
                        textposition='auto'
                    ))
                    
                    fig.update_layout(
                        yaxis_title="Score (%)",
                        yaxis_range=[0, 100],
                        showlegend=False,
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Strengths
                    st.markdown("---")
                    st.markdown("### ✅ Strengths")
                    strengths = feedback_data['strengths'].split('\n') if feedback_data['strengths'] else []
                    for strength in strengths:
                        if strength.strip():
                            st.success(f"✓ {strength}")
                    
                    # Weaknesses
                    st.markdown("---")
                    st.markdown("### 🎯 Areas for Improvement")
                    weaknesses = feedback_data['weaknesses'].split('\n') if feedback_data['weaknesses'] else []
                    for weakness in weaknesses:
                        if weakness.strip():
                            st.warning(f"⚠ {weakness}")
                    
                    # Recommendations
                    st.markdown("---")
                    st.markdown("### 💡 Actionable Recommendations")
                    recommendations = feedback_data['recommendations'].split('\n') if feedback_data['recommendations'] else []
                    for idx, rec in enumerate(recommendations, 1):
                        if rec.strip():
                            st.info(f"{idx}. {rec}")
                    
                    # Question-wise Analysis
                    st.markdown("---")
                    st.markdown("### 📝 Question-by-Question Analysis")
                    
                    if feedback_data['question_wise_analysis']:
                        import json
                        
                        analyses = feedback_data['question_wise_analysis']
                        if isinstance(analyses, str):
                            analyses = json.loads(analyses)
                        
                        for analysis in analyses:
                            with st.expander(f"Question {analysis['question_number']}: {analysis['question_text'][:50]}..."):
                                st.write("**Your Answer:**")
                                st.info(analysis['user_answer'][:200] + "..." if len(analysis['user_answer']) > 200 else analysis['user_answer'])
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Keywords", f"{analysis['keyword_match']:.0f}%")
                                with col2:
                                    st.metric("Sentiment", analysis['sentiment'])
                                with col3:
                                    st.metric("Grammar", f"{analysis['grammar']:.0f}%")
                                with col4:
                                    st.metric("Eye Contact", f"{analysis['eye_contact']:.0f}%")
                    
                    # Regenerate button
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🔄 Regenerate Feedback", use_container_width=True):
                            with st.spinner("✨ Regenerating feedback..."):
                                from modules.feedback_generator import FeedbackGenerator
                                
                                generator = FeedbackGenerator()
                                feedback_id = generator.save_feedback(st.session_state.interview_id)
                                
                                if feedback_id:
                                    st.success("✅ Feedback updated!")
                                    st.rerun()
                                    
                    # Email Report button
                    st.markdown("---")
                    st.markdown("### 📧 Email Your Report")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("📧 Email My Report", type="primary", use_container_width=True):
                            if st.session_state.user_email:
                                with st.spinner("📨 Sending email..."):
                                    from modules.email_sender import EmailSender
                                    
                                    email_sender = EmailSender()
                                    success = email_sender.send_feedback_email(
                                        user_email=st.session_state.user_email,
                                        user_name=st.session_state.user_name,
                                        feedback_data=feedback_data
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Report sent to {st.session_state.user_email}!")
                                        st.balloons()
                                    else:
                                        st.error("❌ Failed to send email. Please try again.")
                            else:
                                st.error("❌ No email found. Please update your profile.")


                    # Start New Interview button
                    st.markdown("---")
                    st.markdown("### 🔄 Want to practice more?")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🎯 Start New Interview", type="secondary", use_container_width=True):
                            reset_interview()
                            st.success("✅ Session reset! Click on 'Domain Q&A' tab to generate new questions and start fresh.")
                            st.balloons()
    # Tab 6: History
    with tab6:
        st.markdown("## 📜 Interview History")
        
        if st.session_state.user_id is None:
            st.warning("⚠️ Please complete Personal Info first")
        
        else:
            from config.database import DatabaseSession
            from models.database_models import Interview, Feedback
            from datetime import datetime
            
            with DatabaseSession() as session:
                # Get all interviews for this user
                interviews = session.query(Interview).filter_by(
                    user_id=st.session_state.user_id
                ).order_by(Interview.started_at.desc()).all()
                
                # Load data into list
                interview_data = []
                for interview in interviews:
                    feedback = session.query(Feedback).filter_by(
                        interview_id=interview.id
                    ).first()
                    
                    interview_data.append({
                        'id': interview.id,
                        'status': interview.status,
                        'started_at': interview.started_at,
                        'completed_at': interview.completed_at,
                        'overall_score': feedback.overall_score if feedback else None,
                        'content_score': feedback.content_score if feedback else None,
                        'audio_score': feedback.audio_score if feedback else None,
                        'video_score': feedback.video_score if feedback else None
                    })
            
            if not interview_data:
                st.info("📝 No interview history yet. Complete an interview to see your progress!")
            
            else:
                st.success(f"📊 You have completed **{len(interview_data)}** interview(s)")
                
                st.markdown("---")
                
                # Display each interview
                for idx, interview in enumerate(interview_data, 1):
                    with st.expander(
                        f"🎯 Interview #{interview['id']} - "
                        f"{interview['started_at'].strftime('%B %d, %Y at %I:%M %p')}" if interview['started_at'] else "Date unknown",
                        expanded=(idx == 1)
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Status:** {interview['status'].title()}")
                            if interview['completed_at']:
                                duration = (interview['completed_at'] - interview['started_at']).seconds // 60
                                st.write(f"**Duration:** {duration} minutes")
                        
                        with col2:
                            if interview['overall_score']:
                                score = interview['overall_score']
                                color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                                st.metric("Overall Score", f"{score:.0f}% {color}")
                        
                        if interview['overall_score']:
                            st.markdown("**Score Breakdown:**")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Content", f"{interview['content_score']:.0f}%")
                            with col2:
                                st.metric("Communication", f"{interview['audio_score']:.0f}%")
                            with col3:
                                st.metric("Presence", f"{interview['video_score']:.0f}%")
                            
                            # Button to view full feedback
                            if st.button(f"📄 View Full Report", key=f"view_{interview['id']}"):
                                st.session_state.interview_id = interview['id']
                                st.session_state.questions_generated = True
                                st.info("👉 Go to **Feedback** tab to see the full report")
                        else:
                            st.warning("⚠️ Interview incomplete or feedback not generated")
                
                # Progress Chart
                if len(interview_data) > 1:
                    st.markdown("---")
                    st.markdown("### 📈 Progress Over Time")
                    
                    import plotly.graph_objects as go
                    
                    # Filter completed interviews with scores
                    scored_interviews = [i for i in interview_data if i['overall_score'] is not None]
                    scored_interviews.reverse()  # Chronological order
                    
                    if len(scored_interviews) > 1:
                        dates = [i['started_at'].strftime('%b %d') for i in scored_interviews]
                        scores = [i['overall_score'] for i in scored_interviews]
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=scores,
                            mode='lines+markers',
                            name='Overall Score',
                            line=dict(color='#1f77b4', width=3),
                            marker=dict(size=12)
                        ))
                        
                        fig.update_layout(
                            xaxis_title="Interview Date",
                            yaxis_title="Score (%)",
                            yaxis_range=[0, 100],
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate improvement
                        first_score = scored_interviews[0]['overall_score']
                        last_score = scored_interviews[-1]['overall_score']
                        improvement = last_score - first_score
                        
                        if improvement > 0:
                            st.success(f"🎉 You've improved by **{improvement:.1f}%** since your first interview!")
                        elif improvement < 0:
                            st.info(f"📚 Keep practicing! Your score changed by **{improvement:.1f}%**")
                        else:
                            st.info("📊 Your score remained consistent")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🚀 Built with Streamlit | Powered by Gemini AI, Whisper, MediaPipe</p>
        <p style='font-size: 0.9rem;'>AI Interview Practice System</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()