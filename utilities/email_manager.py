# utilities/email_manager.py
import smtplib
import os
# from dotenv import load_dotenv
# load_dotenv()

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_CONFIG
from .email_reader import EmailReader  # Add this import

class EmailManager:
    def __init__(self):
        self.config = EMAIL_CONFIG
        self.reader = EmailReader()  # Make sure this line is present
    
    def send_email(self, recipient, subject, body):
        try:
            # Validate credentials
            if not self.config['sender_email'] or not self.config['sender_password']:
                return "Email not configured. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables."
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Create server
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            
            # Login
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.config['sender_email'], recipient, text)
            server.quit()
            
            print(f"✅ Email sent to {recipient}")
            return f"Email successfully sent to {recipient}"
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return f"Failed to send email: {str(e)}"
    
    def get_email_templates(self):
        return {
            "meeting": "Hi {name},\n\nI'd like to schedule a meeting to discuss {topic}. Please let me know your availability.\n\nBest regards,\n{my_name}",
            "followup": "Hi {name},\n\nJust following up on our previous conversation about {topic}. Looking forward to your response.\n\nBest,\n{my_name}",
            "thank you": "Dear {name},\n\nThank you for your help with {topic}. I really appreciate your support.\n\nSincerely,\n{my_name}",
            "professional": "Dear {name},\n\nI hope this email finds you well. Regarding {topic}, I wanted to discuss {main_point}.\n\nBest regards,\n{my_name}",
            "quick question": "Hi {name},\n\nQuick question about {topic}.\n\nThanks,\n{my_name}"
        }
    
    def create_email_from_template(self, template_type, recipient_name, topic="", my_name="User"):
        templates = self.get_email_templates()
        if template_type in templates:
            return templates[template_type].format(
                name=recipient_name,
                topic=topic,
                my_name=my_name
            )
        return None
    
    # NEW EMAIL READING METHODS
    def check_inbox(self):
        """Check for unread emails"""
        return self.reader.get_unread_emails()
    
    def get_unread_count(self):
        """Get number of unread emails"""
        return self.reader.get_email_count()
    
    def read_email_aloud(self, email_id, tts):
        """Read a specific email aloud"""
        email_data = self.reader.read_full_email(email_id)
        
        if isinstance(email_data, dict):
            # Mark as read after reading
            self.reader.mark_as_read(email_id)
            
            # Read email content
            tts.speak(f"Email from {email_data['from']}")
            tts.speak(f"Subject: {email_data['subject']}")
            tts.speak(f"Content: {email_data['body']}")
            
            return f"Read email from {email_data['from']}"
        else:
            return email_data  # Error message