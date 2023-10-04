'''
This file defines additional member functions for the Class astparser, These
functions parse the Python unit types.
'''

import ast

class unit_types_mixin:

  def string_constant_process(self, value:str):
    '''
    process string to handle certain punctuation marks and special
    characters
    '''
    # For explicitly reading punctuation marks.
    s = value.replace(',', " comma ")
    s = s.replace('!', " exclamation mark ")

    return s
  
  def gen_ast_Constant(self, node):
    '''
    Generate speech for ast.Constant.
    For int, Just use the string, i.e., str(), of the constant as the speech
    For string, process it to handle certain punctuation marks and special
    characters, then add "string" before the actual string
    '''

    if isinstance(node.value, str):
      # process string to handle certain punctuation marks and special
      # characters
      s = self.string_constant_process(node.value)
      node.jvox_speech = {"default": f"string {s}"}
    else:
      node.jvox_speech = {"default": str(node.value)}

    return
