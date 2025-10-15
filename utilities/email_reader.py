# utilities/email_reader.py
import imaplib
import email
import os
import re
from email.header import decode_header
import datetime
from config import EMAIL_CONFIG

class EmailReader:
    def __init__(self):
        self.config = EMAIL_CONFIG
    
    def connect_to_inbox(self):
        """Connect to IMAP server and return mailbox"""
        try:
            # Check if credentials are available
            if not self.config.get('sender_email') or not self.config.get('sender_password'):
                print("❌ Email credentials not configured")
                return None
            
            mail = imaplib.IMAP4_SSL(self.config['imap_server'])
            mail.login(self.config['sender_email'], self.config['sender_password'])
            mail.select('inbox')
            print("✅ Connected to email inbox")
            return mail
        except Exception as e:
            print(f"❌ IMAP connection error: {e}")
            return None
    
    def get_unread_emails(self, limit=5):
        """Fetch unread emails from inbox"""
        try:
            mail = self.connect_to_inbox()
            if not mail:
                return "Could not connect to email server. Please check your email credentials."
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                mail.close()
                mail.logout()
                return "No unread emails found."
            
            email_ids = messages[0].split()
            if not email_ids:
                mail.close()
                mail.logout()
                return "No unread emails in your inbox."
            
            emails = []
            # Get the latest emails (up to limit)
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Decode subject
                    subject = "No Subject"
                    if msg["Subject"]:
                        subject_part, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject_part, bytes):
                            subject = subject_part.decode(encoding if encoding else 'utf-8')
                        else:
                            subject = str(subject_part)
                    
                    # Decode sender
                    from_ = "Unknown Sender"
                    if msg.get("From"):
                        from_part, encoding = decode_header(msg.get("From"))[0]
                        if isinstance(from_part, bytes):
                            from_ = from_part.decode(encoding if encoding else 'utf-8')
                        else:
                            from_ = str(from_part)
                    
                    # Get date
                    date = msg.get("Date", "Unknown Date")
                    
                    # Get email body
                    body = self.get_email_body(msg)
                    
                    emails.append({
                        'id': email_id.decode(),
                        'subject': subject,
                        'from': from_,
                        'date': date,
                        'body': body[:200] + "..." if len(body) > 200 else body  # Preview
                    })
            
            mail.close()
            mail.logout()
            
            print(f"✅ Found {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            return f"Error reading emails: {str(e)}"
    
    def get_email_body(self, msg):
        """Extract text body from email"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except Exception as e:
                        print(f"Error decoding part: {e}")
                        continue
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except Exception as e:
                    print(f"Error decoding message: {e}")
        
        return body.strip() if body else "No readable content"
    
    def mark_as_read(self, email_id):
        """Mark an email as read"""
        try:
            mail = self.connect_to_inbox()
            if mail:
                mail.store(email_id.encode(), '+FLAGS', '\\Seen')
                mail.close()
                mail.logout()
                print(f"✅ Marked email {email_id} as read")
                return True
            return False
        except Exception as e:
            print(f"❌ Error marking email as read: {e}")
            return False
    
    def get_email_count(self):
        """Get count of unread emails"""
        try:
            mail = self.connect_to_inbox()
            if not mail:
                return 0
            
            status, messages = mail.search(None, 'UNSEEN')
            mail.close()
            mail.logout()
            
            if status == 'OK':
                count = len(messages[0].split())
                print(f"✅ Unread email count: {count}")
                return count
            return 0
        except Exception as e:
            print(f"❌ Error getting email count: {e}")
            return 0
    
    def read_full_email(self, email_id):
        """Get complete email content"""
        try:
            mail = self.connect_to_inbox()
            if not mail:
                return "Could not connect to email server."
            
            status, msg_data = mail.fetch(email_id.encode(), '(RFC822)')
            if status != 'OK':
                mail.close()
                mail.logout()
                return "Could not fetch email."
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Decode subject
            subject = "No Subject"
            if msg["Subject"]:
                subject_part, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject_part, bytes):
                    subject = subject_part.decode(encoding if encoding else 'utf-8')
                else:
                    subject = str(subject_part)
            
            # Decode sender
            from_ = "Unknown Sender"
            if msg.get("From"):
                from_part, encoding = decode_header(msg.get("From"))[0]
                if isinstance(from_part, bytes):
                    from_ = from_part.decode(encoding if encoding else 'utf-8')
                else:
                    from_ = str(from_part)
            
            # Get full body
            body = self.get_email_body(msg)
            
            mail.close()
            mail.logout()
            
            return {
                'subject': subject,
                'from': from_,
                'body': body
            }
            
        except Exception as e:
            return f"Error reading email: {str(e)}"