#
# Class for JVox AI explanation
#

import json
import base64

import tornado
from jupyter_server.base.handlers import APIHandler

# import sys
# from pathlib import Path
# # get the path to the interface package
# BASE_DIR = Path(__file__).resolve().parent
# web_api_path = f"{BASE_DIR}/../../../web_api/"
# if web_api_path not in sys.path:
#    sys.path.append(web_api_path)

from jupytervox.interface import jvox_interface  

class JVoxAIExplanationRouteHandler(APIHandler):
    '''
    JVox AI explanation endpoint for explaining code
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface("default")
        print("hello jvox:", jvox)
        
        # retrieve statement and command
        input_data = self.get_json_body()
        stmt = input_data["statement"]
        command = input_data["command"]
        ai_client = input_data.get("ai_client")    # "ollama" or "gemini"
        api_key = input_data.get("api_key", "")     # Gemini API key (may be empty)
        print("JVox AI explanation web api got statement", stmt)
        print("JVox AI explanation web api got command", command)
        print("JVox AI explanation web api got ai_client", ai_client)

        ai_response = ""
        if command == "codeExplain":
            ai_response = jvox.ai_explain_code(stmt, ai_client=ai_client, api_key=api_key) 
        elif command == "nestedCodeExplain":
            ai_response = jvox.ai_explain_nested_code(stmt, ai_client=ai_client, api_key=api_key)

        # generate audio bytes
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(ai_response)

        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON
        result = {
                "speech": ai_response,
                "audio": encoded_audio
            }

        # send the JSON
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(result))


