'''
This file defines additional member functions for the Class astparser, These
functions parse the Python assignment expressions.
'''

import ast

class assignments_mixin:

  def gen_ast_Assign_default(self, node):
    '''
    Generate speech for ast.Assign. Style '"default"

    Examples:
    1. e.g., a = b * c: a equals b multiply c
    2. e.g., a = b = b * c: a equals b equals b multiply c

    Note: "selected_style" is used for the right-hand expression (i.e., value)
    '''

    style_name = "default"

    # generate the speech for the targets
    target_speech = "" #node.targets[0].jvox_speech["default"] + " equals "
    for t in node.targets:
      target_speech += t.jvox_speech["default"] + " equals "

    # get the value speech
    value_speech = node.value.jvox_speech["selected_style"]

    # generate the final speech
    speech = target_speech + value_speech

    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = speech

    return speech

    return

  def gen_ast_Assign_indirect(self, node):
    '''
    Generate speech for ast.Assign. Style "default"

    Examples:
    1. e.g., a = b * c: a is assigned with value, b multiply c
    2. e.g., a = b = b * c: a and b are assigned with value, b multiply c

    Note: "selected_style" is used for the right-hand expression (i.e., value)
    '''

    style_name = "indirect"

    # figure whether to use "is" or "are"
    if len(node.targets) == 1:
      verb = " is "
    else:
      verb = " are "
    
    # generate the speech for the targets
    target_speech = "" 
    for t in node.targets:
      target_speech += t.jvox_speech["default"] + ", "
    target_speech += verb + "assigned with value, "

    # get the value speech
    value_speech = node.value.jvox_speech["selected_style"]

    # generate the final speech
    speech = target_speech + value_speech

    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = speech

    return speech

    return

  def gen_ast_Assign(self, node):
    '''
    Generate speech for ast.Assign.
    '''

    # style default
    self.gen_ast_Assign_default(node)

    # style indirect
    self.gen_ast_Assign_indirect(node)

    return

  def gen_ast_AugAssign_default(self, node):
    '''
    Generate speech for ast.AugAssign. Style "default"
    '''

    style_name = "default"

    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = "To be generated"

    return

  def gen_ast_AugAssign(self, node):
    '''
    Generate speech for ast.AugAssign.
    '''

    # style default
    self.gen_ast_AugAssign_default(node)

    return
