import os
import json
import pandas as pd
import time
from functools import wraps
from datetime import datetime
from flask import Flask, request, jsonify
from utils.instruction_loader import load_instructions
from config import OUTPUT_FILE_PATH, COSTING_FILE_PATH
from utils.openai_client import send_evaluation_request
from utils.data_processing import is_valid_image_url, save_to_csv
from utils.token_cost_calculator import calculate_tokens_and_cost

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"status": "error", "message": "Missing or invalid Authorization header."}), 401
        token = auth_header.split(" ")[1]  # Extract the token
        if token != API_KEY:
            return jsonify({"status": "error", "message": "Invalid API key."}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/evaluate', methods=['POST'])
@require_api_key
def evaluate():
    print("Received evaluation request.")
    data = request.json
    instruction_file = data.get('instruction_file')
    input_data = data.get('data')

    if not instruction_file or not input_data:
        return jsonify({"status": "error", "message": "Missing instruction file or data."})

    instructions = load_instructions(instruction_file)
    evaluations = []

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    csv_filename = f"{timestamp}.csv"
    token_data = [] 

    if isinstance(input_data, dict):
        input_data_list = [input_data]
    elif isinstance(input_data, list):
        input_data_list = input_data
    else:
        return jsonify({"status": "error", "message": "Invalid data format. 'data' should be a dictionary or a list of dictionaries."})

    for idx, item in enumerate(input_data_list):
        row = pd.Series(item)

        if row.isnull().all():
            print(f"Input data at index {idx} is empty or null, skipping.")
            continue

        print(f"Evaluating input data at index {idx}...")

        if pd.notna(row.get('Type of Question')):
            question_type = row['Type of Question'].strip().lower()
            if question_type not in ["short question", "numerical", "long question", "diagram", "equation"]:
                print(f"Input data at index {idx} has an invalid or unsupported 'Type of Question', skipping...")
                continue
        else:
            print(f"Input data at index {idx} has missing 'Type of Question', skipping...")
            continue

        if pd.isna(row.get('Individual Marks')) or (pd.isna(row.get('Marking Scheme')) and pd.isna(row.get('Marking Scheme (Image)'))) or (pd.isna(row.get('Student Answer')) and question_type not in ['diagram', 'equation']):
            if pd.isna(row.get('Individual Marks')):
                print(f"Input data at index {idx} is missing 'Individual Marks'")
            if pd.isna(row.get('Marking Scheme')) and pd.isna(row.get('Marking Scheme (Image)')):
                print(f"Input data at index {idx} is missing 'Marking Scheme'")
            if pd.isna(row.get('Student Answer')) and question_type not in ['diagram', 'equation']:
                print(f"Input data at index {idx} is missing 'Student Answer'")
            continue

        image_contents = []

        for col in ['Label Image', 'Student Answer [Image]', 'Marking Scheme (Image)']:
            if pd.notna(row.get(col)):
                image_urls = row[col].split()
                for url in image_urls:
                    if is_valid_image_url(url):
                        image_contents.append({'url': url, 'column_name': col})
                    else:
                        print(f"Invalid image URL in '{col}': {url}")

        response, messages = send_evaluation_request(instructions, row, image_contents)
    
        evaluations.append({
            **row.to_dict(),
            "GPT Response": json.dumps(response, ensure_ascii=False),
            "Prompt": messages
        })

        token_cost_info = calculate_tokens_and_cost(instructions, row, image_contents)
        token_data.append({
            "Row Index": idx,
            "Total Input Tokens": token_cost_info["total_input_tokens"],
            "Total Cost ($)": token_cost_info["total_cost"],
            "Instruction Tokens": token_cost_info["instruction_tokens"],
            "Text Tokens": token_cost_info["text_tokens"],
            "Image Cost ($)": token_cost_info["image_cost"],
            "Input Token Cost ($)": token_cost_info["input_token_cost"],
            "Output Token Cost ($)": token_cost_info["output_token_cost"]
        })

        save_to_csv(OUTPUT_FILE_PATH, evaluations)

    token_cost_df = pd.DataFrame(token_data)
    token_cost_df.to_csv(f"{COSTING_FILE_PATH}", index=False)

    print(f"Evaluation complete. Token data saved to {csv_filename}.")
    return jsonify({"status": "success", "message": "Evaluation complete.", "evaluations": evaluations})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
