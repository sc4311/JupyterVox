#!/usr/bin/python3

# interface between PyASTVox and the web service

# packages for AST parsing
import ast
# packages for Text2Speech and audio manipulation
from gtts import gTTS

# help import sibling directories
import sys
sys.path.append("../../pyastvox")

# load the Vox parser
#from astparser import astparser
#from speech import Speech
import utils

from screenreader import pyastvox_speech_generator

class jvox_interface:
    vox_gen = None;
    style = "default"

    # constructor    
    def __init__(self, style="default"):
        # create the parser
        self.vox_gen = pyastvox_speech_generator()
        self.style = style
        self.vox_gen.set_speech_style(ast.BinOp, style)
        print("jvox interface created with style", style)

    # generate the speech for one statement
    def gen_speech_for_one(self, stmt, verbose):
        # generate AST tree
        tree = ast.parse(stmt)

        # print the tree if verbose
        if verbose:
            utils.ast_visit(tree)

        # generate speech
        self.vox_gen.generate(tree)

        return tree.jvox_speech[self.style]

    # generate the mp3 file
    def gen_mp3_from_speech(self, speech, file_name):
        tts = gTTS(speech, slow=False)
        tts.save(file_name)
        print("jvox created mp3 file at", file_name)

        return
    
