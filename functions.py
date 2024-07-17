import json
from datetime import datetime

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