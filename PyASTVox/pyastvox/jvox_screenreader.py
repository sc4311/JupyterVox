'''
Module jvox_screenreader: entry point class for JupyterVox screen reader
'''

# Python packages
import ast
import traceback

# for ASTVox_Anltr4
import sys
sys.path.append("../ASTVox_Antlr4/src/antlr2pyast/")

# Speech generation mixin classes, which have the actual implementation
# for gen_ast_XXX functions
import _binops
import _constants_ids
import _unaryops
import _lists_dicts
import _boolops_compares
import _unit_types
import _assignments
import _subscript
import _if_stmt
import _simple_stmt
import _functions
import _class
import _loops

# packages for AST-based speech generation
import utils
from pyastvox_speech_generator import pyastvox_speech_generator
from pyastvox_speech_styles import pyastvox_speech_styles

# package for JVox parser based on Antlr4
from converter import antlr2pyast


class jvox_screenreader():
  '''
  Entry point class for JupyterVox screen reader. This class also handles
  statement reading that don't involve parsing, including indent reading,
  comment reading, and non-parse-able/standalone (e.g., else/try) statement
  reading.

  When creating this class, you can use any 
  
  Call generate_speech with one of statement to generate the reading
  as a return value.
  '''
  # fields
  vox_gen = None  # the pyastvox_speech_generator instance
  use_antlr4: bool # whether to use ANTLR4 parser or not. If no,
                   # then use Python AST. Python AST should only be use for
                   # debugging, since it can't parse partial statements
  

  def __init__(self, use_antlr4 = True):
      self.vox_gen = pyastvox_speech_generator()
      self.use_antlr4 = use_antlr4
      
      return


  # generate speech for one "stmt". If "verbose" is true, then
  # print out the debugging information (e.g., AST tree)
  def generate_for_one(self, stmt, verbose=False):        
    # first, check if it is an empty line
    if stmt.lstrip() == "":
      return "empty line" # reading is "empty line"
        
    # generate reading for indention (leading white spaces).
    whitespace_speech = self.gen_leading_whitespace_speech(stmt)
    if whitespace_speech != "":
      whitespace_speech += ", "

    # remove leading white spaces. Otherwise, parsing will fail, since
    # indents have meanings semantically.
    stmt = stmt.lstrip()

    # second, check if it is comment
    if stmt[0] == '#':
      speech = self.gen_comment_speech(stmt)
      return whitespace_speech + speech
        
    # third, check if it is a standalone non-parse-able statement,
    # e.g., "try", "else", "except". They will be read without
    # parsing.
    standalone_speech = self.gen_standalone_statemetns(stmt)
    if standalone_speech != "":
      return whitespace_speech + standalone_speech
        
    # This is a normal statement, parse the statement to generate the
    # AST tree first
    # generate and convert tree
    try:
      if self.use_antlr4:
        # parse with antlr4 and converter
        antlr4_tree = antlr2pyast.generate_ast_tree(stmt)
        tree, converter = antlr2pyast.convert_tree(antlr4_tree)
      else: 
        # parse with Python AST
        tree = ast.parse(stmt)
    except Exception as e:
      # parsing error, this could be due to a completely unparse-able
      # partial statement, e.g., "else:\n"
      print("Statement parsing error")
      antlr4_parse_error = True
      if verbose:
        traceback.print_exc()
        
      # error parsing, just return the statement itself
      return whitespace_speech + stmt 
    
    # print the tree
    if verbose:
      ast_tree_str = []
      utils.ast_visit_non_print(tree, ast_tree_str)
      for tree_line in ast_tree_str:
        print(tree_line)

    # generate speech
    self.vox_gen.generate(tree)

    # final speech including both indent reading and statement reading
    speech = whitespace_speech + tree.jvox_speech["selected_style"]

    return speech
  
  def gen_standalone_statemetns(self, text):
    '''
    Function to handle statements "else:", "try:", "except:"
    Simply read the text as it is
    '''

    # remove leading and ending white spaces and newline
    t = text.strip().rstrip('\n')
    
    if t == "else:":
      return "else"
    elif t == "try:":
      return "try"
    elif t == "except:":
      return "except"
    else:
      return ""

  def gen_leading_whitespace_speech(self, text):
    '''
    Function to read the leading white spaces. 
    '''

    # count white spaces
    whitespaces = []
    i = 0
    while (i < len(text)):
      # count continuous spaces
      count = 0
      while(text[i] == ' '):
        i += 1
        count += 1
      if count>0:
        whitespaces.append(f"{count} white spaces")

      # count continuous tab
      count = 0
      while(text[i] == '\t'):
        i += 1
        count += 1
      if count>0:
        whitespaces.append(f"{count} tabs")

      # break if not whitespace
      if (text[i] != ' ') and (text[i] != '\t'):
        break

    # generate the speech
    speech = ", ".join(whitespaces)

    return speech

  def gen_comment_speech(self, text):
    '''
    Function to read a comment line.
    Simply just read the line.
    '''

    text = text.lstrip()

    speech = ""
    
    if text[0] == "#":
      speech = "comment: " + text

    return speech

