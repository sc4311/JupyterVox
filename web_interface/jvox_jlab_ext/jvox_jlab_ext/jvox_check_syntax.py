#
# Class for single-line syntax checking support
#

import json
import base64

import tornado
from jupyter_server.base.handlers import APIHandler

from jupytervox.interface import jvox_interface

class JVoxCheckLineSyntaxRouteHandler(APIHandler):
    '''
    JVox endpoint for checking the syntax of a single line of code.
    Calls single_line_parsing_check and returns the result with audio.
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface("default")

        # extract input information
        input_data = self.get_json_body()
        stmt = input_data["stmt"]

        # perform syntax check
        result = jvox.single_line_parsing_check(stmt, True)
        print("Syntax check result:", result.msg, "offset:", result.offset)

        # generate audio bytes from the message
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(result.msg)

        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON response
        reply = {
            "msg": result.msg,
            "offset": result.offset,
            "audio": encoded_audio
        }

        self.finish(json.dumps(reply))
