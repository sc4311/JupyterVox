'''
This file defines additional member functions for the Class astparser, These
functions parse the Python assignment expressions.
'''

import ast

class if_stmt_mixin:
    def gen_ast_If_default(self, node):
        print(node.test.jvox_speech)
        '''
        Generate speech for ast.IfExp. Style "default"
        
        wrote in call: 
        if a>b return =>
        
        if (a > b) {
            return '=>'
        }
        
        
        Examples:
        1. e.g.,a > b if a > b else b: a greater than b if a greater than b else b
        
        2. e.g.,a > b if a > b else b if a > b else c: a greater than b if a greater than b else b if a greater than b else c
        '''

        style_name = "default"

        # generate the speech for the test
        test_speech = node.test.jvox_speech["default"] + " "

        # generate the speech for the body
        body_speech = "if " + node.body.jvox_speech["default"] + " "

        # generate the speech for the orelse
        orelse_speech = "else " + node.orelse.jvox_speech["default"]

        # generate the final speech
        speech = test_speech + body_speech + orelse_speech

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
        node.jvox_speech[style_name] = speech

        return speech

    def gen_ast_If(self, node):
        '''
        Generate speech for ast.IfExp.
        '''

        # style default
        self.gen_ast_If_default(node)

        return
