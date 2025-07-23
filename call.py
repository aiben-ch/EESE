import time

def call_llm(message, client, model_name="gpt-4o"):
    try:
        response = client.chat.completions.create(
            model= model_name,
            messages=message,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error during answering: {e}")
        return None


def try_call_3times(
    messages, 
    client, 
    model: str = "gpt-4o",
    max_retries: int = 3,
):
    attempts = 0
    answer = None
    while attempts < max_retries:
        try:  
            answer = call_llm(messages, client, model)
            break
            
        except Exception as e:
            attempts += 1
            time.sleep(1)

    if not answer:
        answer = 'no response'
    #time.sleep(0.5)

    return answer
