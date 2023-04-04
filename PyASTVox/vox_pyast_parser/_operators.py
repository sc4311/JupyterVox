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

    # generate speech for comparison
    def emit_compare(self, node, level):

        # create an empty array to hold the values
        speech = Speech()
        
        # handle left operand
        print(node.left)
        left_speech = self.emit(node.left)
        
        # handle the comparator
        ops = node.ops[0]
        
        if isinstance(ops, ast.NotIn):
            op_text = "not in"
        elif isinstance(ops, ast.Lt):
            print('less than')
            op_text = "less than"
        elif isinstance(ops, ast.Gt):
            op_text = "greater than"
        elif isinstance(ops, ast.GtE):
            op_text = "great than equal to"
        elif isinstance(ops, ast.LtE):
            op_text = "less than equal to"
        elif isinstance(ops, ast.Eq):
            op_text = "equal to"
        elif isinstance(ops, ast.NotEq):
            op_text = "not equal to"
        elif isinstance(ops, ast.Is):
            op_text = "Is"
        elif isinstance(ops, ast.If):
            op_text = "if"
        else:
            raise Exception("Unknown Opcode" + str(test))

        # handle the right operand
        # this only handles one right operand, not sure what multi-operand test
        # look like
        for right_opr in node.comparators:
            right_speech = self.emit(right_opr)
            
            speech.text = left_speech.text + " " + op_text + " " + right_speech.text
            
        return speech

    # emit for UnaryOp nodes
    def emit_UnaryOp(self, node, level):
        # create an empty array to hold the values
        speech = Speech()
        
        # visit operation
        speech.data['op'] = self.emit_Opcode(node.op)
        
        # generate speech for operand
        unary_operand = self.emit(node.operand)
        
        speech.text = (speech.data['op']+ " " + unary_operand.text)
        return speech

    # parse an ast.Add/Mult/Assi... node
    def emit_Opcode(self, node):
        if isinstance(node, ast.Add):
            return 'plus'
        elif isinstance(node, ast.Mult):
            return 'multiply'
        elif isinstance(node, ast.Sub):
            return "minus"
        elif isinstance(node, ast.Div):
            return "divide"
        elif isinstance(node, ast.Mod):
            return "Mod"
        elif isinstance(node, ast.FloorDiv):
            return "FloorDiv"
        elif isinstance(node, ast.MatMult):
            return "MatMult"
        elif isinstance(node, ast.Pow):
            return "to the power of"
        elif isinstance(node, ast.USub):
            return "negative"
        else:
            raise Exception("Unknown Opcode" + str(node))

    # emit for AugAssign nodes (e.g., +=)
    def emit_AugAssign(self, node, level):
        # an empty array that holds a value is created
        speech = Speech()

        # visit operation
        speech.data['op'] = self.emit_Opcode(node.op)

        # generate speech for target
        target_str = self.emit(node.target).text
    
        # handles the RHS of assignment
        value_str = self.emit(node.value).text

        speech.text = (target_str + " " + speech.data['op']+ " equal " +
                       value_str)
        
        return speech
