# -*- coding: utf-8 -*-
# config.py
# 配置文件

# 测试LLM配置
'''
LLM_CONFIG = {
    "base_url": "https://api.openai.com/v1",  # 请根据实际情况修改
    "api_key": "your-api-key-here",  # 请填入你的API密钥
    "model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3
}'''
LLM_CONFIG = {
    "base_url": "http://35.220.164.252:3888/v1/",  # 请根据实际情况修改
    "api_key": "sk-QYdqbcXa0kNOQLNxWGmXobROc2S7OnAcadm37Q17XMD9cvY2",  # 请填入你的API密钥
    "model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3
}
# 打分LLM配置
JUDGE_LLM_CONFIG = {
    "base_url": "http://35.220.164.252:3888/v1/",  # 请根据实际情况修改
    "api_key": "sk-QYdqbcXa0kNOQLNxWGmXobROc2S7OnAcadm37Q17XMD9cvY2",  # 请填入你的API密钥
    "model": "gpt-4o",
    "temperature": 0.0,
    "max_retries": 3
}

# 数据处理配置
DATA_CONFIG = {
    "input_file": "esee.jsonl",
    "input_image_dir": "",  # 图片目录路径，如果有的话
    "detail": "auto"
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "log/evaluation.log"
}

# 输出配置
OUTPUT_CONFIG = {
    "detailed_results": "results/detailed_results.json",
    "summary_results": "results/summary_results.json"
} 