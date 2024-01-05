#!/usr/bin/python3

# interface between PyASTVox and the web service

# packages for AST parsing
import ast
# packages for Text2Speech and audio manipulation
from gtts import gTTS

# help import sibling directories
import sys
sys.path.append("../../pyastvox")
sys.path.append("../../../ASTVox_Antlr4/src/antlr2pyast/")

# other system packages
import traceback

# load the Vox parser utilities
import utils

# import JVox speech generator
from jvox_screenreader import jvox_screenreader


class jvox_interface:
    vox_gen = None;
    jvox = None;
    style = "default";

    # constructor    
    def __init__(self, style="default"):
        self.jvox =  jvox_screenreader()

    # generate the speech for one statement
    def gen_speech_for_one(self, stmt, verbose):
        speech = self.jvox.generate_for_one(stmt, verbose)

        return speech

    # generate the mp3 file
    def gen_mp3_from_speech(self, speech, file_name):
        tts = gTTS(speech, slow=False)
        tts.save(file_name)
        print("jvox created mp3 file at", file_name)

        return
    
