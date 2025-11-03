"""
Email Sender Module
Sends interview feedback reports via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
load_dotenv()

class EmailSender:
    """
    Sends email reports to users
    """    
    def __init__(self):
        self.email_host = os.getenv('EMAIL_HOST')
        self.email_port = int(os.getenv('EMAIL_PORT'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
    def send_feedback_email(self, user_email, user_name, feedback_data):
        """
        Send feedback report via email
        Args:
            user_email: Recipient email
            user_name: Recipient name
            feedback_data: Dict with scores and feedback
        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 Your Interview Performance Report - Score: {feedback_data['overall_score']:.0f}%"
            msg['From'] = self.email_user
            msg['To'] = user_email
            # Create HTML email body
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                        <h2 style="color: #1f77b4; text-align: center;">🎯 Interview Performance Report</h2>
                        
                        <p>Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Thank you for completing your AI interview practice! Here's your detailed performance report:</p>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                            <h3 style="color: #1f77b4;">📊 Overall Performance</h3>
                            <p style="font-size: 24px; font-weight: bold; color: #1f77b4;">
                                Score: {feedback_data['overall_score']:.0f}%
                            </p>
                            
                            <h4>Score Breakdown:</h4>
                            <ul style="list-style: none; padding: 0;">
                                <li>📝 <strong>Content Knowledge:</strong> {feedback_data['content_score']:.0f}%</li>
                                <li>💬 <strong>Communication Quality:</strong> {feedback_data['audio_score']:.0f}%</li>
                                <li>🎥 <strong>Professional Presence:</strong> {feedback_data['video_score']:.0f}%</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin: 20px 0;">
                            <h3 style="color: #2e7d32;">✅ Your Strengths</h3>
                            <ul>
                                {''.join([f'<li>{s.strip()}</li>' for s in feedback_data['strengths'].split('\\n') if s.strip()])}
                            </ul>
                        </div>
                        
                        <div style="background-color: #fff3e0; padding: 15px; border-radius: 10px; margin: 20px 0;">
                            <h3 style="color: #e65100;">📈 Areas for Improvement</h3>
                            <ul>
                                {''.join([f'<li>{w.strip()}</li>' for w in feedback_data['weaknesses'].split('\\n') if w.strip()])}
                            </ul>
                        </div>
                        
                        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 20px 0;">
                            <h3 style="color: #1565c0;">💡 Actionable Recommendations</h3>
                            <ol>
                                {''.join([f'<li>{r.strip()}</li>' for r in feedback_data['recommendations'].split('\\n') if r.strip()])}
                            </ol>
                        </div>
                        
                        <hr style="border: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="text-align: center; color: #666;">
                            Keep practicing to improve your interview skills!<br>
                            <strong>AI Interview Evaluation System</strong>
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {user_email}")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False