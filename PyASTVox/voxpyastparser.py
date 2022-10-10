import ast
from pprint import pprint

# class for the object used for returns from emit functions
# making the return to a class to make it easier for future expension
class Speech:
    def __init__(self):  # initialize member variables
        self.text = []  # used to hold the generate speech text
        self.data = {}  # used to hold other data
        return

class astparser:
    # init function. does nothing at the moment
    def __init__(self):
        return

    # helper function to study the internal of a ast node
    def ast_node_explore(self, node):
        # print("Iter fields")
        for field, value in ast.iter_fields(node):
            print(field, value)

        print("Iter children")
        for child in ast.iter_child_nodes(node):
            print(child)


    # generate dict key for statements
    def gen_Dict_Key(self, node, level):
        if isinstance(node, ast.Expr):
            return "ExprStmt-" + str(level)
        elif isinstance(node, ast.BinOp):
            return "BinOpStmt-" + str(level)
        elif isinstance(node, ast.Assign):
            return "BinOpStmt-" + str(level)

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


    # generate speech for comparison
    def emit_compare(self, node, level):

        # create an empty array to hold the values
        speech = Speech()
        
        # handle left operand
        # print(node.left)
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

    # parse an ast.Name code and # parse an ast.Num code$$ Helping extract the
    # num part from the comparators
    def emit_Name(self, node):
        speech = Speech()
        
        speech.text = node.id
        speech.data = ast.dump(node)

        return speech

    # parse an ast.Num code$$ Helping extract the num part from the comparators
    def emit_Num(self, node, level):
        speech = Speech()

        speech.text = str(node.n)
        speech.data = ast.dump(node)

        return speech

    # parse an ast.Str Helping extract the string part from stmt
    def emit_Str(self, node, level):
        speech = Speech()

        speech.text = "string "+ node.s
        speech.data = ast.dump(node)

        return speech


    # emit for Assign nodes
    def emit_Assign(self, node, level):
        # an empty array that holds a value is created
        speech = Speech()
        
        # handles the LHS of assigments
        target_str = []

        # there could be multiple targets, i.e., multiple variables being
        # assigned values to. Cannot handle this multi-target case yet.
        # need to implement tuple support
        for target in node.targets:
            target_str.append(self.emit(target).text)

            # handles the RHS of assigment
            value_str = self.emit(node.value).text

        #   language specification based on number of items in target_str
        if (len(target_str) == 1):
            speech.text = ",".join(target_str)
            speech.text = speech.text + " is assigned with " + value_str
        else:
            speech.text = ",".join(target_str)
            speech.text = speech.text + " are assigned with " + value_str

        return speech


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

    # emit for Assign nodes
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


    # parse an ast.Return statment
    # current probably only handles returning a variable or a number
    def emit_Return(self, node, level):
        speech = Speech()
        
        # generate speech for return value
        ret_val_speech = self.emit(node.value)
        
        # combine and generate speech
        speech.text = "return value " + ret_val_speech.text
        
        return speech

    # emit for ast.If
    def emit_IfExp(self, node, level):
        # create an empty array to hold the values
        speech = Speech()
        
        # generate the speech for the test
        # I use emit() here to make the processing generic
        test_speech = self.emit(node.test, level+1)
        
        # generate the speech for the body
        # again, I use emit() here to make the processing generic
        for stmt in node.body:
            body_speech = self.emit(stmt, level+1)
            
        # combine speech
        speech.text = "if statement with the test is " + test_speech.text
        speech.text = speech.text + " and the body is " + body_speech.text
        
        return speech


    # emit for ast.Expr
    def emit_Expr(self, node, level):
        speech = Speech()
        # for each child, emit the speech for it
        # !!! This is very likely WRONG: only tested1 for BinOp child.
        # This will also only return the speech of the last child
        for child in ast.iter_child_nodes(node):
            speech = self.emit(child, level + 1)

        return speech

    def emit_For_loop(self, node, level):
        speech = Speech()
        body_speech = Speech()
        

        s1 = self.emit(node.target)
        s2 = self.emit(node.iter)
        s3 = ''

        for i in range(len(node.body)-1):
            body_speech = self.emit(node.body[i])
            s3 += f"{body_speech.text}, "

        body_speech = self.emit(node.body[-1])
        s3 += body_speech.text

        if isinstance(s1, Speech) and isinstance(s2, Speech):
            speech.text = f"for {s1.text} in {s2.text} {s3}"
        elif isinstance(s1, Speech) and isinstance(s2, str):
            speech.text = f"for {s1.text} in {s2} {s3}"
        else:
            speech.text = f"for {s1} in {s2} {s3}"

        return speech

    def emit_List(self, node, level):
        speech = Speech()
        text = "list "
        for i in range(len(node.elts)-1):
            speech = self.emit(node.elts[i])
            text += f"{speech.text}, "
        
        speech = self.emit(node.elts[-1])
        text += speech.text
        speech.text = text

        return speech

    def emit_Call(self, node, level):
        speech_text = ''
        text = self.emit(node.func)

        speech_text += text.text
        if speech_text == "len":
                    speech_text = "length of"

        for arg in node.args:
            body = self.emit(arg)
            if isinstance(body, str):
                speech_text += f" {body}"
            else:
                speech_text += f" {body.text}"
        
        text.text = speech_text

        return text

    def emit_Dict(self, node, level):
        text = "dictionary with "
            
        for i in range(len(node.keys)-1):
            text += f"key {self.emit(node.keys[i])} "
            text += f"value {self.emit(node.values[i])} "
        

        text += f"and key {self.emit(node.keys[-1])} "
        text += f"value {self.emit(node.values[-1])}"

        
        return text

    def emit_Constant(self, node, level):
        constant = ''
        for value in node.value:
            constant += value
        
        if constant:
            return f"\"{constant}\""

        return ""

    def emit_None(self, node, level):
        speech = Speech()

        speech.text = "None"

        return speech

    # emit for ast.Module
    def emit_Module(self, node, level):
        # for each child, emit the speech for it
        # !!! This is likely WRONG: I don't know how many children there
        # can be in a Module node. So "speech" will be set by
        # only the last child
        for child in ast.iter_child_nodes(node):
            speech = self.emit(child, level + 1)

        return speech


    # emit: the main entrance function
    # It calls the emit function for each type of nodes
    #
    def emit(self, node, level=0):
        # for each type of the node, call the corresponding emit function
        if isinstance(node, ast.Module):
            return self.emit_Module(node, level)
        if isinstance(node, ast.Expr):
            return self.emit_Expr(node, level)
        elif isinstance(node, ast.BinOp):
            return self.emit_BinOp(node, level)
        elif isinstance(node, ast.UnaryOp):
            return self.emit_UnaryOp(node, level)
        elif isinstance(node, ast.Assign):
            return self.emit_Assign(node, level)
        elif isinstance(node, ast.If):
            return self.emit_IfExp(node, level)
        elif isinstance(node, ast.AugAssign):
            return self.emit_AugAssign(node, level)
        elif isinstance(node, ast.Compare):
            return self.emit_compare(node, level)
        elif isinstance(node, ast.Name):
            return self.emit_Name(node)
        elif isinstance(node, ast.Num):
            return self.emit_Num(node, level)
        elif isinstance(node, ast.Str):
            return self.emit_Str(node,level)
        elif isinstance(node, ast.Return):
            return self.emit_Return(node, level)
        elif isinstance(node, ast.For):
            return self.emit_For_loop(node, level)
        elif isinstance(node, ast.List):
            return self.emit_List(node, level)
        elif isinstance(node, ast.Call):
            return self.emit_Call(node, level)
        elif isinstance(node, ast.Dict):
            return self.emit_Dict(node, level)
        elif isinstance(node, ast.Constant):
            return self.emit_Constant(node, level)
        elif isinstance(node, type(None)):
            return self.emit_None(node, level)
        else:
            print("Unhandled node type:", type(node))
            return
