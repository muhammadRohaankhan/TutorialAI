import os
import json
import pandas as pd
from datetime import datetime
from flask_cors import CORS
from functools import wraps
from flask import Flask, request, jsonify

from utils.logger import save_log
from utils.data_processing import is_valid_image_url
from utils.instruction_loader import load_instructions
from utils.openai_client import send_evaluation_request
from utils.token_cost_calculator import calculate_tokens_and_cost
from utils.save_csv import update_csv_file, save_token_cost_data

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

API_KEY = os.getenv("API_KEY")
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), config["image-folder"])
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), config["output-folder"])    
LOG_FOLDER = os.path.join(os.path.dirname(__file__), config["log-folder"])    


OUTPUT_FILE_PATH = os.path.join(OUTPUT_FOLDER, "output_file.csv")
COSTING_FILE_PATH = os.path.join(OUTPUT_FOLDER, "costing_file.csv")

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Missing or invalid Authorization header."}), 401
        token = auth_header.split(" ")[1]
        if token != API_KEY:
            return jsonify({"status": "error", "message": "Invalid API key."}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/evaluate', methods=['POST'])
@require_api_key
def evaluate():
    data = request.json
    instruction_file = data.get('instruction_file')
    input_data = data.get('data')
    model_name = data.get('model_name')

    if not instruction_file or not input_data:
        return jsonify({"status": "error", "message": "Missing instruction file or data."})

    instructions = load_instructions(instruction_file)
    evaluations = []
    token_data = []

    input_data_list = input_data if isinstance(input_data, list) else [input_data]

    for idx, item in enumerate(input_data_list):
        row = pd.Series(item)

        if pd.isna(row.get('Type of Question')) or pd.isna(row.get('Individual Marks')) or pd.isna(row.get('Student Answer')):
            print(f"Skipping invalid row at index {idx}.")
            continue

        image_contents = []
        for col in ['Label Image', 'Student Answer [Image]', 'Marking Scheme (Image)']:
            if pd.notna(row.get(col)):
                image_urls = row[col].split()
                for url in image_urls:
                    if is_valid_image_url(url):
                        image_contents.append({'url': url, 'column_name': col})

        save_log(LOG_FOLDER, instructions, row.to_dict(), image_contents)
        response, messages = send_evaluation_request(instructions, row, image_contents, model_name)

        evaluations.append({
            **row.to_dict(),
            "GPT Response": response,
            "Prompt": messages
        })

        token_cost_info = calculate_tokens_and_cost( instructions, row, image_contents, model_name)
        token_data.append({
            "Row Index": idx,
            "Total Input Tokens": token_cost_info["total_input_tokens"],
            "Total Cost ($)": token_cost_info["total_cost"]
        })

    update_csv_file(OUTPUT_FILE_PATH, evaluations)
    save_token_cost_data(COSTING_FILE_PATH, token_data)

    return jsonify({"status": "success", "message": "Evaluation complete.", "evaluations": evaluations})

if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(port=5000, debug=True)
