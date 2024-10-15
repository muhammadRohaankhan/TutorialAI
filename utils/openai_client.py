
import time
from utils.json_utils import try_parse_json_or_fix
from utils.encoding_utils import decode_and_fix_text
from utils.openai_helper import get_openai_client

def send_evaluation_request(instructions, row_data, image_contents=None):
    print("Sending evaluation request...")
    MODEL = "gpt-4o-mini"
    messages = [{"role": "system", "content": instructions}]
    client = get_openai_client()

    row_data_decoded = row_data.apply(decode_and_fix_text)

    joined_statements = (
        f"Main Statements: {row_data_decoded['Main Statements']}, "
        f"Child Statement: {row_data_decoded['child statement']}, "
        f"Question: {row_data_decoded['Question']}, "
        f"Individual Marks: {row_data_decoded['Individual Marks']}, "
        f"Student Answer: {row_data_decoded['Student Answer']}, "
        f"Marking Scheme: {row_data_decoded['Marking Scheme']}"
    )

    content = [{"type": "text", "text": joined_statements}]

    if image_contents:
        for item in image_contents:
            column_name = item['column_name']
            url = item['url']
            content.append({
                "type": "text",
                "text": f"This image is from '{column_name}':"
            })
            content.append({
                "type": "image_url",
                "image_url": {"url": url}
            })
        MODEL = "gpt-4o-2024-08-06"
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": joined_statements})

    retry_attempts = 3
    retry_delay = 10

    for attempt in range(retry_attempts):
        try:
            time.sleep(retry_delay * attempt)
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.0,
                response_format = { "type": "json_object"}
            )
            parsed_json, is_valid = try_parse_json_or_fix(completion.choices[0].message.content)
            if not is_valid:
                print("JSON was corrected.")
            return parsed_json, messages[1:]
        except Exception as e:
            print(f"Attempt {attempt + 1} - Error in sending evaluation request: {e}")
            if "rate_limit_exceeded" in str(e) and attempt < retry_attempts - 1:
                print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                continue
            raise Exception(f"Error in sending evaluation request: {e}")

    print("All attempts to send evaluation have failed.")
    return None, None