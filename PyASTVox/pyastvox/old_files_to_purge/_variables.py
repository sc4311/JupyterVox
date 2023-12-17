# This file defines additional member functions for the Class astparser, These
# functions parse the Python variables and constants.

import ast

from speech import Speech

class vars_mixin:
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
