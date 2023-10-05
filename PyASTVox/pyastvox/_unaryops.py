'''
This file defines additional member functions for the class
pyastvox_screen_reader, These functions parse the Python unary operations.
'''

import ast

class unaryops_mixin:
  def gen_ast_USub(self, node):
    '''
    Styles:
    1. default: "negative"
    '''
    node.jvox_speech = {"default":"negative"}

    return

  def gen_ast_UAdd(self, node):
    '''
    Styles:
    1. default: "positive"
    2. succinct: ""
    '''
    node.jvox_speech = {"default":"positive", "succinct":""}

    return

  def gen_ast_Not(self, node):
    '''
    Styles:
    1. default: "Not"
    2. indirect: "the negation of"
    '''
    node.jvox_speech = {"default":"Not", "indirect": "the negation of"}

    return

  def gen_ast_Invert(self, node):
    '''
    Styles:
    1. default: "invert"
    2. indirect: "the inversion of"
    '''
    node.jvox_speech = {"default":"invert", "indirect": "the inversion of"}

    return

  def gen_ast_UnaryOp_default(self, node):
    '''
    Generate speech for ast.UnaryOp
    E.g.,
    1. -3.14: negative 3.14
    2. +3.14: positive 3.14
    3. not a: not a
    4. ^ a: invert a
    '''

    style_name = "default"

    # generate speech for operator and operand
    op_speech = node.op.jvox_speech["default"]
    operand_speech = node.operand.jvox_speech["default"]

    # generate the speech
    speech = op_speech + " " + operand_speech

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_UnaryOp_indirect(self, node):
    '''
    Generate speech for ast.UnaryOp
    E.g.,

    '''

    style_name = "indirect"

    # generate speech for operator and operand
    if "indirect" in node.op.jvox_speech:
      op_speech = node.op.jvox_speech["indirect"]
    else:
      op_speech = node.op.jvox_speech["default"]
      
    operand_speech = node.operand.jvox_speech["default"]

    # generate the speech
    speech = op_speech + " " + operand_speech

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech
    

  def gen_ast_UnaryOp(self, node):
    '''
    Generate speech for ast.UnaryOp
    '''

    # default style
    self.gen_ast_UnaryOp_default(node)
    # indirect style
    self.gen_ast_UnaryOp_indirect(node)

    return
