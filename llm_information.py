# -*- coding: utf-8 -*- 
# llm_information.py
# 获取llm的client

from openai import OpenAI
from config import JUDGE_LLM_CONFIG,LLM_CONFIG

client = OpenAI(
    base_url=LLM_CONFIG["base_url"],
    api_key=LLM_CONFIG["api_key"],
)

client_judge = OpenAI(
    base_url=JUDGE_LLM_CONFIG["base_url"],
    api_key=JUDGE_LLM_CONFIG["api_key"],
)

def get_llm_client(model_name,judge=False):
    if judge:
        return client_judge
    else:
        return client