# Functions for processing images and error responses

import json
import os
import requests
from io import BytesIO
import base64
from config import OUTPUT_CONFIG
import re


def load_json_dataset(path, suffix=""):
    """Load the JSON dataset"""
    base = os.path.splitext(path)[0]
    new_path = f"{base}{suffix}.json"
    with open(new_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl_data(file_path):
    """Load the data in JSONL format"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def save_results(data, results, overall_avg):
    """Save the results to files"""
    save_path = OUTPUT_CONFIG["detailed_results"]
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Save the summary results
    summary = {
        'discipline_results': results,
        'overall_average': overall_avg,
        'total_questions': len(data)
    }
    
    with open(OUTPUT_CONFIG["summary_results"], 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def fetch_image_content(image_url):
    """Fetch the image content from the URL"""
    response = requests.get(image_url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None


def encode_image(image):
    """Encode the image to base64"""
    if image is None:
        return None
    buffered = BytesIO()
    try:
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return 'data:image/jpeg;base64,' + img_str
    except Exception as e:
        print(f"Encoding error: {e}")
        return None


def extract_first_numeric_score(score_text):
    """
    extract the first numeric score from the score text
    
    Args:
        score_text (str): the text containing the score
        
    Returns:
        int or None: the first numeric score, if not found, return None
        
    """
    try:
        return int(score_text)
    except:
        # Validate input
        if not isinstance(score_text, str) or not score_text.strip():
            return None
        
        match = re.search(r'(?<!\d)\d+(?!\d)', score_text)
        
        if match:
            return int(match.group())
        return 0
