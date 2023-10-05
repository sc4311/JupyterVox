'''
This file defines additional member functions for the class
pyastvox_screen_reader, These functions parse boolean operations and
comparisons.
'''

import ast

class boolops_compares_mixin:
  def gen_ast_And(self, node):
    '''
    Styles:
    1. default: "and"
    2. indirect: "the logical and of"
    '''
    node.jvox_speech = {"default":"and", "indirect":"the logical and of"}

    return

  def gen_ast_Or(self, node):
    '''
    Styles:
    1. default: "or"
    2. indirect: "the logical or of"
    '''
    node.jvox_speech = {"default":"or", "indirect":"the logical or of"}

    return

  def gen_ast_Eq(self, node):
    '''
    Styles:
    1. default: "is equal to"
    '''
    node.jvox_speech = {"default":"is equal to"}

    return

  def gen_ast_NotEq(self, node):
    '''
    Styles:
    1. default: "is not equal to"
    '''
    node.jvox_speech = {"default":"is not equal to"}

    return

  def gen_ast_Lt(self, node):
    '''
    Styles:
    1. default: "is less than"
    '''
    node.jvox_speech = {"default":"is less than"}

    return

  def gen_ast_LtE(self, node):
    '''
    Styles:
    1. default: "is less than or equal to"
    '''
    node.jvox_speech = {"default":"is less than or equal to"}

    return

  def gen_ast_Gt(self, node):
    '''
    Styles:
    1. default: "is greater than"
    '''
    node.jvox_speech = {"default":"is greater than"}

    return

  def gen_ast_GtE(self, node):
    '''
    Styles:
    1. default: "is greater than or equal to"
    '''
    node.jvox_speech = {"default":"is greater than or equal to"}

    return

  def gen_ast_Is(self, node):
    '''
    Styles:
    1. default: "is the same as"
    '''
    node.jvox_speech = {"default":"is the same as"}

    return

  def gen_ast_IsNot(self, node):
    '''
    Styles:
    1. default: "is not the same as"
    '''
    node.jvox_speech = {"default":"is not the same as"}

    return

  def gen_ast_In(self, node):
    '''
    Styles:
    1. default: "is in"
    '''
    node.jvox_speech = {"default":"is in"}

    return

  def gen_ast_NotIn(self, node):
    '''
    Styles:
    1. default: "is not in"
    '''
    node.jvox_speech = {"default":"is not in"}

    return

  def gen_ast_BoolOp_default(self, node):
    '''
    Generate speech for ast.BoolOp, style "default"

    Examples:
    1. e.g., a or b or c: a or b, then or c
    2. e.g., a or b and c: a or b and c
    3. e.g., a and b or c, a and b, then or c
    '''

    style_name = "default"

    # first, check if the first value is unit type
    first_val_is_unit_type = (isinstance(node.values[0], ast.Constant) or
                         isinstance(node.values[0], ast.Name))

    # use ", then" if the first value is not a unit type
    use_then = not first_val_is_unit_type
    if use_then:
      connect_string = ", then "
    else:
      connect_string = " "

    # generate the string
    speech = node.values[0].jvox_speech["default"] + connect_string
    for i in range(1, len(node.values)-1):
      speech += (node.op.jvox_speech["default"] + " " +
                 node.values[i].jvox_speech["default"] +
                 ", then ")
    speech += (node.op.jvox_speech["default"] + " " + 
               node.values[-1].jvox_speech["default"])
    
    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_BoolOp_indirect(self, node):
    '''
    Generate speech for ast.BoolOp, style "indirect"

    Examples:

    '''

    style_name = "indirect"

    # generate the string
    speech = node.op.jvox_speech["indirect"] + " "
    speech += node.values[0].jvox_speech["default"]
    for i in range(1, len(node.values)-1):
      # if "indirect" in v.jvox_speech:
      #   s = v.jvox_speech["indirect"]
      # else:
      s = node.values[i].jvox_speech["default"]  
      speech += ", " + s
      
    speech += ", and " + node.values[-1].jvox_speech["default"]
    
    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_BoolOp_alternate_v2(self, node):
    '''Speech generation for ast.BinOp, style "alternate".

    Use direct/default for unit-typed right operand, use indirect for
    non-unit-typed right operand
    
    Examples,

    '''

    style_name = "alternatev2"

    # first, check if the first value is unit type
    first_val_is_unit_type = (isinstance(node.values[0], ast.Constant) or
                              isinstance(node.values[0], ast.Name))

    # use ", then" if the first value is not a unit type
    use_then = not first_val_is_unit_type
    if use_then:
      connect_string = ", then "
    else:
      connect_string = " "

    # get the speech for the first operand
    if style_name in node.values[0].jvox_speech:
      speech = node.values[0].jvox_speech[style_name]
    else:
      speech = node.values[0].jvox_speech["default"]

    # Generate the speech for the rest of the operands. Use indirect style if
    # the operand is not unit type, otherwise, use the default style.
    for i in range(1, len(node.values)):
      # add the operate speech
      speech += connect_string + node.op.jvox_speech["default"] + " "
      connect_string = ", then" # always use "then" for the rest of the operands

      # add the operand speech
      is_unit_type = (isinstance(node.values[i], ast.Constant) or
                      isinstance(node.values[i], ast.Name))
      if ((not is_unit_type) and
          "indirect" in node.values[i].jvox_speech):
        speech += ", " + node.values[i].jvox_speech["indirect"]
      else:
        speech += node.values[i].jvox_speech["default"]
        
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = speech

    return speech

  def gen_ast_BoolOp(self, node):
    '''
    '''

    # style default
    self.gen_ast_BoolOp_default(node)
    # style indirect
    self.gen_ast_BoolOp_indirect(node)
    # style alternatev2
    self.gen_ast_BoolOp_alternate_v2(node)

    return


  def gen_ast_Compare_default(self, node):
    '''
    Generate speech for ast.Compare, style "default"

    Examples:
    
    '''

    style_name = "default"

    # generate the string
    speech = node.left.jvox_speech["default"] 
    for i in range(len(node.ops)):
      speech += (" " + node.ops[i].jvox_speech["default"] + " " +
                 node.comparators[i].jvox_speech["default"])
      
    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech


  def gen_ast_Compare(self, node):
    '''
    '''

    # style default
    self.gen_ast_Compare_default(node)

    return
