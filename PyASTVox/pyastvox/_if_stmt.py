'''
This file defines additional member functions for the Class astparser, These
functions parse the Python assignment expressions.
'''

import ast

class if_stmt_mixin:
    def gen_ast_If_default(self, node):
        '''
        Generate speech for ast.If. Style "default"
        Read as "If statement with test" + test + "If true, the code is." + body + "If false, the code is." + orelse.
        E.g.,
        1. if (a>b): return;: 'If statement with test, a- greater than b.. If true, the code is. return. ' 
        '''

        style_name = "default"

        # get the test
        test = node.test.jvox_speech["selected_style"]
        
        # get the body.
        body = ""
        if ((node.body is not None) and (len(node.body) > 0) and
            (node.body[0] is not None)):
            body = ". If true, the code is. "
            for stmt in node.body:
                body += stmt.jvox_speech["selected_style"] + '. '

        # get the orelse
        orelse = ""
        if (node.orelse is not None) and (len(node.orelse) > 0):
            orelse = " If false the code is. "
            for stmt in node.orelse:
                orelse += stmt.jvox_speech["selected_style"] + '. '

        # generate the whole speech
        speech = ("If statement with test, " + test + "." + 
                  body + orelse)

        

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return

    def gen_ast_If(self, node):
        '''
        Generate speech for ast.If.
        '''

        # style default
        self.gen_ast_If_default(node)

        return
