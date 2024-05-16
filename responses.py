import os 
import json
from get_rice import get_rice_info

def load_json(filepath):
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {filepath} does not exist.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from the file {filepath}.")
        return None

def get_last_json_file_number(directory):
    try:
        files = os.listdir(directory)
        json_files = [file for file in files if file.endswith(".json")]
        if not json_files:
            return -1  # Return -1 if no JSON files are found
        numbers = [int(file.split("_")[1].split(".")[0]) for file in json_files]
        return max(numbers)
    except Exception as e:
        print(f"Error: Failed to process files in directory {directory} - {e}")
        return -1

def get_responses_from_safe(SAFE_NAME, AUTH_KEY):
    responses_dir = os.path.join("./dataset/responses", SAFE_NAME)
    json_path = os.path.join("./dataset/refs", SAFE_NAME + ".json")
    metadata = load_json(json_path)
    os.makedirs(responses_dir, exist_ok=True)

    if metadata and "bbox" in metadata:
        y_min = metadata["bbox"]["y_min"]
        x_min = metadata["bbox"]["x_min"]
        y_max = metadata["bbox"]["y_max"]
        x_max = metadata["bbox"]["x_max"]

        last_json_file_number = get_last_json_file_number(responses_dir)
        if last_json_file_number == -1:
            get_rice_info(AUTH_KEY,
                        y_min=y_min,
                        x_min=x_min,
                        y_max=y_max,
                        x_max=x_max,
                        json_dir=responses_dir,
                        start_index=0)
        else:
            get_rice_info(AUTH_KEY,
                        y_min=y_min,
                        x_min=x_min,
                        y_max=y_max,
                        x_max=x_max,
                        json_dir=responses_dir,
                        start_index=last_json_file_number * 1000)
    else:
        print("Error: Metadata is missing or does not contain bounding box information.")


SAFE_NAME = ""
AUTH_KEY = ""

get_responses_from_safe(SAFE_NAME=SAFE_NAME, AUTH_KEY=AUTH_KEY)