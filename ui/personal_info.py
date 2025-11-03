"""
Personal Info Collection Module
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import DatabaseSession
from models.database_models import User
import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return True
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None


def save_user_to_database(user_data):
    """Save user to database"""
    try:
        with DatabaseSession() as session:
            existing_user = session.query(User).filter_by(email=user_data['email']).first()
            
            if existing_user:
                existing_user.name = user_data['name']
                existing_user.phone = user_data['phone']
                existing_user.target_role = user_data['target_role']
                existing_user.domain = user_data['domain']
                existing_user.skills = user_data['skills']
                existing_user.experience_years = user_data['experience_years']
                user_id = existing_user.id
                st.info(f"ℹ️ Updated profile for {user_data['email']}")
            else:
                new_user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    target_role=user_data['target_role'],
                    domain=user_data['domain'],
                    skills=user_data['skills'],
                    experience_years=user_data['experience_years']
                )
                session.add(new_user)
                session.flush()
                user_id = new_user.id
            
            return user_id
    
    except Exception as e:
        st.error(f"❌ Error saving: {e}")
        return None


def render_personal_info_form():
    """Render personal info form"""
    
    st.markdown("### 👤 Basic Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name *", placeholder="Enter your full name")
    
    with col2:
        email = st.text_input("Email Address *", placeholder="your.email@example.com")
    
    phone = st.text_input("Phone Number (Optional)", placeholder="1234567890")
    
    st.markdown("---")
    st.markdown("### 💼 Professional Details")
    
    target_role = st.text_input(
        "Target Role/Position *",
        placeholder="e.g., Data Scientist, ML Engineer"
    )
    
    domains = [
        "Data Science",
        "Machine Learning",
        "Artificial Intelligence",
        "Deep Learning",
        "Natural Language Processing (NLP)",
        "Computer Vision",
        "Backend Development",
        "Frontend Development",
        "Full Stack Development",
        "DevOps",
        "Cloud Computing",
        "Other"
    ]
    
    domain = st.selectbox("Primary Domain/Field *", options=domains)
    
    st.markdown("#### 🛠️ Skills You Know *")
    skills = st.text_area(
        "Your Skills",
        placeholder="Python, SQL, Machine Learning, Data Analysis",
        height=100
    )
    
    st.markdown("#### 📊 Experience Level *")
    experience_years = st.number_input(
        "Years of Experience",
        min_value=0,
        max_value=50,
        value=0,
        step=1
    )
    
    if experience_years == 0:
        st.info("ℹ️ Fresher - Questions will be entry-level")
    elif experience_years <= 2:
        st.info("ℹ️ Junior level - Fundamental questions")
    else:
        st.info("ℹ️ Experienced - Advanced questions")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button(
            "🚀 Save & Continue",
            type="primary",
            use_container_width=True
        )
    
    if submit_button:
        errors = []
        
        if not name.strip():
            errors.append("Name is required")
        if not email.strip():
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        if not target_role.strip():
            errors.append("Target role is required")
        if not skills.strip():
            errors.append("Skills are required")
        if phone and not validate_phone(phone):
            errors.append("Invalid phone number")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            user_data = {
                'name': name.strip(),
                'email': email.strip().lower(),
                'phone': phone.strip() if phone else None,
                'target_role': target_role.strip(),
                'domain': domain,
                'skills': skills.strip(),
                'experience_years': experience_years
            }
            
            with st.spinner("Saving profile..."):
                user_id = save_user_to_database(user_data)
            
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.user_name = user_data['name']
                st.session_state.user_email = user_data['email']
                st.session_state.user_domain = user_data['domain']
                st.session_state.user_role = user_data['target_role']
                st.session_state.user_skills = user_data['skills']
                st.session_state.user_experience = user_data['experience_years']
                
                st.success("✅ Profile saved!")
                st.balloons()
                st.info("👉 Go to **Domain Q&A** tab!")
                
                return True
    
    return False


def display_user_profile():
    """Display saved profile"""
    if st.session_state.user_id:
        st.success(f"✅ Profile created for **{st.session_state.user_name}**")
        
        with st.expander("📋 View Profile Details"):
            st.write(f"**Email:** {st.session_state.user_email}")
            st.write(f"**Target Role:** {st.session_state.user_role}")
            st.write(f"**Domain:** {st.session_state.user_domain}")