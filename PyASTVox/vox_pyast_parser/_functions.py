# This file defines additional member functions for the Class astparser, These
# functions parse the functions

import ast

from speech import Speech

class functions_mixin:
    # parse an ast.Return statment
    # current probably only handles returning a variable or a number
    def emit_Return(self, node, level):
        speech = Speech()
        
        # generate speech for return value
        ret_val_speech = self.emit(node.value)
        
        # combine and generate speech
        speech.text = "return value " + ret_val_speech.text
        
        return speech
