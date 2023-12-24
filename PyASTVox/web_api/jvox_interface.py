#!/usr/bin/python3

# interface for 

import ast
import argparse

# help import sibling directories
import sys
sys.path.append("../pyastvox")

# load the Vox parser
#from astparser import astparser
#from speech import Speech
import utils

from screenreader import pyastvox_speech_generator

class jvox_interface:
    vox_gen = None;

    # constructor    
    def __init__(self, style="alternatev2"):
        # create the parser
        self.vox_gen = pyastvox_speech_generator()
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

        return tree.jvox_speech
    
