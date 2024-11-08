import requests
import json

# Define the API endpoint
api_url = "http://localhost:5000/evaluate"

# Prepare the payload
payload = {
    "instruction_file": "prompts/chemistry_prompt.txt",
    "data": [{
        "Question Number": "1",
        "Main Statements": "Fig. 1 shows a photograph of a woodlouse.",
        "child statement": "The magnification of the woodlouse in Fig.1 is ×9. The length of line PQ is 48 mm.\n\nmagnification= length of line PQ / actual width of woodlouse",
        "Category": "Main Statement: 2(a)",
        "Question": "Calculate the actual width of the woodlouse using the formula and the measurement of line PQ.",
        "Type of Question": "numerical",
        "Total marks": "6",
        "Individual Marks": "2",
        "Student Answer": "magnification= length of line PQ / actual width of woodlouse\n\n= 48mm / 9   =5.33mm\n\nActual width of woodlouse=48×9= 432mm",
        "Label Image": "",
        "Correct Answer": "",
        "Student Answer [Image]": "",
        "Reason for Correct Answer": "",
        "Marking Scheme": "The actual width of the woodlouse can be calculated as follows...\n\n• 48 ÷ 9: [mark]\n\n• 5.33: [mark]\n\nAnswer must be correctly rounded to three significant figures to obtain mark.\n\nFull marks can be awarded for the correct answer in the absence of other",
        "Marking Scheme (Image)": "",
        "Possible Wrong Answers": "",
        "Topic": "",
        "Link": ""
    },
    {
        "Question Number": "2",
        "Main Statements": "Fig. 1 shows a photograph of a woodlouse.",
        "child statement": "The magnification of the woodlouse in Fig.1 is ×9. The length of line PQ is 48 mm.\n\nmagnification= length of line PQ / actual width of woodlouse",
        "Question": "Calculate the actual width of the woodlouse using the formula and the measurement of line PQ.",
        "Type of Question": "numerical",
        "Total marks": "6",
        "Individual Marks": "2",
        "Student Answer": "magnification= length of line PQ / actual width of woodlouse\n\n= 48mm / 9   =5.33mm\n\nActual width of woodlouse=48×9= 432mm",
        "Marking Scheme": "The actual width of the woodlouse can be calculated as follows...\n\n• 48 ÷ 9: [mark]\n\n• 5.33: [mark]\n\nAnswer must be correctly rounded to three significant figures to obtain mark.\n\nFull marks can be awarded for the correct answer in the absence of other",
}]
}

# Send the POST request
response = requests.post(api_url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    print("Request was successful.")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Request failed with status code {response.status_code}")
    print("Response:")
    print(response.text)
