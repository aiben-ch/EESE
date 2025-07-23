import logging
import json
import os
from inference import process_single_item, analyze_results_by_discipline
from llm_information import get_llm_client
from utils import load_jsonl_data, save_results
from config import DATA_CONFIG, LOG_CONFIG, LLM_CONFIG, JUDGE_LLM_CONFIG

def setup_logging():
    """initialize the logger"""
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG["level"]),
        format=LOG_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOG_CONFIG["file"], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)




def print_results(results, overall_avg):
    """print the results"""
    print("\n" + "="*60)
    print("Summary of evaluation results")
    print("="*60)
    
    print(f"\nPerformance of each discipline:")
    print("-" * 40)
    
    for discipline, stats in results.items():
        print(f"{discipline}:")
        print(f"  Average score: {stats['average_score']}")
        print(f"  Number of questions: {stats['count']}")
        print(f"  Score distribution: {stats['scores'][:5]}{'...' if len(stats['scores']) > 5 else ''}")
        print()
    
    print("-" * 40)
    print(f"Overall average score: {overall_avg}")
    print(f"Total number of questions: {sum(stats['count'] for stats in results.values())}")
    print("="*60)

def main():
    """main function"""
    # 1. initialize the logger
    logger = setup_logging()
    logger.info("Start evaluating the model")
    
    # 2. load the data
    jsonl_file = DATA_CONFIG["input_file"]
    if not os.path.exists(jsonl_file):
        logger.error(f"File {jsonl_file} does not exist")
        return
    
    logger.info(f"Loading data file: {jsonl_file}")
    data = load_jsonl_data(jsonl_file)
    logger.info(f"Successfully loaded {len(data)} data")
    
    # 3. initialize the LLM clients
    logger.info("Initializing LLM clients")
    client = get_llm_client(LLM_CONFIG["model"],judge=False)
    client_judge = get_llm_client(JUDGE_LLM_CONFIG["model"],judge=True)
    
    # 4. process each line of data
    logger.info("Processing data...")
    processed_data = []
    
    for i, item in enumerate(data):
        logger.info(f"Processing {i+1}/{len(data)} data")
        processed_item = process_single_item(
            item, 
            client, 
            client_judge,
            DATA_CONFIG["input_image_dir"], 
            DATA_CONFIG["detail"]
        )
        processed_data.append(processed_item)
        
        # print the progress every 10 data
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i+1}/{len(data)} data")
    
    # 5. analyze the results by discipline
    logger.info("Analyzing results...")
    results, overall_avg = analyze_results_by_discipline(processed_data)
    
    # 6. save the results
    logger.info("Saving results...")
    save_results(processed_data, results, overall_avg)
    
    # 7. print the results
    print_results(results, overall_avg)
    
    logger.info("Evaluation completed")

if __name__ == "__main__":
    main()

