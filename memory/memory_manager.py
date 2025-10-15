# memory/memory_manager.py
import json
import os
from dotenv import load_dotenv
load_dotenv()

import datetime
from config import MEMORY_FILE

class MemoryManager:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.conversation_history = self.load_memory()
    
    
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        today = str(datetime.date.today())
                        return {today: data}
                    elif isinstance(data, dict):
                        return data
                    else:
                        return {}
            except:
                return {}
        return {}
    
    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.conversation_history, f, indent=4)
    
    def add_to_memory(self, question, answer):
        today = str(datetime.date.today())
        if today not in self.conversation_history:
            self.conversation_history[today] = []
        self.conversation_history[today].append({"q": question, "a": answer})
        self.save_memory()
    
    def list_history(self, day="all"):
        if not isinstance(self.conversation_history, dict) or not self.conversation_history:
            return "I don't have any history stored yet."

        today = datetime.date.today().isoformat()
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        result = []
        counter = 1

        if day == "today":
            if today in self.conversation_history:
                result.append("Today's history:")
                for q in self.conversation_history[today]:
                    result.append(f"{counter}. {q['q']}")
                    counter += 1
            else:
                result.append("No history recorded for today.")

        elif day == "yesterday":
            if yesterday in self.conversation_history:
                result.append("Yesterday's history:")
                for q in self.conversation_history[yesterday]:
                    result.append(f"{counter}. {q['q']}")
                    counter += 1
            else:
                result.append("No history recorded for yesterday.")

        else:
            result.append("All recorded history:")
            for date_key in sorted(self.conversation_history.keys()):
                result.append(f"\n{date_key}:")
                for q in self.conversation_history[date_key]:
                    result.append(f"{counter}. {q['q']}")
                    counter += 1

        return "\n".join(result)
    
    def clear_memory(self, command_text=""):
        if not self.conversation_history:
            return "No memory to clear."

        command_text = command_text.lower().strip() if command_text else ""
        
        if "delete history" in command_text:
            self.conversation_history.clear()
            self.save_memory()
            return "Deleted all history successfully."

        dates = list(self.conversation_history.keys())
        
        # For voice interaction, we'll return the dates list for the main handler to manage
        return {"dates": dates, "action": "clear_memory"}
    
    def clear_specific_date(self, date):
        if date in self.conversation_history:
            del self.conversation_history[date]
            self.save_memory()
            return f"Cleared memory for {date}."
        return "Date not found in memory."
    
    def clear_all_memory(self):
        self.conversation_history.clear()
        self.save_memory()
        return "Cleared all history successfully."
