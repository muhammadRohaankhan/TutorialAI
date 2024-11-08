import json
import pandas as pd
from config import OUTPUT_FILE_PATH
from flask import Flask, request, jsonify
from utils.instruction_loader import load_instructions
from utils.openai_client import send_evaluation_request
from utils.data_processing import is_valid_image_url, save_to_csv

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    print("Received evaluation request.")
    data = request.json
    instruction_file = data.get('instruction_file')
    input_data = data.get('data')

    if not instruction_file or not input_data:
        return jsonify({"status": "error", "message": "Missing instruction file or data."})

    instructions = load_instructions(instruction_file)
    evaluations = []

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

        save_to_csv(OUTPUT_FILE_PATH, evaluations)

    print("Evaluation complete.")
    return jsonify({"status": "success", "message": "Evaluation complete.", "evaluations": evaluations})

if __name__ == "__main__":
    app.run(port=5000, debug=True)