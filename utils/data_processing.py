import requests
import csv

def is_valid_image_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'image' in content_type.lower():
            return True
        else:
            return False
    except requests.RequestException as e:
        print(f"Error validating image URL '{url}': {e}")
        return False

def save_to_csv(file_path, data):
    print(f"Saving data to CSV at {file_path}...")
    fieldnames = data[0].keys()
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print("Data saved successfully.")
