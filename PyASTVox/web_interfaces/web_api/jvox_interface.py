#!/usr/bin/python3

# interface between PyASTVox and the web service

# packages for AST parsing
import ast
# packages for Text2Speech and audio manipulation
from gtts import gTTS

# help import sibling directories
import sys
sys.path.append("../../pyastvox")
# import ASTVox_Anltr4
sys.path.append("../../../ASTVox_Antlr4/src/antlr2pyast/")

# other system packages
import traceback

# load the Vox parser
#from astparser import astparser
#from speech import Speech
import utils

# import JVox speech generator
from screenreader import pyastvox_speech_generator

# import JVox parser based on Antlr4
from converter import antlr2pyast


####### functions to print an AST tree
def str_node(node):
    #if isinstance(node, ast.Module):
    # for module, just print its class name and type_ignores
    # otherwise, the pointer addresses will never match between trees
    # s = "Module(type_ignores=" + repr(node.type_ignores) + ")"
    # return s   
    #elif isinstance(node, ast.AST):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)

# output node to out_str,and visit its children
def ast_visit(node, out_str, level=0):
    #print('  ' * level + str_node(node))
    out_str.append('  ' * level + str_node(node))
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    ast_visit(item, out_str, level=level+1)
        elif isinstance(value, ast.AST):
            ast_visit(value, out_str, level=level+1)

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
        # first, check if it is an empty line
        if stmt.lstrip() == "":
            return "empty line"
        
        # generate reading for indention (leading white spaces).
        whitespace_speech = self.vox_gen.gen_leading_whitespace_speech(stmt)

        # remove leading white spaces. Otherwise, parsing will fail, since
        # indents have meanings semantically.
        stmt = stmt.lstrip()

        # second, check if it is comment
        if stmt[0] == '#':
            speech = self.vox_gen.gen_comment_speech(stmt)
            return whitespace_speech + ", " + speech
        
        # third, check if it is a standalone non-parse-able statement,
        # e.g., "try", "else", "except". They will be read without
        # parsing.
        standalone_speech = self.vox_gen.gen_standalone_statemetns(stmt)
        if standalone_speech != "":
            return whitespace_speech + ", " + standalone_speech
        
        
        # generate AST tree
        #tree = ast.parse(stmt)

        # print the tree if verbose
        # if verbose:
        #     utils.ast_visit(tree)

        # generate AST tree
        # tree = ast.parse(stmt)
        # generate and convert tree
        try:
            tree = antlr2pyast.generate_ast_tree(stmt)
            converted_tree, converter = antlr2pyast.convert_tree(tree)
        except Exception as e:
            # parsing error, this could be due to a completely unparse-able
            # partial statement, e.g., "else:\n"
            antlr4_parse_error = True
            if verbose:
                traceback.print_exc()
            return "Antlr4 Converter error for code"
    
        # print the tree
        if verbose:
            converted_tree_str = []
            ast_visit(converted_tree, converted_tree_str)
            for tree_line in converted_tree_str:
                print(tree_line)

        # generate speech
        self.vox_gen.generate(converted_tree)

        # final speech including both indent reading and statement reading
        speech = (whitespace_speech + ", " +
                  converted_tree.jvox_speech["selected_style"]) 

        return speech

    # generate the mp3 file
    def gen_mp3_from_speech(self, speech, file_name):
        tts = gTTS(speech, slow=False)
        tts.save(file_name)
        print("jvox created mp3 file at", file_name)

        return
    
