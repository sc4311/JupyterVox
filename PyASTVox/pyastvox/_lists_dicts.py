'''
This file defines additional member functions for the class
pyastvox_screen_reader, These functions parse lists and dictionaries.
'''

import ast

#from speech import Speech

class lists_dicts_mixin:

  def gen_ast_List_default(self, node):
    '''
    Generate speech for ast.List
    E.g.,
    1. [1, 2, a]: a list with items of 1, 2, a
    '''

    style_name = "default"

    if len(node.elts) == 0:
      # handle the empty string case first
      speech = "an empty string"
    else:
      # has more than one items
      speech = f"a list with {len(node.elts)} items of "
      # get the speech of each item
      speech += node.elts[0].jvox_speech["default"]
      for i in range(1, len(node.elts)-1):
        speech += ", " + node.elts[i].jvox_speech["default"]

        # process the last item, if there are more than one item
      if len(node.elts) > 1:
        speech += ", and " + node.elts[-1].jvox_speech["default"]

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

    if len(node.keys) == 0:
      # empty dictionary
      speech = "an empty dictionary"
    else:
      speech = f"a dictionary with {len(node.keys)} items of, "
      # get the speech of each item
      key_speech = node.keys[0].jvox_speech["default"]
      val_speech = node.values[0].jvox_speech["default"]
      speech += f"item {1} has key of {key_speech}, and value of {val_speech}"
      for i in range(1, len(node.keys)-1):
        key_speech = node.keys[i].jvox_speech["default"]
        val_speech = node.values[i].jvox_speech["default"]
        speech += (f", item {i+1} has key of {key_speech}, and value of "
                   f"{val_speech}")

      # process the last item, if there are more than one item
      if len(node.keys) > 1:
        key_speech = node.keys[-1].jvox_speech["default"]
        val_speech = node.values[-1].jvox_speech["default"]
        speech += (f", and item {len(node.keys)} has key of {key_speech}, and"
                   f"value of {val_speech}")

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

  #   
  def gen_ast_Tuple_default(self, node):
    '''
    Generate speech for ast.Tuple
    E.g.,
    1. [1, 2, a]: a list with items of 1, 2, a
    '''

    style_name = "default"

    if len(node.elts) == 0:
      # handle the empty string case first
      speech = "an empty string"
    else:
      # has more than one items
      speech = f"a tuple with {len(node.elts)} items of "
      # get the speech of each item
      speech += node.elts[0].jvox_speech["default"]
      for i in range(1, len(node.elts)-1):
        speech += ", " + node.elts[i].jvox_speech["default"]

        # process the last item, if there are more than one item
      if len(node.elts) > 1:
        speech += ", and " + node.elts[-1].jvox_speech["default"]

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  #  
  def gen_ast_Tuple(self, node):
    '''
    Generate the speech for ast.Tuple
    '''
    # default style
    self.gen_ast_Tuple_default(node)

#   
  def gen_ast_Set_default(self, node):
    '''
    Generate speech for ast.Set
    E.g.,
    1. [1, 2, a]: a list with items of 1, 2, a
    '''

    style_name = "default"

    if len(node.elts) == 0:
      # handle the empty string case first
      speech = "an empty string"
    else:
      # has more than one items
      speech = f"a set with {len(node.elts)} items of "
      # get the speech of each item
      speech += node.elts[0].jvox_speech["default"]
      for i in range(1, len(node.elts)-1):
        speech += ", " + node.elts[i].jvox_speech["default"]

        # process the last item, if there are more than one item
      if len(node.elts) > 1:
        speech += ", and " + node.elts[-1].jvox_speech["default"]

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  #  
  def gen_ast_Set(self, node):
    '''
    Generate the speech for ast.Set
    '''
    # default style
    self.gen_ast_Set_default(node)

