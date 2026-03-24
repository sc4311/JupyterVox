import json
import base64

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

from gtts import gTTS

""" # import JVox packages
import sys
from pathlib import Path
# get the path to the interface package
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(f"{BASE_DIR}/../../../web_api/")
# sys.path.append(BASE_DIR)

import jvox_interface
 """

# from jupytervox.interface import jvox_interface 

# this should be put into a common configuration file
EXTENSION_URL = "jvox-lab-ext"

# import endpoint files
from . import jvox_read_chunk
from . import jvox_audio_support
from . import jvox_read_line
from . import jvox_ai_explanation
from . import jvox_check_syntax
from . import jvox_check_cell_syntax

class HelloRouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({
            "data": (
                "Hello1, world!"
                f"'/{EXTENSION_URL}/hello' endpoint started correctly. "
            ),
        }))

def setup_route_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # register the hello testing interface
    hello_route_pattern = url_path_join(base_url, EXTENSION_URL, "hello")
    handlers = [(hello_route_pattern, HelloRouteHandler)]

    web_app.add_handlers(host_pattern, handlers)

    # add JVox screen reader endpoint
    jvox_screenreader_route_pattern = url_path_join(base_url, EXTENSION_URL, "readline")
    handlers = [(jvox_screenreader_route_pattern, jvox_read_line.JVoxScreenReaderRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # add JVox audio endpoint
    jvox_audio_route_pattern = url_path_join(base_url, EXTENSION_URL, "audio")
    handlers = [(jvox_audio_route_pattern, jvox_audio_support.JVoxAudioRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Add JVox chunked reading endpoint
    jvox_chunked_route_pattern = url_path_join(base_url, EXTENSION_URL, "readChunk")
    handlers = [(jvox_chunked_route_pattern, jvox_read_chunk.JVoxChunkedReadingRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Add JVox AI explanation endpoint
    jvox_ai_explanation_route_pattern = url_path_join(base_url, EXTENSION_URL, "AIExplain")
    handlers = [(jvox_ai_explanation_route_pattern, jvox_ai_explanation.JVoxAIExplanationRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Add JVox single-line syntax check endpoint
    jvox_check_syntax_route_pattern = url_path_join(base_url, EXTENSION_URL, "checkLineSyntax")
    handlers = [(jvox_check_syntax_route_pattern, jvox_check_syntax.JVoxCheckLineSyntaxRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    # Add JVox cell-level syntax check endpoint
    jvox_check_cell_syntax_route_pattern = url_path_join(base_url, EXTENSION_URL, "checkCellSyntax")
    handlers = [(jvox_check_cell_syntax_route_pattern, jvox_check_cell_syntax.JVoxCheckCellSyntaxRouteHandler)]
    web_app.add_handlers(host_pattern, handlers)

    
