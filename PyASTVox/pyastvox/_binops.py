'''
This file defines additional member functions for the Class astparser, These
functions parse the Python binary operators.
'''

import ast

class binops_mixin:

  def gen_ast_Add(self, node):
    '''
    Styles:
    1. default: "plus"
    2. indirect: "the sum of"
    '''
    node.jvox_speech = {"default":"plus", "indirect":"the sum of"}

    return

  def gen_ast_Mult(self, node):
    '''
    Styles:
    1. default: "multiply"
    2. indirect: "the product of"
    '''
    node.jvox_speech = {"default":"multiply", "indirect":"the product of"}

    return

  def gen_ast_Sub(self, node):
    '''
    Styles:
    1. default: "minus"
    2. indirect: "the sum of"
    '''
    node.jvox_speech = {"default":"minus", "indirect":"the difference of"}

    return

  def gen_ast_Div(self, node):
    '''
    Styles:
    1. default: "divide"
    '''
    node.jvox_speech = {"default":"divide"}

    return

  def gen_ast_Mod(self, node):
    '''
    Styles:
    1. default: "modulo"
    '''
    node.jvox_speech = {"default":"modulo"}

    return

  def gen_ast_FloorDiv(self, node):
    '''
    Styles:
    1. default: "floor divide"
    '''
    node.jvox_speech = {"default":"floor divide"}

    return

  def gen_ast_Pow(self, node):
    '''
    Styles:
    1. default: "to the power of"
    '''
    node.jvox_speech = {"default":"to the power of"}

    return

  def gen_ast_LShift(self, node):
    '''
    Styles:
    1. default: "left shift by"
    '''
    node.jvox_speech = {"default":"left shift by"}

    return

  def gen_ast_RShift(self, node):
    '''
    Styles:
    1. default: "right shift by"
    '''
    node.jvox_speech = {"default":"right shift by"}

    return

  def gen_ast_BitOr(self, node):
    '''
    Styles:
    1. default: "bit-wise or"
    '''
    node.jvox_speech = {"default":"bit-wise or"}

    return

  def gen_ast_BitXor(self, node):
    '''
    Styles:
    1. default: "bit-wise xor"
    '''
    node.jvox_speech = {"default":"bit-wise xor"}

    return

  def gen_ast_BitAnd(self, node):
    '''
    Styles:
    1. default: "bit-wise and"
    '''
    node.jvox_speech = {"default":"bit-wise and"}

    return

  def gen_ast_USub(self, node):
    '''
    Styles:
    1. default: "negative"
    '''
    node.jvox_speech = {"default":"negative"}

    return

  def gen_ast_BinOp_style_default(self, node):
    '''
    Speech generation for ast.BinOp, style "default".
    Examples,
    1. e.g., "a+b*c", a plus b multiply c
    2. e.g., "(a+b)*c", a plus b, then multiply c
    '''

    style_name = "default"
    
    # first, check if the left and right children are unit type
    left_is_unit_type = (isinstance(node.left, ast.Constant) or
                         isinstance(node.left, ast.Name))
    right_is_unit_type = (isinstance(node.right, ast.Constant) or
                          isinstance(node.right, ast.Name))

    # add ", then" if left is not a unit-type
    use_then = not left_is_unit_type
    
    # generate the speech
    if use_then:
      speech = (node.left.jvox_speech["default"] + ", then " +
                node.op.jvox_speech["default"] + " " + 
                node.right.jvox_speech["default"])
    else:
      speech = (node.left.jvox_speech["default"] + " " +
                node.op.jvox_speech["default"] + " " + 
                node.right.jvox_speech["default"])

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_BinOp_style_indirect(self, node):
    '''
    Speech generation for ast.BinOp, style "indirect".
    Examples,
    1. e.g., "a+b*c", the sum of a and the sum of b and c
    2. e.g., "(a+b)*c", the product of the sum of a and b, and c
    '''

    style_name = "indirect"

    # first, check if the left and right children are unit type
    left_is_unit_type = (isinstance(node.left, ast.Constant) or
                         isinstance(node.left, ast.Name))
    right_is_unit_type = (isinstance(node.right, ast.Constant) or
                          isinstance(node.right, ast.Name))

    # whether to add coma after "and" in the speech
    coma_after_and = not right_is_unit_type
    # coma_after_and = False
    and_str = " and, " if coma_after_and else " and "
    
    # get the string for the left/right operand node. If the operand node is
    # ast.Constant or ast.Name it does not have indirect speech. Use "default"
    # in that case.
    if "indirect" in node.left.jvox_speech:
      left_speech = node.left.jvox_speech["indirect"]
    else:
      left_speech = node.left.jvox_speech["default"]
      
    if "indirect" in node.right.jvox_speech:
      right_speech = node.right.jvox_speech["indirect"]
    else:
      right_speech = node.right.jvox_speech["default"]
    
    # generate the speech
    if "indirect" in node.op.jvox_speech:
      # operator has indirect speech
      speech = (node.op.jvox_speech["indirect"] + " " +
                left_speech + and_str + right_speech + ", ")
    else:
      # operator does not have indirect speech, use the direct speech
      speech = (left_speech + " " + node.op.jvox_speech["default"] + " " + 
                right_speech)

    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_BinOp_style_alternate(self, node):
    '''
    Speech generation for ast.BinOp, style "alternate".
    Examples,
    1. e.g., "a+b*c", a plus the product of b and c
    2. e.g., "(a+b)*c", the sum of a plus b, then multiply c
    '''

    style_name = "alternate"

    # determine what style to use
    use_style = "indirect"
    if ((hasattr(node.left, "jvox_data") and
         "alternate" in node.left.jvox_data and 
         node.left.jvox_data["alternate"] == "indirect") or
        (hasattr(node.right, "jvox_data") and
         "alternate" in node.right.jvox_data and 
         node.right.jvox_data["alternate"] == "indirect")):
      # if either left or right operand speeches are "indirect" use direct
      use_style = "direct"

    if not ("indirect" in node.op.jvox_speech):
      # if the operator does not support indirect style, use direct
      use_style = "direct"

    # first, check if the left and right children are unit type
    left_is_unit_type = (isinstance(node.left, ast.Constant) or
                         isinstance(node.left, ast.Name))
    right_is_unit_type = (isinstance(node.right, ast.Constant) or
                          isinstance(node.right, ast.Name))

    # whether to add coma after "and" in the speech
    coma_after_and = not right_is_unit_type
    # coma_after_and = False
    and_str = " and, " if coma_after_and else " and "

    # get left and right speech if they have "alternate" speech. If
    # "alternate" does not exist, use "default"
    if style_name in node.left.jvox_speech:
      left_speech = node.left.jvox_speech[style_name]
    else:
      left_speech = node.left.jvox_speech["default"]
      
    if style_name in node.right.jvox_speech:
      right_speech = node.right.jvox_speech[style_name]
    else:
      right_speech = node.right.jvox_speech["default"]

    # generate the speech
    if use_style == "indirect":
      # operator has indirect speech
      speech = (node.op.jvox_speech["indirect"] + " " +
                left_speech + and_str + right_speech + ", ")
    else:
      # operator does not have indirect speech, use the direct speech
      speech = (left_speech + " " + node.op.jvox_speech["default"] + " " +
                right_speech + ", ")
      
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = speech
    if not hasattr(node, "jvox_data"):
      node.jvox_data = {}
    node.jvox_data[style_name] = use_style

    return speech

  def gen_ast_BinOp_style_alternate_v2(self, node):
    '''Speech generation for ast.BinOp, style "alternate".

    Use direct/default for unit-typed right operand, use indirect for
    non-unit-typed right operand
    
    Examples,
    1. e.g., "a+b*c", a- plus the product of b and c
    2. e.g., "(a+b)*c", a- plus b, then multiply c
    '''

    style_name = "alternatev2"

    # first, check if the left and right children are unit type
    left_is_unit_type = (isinstance(node.left, ast.Constant) or
                         isinstance(node.left, ast.Name))
    right_is_unit_type = (isinstance(node.right, ast.Constant) or
                          isinstance(node.right, ast.Name))

    # add ", then" if left is not a unit-type
    use_then = not left_is_unit_type


    # get the left string
    if style_name in node.left.jvox_speech:
      left_speech = node.left.jvox_speech[style_name]
    else:
      left_speech = node.left.jvox_speech["default"]
    
    # get the right string based on its unit type
    if ((not right_is_unit_type) and
        "indirect" in node.right.jvox_speech):
      right_speech = node.right.jvox_speech["indirect"]
    else:
      right_speech = node.right.jvox_speech["default"]

    # generate the speech
    if use_then:
      speech = (left_speech + ", then " +
                node.op.jvox_speech["default"] + " " +  right_speech)
    else:
      speech = (left_speech + " " +
                node.op.jvox_speech["default"] + " " + right_speech)
      
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
    node.jvox_speech[style_name] = speech

    return speech

  def gen_ast_BinOp_style_semantic_oriented(self, node):
    '''
    Speech generation for ast.BinOp, style "semantic_oriented".
    
    This style reads the expression based on the semantic order (i.e., operation
    precedence), instead of the text order. There is a still a problem reading
    complex expression with multiple complex subexpressions, e.g., (a+b)*(a-b)
    
    Examples,
    1. e.g., "a+b*c", b multiply c, then plus a
    2. e.g., "(a+b)*c", a plus b, then multiply c

    '''

    style_name = "semantic_oriented"
    
    # first, check if the left and right children are unit type
    left_is_unit_type = (isinstance(node.left, ast.Constant) or
                         isinstance(node.left, ast.Name))
    right_is_unit_type = (isinstance(node.right, ast.Constant) or
                          isinstance(node.right, ast.Name))

    # determine whether we should switch left and right in reading.
    # Only switch if left is a constant/id and right is not
    switch_left_right = left_is_unit_type and (not right_is_unit_type)

    # add ", then" before the operator if actual left is not a unit-type
    if switch_left_right:
      use_then = not right_is_unit_type
    else:
      use_then = not left_is_unit_type
    if use_then:
      connect_string = ", then "
    else:
      connect_string = " "
      
    # get the left and right speeches based on whether we need to switch
    if switch_left_right:
      # switch left and right
      if style_name in node.left.jvox_speech:
        right_speech = node.left.jvox_speech[style_name]
      else:
        right_speech = node.left.jvox_speech["selected_style"]

      if style_name in node.right.jvox_speech:
        left_speech = node.right.jvox_speech[style_name]
      else:
        left_speech = node.right.jvox_speech["selected_style"]
        
    else:
      # do not switch left and right
      if style_name in node.left.jvox_speech:
        left_speech = node.left.jvox_speech[style_name]
      else:
        left_speech = node.left.jvox_speech["selected_style"]

      if style_name in node.right.jvox_speech:
        right_speech = node.right.jvox_speech[style_name]
      else:
        right_speech = node.right.jvox_speech["selected_style"]
    
    # generate the speech
    speech = (left_speech + connect_string +
              node.op.jvox_speech["default"] + " " + right_speech)
    
    # add the speech to jvox_speech
    if hasattr(node, "jvox_speech"):
      node.jvox_speech[style_name] = speech
    else:
      node.jvox_speech = {style_name: speech}

    return speech

  def gen_ast_BinOp(self, node):
    '''
    Generate speech for ast.BinOp. Call the generator for each style.
    '''
    node.jvox_speech = {}
    
    # style: plain
    self.gen_ast_BinOp_style_default(node)
    # style: indirect
    self.gen_ast_BinOp_style_indirect(node)
    # style: alternate
    self.gen_ast_BinOp_style_alternate(node)
    # style: semantic oriented
    self.gen_ast_BinOp_style_semantic_oriented(node)
    # style: alternate
    self.gen_ast_BinOp_style_alternate_v2(node)

    return
    
#####################################################################################
    
    # # generate speech for comparison
    # def emit_Compare(self, node, level):

    #     # create an empty array to hold the values
    #     speech = Speech()
        
    #     # handle left operand
    #     print(node.left)
    #     left_speech = self.emit(node.left)
        
    #     # handle the comparator
    #     ops = node.ops[0]
        
    #     if isinstance(ops, ast.NotIn):
    #         op_text = "not in"
    #     elif isinstance(ops, ast.Lt):
    #         print('less than')
    #         op_text = "less than"
    #     elif isinstance(ops, ast.Gt):
    #         op_text = "greater than"
    #     elif isinstance(ops, ast.GtE):
    #         op_text = "great than equal to"
    #     elif isinstance(ops, ast.LtE):
    #         op_text = "less than equal to"
    #     elif isinstance(ops, ast.Eq):
    #         op_text = "equal to"
    #     elif isinstance(ops, ast.NotEq):
    #         op_text = "not equal to"
    #     elif isinstance(ops, ast.Is):
    #         op_text = "Is"
    #     elif isinstance(ops, ast.If):
    #         op_text = "if"
    #     else:
    #         raise Exception("Unknown Opcode" + str(test))

    #     # handle the right operand
    #     # this only handles one right operand, not sure what multi-operand test
    #     # look like
    #     for right_opr in node.comparators:
    #         right_speech = self.emit(right_opr)
            
    #         speech.text = (left_speech.text + " " + op_text + " " +
    #                        right_speech.text)
            
    #     return speech

    # # emit for AugAssign nodes (e.g., +=)
    # def emit_AugAssign(self, node, level):
    #     # an empty array that holds a value is created
    #     speech = Speech()

    #     # visit operation
    #     speech.data['op'] = self.emit_Opcode(node.op)

    #     # generate speech for target
    #     target_str = self.emit(node.target).text
    
    #     # handles the RHS of assignment
    #     value_str = self.emit(node.value).text

    #     speech.text = (target_str + " " + speech.data['op']+ " equal " +
    #                    value_str)
        
    #     return speech
