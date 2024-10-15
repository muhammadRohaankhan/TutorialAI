import re
import json
from utils.openai_helper import get_openai_client

def try_parse_json_or_fix(response):
    print("Attempting to parse JSON...")
    if not response.strip():
        print("Received an empty response; cannot parse JSON.")
        return None, False

    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        response = json_match.group(0)

    try:
        parsed_json = json.loads(response)
        print("JSON parsed successfully.")
        if "evaluations" in parsed_json:
            all_evals_valid = all(
                "id" in eval and "obtained_marks" in eval and "total_marks" in eval
                for eval in parsed_json["evaluations"]
            )
            if all_evals_valid:
                print("JSON structure is complete and valid.")
                return parsed_json, True
            else:
                print("JSON structure is incomplete or incorrect. Missing required fields in some evaluations.")
                return fix_json_response(response), False
        else:
            print("Expected key 'evaluations' not found in JSON. Attempting to add missing key...")
            return fix_json_response(response), False
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed due to an error: {e}")
        print("Raw response that caused failure:", response)
        return fix_json_response(response), False

def fix_json_response(raw_response):
    print("Fixing incorrect JSON response...")
    fix_instructions = "The JSON response is incorrect. Please correct it to form a valid JSON structure."
    MODEL = "gpt-4o-mini"
    attempts = 5
    client = get_openai_client()

    for attempt in range(attempts):
        try:
            if not raw_response.strip():
                print("No content to fix, returning None.")
                return None
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": fix_instructions},
                    {"role": "user", "content": raw_response},
                ],
                temperature=0.0,
            )
            fixed_json = completion.choices[0].message.content
            print('***********************************************')
            print(fixed_json)
            print('***********************************************')

            if not fixed_json.strip():
                print(f"Attempt {attempt + 1}: Received an empty response after trying to fix JSON.")
                continue
            return json.loads(fixed_json)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1}: JSON still incorrect, retrying... Error: {e}")
            continue
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to fix JSON. Error: {e}")
            if attempt == attempts - 1:
                return None

    print("All attempts to fix JSON have failed.")
    return None