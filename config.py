import json
import os

with open('config.json', 'r', encoding='utf-8') as file:
    config_file = json.load(file)

OPENAI_API_KEY = config_file['openai-api-key']

IMAGE_DIR = config_file["image-folder"]
OUTPUT_DIR = config_file["output-folder"]
COSTING_DIR = os.path.join(OUTPUT_DIR, "costing")

OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, "evaluated_output.csv")
COSTING_FILE_PATH = os.path.join(COSTING_DIR, "costing_details.csv")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(COSTING_DIR, exist_ok=True)
