# This file defines additional member functions for the Class astparser, These
# functions parse the Python operators.
#
# I use mixin class here to scatter member functions across multiple files for
# Class astparser.

import ast

from speech import Speech

class ops_mixin:

    # parse an ast.Add/Mult/Assi... node
    # generate multiple types of speeches:
    # 1. direct style: "plus/multiply/minus/
    # 2. indirect style: the sum/product/difference
    #
    # Please also see emit_BinOp for details
    def emit_Opcode_Complex(self, node):
        if isinstance(node, ast.Add):
            return {"direct":"plus", "indirect":"the sum of"}
        elif isinstance(node, ast.Mult):
            return {"direct":"multiply", "indirect":"the product of"}
        elif isinstance(node, ast.Sub):
            return {"direct":"minus", "indirect":"the difference of"}
        elif isinstance(node, ast.Div):
            return {"direct":"divide"} # no indirect, quotient is a less-known
        elif isinstance(node, ast.Mod):
            return {"direct":"Mod"}
        elif isinstance(node, ast.FloorDiv):
            return {"direct": "floor division"}
        elif isinstance(node, ast.MatMult):
            return {"direct": "matrix multiply"}
        elif isinstance(node, ast.Pow):
            return {"direct": "to the power of"}
        elif isinstance(node, ast.USub):
            return {"direct": "negative"}
        else:
            raise Exception("Unknown Opcode" + str(node))
    
    # emit for BinOp nodes
    def emit_BinOp(self, node, level):
        # notes on the implementation and speech generation:
        # For a statement of a + b * c, it is better to read as "a plus the
        # the product of b and c". However, if the statement is "a + b + c",
        # it is better to read it as "the sum of a and b, plus c".
        #
        # Currently, I don't have a perfect solution to more intelligently
        # generate the speech (may be an AI model?). So I will limit the
        # use of "the sum/product/difference" to expression with unit type of
        # operands, i.e., single variable or constant.
        # This solution still cannot handle long nested expressions, where there
        # is probably no good way to read it.
    
        # create an empty array to hold the values
        speech = Speech()
    
        # generate speech for left operand
        left_speech = self.emit(node.left, level+1)
    
        # visit the operator
        operator_speech = self.emit_Opcode_Complex(node.op)
        
        # generate speech for right operand
        right_speech = self.emit(node.right, level+1)
    
        # check if the left and right children are unit type
        left_is_unit_type = (isinstance(node.left, ast.Num) or 
                             isinstance(node.left, ast.Name))
        right_is_unit_type = (isinstance(node.right, ast.Num) or 
                              isinstance(node.right, ast.Name))
    
        # check if we should use direct or indirect speech
        use_indirect = False
        if (left_is_unit_type and right_is_unit_type and
            "indirect" in operator_speech):
            use_indirect = True
        
        if use_indirect == False:
            speech.text = (left_speech.text + " " +
                           operator_speech["direct"] + " " +
                           right_speech.text)
        else:
            speech.text = (operator_speech["indirect"] + " " +
                           left_speech.text + " and " +
                           right_speech.text + ", ")
        
        return speech
