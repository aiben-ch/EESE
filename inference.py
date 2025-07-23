from call import try_call_3times
from utils import extract_first_numeric_score
from config import LLM_CONFIG, JUDGE_LLM_CONFIG
from collections import defaultdict
import logging


# Construct the prompts for tested models
def construct_test_messages(item, input_image_dir, detail='auto'):
    base_prompt = item["question"]
    if item["question_type"] == "Closed-ended":
        base_prompt += "\n Answer this question directly (if it's a single/multiple-choice question, only provide the corresponding letters of your answer options). Please do not provide any analysis process."
    else:
        base_prompt += "\n This is an open-ended question and answer session, which can provide the problem-solving process."

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]
    return message


# Construct the prompts for judging model
def construct_judge_messages_en(item, input_image_dir, detail='auto'):
    base_prompt = f"""Please rate according to the following information:\n
    - Question: {item['question']}\n
    - Reference Answer: {item['final_answer']}\n
    - Correct Analysis: {item.get("solution", "")}\n
    - Candidate's Answer: {item.get("result", "")}\n
    """

    if item["question_type"] == "Closed-ended":
        base_prompt += "\n This is an objective question. Directly determine whether it is right or wrong. If it is wrong, 0 points will be given; if it is right, 10 points will be given. Please directly provide the score figures and do not output any explanations."
    else:
        base_prompt += "\n This is an open-ended question and answer. You can rate the answer on a scale of 0 to 10 (with an integer score). Please directly provide the score figures and do not output any explanations."

    message = [{
        "role": "user",
        "content": [{"type": "text", "text": base_prompt}]
    }]
    
    return message


def process_single_item(item, client, client_judge, input_image_dir="", detail='auto'):
    """process a single data item: generate answer and score"""
    try:
        
        logging.info(f"[question]: {item.get('question')[:30]}")
        messages = construct_test_messages(item, input_image_dir, detail)
        
        # call the model to generate answer
        result = try_call_3times(messages, client, model=LLM_CONFIG["model"])
        logging.info(f"[result]: {result[:30]}")
        
        # add the result to the item
        item['result'] = result
        
        # construct the score messages
        judge_messages = construct_judge_messages_en(item, input_image_dir, detail)

        
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
