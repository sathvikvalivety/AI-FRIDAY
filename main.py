# main.py
import sys
import signal
import threading
import re
import wikipedia
from speech.speech_recognition import SpeechRecognizer
from speech.text_to_speech import TextToSpeech
from memory.memory_manager import MemoryManager
from study_planner.study_planner import StudyPlanner
from reminders.reminder_manager import ReminderManager
from ai.gemini_client import GeminiClient
from utilities.weather import WeatherService
from utilities.web_search import WebSearch
from utilities.calendar import CalendarService
from utilities.music_player import MusicPlayer
from utilities.email_manager import EmailManager
from utilities.contact_manager import ContactManager
from utilities.email_reader import EmailReader
from system.system_commands import SystemCommands
from security.voice_biometrics import VoiceBiometrics  # NEW IMPORT


class FridayAssistant:
    def __init__(self):
        self.speech_recognizer = SpeechRecognizer()
        self.tts = TextToSpeech()
        self.memory_manager = MemoryManager()
        self.study_planner = StudyPlanner()
        self.reminder_manager = ReminderManager()
        self.gemini_client = GeminiClient()
        self.weather_service = WeatherService()
        self.web_search = WebSearch()
        self.calendar_service = CalendarService()
        self.music_player = MusicPlayer()
        self.system_commands = SystemCommands()
        
        # NEW: Email and Contact managers
        self.email_manager = EmailManager()
        self.contact_manager = ContactManager()
        
        # NEW: Voice Biometrics
        self.voice_biometrics = VoiceBiometrics()
        
        # Conversation state
        self.conversation_state = {
            'active': False,
            'current_context': None,
            'retry_count': 0,
            'max_retries': 3
        }
    
    def greet_user(self):
        greeting = self.system_commands.get_greeting()
        # NEW: Include voice security status in greeting
        security_status = "enabled" if self.voice_biometrics.enabled else "disabled"
        full_greeting = f"{greeting} Voice security is {security_status}."
        self.tts.speak(full_greeting)
    
    def reset_conversation_state(self):
        self.conversation_state = {
            'active': False,
            'current_context': None,
            'retry_count': 0,
            'max_retries': 3
        }
    
    def listen_with_retry(self, context=None, prompt=None, max_retries=3):
        if context:
            self.conversation_state['active'] = True
            self.conversation_state['current_context'] = context
            self.conversation_state['retry_count'] = 0
            self.conversation_state['max_retries'] = max_retries
        
        retry_count = 0
        while retry_count < max_retries:
            if prompt and retry_count == 0:
                self.tts.speak(prompt)
            elif retry_count > 0:
            
                if context == "email_confirmation":
                    self.tts.speak("Please say 'yes' to send the email or 'no' to cancel.")
                    
                elif context == "delete_subjects":
                    self.tts.speak("I didn't catch which subjects to delete. Please say the number again, 'one' or 'one and thre'.")
                elif context == "study_hours":
                    self.tts.speak("I didn't understand how many hours you can study. Please say a number like '3' or 'four hours'.")
                elif context == "exam_date":
                    self.tts.speak("I didn't catch the exam date. Please say it again, like 'December 15 2025'.")
                elif context == "subject_difficulty":
                    self.tts.speak("I didn't understand the difficulty. Please say 'easy', 'medium', or 'hard'.")
                elif context == "subject_name":
                    self.tts.speak("I didn't catch the subject name. Please say it again.")
                elif context == "reminder_choice":
                    self.tts.speak("I didn't catch which reminder to delete. Please say the number again.")
                elif context == "memory_choice":
                    self.tts.speak("I didn't catch which date to clear. Please say the number again.")
                elif context == "search_query":
                    self.tts.speak("I didn't catch what you want to search for. Please say your search query again.")
                elif context == "wikipedia_topic":
                    self.tts.speak("I didn't catch the topic. Please say it again.")
                elif context == "email_check_response":
                    self.tts.speak("Please say 'yes' to read emails or 'no' to skip.")
                elif context == "email_read_choice":
                    self.tts.speak("Please say 'yes' to read this email, 'no' to skip it, or 'next' for next email.")
                    
                elif context == "email_action":
                    self.tts.speak("Please say 'reply' to respond, 'delete' to delete, or 'next' for next email.")
                    
                elif context == "email_reply_content":
                    self.tts.speak("Please speak your reply message now.")
                else:
                    self.tts.speak("I didn't catch that. Please say it again.")
            
            command = self.speech_recognizer.listen_for_command()
            if command:
                self.reset_conversation_state()
                return command
            
            retry_count += 1
            self.conversation_state['retry_count'] = retry_count
        
        self.reset_conversation_state()
        self.tts.speak("I'm having trouble understanding. Let's go back to the main menu.")
        return None

    def _extract_city_from_text(self, text):
        city = "Chennai"
        if "in" in text:
            parts = text.split("in")
            if len(parts) > 1:
                city = parts[1].strip()
        elif "weather" in text:
            parts = text.split("weather")
            if len(parts) > 1 and parts[1].strip():
                city = parts[1].replace("in", "").strip()
        return city

    def _handle_study_plan_creation(self, text):
        subject_name = None
        exam_date = None
        
        patterns = [
            r'(?:create|make).*study.*plan.*for (.+?) (?:for|on) exam (?:on|at) (.+)',
            r'(?:create|make).*study.*plan.*for (.+?) exam (.+)',
            r'study.*plan.*for (.+?) on (.+)',
            r'create.*study.*schedule.*for (.+?) (?:for|on) exam (.+)',
            r'i want to study (.+?) for exam on (.+)',
            r'plan.*study.*for (.+?) exam (.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                subject_name = match.group(1).strip()
                date_part = match.group(2).strip()
                exam_date = self.study_planner.parse_spoken_date(date_part)
                if subject_name and exam_date:
                    break
        
        if not subject_name:
            subject_patterns = [
                r'(?:study|learn|prepare).*for (.+)',
                r'create.*plan.*for (.+)',
                r'i want to study (.+)',
                r'help me with (.+)'
            ]
            
            for pattern in subject_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    subject_name = match.group(1).strip()
                    subject_name = re.sub(r'\b(exam|test|final|midterm|quiz)\b', '', subject_name, flags=re.IGNORECASE).strip()
                    if subject_name:
                        break
        
        if subject_name and exam_date:
            self.tts.speak(f"Creating study plan for {subject_name} with exam on {exam_date}...")
            study_plan = self.study_planner.create_study_plan_from_single_command(subject_name, exam_date)
            if study_plan:
                return f"Study plan created for {subject_name} with exam on {exam_date}. Found {len(study_plan['subjects'][0]['topics'])} topics to study."
            else:
                return "Failed to create study plan. Please try again."
        elif subject_name and not exam_date:
            self.tts.speak(f"Got {subject_name}. When is the exam date? Please say something like 'December 15 2025'.")
            date_text = self.listen_with_retry(context="exam_date", max_retries=2)
            if date_text:
                exam_date = self.study_planner.parse_spoken_date(date_text)
                if exam_date:
                    self.tts.speak(f"Creating study plan for {subject_name} with exam on {exam_date}...")
                    study_plan = self.study_planner.create_study_plan_from_single_command(subject_name, exam_date)
                    if study_plan:
                        return f"Study plan created for {subject_name}."
                    else:
                        return "Failed to create study plan."
                else:
                    return "Could not understand the exam date."
            else:
                return "No exam date provided."
        else:
            self.tts.speak("I need more details. What subject do you want to study?")
            subject_name = self.listen_with_retry(context="subject_name", max_retries=2)
            if subject_name:
                self.tts.speak(f"Got {subject_name}. When is the exam date? Please say something like 'December 15 2025'.")
                date_text = self.listen_with_retry(context="exam_date", max_retries=2)
                if date_text:
                    exam_date = self.study_planner.parse_spoken_date(date_text)
                    if exam_date:
                        self.tts.speak(f"Creating study plan for {subject_name} with exam on {exam_date}...")
                        study_plan = self.study_planner.create_study_plan_from_single_command(subject_name, exam_date)
                        if study_plan:
                            return f"Study plan created for {subject_name}."
                        else:
                            return "Failed to create study plan."
                    else:
                        return "Could not understand the exam date."
                else:
                    return "No exam date provided."
            else:
                return "No subject provided."

    def _handle_list_history(self, text):
        if "today" in text:
            return self.memory_manager.list_history("today")
        elif "yesterday" in text:
            return self.memory_manager.list_history("yesterday")
        else:
            return self.memory_manager.list_history("all")

    def _handle_memory_clear_interaction(self, text):
        result = self.memory_manager.clear_memory(text)
        if isinstance(result, dict) and "dates" in result:
            dates = result["dates"]
            self.tts.speak("I found conversations on these dates:")
            for idx, date in enumerate(dates, 1):
                self.tts.speak(f"{idx}. {date}")

            choice_text = self.listen_with_retry(
                context="memory_choice",
                prompt="Please say the number of the date you want me to clear, or say 'delete all' to clear everything.",
                max_retries=3
            )
            
            if not choice_text:
                return "I couldn't understand your choice after several attempts."

            choice_text = choice_text.lower().strip()

            if any(phrase in choice_text for phrase in ['delete all', 'clear all', 'everything', 'all']):
                return self.memory_manager.clear_all_memory()

            num_match = re.search(r'\d+', choice_text)
            if num_match:
                choice_num = int(num_match.group())
            else:
                mapping = {
                    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5
                }
                choice_num = None
                for word, num in mapping.items():
                    if word in choice_text:
                        choice_num = num
                        break

            if not choice_num or choice_num > len(dates):
                return "Invalid choice. No memory cleared."

            selected_date = dates[choice_num - 1]
            return self.memory_manager.clear_specific_date(selected_date)
        else:
            return result

    def _extract_recipient_name(self, text):
        """Extract recipient name from email command - IMPROVED VERSION"""
        text = text.lower().strip()

        # More comprehensive patterns to catch names
        patterns = [
            r'(?:write|send|compose|email).*to (.+?)(?:$| with| about| for| subject)',
            r'(?:write|send|compose|email).*to (.+)',
            r'to (.+?)(?:$| with| about| for| subject)',
            r'email.*to (.+)',
            r'send.*to (.+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Clean up the name - remove common stop words
                name = re.sub(r'\b(an|a|the|email|message|send|write|compose)\b', '', name, flags=re.IGNORECASE)
                name = re.sub(r'\s+', ' ', name).strip()
                if name and len(name) > 1:  # Ensure it's a valid name
                    return name

        return None

    def _handle_email_creation(self, text):
        """Handle complete email creation flow"""
        # Extract recipient name from the initial command
        recipient_name = self._extract_recipient_name(text)

        # If name not found in command, ask for it immediately
        if not recipient_name:
            self.tts.speak("Who would you like to send an email to?")
            recipient_name = self.listen_with_retry(context="email_recipient", max_retries=2)
            if not recipient_name:
                return "I didn't catch the recipient name."

        # Find or get email address
        self.tts.speak(f"Looking up email for {recipient_name}...")
        recipient_email = self.contact_manager.find_email(recipient_name, self.tts)

        if not recipient_email:
            return f"Could not find or get email address for {recipient_name}."

        # Get subject immediately
        self.tts.speak("What should the subject be?")
        subject = self.listen_with_retry(context="email_subject", max_retries=2)
        if not subject:
            return "Email subject is required."

        # Get content immediately
        self.tts.speak("What should the email say?")
        content = self.listen_with_retry(context="email_content", max_retries=2)
        if not content:
            return "Email content is required."

        # Send immediately without confirmation
        result = self.email_manager.send_email(recipient_email, subject, content)
        return result

    def _handle_quick_email(self, text):
        """Handle quick email with templates"""
        if "meeting" in text:
            template_type = "meeting"
        elif "thank" in text:
            template_type = "thank you"
        elif "follow" in text:
            template_type = "followup"
        else:
            template_type = "professional"

        # Extract recipient name from command
        recipient_name = self._extract_recipient_name(text)
        if not recipient_name:
            self.tts.speak("Who should I send the email to?")
            recipient_name = self.listen_with_retry(context="email_recipient", max_retries=2)
            if not recipient_name:
                return "I didn't catch the recipient name."

        # Find email
        recipient_email = self.contact_manager.find_email(recipient_name, self.tts)
        if not recipient_email:
            return f"Could not find email for {recipient_name}."

        # Get topic if needed
        topic = ""
        if template_type in ["meeting", "followup", "thank you"]:
            self.tts.speak(f"What is the email about?")
            topic = self.listen_with_retry(context="email_topic", max_retries=2) or ""

        # Generate content from template
        content = self.email_manager.create_email_from_template(
            template_type, recipient_name, topic, "User"
        )

        subject_map = {
            "meeting": f"Meeting about {topic}" if topic else "Meeting Request",
            "thank you": f"Thank you {recipient_name}",
            "followup": f"Follow up: {topic}" if topic else "Follow up",
            "professional": "Update" if topic else "Message"
        }
        subject = subject_map.get(template_type, "Message")

        # Send immediately without confirmation
        result = self.email_manager.send_email(recipient_email, subject, content)
        return result

    # NEW: Voice Security Training Function
    def train_voice_profile(self):
        """Train Friday to recognize your voice"""
        self.tts.speak("Starting voice training. Please say 'Friday' three times clearly.")
        
        voice_samples = []
        for i in range(3):
            self.tts.speak(f"Say 'Friday' - {i+1} of 3")
            audio = self.speech_recognizer.listen_for_command()
            if audio:
                # Convert audio for processing
                raw_audio = audio.get_raw_data(convert_rate=16000, convert_width=2)
                voice_samples.append(raw_audio)
        
        if len(voice_samples) >= 2:
            self.tts.speak("Voice training completed successfully!")
            return True
        else:
            self.tts.speak("Voice training failed. Please try again.")
            return False
            
    
    def handle_intent(self, text):
        text = (text or "").lower().strip()
        print(f"🔍 DEBUG: Command received: '{text}'")  # Add debug line

        try:
            # NEW: Email Inbox Commands
            if any(cmd in text for cmd in ["check my email", "check my emails", "any new emails", "unread emails","any mails","check my mail"]):
                print("🎯 DEBUG: Routing to _handle_email_check")
                return self._handle_email_check(text)
            
            elif any(cmd in text for cmd in ["read my emails", "read emails", "check inbox"]):
                print("🎯 DEBUG: Routing to _read_emails_interactive")
                return self._read_emails_interactive()
            
        # NEW: Voice Security Commands
            if "disable voice lock" in text:
                self.voice_biometrics.enabled = False
                return "Voice security disabled. Anyone can activate me now."
        
            elif "enable voice lock" in text:
                self.voice_biometrics.enabled = True  
                return "Voice security enabled. Only human voices can activate me."
        
            elif "voice security status" in text:
                status = "enabled" if self.voice_biometrics.enabled else "disabled"
                return f"Voice security is {status}"
        
            elif "set voice sensitivity to low" in text:
                return self.voice_biometrics.set_sensitivity("low")
        
            elif "set voice sensitivity to high" in text:
                return self.voice_biometrics.set_sensitivity("high")
        
            elif "set voice sensitivity to medium" in text:
                return self.voice_biometrics.set_sensitivity("medium")
        
            elif "train my voice" in text:
                success = self.train_voice_profile()
                return "Voice training completed" if success else "Voice training failed"

        # Email Commands
            elif any(cmd in text for cmd in ["write email to", "compose email to", "create email to"]):
                return self._handle_email_creation(text)

            elif any(cmd in text for cmd in ["send email to", "email to", "mail to"]):
                return self._handle_email_creation(text)

        # Quick email templates
            elif any(cmd in text for cmd in ["send meeting email to", "send thank you email to", "send followup to"]):
                return self._handle_quick_email(text)

        # Fallback - if it has "email" and "to" anywhere in the command
            elif "email" in text and " to " in text:
                return self._handle_email_creation(text)

        # Contact management
            elif "list contacts" in text:
                return self.contact_manager.list_contacts()
    
        # Shutdown command
            elif any(cmd in text for cmd in ["shutdown", "power off", "turn off computer"]):
                return self.system_commands.shutdown_computer(self.tts)
        
        # Study Planner commands
            elif any(cmd in text for cmd in ["today's study", "study schedule", "what should i study", "today study"]):
                schedule = self.study_planner.get_todays_study_schedule()
                return schedule if schedule else "No study plan found. Please create a study plan first by saying 'create study plan'."

            elif any(cmd in text for cmd in ["show study plan", "view study plan", "display study plan"]):
                study_plan = self.study_planner.load_study_plan()
                if study_plan:
                    total_subjects = len(study_plan['subjects'])
                    total_days = study_plan['total_study_days']
                    hours_per_day = study_plan['available_hours_per_day']
                    return f"You have a study plan with {total_subjects} subjects over {total_days} days, studying {hours_per_day} hours daily. Say 'today's study schedule' for details."
                else:
                    return "No study plan found. Say 'create study plan' to make one."

            elif any(cmd in text for cmd in ["create study plan", "make study schedule", "new study plan"]):
                return self._handle_study_plan_creation(text)
            
            elif any(phrase in text for phrase in ["clear study plan", "delete study plan", "remove study plan", "erase study plan"]):
                return self.study_planner.clear_study_plan()

        # Google Search
            elif "search" in text or "google" in text:
                query = self.web_search.extract_search_query(text)
                return self.web_search.google_search(query)

        # Wikipedia
            elif "tell me about" in text or "information about" in text or "wikipedia" in text:
                topic = self.web_search.extract_topic_from_text(text)
                return self.web_search.wikipedia_search(topic)

        # Weather
            elif "weather" in text:
                city = self._extract_city_from_text(text)
                return self.weather_service.get_weather(city)

        # Reminders
            elif "remind me" in text:
                return self.reminder_manager.add_reminder_from_text(text)

            elif any(cmd in text for cmd in ["list reminders", "show reminders", "what reminders"]):
                return self.reminder_manager.list_reminders_text()

            elif any(cmd in text for cmd in ["clear reminders", "delete all reminders", "remove all reminders"]):
                return self.reminder_manager.clear_all_reminders()

        # Memory commands
            elif "list history" in text:
                return self._handle_list_history(text)

            elif "clear history" in text or "delete history" in text:
                return self._handle_memory_clear_interaction(text)

        # Music
        # Music
            elif "play playlist" in text or "play all songs" in text:
                return self.music_player.play_playlist()
        
            elif text.startswith("play "):
                song = self.music_player.extract_song_name(text)
                return self.music_player.play_song(song)

        # Websites
            elif any(cmd in text for cmd in ["open youtube", "open instagram", "open github", "open linkedin", "open chat gpt", "open gmail", "open whatsapp", "open aums"]):
                website_commands = {
                    "open youtube": "youtube",
                    "open instagram": "instagram", 
                    "open github": "github",
                    "open linkedin": "linkedin",
                    "open chat gpt": "chat gpt",
                    "open gmail": "gmail",
                    "open whatsapp": "whatsapp",
                    "open aums": "aums"
                }
                for cmd,site in website_commands.items():
                    if cmd in text:
                        return self.web_search.open_website(site)

                    # Date & Time
                    elif "date" in text or "time" in text:
                        return self.system_commands.get_date_time(text)

                # Greetings
                    elif "how are you" in text:
                        return "I'm great, thanks for asking!"
                    elif "who are you" in text:
                        return "I am Friday, your personal AI assistant. I'm here to help you with tasks, searches, and more."
                    elif "what is your name" in text:
                        return "My name is Friday."

                # Holidays
                    elif "holiday" in text or "important day" in text or "today special" in text:
                        return self.calendar_service.get_important_days()

                # Exit
                    elif "goodbye" in text or "bye" in text:
                        response = "Goodbye, have a nice day, Friday going offline."
                        self.tts.speak(response)
                        sys.exit(0)

                    # Gemini fallback for everything else             
                    elif any(cmd in text for cmd in ["do i have any emails", "any emails", "email notification"]):
                        unread_count = self.email_manager.get_unread_count()
                        if unread_count == 0:
                            return "Your inbox is clear. No unread emails."
                        elif unread_count == 1:
                            return f"You have 1 unread email. Say 'check my emails' to read it."
                        else:
                            return f"You have {unread_count} unread emails. Say 'check my emails' to read them."

                    # Email Commands - MORE AGGRESSIVE MATCHING
                    elif any(cmd in text for cmd in ["write email to", "compose email to", "create email to"]):
                        return self._handle_email_creation(text)

                    elif any(cmd in text for cmd in ["send email to", "email to", "mail to"]):
                        return self._handle_email_creation(text)

                    # Quick email templates
                    elif any(cmd in text for cmd in ["send meeting email to", "send thank you email to", "send followup to"]):
                        return self._handle_quick_email(text)

                    # Fallback - if it has "email" and "to" anywhere in the command
                    elif "email" in text and " to " in text:
                        return self._handle_email_creation(text)

                    # Contact management
                    elif "list contacts" in text:
                        return self.contact_manager.list_contacts()

                    # Shutdown command
                    elif any(cmd in text for cmd in ["shutdown", "power off", "turn off computer"]):
                        return self.system_commands.shutdown_computer(self.tts)
                    
                    # Study Planner commands
                    elif any(cmd in text for cmd in ["today's study", "study schedule", "what should i study", "today study"]):
                        schedule = self.study_planner.get_todays_study_schedule()
                        return schedule if schedule else "No study plan found. Please create a study plan first by saying 'create study plan'."

                    elif any(cmd in text for cmd in ["show study plan", "view study plan", "display study plan"]):
                        study_plan = self.study_planner.load_study_plan()
                        if study_plan:
                            total_subjects = len(study_plan['subjects'])
                            total_days = study_plan['total_study_days']
                            hours_per_day = study_plan['available_hours_per_day']
                            return f"You have a study plan with {total_subjects} subjects over {total_days} days, studying {hours_per_day} hours daily. Say 'today's study schedule' for details."
                        else:
                            return "No study plan found. Say 'create study plan' to make one."

                    elif any(cmd in text for cmd in ["create study plan", "make study schedule", "new study plan"]):
                        return self._handle_study_plan_creation(text)
                        
                    elif any(phrase in text for phrase in ["clear study plan", "delete study plan", "remove study plan", "erase study plan"]):
                        return self.study_planner.clear_study_plan()

                    # Google Search
                    elif "search" in text or "google" in text:
                        query = self.web_search.extract_search_query(text)
                        return self.web_search.google_search(query)

                    # Wikipedia
                    elif "tell me about" in text or "information about" in text or "wikipedia" in text:
                        topic = self.web_search.extract_topic_from_text(text)
                        return self.web_search.wikipedia_search(topic)

                    # Weather
                    elif "weather" in text:
                        city = self._extract_city_from_text(text)
                        return self.weather_service.get_weather(city)

                    # Reminders
                    elif "remind me" in text:
                        return self.reminder_manager.add_reminder_from_text(text)

                    elif any(cmd in text for cmd in ["list reminders", "show reminders", "what reminders"]):
                        return self.reminder_manager.list_reminders_text()

                    elif any(cmd in text for cmd in ["clear reminders", "delete all reminders", "remove all reminders"]):
                        return self.reminder_manager.clear_all_reminders()

                    # Memory commands
                    elif "list history" in text:
                        return self._handle_list_history(text)

                    elif "clear history" in text or "delete history" in text:
                        return self._handle_memory_clear_interaction(text)

                    # Music
                    elif "play playlist" in text or "play all songs" in text:
                        return self.music_player.play_playlist()
                    
                    elif text.startswith("play "):
                        song = self.music_player.extract_song_name(text)
                        return self.music_player.play_song(song)

                    # Websites
                    website_commands = {
                        "open youtube": "youtube",
                        "open instagram": "instagram", 
                        "open github": "github",
                        "open linkedin": "linkedin",
                        "open chat gpt": "chat gpt",
                        "open gmail": "gmail",
                        "open whatsapp": "whatsapp",
                        "open aums": "aums"
                    }
                    
                    for cmd, site in website_commands.items():
                        if cmd in text:
                            return self.web_search.open_website(site)

                        # Date & Time
                        elif "date" in text or "time" in text:
                            return self.system_commands.get_date_time(text)

                        # Greetings
                        elif "how are you" in text:
                            return "I'm great, thanks for asking!"
                        elif "who are you" in text:
                            return "I am Friday, your personal AI assistant. I'm here to help you with tasks, searches, and more."
                        elif "what is your name" in text:
                            return "My name is Friday."

                        # Holidays
                        elif "holiday" in text or "important day" in text or "today special" in text:
                            return self.calendar_service.get_important_days()

                        # Exit
                        elif "goodbye" in text or "bye" in text:
                            response = "Goodbye, have a nice day, Friday going offline."
                            self.tts.speak(response)
                            sys.exit(0)

                        # Gemini fallback for everything else
                        else:
                            response = self.gemini_client.query_gemini(text, self.memory_manager.conversation_history)
                            if isinstance(response, str) and ("Gemini API error" in response or "did not return" in response):
                                try:
                                    info = wikipedia.summary(text, sentences=2)
                                    return info
                                except:
                                    return f"Could not find an answer. You can search online: https://www.google.com/search?q={text}"
                            return response
                        
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def run(self):
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        self.greet_user()
        
        # Start reminder checking thread
        reminder_thread = threading.Thread(target=self.reminder_manager.check_reminders_loop, daemon=True)
        reminder_thread.start()
        
        # Remind about study schedule on startup
        study_plan = self.study_planner.load_study_plan()
        if study_plan:
            self.study_planner.remind_study_schedule(self.tts)

        while True:
            if self.speech_recognizer.listen_for_wake_word():
                self.tts.speak("Yes, how can I help you?")
                command = self.speech_recognizer.listen_for_command()
                if command:
                    self.reset_conversation_state()
                    response = self.handle_intent(command)
                    
                    # Handle special cases that need voice interaction
                    if response and isinstance(response, dict) and "action" in response:
                        if response["action"] == "shutdown_confirmation":
                            confirmation = self.listen_with_retry(context="shutdown_confirmation", max_retries=2)
                            if confirmation and "yes" in confirmation.lower():
                                shutdown_result = self.system_commands.execute_shutdown()
                                self.tts.speak(shutdown_result)
                            else:
                                self.tts.speak("Shutdown cancelled!")
                        continue
                    
                    if response:
                        self.memory_manager.add_to_memory(command, response)
                        self.tts.speak(response)
    

    def _handle_email_check(self, text):
        """Handle email inbox checking"""
        try:
            unread_count = self.email_manager.get_unread_count()
            
            if unread_count == 0:
                return "You have no unread emails."
            
            # Speak notification
            if unread_count == 1:
                self.tts.speak(f"You have {unread_count} unread email. Would you like me to read it?")
            else:
                self.tts.speak(f"You have {unread_count} unread emails. Would you like me to read them?")
            
            
            # Get user response with flexible matching
            response = self.listen_with_retry(
                context="email_check_response",
                max_retries=3  # Increased retries
            )
            
            if response:
                # Flexible yes detection
                yes_words = ["yes", "yeah", "yep", "sure", "okay", "ok", "go ahead", "please", "read", "read them"]
                no_words = ["no", "nope", "nah", "skip", "cancel", "not now"]
                
                response_lower = response.lower()
                
                if any(word in response_lower for word in yes_words):
                    return self._read_emails_interactive()
                elif any(word in response_lower for word in no_words):
                    return "Okay, I won't read your emails right now."
                else:
                    self.tts.speak("I didn't understand. Please say yes to read emails or no to skip.")
                    return "Email check cancelled."
            else:
                return "I didn't get a response. Email check cancelled."
        except Exception as e:
            return f"Error checking emails: {str(e)}"

    def _read_emails_interactive(self):
        """Interactive email reading session"""
        try:
            emails = self.email_manager.check_inbox()
            
            if isinstance(emails, str):  # Error message
                self.tts.speak(emails)
                return emails
            
            if not emails:
                return "No unread emails found."
            
            self.tts.speak(f"I found {len(emails)} unread emails.")
            
            for i, email in enumerate(emails, 1):
                self.tts.speak(f"Email {i} of {len(emails)}")
                self.tts.speak(f"From: {email['from']}")
                self.tts.speak(f"Subject: {email['subject']}")
                
                # Ask if user wants to hear full content
                self.tts.speak("Would you like me to read the full email? Say 'yes', 'no', or 'next' to skip to next email.")
                
                response = self.listen_with_retry(
                    context="email_read_choice",
                    max_retries=2
                )
                
                if response and 'yes' in response.lower():
                    # Read full email
                    result = self.email_manager.read_email_aloud(email['id'], self.tts)
                    if "Error" in result:
                        self.tts.speak("Sorry, I couldn't read that email.")
                    
                    # Ask for action
                    self.tts.speak("Say 'reply' to respond, 'delete' to delete, or 'next' for next email.")
                    action = self.listen_with_retry(context="email_action", max_retries=2)
                    
                    if action and 'reply' in action.lower():
                        self._handle_email_reply(email)
                    elif action and 'delete' in action.lower():
                        self.tts.speak("Delete functionality not implemented yet.")
                
                elif response and 'next' in response.lower():
                    continue
                elif response and 'stop' in response.lower():
                    break
            
            return "Finished reading emails."
        except Exception as e:
            return f"Error reading emails: {str(e)}"

    def _handle_email_reply(self, original_email):
        """Handle replying to an email"""
        self.tts.speak(f"Replying to email from {original_email['from']}")
        
        # Extract sender name for addressing
        sender_name = original_email['from'].split('<')[0].strip()
        if not sender_name or '@' in sender_name:
            sender_name = "there"
        
        # Get reply content
        self.tts.speak("What would you like to say in your reply?")
        reply_content = self.listen_with_retry(context="email_reply_content", max_retries=2)
        
        if reply_content:
            # Extract email from "From" field
            from_field = original_email['from']
            email_match = re.search(r'<(.+?)>', from_field)
            if email_match:
                recipient_email = email_match.group(1)
            else:
                recipient_email = from_field  # Fallback
            
            subject = f"Re: {original_email['subject']}"
            
            # Send reply
            result = self.email_manager.send_email(recipient_email, subject, reply_content)
            self.tts.speak(result)
        else:
            self.tts.speak("No reply content provided.")

    def _handle_quick_email_check(self):
        """Quick check for unread emails"""
        unread_count = self.email_manager.get_unread_count()
        
        if unread_count == 0:
            return "Your inbox is clear. No unread emails."
        elif unread_count == 1:
            return f"You have 1 unread email. Say 'check my emails' to read it."
        else:
            return f"You have {unread_count} unread emails. Say 'check my emails' to read them."

if __name__ == "__main__":
    assistant = FridayAssistant()
    assistant.run()