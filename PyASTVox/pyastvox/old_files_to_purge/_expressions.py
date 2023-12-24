# This file defines additional member functions for the Class astparser, These
# functions parse the Python expressions.

import ast

from speech import Speech

class exprs_mixin:
    
    # emit for ast.Expr
    def emit_Expr(self, node, level):
        speech = Speech()
        # for each child, emit the speech for it
        # !!! This is very likely WRONG: only tested1 for BinOp child.
        # This will also only return the speech of the last child
        for child in ast.iter_child_nodes(node):
            speech = self.emit(child, level + 1)

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
