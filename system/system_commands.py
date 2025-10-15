# system/system_commands.py
import os
from dotenv import load_dotenv
load_dotenv()

import platform
import threading
import time
import datetime

class SystemCommands:
    def __init__(self):
        pass
    
    def shutdown_computer(self, tts):
        tts.speak("Are you sure you want to shut down the computer? Please say yes or no.")
        return {"action": "shutdown_confirmation"}
    
    def execute_shutdown(self):
        os_name = platform.system()
        try:
            if os_name == "Windows":
                os.system("shutdown /s /t 5")
            elif os_name == "Linux" or os_name == "Darwin":
                threading.Thread(target=lambda: (time.sleep(5), os.system("sudo shutdown -h now"))).start()
            else:
                return "Sorry, I can't shut down this operating system."
            return "Shutting down in 5 seconds!"
        except Exception as e:
            return f"Failed to shut down. Error: {e}"
    
    def get_date_time(self, text):
        today = datetime.date.today()
        if "tomorrow" in text:
            target_day = today + datetime.timedelta(days=1)
        elif "day after tomorrow" in text:
            target_day = today + datetime.timedelta(days=2)
        else:
            target_day = today
        
        if "time" in text and "date" not in text:
            now = datetime.datetime.now()
            return f"The time is {now.strftime('%I:%M %p')}"
        elif "date" in text and "time" not in text:
            return f"The date is {target_day.strftime('%A, %d %B %Y')}"
        else:
            now = datetime.datetime.now()
            return f"Today is {target_day.strftime('%A, %d %B %Y')} and the time is {now.strftime('%I:%M %p')}"
    
    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            return "Hello, Good morning!"
        elif 12 <= hour < 16:
            return "Hello, Good afternoon!"
        elif 16 <= hour < 22:
            return "Hello, Good evening!"
        else:
            return "Hello, it's quite late!"
