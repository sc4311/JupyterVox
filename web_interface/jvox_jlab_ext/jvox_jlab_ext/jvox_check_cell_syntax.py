#
# Class for cell-level (code snippet) syntax checking support
#

import json
import base64

import tornado
from jupyter_server.base.handlers import APIHandler

from jupytervox.interface import jvox_interface

class JVoxCheckCellSyntaxRouteHandler(APIHandler):
    '''
    JVox endpoint for checking the syntax of a code snippet (full cell).
    Calls code_snippet_parsing_check and returns the result with audio.
    '''
    @tornado.web.authenticated
    def post(self):
        jvox = jvox_interface("default")

        # extract input information
        input_data = self.get_json_body()
        stmts = input_data["stmts"]

        # perform syntax check
        result = jvox.code_snippet_parsing_check(stmts, True)
        print("Cell syntax check result:", result.msg,
              "line_no:", result.line_no, "offset:", result.offset,
              "error_no:", result.error_no)

        # generate audio bytes from the message
        mp3_bytes = jvox.gen_mp3_bytes_from_speech_gtts(result.msg)

        # Encode bytes to Base64 string so that we can send bytes in JSON
        encoded_audio = base64.b64encode(mp3_bytes).decode('ascii')

        # Prepare and send the JSON response
        reply = {
            "msg": result.msg,
            "line_no": result.line_no,
            "offset": result.offset,
            "error_no": result.error_no,
            "audio": encoded_audio
        }

        self.finish(json.dumps(reply))
