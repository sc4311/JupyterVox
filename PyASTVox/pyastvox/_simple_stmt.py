'''
This file defines additional member functions for the Class astparser, These
functions parse some simple Python statements, including,
return
pass
continue
break
'''

import ast

class simple_stmt_mixin:
    def gen_ast_Return_default(self, node):
        '''
        Generate speech for ast.Return. Style "default"
        E.g.,
        1. return a: return a
        2. return (a+b): return a+b
        '''

        style_name = "default"

        # get the value node and its jvox_speech
        if node.value is not None:
            val_speech = node.value.jvox_speech["selected_style"]
            speech = "return, " + val_speech
        else:
            speech = "return"

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return

    def gen_ast_Return(self, node):
        '''
        Generate speech for ast.Return
        '''

        # style default
        self.gen_ast_Return_default(node)

        return

    def gen_ast_Continue_default(self, node):
        '''
        Generate speech for ast.Return. Style "default".
        Just read "continue", there is nothing more to read.
        '''

        style_name = "default"

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = "continue"

        return

    def gen_ast_Continue(self, node):
        '''
        Generate speech for ast.Continue
        '''

        # style default
        self.gen_ast_Continue_default(node)

        return

    def gen_ast_Break_default(self, node):
        '''
        Generate speech for ast.Break. Style "default".
        Just read "break", there is nothing more to read.
        '''

        style_name = "default"

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = "break"

        return

    def gen_ast_Break(self, node):
        '''
        Generate speech for ast.Break
        '''

        # style default
        self.gen_ast_Break_default(node)

        return

    def gen_ast_Pass_default(self, node):
        '''
        Generate speech for ast.Break. Style "default".
        Just read "pass", there is nothing more to read.
        '''

        style_name = "default"

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = "pass"

        return

    def gen_ast_Pass(self, node):
        '''
        Generate speech for ast.Pass
        '''

        # style default
        self.gen_ast_Pass_default(node)

        return
