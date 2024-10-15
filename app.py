import datetime
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
    file_path = data.get('file_path')
    instruction_file = data.get('instruction_file')

    if not file_path or not instruction_file:
        return jsonify({"status": "error", "message": "Missing file path or instruction file."})

    instructions = load_instructions(instruction_file)
    try:
        df = pd.read_csv(file_path, encoding='cp1252')
    except Exception as e:
        print(e)
        df = pd.read_csv(file_path, encoding='utf-8')
    evaluations = []

    ts = int(datetime.datetime.now().timestamp())

    for row_idx, row in df.iterrows():
        if row.isnull().all():
            print(f"Row {row_idx} is entirely null, skipping this row.")
            continue

        print(f"Evaluating row {row_idx}...")
        if pd.notna(row.get('Type of Question')):
            question_type = row['Type of Question'].strip().lower()
            if question_type not in ["short question", "numerical", "long question", "diagram", "equation"]:
                print(f"Row {row_idx} has an invalid or unsupported type of question, skipping...")
                continue
        else:
            print(f"Row {row_idx} has missing 'Type of Question', skipping...")
            continue

        if pd.isna(row['Individual Marks']) or (pd.isna(row['Marking Scheme']) and pd.isna(row['Marking Scheme (Image)'])) or (pd.isna(row['Student Answer']) and question_type not in ['diagram', 'equation']):
            if pd.isna(row['Individual Marks']):
                print(f"Row {row_idx} is missing 'Individual Marks'")
            if pd.isna(row['Marking Scheme']) and pd.isna(row['Marking Scheme (Image)']):
                print(f"Row {row_idx} is missing 'Marking Scheme'")
            if pd.isna(row['Student Answer']) and question_type not in ['diagram', 'equation']:
                print(f"Row {row_idx} is missing 'Student Answer'")
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
        save_to_csv(OUTPUT_FILE_PATH.replace(".csv", f"_{str(ts)}.csv"), evaluations)
    print("Evaluation complete.")
    return jsonify({"status": "success", "message": "Evaluation complete.", "evaluations": evaluations})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
