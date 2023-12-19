'''
This file defines additional member functions for the Class astparser, These
functions parse the Python assignment expressions.
'''

import ast

class if_stmt_mixin:
    def gen_ast_If_default(self, node):
        '''
        Generate speech for ast.IfExp. Style "default"
        '''

        style_name = "default"

        print(node.test.jvox_speech)

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = "To be generated"

        return

    def gen_ast_If(self, node):
        '''
        Generate speech for ast.IfExp.
        '''

        # style default
        self.gen_ast_If_default(node)

        return
