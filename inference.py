import PIL.Image as Image
from call import try_call_3times
from utils import encode_image, extract_first_numeric_score
from config import LLM_CONFIG, JUDGE_LLM_CONFIG
from collections import defaultdict
import logging

# Construct the prompts for tested models
def construct_test_messages_cn(item, input_image_dir, detail='auto'):
    base_prompt = item["question_en"]
    if item["img"]:
        base_prompt += "\n <image>"
    if item["question_type"] == "Closed-ended":
        base_prompt += "\n直接回答该问题(如果是选择题，直接给出选项即可)，请不要给出任何解析过程。"
    else:
        base_prompt += "\n此为开放式问答，可以给出解题过程。"

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]
    
    if item["img"]:
        """如果有 question图片"""
        for img_file in item.get("img", []):
            image_path = f"{input_image_dir}/{img_file}"
            if isinstance(image_path, str):
                image = Image.open(image_path)
                image_encoded = encode_image(image)  # 图片编码
                message[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_encoded, "detail": detail}
                })
            else:
                print(f'question图片{image_path}未找到!')
                continue   
    else:
        pass
    
    return message

# Construct the prompts for tested models
def construct_test_messages_en(item, input_image_dir, detail='auto'):
    base_prompt = item["question_en"]
    if item["img"]:
        base_prompt += "\n <image>"
    if item["question_type"] == "Closed-ended":
        base_prompt += "\n Answer this question directly (if it's a single/multiple-choice question, only provide the corresponding letters of your answer options). Please do not provide any analysis process."
    else:
        base_prompt += "\n This is an open-ended question and answer session, which can provide the problem-solving process."

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]
    
    if item["img"]:
        """if there is question image"""
        for img_file in item.get("img", []):
            image_path = f"{input_image_dir}/{img_file}"
            if isinstance(image_path, str):
                image = Image.open(image_path)
                image_encoded = encode_image(image) 
                message[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_encoded, "detail": detail}
                })
            else:
                print(f'question image {image_path} not found!')
                continue   
    else:
        pass
    
    return message


# Construct the prompts for judging model
def construct_judge_messages_cn(item, input_image_dir, detail='auto'):
    base_prompt = f"""请根据以下信息评分：\n
    - 问题内容：{item['question']}\n
    - 正确答案：{item['final_answer']}\n
    - 正确解析：{item.get("solution", "")}\n
    - 考生回答：{item.get("result", "")}\n
    """

    if item["solution_img"]:
        base_prompt += "\n <image>"
    if item["question_type"] == "Closed-ended":
        base_prompt += "\n此为客观题，直接判断对与错，错则给0分，对则给10分。请直接给出分数数字，不要输出任何解释。"
    else:
        base_prompt += "\n此为开放式问答，你可以从0到10分中为该回答打分（整数分数）。请直接给出分数数字，不要输出任何解释。"

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]

    # add images
    if item["solution_img"]:
        for img_file in item.get("solution_img", []):
            image_path = f"{input_image_dir}/{img_file}"
            if isinstance(image_path, str):
                image = Image.open(image_path)
                image_encoded = encode_image(image)  # 图片编码
                message[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_encoded, "detail": detail}
                })
            else:
                print(f'solution图片{image_path}未找到!')
                continue   
    else:
        pass
    
    return message

# Construct the prompts for judging model
def construct_judge_messages_en(item, input_image_dir, detail='auto'):
    base_prompt = f"""Please rate according to the following information:\n
    - Question: {item['question_en']}\n
    - Reference Answer: {item['final_answer_en']}\n
    - Correct Analysis: {item.get("solution_en", "")}\n
    - Candidate's Answer: {item.get("result_en", "")}\n
    """

    if item["solution_img"]:
        base_prompt += "\n <image>"
    if item["question_type"] == "Closed-ended":
        base_prompt += "\n This is an objective question. Directly determine whether it is right or wrong. If it is wrong, 0 points will be given; if it is right, 10 points will be given. Please directly provide the score figures and do not output any explanations."
    else:
        base_prompt += "\n This is an open-ended question and answer. You can rate the answer on a scale of 0 to 10 (with an integer score). Please directly provide the score figures and do not output any explanations."

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]

    # add images
    if item["solution_img"]:
        for img_file in item.get("solution_img", []):
            image_path = f"{input_image_dir}/{img_file}"
            if isinstance(image_path, str):
                image = Image.open(image_path)
                image_encoded = encode_image(image)  
                message[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image_encoded, "detail": detail}
                })
            else:
                print(f'solution image {image_path} not found!')
                continue   
    else:
        pass
    
    return message


def process_single_item(item, client, client_judge, input_image_dir="", detail='auto'):
    """process a single data item: generate answer and score"""
    try:
        # construct the test messages
        if item.get("question_en"):
            logging.info(f"[question_en]: {item.get('question_en')[:30]}")
            messages = construct_test_messages_en(item, input_image_dir, detail)
        else:
            logging.info(f"[question]: {item.get('question')[:30]}")
            messages = construct_test_messages_cn(item, input_image_dir, detail)
        
        # call the model to generate answer
        result = try_call_3times(messages, client, model=LLM_CONFIG["model"])
        logging.info(f"[result]: {result[:30]}")
        
        # add the result to the item
        if item.get("question_en"):
            item['result_en'] = result
        else:
            item['result'] = result
        
        # construct the score messages
        if item.get("question_en"):
            judge_messages = construct_judge_messages_en(item, input_image_dir, detail)
        else:
            judge_messages = construct_judge_messages_cn(item, input_image_dir, detail)
        
        # call the model to score
        score = try_call_3times(judge_messages, client_judge, model=JUDGE_LLM_CONFIG["model"])
        score = extract_first_numeric_score(score)
        logging.info(f"[score]: {score}")
        # try to convert the score to a number
        try:
            if score <=10 and score >=0:
                score_value = score
            else:
                score_value = 0
            item['score'] = score_value
        except (ValueError, AttributeError):
            item['score'] = None
            logging.warning(f"Cannot parse the score: {score}")
        
        return item
        
    except Exception as e:
        logging.error(f"Error processing the item: {e}")
        item['score'] = 0.0
        return item

def analyze_results_by_discipline(data):
    """analyze the results by discipline"""
    discipline_stats = defaultdict(lambda: {'scores': [], 'count': 0})
    
    for item in data:
        discipline = item.get('discipline', 'Unknown discipline')
        score = item.get('score', 0.0)
        
        # handle the case where score is None
        if score is None:
            score = 0.0
        
        discipline_stats[discipline]['scores'].append(score)
        discipline_stats[discipline]['count'] += 1
    
    # calculate the average score of each discipline
    results = {}
    all_scores = []
    
    for discipline, stats in discipline_stats.items():
        avg_score = sum(stats['scores']) / (10*len(stats['scores'])) if stats['scores'] else 0.0
        results[discipline] = {
            'average_score': round(avg_score, 2),
            'count': stats['count'],
            'scores': stats['scores']
        }
        all_scores.extend(stats['scores'])
    
    # calculate the overall average score
    overall_avg = sum(all_scores) / (10*len(all_scores)) if all_scores else 0.0
    
    return results, round(overall_avg, 2)
