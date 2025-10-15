# study_planner/study_planner.py
import json
import os
from dotenv import load_dotenv
load_dotenv()

import datetime
import re
from dateutil import parser
from config import STUDY_PLAN_FILE
from .topic_fetcher import TopicFetcher
from .pdf_generator import PDFGenerator

class StudyPlanner:
    def __init__(self):
        self.study_plan_file = STUDY_PLAN_FILE
        self.topic_fetcher = TopicFetcher()
        self.pdf_generator = PDFGenerator()
    
    def load_study_plan(self):
        if os.path.exists(self.study_plan_file):
            try:
                with open(self.study_plan_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_study_plan(self, plan):
        with open(self.study_plan_file, "w") as f:
            json.dump(plan, f, indent=4)
    
    def parse_spoken_date(self, date_text):
        if not date_text:
            return None
        
        date_text = date_text.strip().lower()
        print(f"🔍 Debug: Processing date text: '{date_text}'")
        
        replacements = {
            "next week": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            "next month": (datetime.date.today().replace(day=28) + datetime.timedelta(days=4)).replace(day=1).strftime("%Y-%m-%d"),
        }
        
        for pattern, replacement in replacements.items():
            if pattern in date_text:
                return replacement
        
        month_mapping = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for month_name, month_num in month_mapping.items():
            if month_name in date_text:
                day_match = re.search(r'(\d{1,2})(?:\s|st|nd|rd|th)', date_text)
                year_match = re.search(r'(\d{4})', date_text)
                
                if day_match:
                    day = int(day_match.group(1))
                    year = int(year_match.group(1)) if year_match else datetime.date.today().year
                    
                    try:
                        exam_date = datetime.date(year, month_num, day)
                        today = datetime.date.today()
                        if exam_date <= today:
                            return None
                        return exam_date.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
        
        try:
            parsed_date = parser.parse(date_text, fuzzy=True)
            exam_date = parsed_date.date()
            
            today = datetime.date.today()
            if exam_date <= today:
                return None
            
            return exam_date.strftime("%Y-%m-%d")
            
        except (ValueError, parser.ParserError):
            print(f"❌ Could not parse date: {date_text}")
            return None
    
    def create_study_plan_from_single_command(self, subject_name, exam_date):
        try:
            existing_plan = self.load_study_plan()
            existing_subjects = existing_plan.get('subjects', []) if existing_plan else []
            
            existing_subject_names = [s['name'].lower() for s in existing_subjects]
            if subject_name.lower() in existing_subject_names:
                existing_subjects = [s for s in existing_subjects if s['name'].lower() != subject_name.lower()]
            
            topics = self.topic_fetcher.get_subject_topics(subject_name)
            
            difficulty = 'medium'
            
            subject_data = {
                'name': subject_name,
                'exam_date': exam_date,
                'topics': topics,
                'difficulty': difficulty
            }
            
            all_subjects = existing_subjects + [subject_data]
            
            today = datetime.date.today()
            
            exam_dates = [datetime.datetime.strptime(s['exam_date'], "%Y-%m-%d").date() for s in all_subjects]
            last_exam = max(exam_dates)
            study_days = (last_exam - today).days + 1
            
            if study_days <= 0:
                return None
            
            available_hours = 4.0
            
            prioritized_subjects = self.calculate_study_priority(all_subjects)
            for i, subject in enumerate(prioritized_subjects):
                subject['priority_rank'] = i + 1
                exam_date_obj = datetime.datetime.strptime(subject['exam_date'], "%Y-%m-%d").date()
                subject['days_until_exam'] = (exam_date_obj - today).days
            
            study_plan = {
                'created_date': today.isoformat(),
                'subjects': prioritized_subjects,
                'available_hours_per_day': available_hours,
                'total_study_days': study_days,
                'daily_schedule': self.allocate_study_hours(prioritized_subjects, available_hours, min(study_days, 30))
            }
            
            self.save_study_plan(study_plan)
            pdf_filename = self.pdf_generator.create_study_pdf(study_plan)
            
            return study_plan
            
        except Exception as e:
            print(f"Error creating study plan: {e}")
            return None
    
    def calculate_study_priority(self, subjects_data):
        today = datetime.date.today()
        prioritized_subjects = []
        
        for subject in subjects_data:
            exam_date = datetime.datetime.strptime(subject['exam_date'], "%Y-%m-%d").date()
            days_until_exam = (exam_date - today).days
            
            priority_score = max(1, 100 - days_until_exam)
            
            difficulty_multiplier = {
                "hard": 1.5,
                "medium": 1.0,
                "easy": 0.7
            }.get(subject.get('difficulty', 'medium'), 1.0)
            
            priority_score *= difficulty_multiplier
            prioritized_subjects.append({
                **subject,
                'priority_score': priority_score,
                'days_until_exam': days_until_exam
            })
        
        prioritized_subjects.sort(key=lambda x: x['priority_score'], reverse=True)
        return prioritized_subjects
    
    def allocate_study_hours(self, subjects, total_hours_per_day, study_days):
        daily_plan = {}
        
        all_topics = []
        for subject in subjects:
            topics = subject.get('topics', [])
            all_topics.extend([(subject['name'], topic) for topic in topics])
        
        topics_per_day = max(1, len(all_topics) // study_days)
        
        for day in range(study_days):
            day_date = (datetime.date.today() + datetime.timedelta(days=day)).isoformat()
            daily_plan[day_date] = []
            
            remaining_hours = total_hours_per_day
            subjects_today = []
            
            start_idx = day * topics_per_day
            end_idx = min(start_idx + topics_per_day, len(all_topics))
            
            day_topics = all_topics[start_idx:end_idx]
            
            subject_topics = {}
            for subject_name, topic in day_topics:
                if subject_name not in subject_topics:
                    subject_topics[subject_name] = []
                subject_topics[subject_name].append(topic)
            
            for subject in subjects:
                subject_name = subject['name']
                if subject_name in subject_topics:
                    subject_hours = min(2.0, remaining_hours)
                    if subject_hours >= 0.5:
                        daily_plan[day_date].append({
                            'subject': subject_name,
                            'hours': round(subject_hours, 1),
                            'topics': subject_topics[subject_name],
                            'start_time': '09:00'
                        })
                        remaining_hours -= subject_hours
        
        return daily_plan
    
    def get_todays_study_schedule(self):
        study_plan = self.load_study_plan()
        if not study_plan:
            return None
        
        today = datetime.date.today().isoformat()
        daily_schedule = study_plan.get('daily_schedule', {}).get(today, [])
        
        if not daily_schedule:
            return "No study sessions scheduled for today. Enjoy your day off!"
        
        sessions_text = []
        total_hours = 0
        current_time = datetime.datetime.strptime("09:00", "%H:%M")
        
        for session in daily_schedule:
            end_time = current_time + datetime.timedelta(hours=session['hours'])
            time_slot = f"{current_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            topics = ", ".join(session['topics']) if session['topics'] else "General Study"
            sessions_text.append(f"{time_slot}: {session['subject']} - {topics}")
            total_hours += session['hours']
            current_time = end_time + datetime.timedelta(minutes=15)
        
        schedule_text = f"Today's study schedule ({total_hours} hours total):\n" + "\n".join(sessions_text)
        return schedule_text
    
    def remind_study_schedule(self, tts):
        schedule = self.get_todays_study_schedule()
        if schedule and "No study sessions" not in schedule:
            tts.speak("Here's your study schedule for today:")
            import time
            time.sleep(1)
            lines = schedule.split('\n')
            tts.speak(lines[0])
            time.sleep(0.5)
            for line in lines[1:]:
                tts.speak(line)
                time.sleep(0.5)
    
    def clear_study_plan(self):
        if os.path.exists(self.study_plan_file):
            os.remove(self.study_plan_file)
            return "Study plan cleared successfully."
        return "No study plan found to clear."
