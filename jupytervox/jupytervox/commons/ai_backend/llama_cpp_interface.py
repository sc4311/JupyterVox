#
# Interface for talking with llama.cpp server
#

import os

import requests

#from jvox_server_commons import jvox_logging
from ..logging import jvox_logging

llama_server_url = ""
temperature = 0

def get_server_url():
    global llama_server_url

    logger = jvox_logging("general", log_to_stderr=False)

    if llama_server_url is "":
        llama_server_url = os.environ.get("LLAMA_CPP_URL")

        if not llama_server_url:
            logger.debug("SERVER_URL environment variable not set")

            # use default URL for llama.cpp server
            llama_server_url = "http://localhost:4590" 
        
    logger.debug(f"Server URL is {llama_server_url}")

    return llama_server_url

def generate(prompt, api_key=None):
    '''
    For sending one prompt
    '''
    global temperature

    logger = jvox_logging("general", log_to_stderr=False)
    logger.debug(f"Sending prompt: {prompt}, with temperature {temperature}.")

    # use llama.cpp's OAI compatible interface
    url  = get_server_url() + "/v1/chat/completions"

    # send request
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [{"role": "user",
                      "content": prompt} ],
        "temperature": temperature,
    }
    
    response = requests.post(url, headers=headers, json=data)
    logger.debug(f"LLama full response:\n{response.json()}")

    choices = response.json().get("choices", [])
    response = choices[0]
    response_text = response["message"]["content"]
    logger.debug(f"LLama response text:\n{response_text}")

    response_reasoning = None
    if "reasoning_content" in response["message"]:
        response_reasoning = response["message"]["reasoning_content"]
        logger.debug(f"LLama response thinking output:\n{response_reasoning}")
    
    return response_text
