'''
This file defines additional member functions for the Class astparser, These
functions parse the Python operators.
'''

import ast

class ops_mixin:
  def gen_ast_Constant(self, node):
    '''
    Generate speech for ast.Constant.
    Just use the string, i.e., str(), of the constant as the speech 
    '''
    node.jvox_speech = str(node.value)
    #node.jvox_data = ast.dump(node)
    return

  def gen_binary_operations_complex(self, node, style:str):
    '''
    Parse  an ast.Add/Mult/Assi... node
    Generate multiple types of speeches:
    1. direct style: "plus/multiply/minus/
    2. indirect style: the sum/product/difference of
   
    Please also see gen_ast_BinOp for details
   
    Note there are no separate implementation for each binary operation, i.e.,
    not implementation for ast.Add (gen_ast_Add) and all
    '''
    
    if isinstance(node, ast.Add):
        s = {"direct":"plus", "indirect":"the sum of"}
    elif isinstance(node, ast.Mult):
        s = {"direct":"multiply", "indirect":"the product of"}
    elif isinstance(node, ast.Sub):
        s = {"direct":"minus", "indirect":"the difference of"}
    elif isinstance(node, ast.Div):
        s = {"direct":"divide"} # no indirect, quotient is a less-known
    elif isinstance(node, ast.Mod):
        s = {"direct":"Mod"}
    elif isinstance(node, ast.FloorDiv):
        s = {"direct": "floor division"}
    elif isinstance(node, ast.MatMult):
        s = {"direct": "matrix multiply"}
    elif isinstance(node, ast.Pow):
        s = {"direct": "to the power of"}
    elif isinstance(node, ast.USub):
        s = {"direct": "negative"}
    else:
        raise ValueError("Unknown Opcode" + str(node))

    if style == "direct":
      # default style, direct
      return s["direct"]
    elif style == "indirect":
      return s["indirect"]
    else:
      raise ValueError("Unknow BinOp Style" + style)

  def gen_ast_BinOp(self, node):
    '''
    Generate speech for ast.BinOp.

    Speeches are generated based on styles.
    '''
    ############ Get Speech Style #################
    if not ast.BinOp in self.speech_styles:
      style = "default"
    else:
      style = self.speech_styles[ast.BinOp]

    # for alternating styple
    if style == "alternating":
      # first, check if the left and right children are unit type
      left_is_unit_type = (isinstance(node.left, ast.Num) or
                           isinstance(node.left, ast.Name))
      right_is_unit_type = (isinstance(node.right, ast.Num) or
                           isinstance(node.right, ast.Name))

      # check if we should use direct or indirect style
      # if left/right children are Num/Name, use direct
      # if there are nested BinOp children, use indirect
      if (left_is_unit_type and right_is_unit_type):
        style = "direct"
      else:
        style = "indirect"

    ######## Generate Speech #####################
    # gen the speech for the operator
    op_str = self.gen_binary_operations_complex(node.op, style)

    # get the speeches for left and right chilren
    left_str = node.left.jvox_speech
    right_str = node.right.jvox_speech

    # get the speech for the op code
    if style == "default" or style == "direct":
      node.jvox_speech = left_str + " " + op_str + " " + right_str
    elif style == "indirect":
      node.jvox_speech = (op_str + " " + left_str + " and " +
                          right_str + ", ")

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

    # # emit for UnaryOp nodes
    # def emit_UnaryOp(self, node, level):
    #     # create an empty array to hold the values
    #     speech = Speech()
        
    #     # visit operation
    #     speech.data['op'] = self.emit_Opcode(node.op)
        
    #     # generate speech for operand
    #     unary_operand = self.emit(node.operand)
        
    #     speech.text = (speech.data['op']+ " " + unary_operand.text)
    #     return speech

    # # parse an ast.Add/Mult/Assi... node
    # def emit_Opcode(self, node):
    #     if isinstance(node, ast.Add):
    #         return 'plus'
    #     elif isinstance(node, ast.Mult):
    #         return 'multiply'
    #     elif isinstance(node, ast.Sub):
    #         return "minus"
    #     elif isinstance(node, ast.Div):
    #         return "divide"
    #     elif isinstance(node, ast.Mod):
    #         return "Mod"
    #     elif isinstance(node, ast.FloorDiv):
    #         return "FloorDiv"
    #     elif isinstance(node, ast.MatMult):
    #         return "MatMult"
    #     elif isinstance(node, ast.Pow):
    #         return "to the power of"
    #     elif isinstance(node, ast.USub):
    #         return "negative"
    #     else:
    #         raise Exception("Unknown Opcode" + str(node))

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
