# utilities/contact_manager.py
import json
import os
from dotenv import load_dotenv
load_dotenv()

import re
import speech_recognition as sr
from config import CONTACTS_FILE

class ContactManager:
    def __init__(self):
        self.contacts_file = CONTACTS_FILE
        self.contacts = self.load_contacts()
    
    def load_contacts(self):
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_contacts(self):
        with open(self.contacts_file, "w") as f:
            json.dump(self.contacts, f, indent=4)
    
    def find_email(self, name, tts=None):
        name_lower = name.lower().strip()
        
        # 1. Check existing contacts
        if name_lower in self.contacts:
            email = self.contacts[name_lower]
            if tts:
                tts.speak(f"Found {name}'s email: {email}")
            return email
        
        # 2. Ask user for email
        if tts:
            tts.speak(f"I don't have an email for {name}. What is their email address? Please say it clearly.")
            email = self._listen_for_email()
            if email and self._validate_email(email):
                self.contacts[name_lower] = email
                self.save_contacts()
                tts.speak(f"Saved {name}'s email. Now I'll remember it.")
                return email
            else:
                tts.speak("I couldn't understand the email address. Let's try again later.")
        
        return None
    
    def _listen_for_email(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening for email address...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            try:
                audio = recognizer.listen(source, timeout=10)
                email_text = recognizer.recognize_google(audio).lower()
                print(f"📧 Heard email: {email_text}")
                
                # Clean up the email
                email_text = email_text.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
                email_text = re.sub(r'\s+', '', email_text)
                
                return email_text
            except sr.WaitTimeoutError:
                print("⏰ Email listening timeout")
                return None
            except Exception as e:
                print(f"❌ Email recognition error: {e}")
                return None
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        print(f"📧 Email validation: {email} -> {is_valid}")
        return is_valid
    
    def list_contacts(self):
        if not self.contacts:
            return "No contacts saved yet."
        
        result = ["Saved contacts:"]
        for name, email in self.contacts.items():
            result.append(f"• {name.title()}: {email}")
        return "\n".join(result)
    
    def delete_contact(self, name):
        name_lower = name.lower()
        if name_lower in self.contacts:
            del self.contacts[name_lower]
            self.save_contacts()
            return f"Deleted contact for {name}"
        return f"No contact found for {name}"
