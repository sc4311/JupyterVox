# This file defines additional member functions for the Class astparser, These
# functions parse the if statements

import ast

from speech import Speech

class if_stmts_mixin:
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
