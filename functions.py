import json
from datetime import datetime
import subprocess
import platform
import os

# Function to save jobs to a JSON file
def save_to_json(jobs, filename=None):
    if filename is None:
        # Generate a filename with current date and time if not provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobs_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=4)
    
    print(f"Jobs saved to {filename}")

def read_file(filename="prompt.txt"):
    try:
        with open(filename, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except IOError:
        print(f"Error: There was an issue reading the file '{filename}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None  # Return None if there was an error

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "rapidApiKey": "",
            "jobQuery": "contador",
            "jobLocation": "chile",
            "jobPlace": "remote",
        }
    
def save_config(config):
    with open("config.json", 'w') as f:
        json.dump(config, f, indent=2)

def append_to_log(text):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{current_time} - {text}"
    
    with open('log.txt', 'a') as log_file:
        log_file.write(log_entry + '\n')


def open_log_file():
    log_file_path = "log.txt"
    
    if not os.path.exists(log_file_path):
        print(f"Error: {log_file_path} not found.")
        return

    try:
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', log_file_path))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(log_file_path)
        else:                                   # linux variants
            subprocess.call(('xdg-open', log_file_path))
        return True
    except Exception as e:
        #print(f"Error opening {log_file_path}: {str(e)}")
        return False
