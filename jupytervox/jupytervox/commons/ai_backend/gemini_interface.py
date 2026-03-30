#
# Interface for talking with Gemini
#

import os

from google import genai

from ..logging import jvox_logging

gemini_model_name = "gemini-2.5-flash-lite"

def get_api_key():
    logger = jvox_logging("general", log_to_stderr=False)
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    logger.debug(f"API Key is {API_KEY}")

    return API_KEY

def generate(prompt, api_key=None):
    '''
    For sending one prompt
    '''
    logger = jvox_logging("general", log_to_stderr=False)

    if not api_key:
        api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=gemini_model_name, contents=prompt
    )

    return response.text

def converse(prompts, api_key=None):
    """
    For sending a sequence of converstaion
    """
    logger = jvox_logging("general", log_to_stderr=False)
    #logger.debug(f"Prompts to send: {prompts}")

    # Setup
    if not api_key:
        api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    chat = client.chats.create(model=gemini_model_name)

    responses = []
    for prompt in prompts:
        logger.debug(f"Sending prompt: {prompt}")
        response = chat.send_message(prompt)
        logger.debug(f"Got response: {response.text}")

        responses.append(response.text)

    #logger.debug(f"Responses received: {responses}")

    return responses