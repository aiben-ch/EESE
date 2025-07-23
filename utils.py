# 处理图片、错误回复的函数

import json
import os
import requests
from io import BytesIO
import base64
from config import OUTPUT_CONFIG
import re


def load_json_dataset(path, suffix=""):
    """load the json dataset"""
    base = os.path.splitext(path)[0]
    new_path = f"{base}{suffix}.json"
    with open(new_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl_data(file_path):
    """load the data in JSONL format"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def save_results(data, results, overall_avg):
    """save the results to files"""
    save_path = OUTPUT_CONFIG["detailed_results"]
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # save the summary results
    summary = {
        'discipline_results': results,
        'overall_average': overall_avg,
        'total_questions': len(data)
    }
    
    with open(OUTPUT_CONFIG["summary_results"], 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def fetch_image_content(image_url):
    """fetch the image content from the url"""
    response = requests.get(image_url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None


def encode_image(image):
    """encode the image to base64"""
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
        print(f"encoding error: {e}")
        return None


def extract_first_numeric_score(score_text):
    """
    从评分文本中提取第一个出现的整数数字作为分数
    
    参数:
        score_text (str): 包含评分的文本
        
    返回:
        int or None: 提取到的第一个整数分数，若无法提取则返回None
        
    说明:
        - 支持提取任意位数的整数（1位、2位、3位等）
        - 适用于中英文混合文本
        - 只提取第一个出现的完整整数
        - 对于小数，只提取整数部分
        - 对于负数，只提取数字部分（不考虑负号）
    """
    # 验证输入
    if not isinstance(score_text, str) or not score_text.strip():
        return None
    
    # 正则表达式匹配第一个出现的整数（支持多位数）
    # 使用非贪婪模式确保获取第一个出现的数字
    # 匹配数字前后不是数字字符的情况（适用于中英文混合文本）
    match = re.search(r'(?<!\d)\d+(?!\d)', score_text)
    
    if match:
        return int(match.group())
    return None

# 测试用例
if __name__ == "__main__":
    test_samples = [
        "这个回答很好，给9分",
        "评分：85分",
        "我认为应该是7分",
        "10分制下得6分",
        "先给5分，再考虑是否加分",
        "最高95分，这个可得80",
        "优秀，打9分",
        "没有具体分数",
        "100分制的话是90分",  # 提取第一个两位数90
        "给1分有点低，7分比较合适",  # 提取第一个数字1
        "这个答案可以得125分",  # 提取三位数125
        "满分1000分，这个回答得850分",  # 提取第一个数字1000
        "评分标准：满分是10000分，这个答案得7500分",  # 提取第一个数字10000
        "12345分制下，这个答案得9876分",  # 提取第一个数字12345
        "在1到100的范围内，这个答案得75分",  # 提取第一个数字1
        "没有数字的文本",
        "",  # 空字符串
        "   ",  # 只有空格的字符串
        "abc123def456",  # 提取第一个数字123
        "分数是0分",  # 提取0
        "负分-5分",  # 只提取5（不考虑负号）
        "3.14分",  # 只提取3（不考虑小数点）
    ]
    
    for sample in test_samples:
        result = extract_first_numeric_score(sample)
        print(f"文本: {sample:35} 提取的分数: {result}")
    
