import ast
from pprint import pprint

# import the speech class
from speech import Speech

# Import member functions from mixing classes.  These functions are just used to
# spread the member functions to multiple Python files for better readability.
import _operators
import _expressions
import _variables

class astparser(_operators.ops_mixin,
                _expressions.exprs_mixin,
                _variables.vars_mixin):
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
        else:
            print("Unhandled node type:", type(node))
            return
