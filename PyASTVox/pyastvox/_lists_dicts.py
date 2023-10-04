'''
This file defines additional member functions for the class
pyastvox_screen_reader, These functions parse lists and dictionaries.
'''

import ast

from speech import Speech

class lists_dicts_mixin:

  def gen_ast_List_default(self, node):
    '''
    Generate speech for ast.List
    E.g.,
    1. [1, 2, a]: a list with items of 1, 2, a
    '''

    style_name = "default"

    # get the speech of each item
    items = []
    for e in node.elts:
      s = e.jvox_speech["default"]
      items.append(s)

    # generate the speech
    speech = "a list with items of " + ", ".join(items)    

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  #  
  def gen_ast_List(self, node):
    '''
    Generate the speech for ast.List
    '''
    # default style
    self.gen_ast_List_default(node)


  def gen_ast_Dict_default(self, node):
    '''Generate speech for ast.Dict
    
    Example, 1. e.g., {"key1":1, "key2":3}: a dictionary with items of, item 1
    has key of a string of key1 and value of 1, and item 2 has key of a string
    of key2 and value 3

    '''

    style_name = "default"

    # get the speech of each item
    items = []
    for i in range(len(node.keys)):
      key_speech = node.keys[i].jvox_speech["default"]
      val_speech = node.values[i].jvox_speech["default"]
      s = f"item {i+1} has key of {key_speech} and value of {val_speech}"
      
      items.append(s)

    # generate the speech
    speech = "a dictionary with items of, " + ", ".join(items)    

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech
  
  #
  def gen_ast_Dict(self, node):
    '''
    Generate the speech for ast.List
    '''
    # default style
    self.gen_ast_Dict_default(node)
