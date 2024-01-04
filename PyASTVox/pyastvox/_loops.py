'''
This file defines additional member functions for the Class
pyastvox_speech_generator, These functions parse AST related to loops,
including,
ast.For
ast.While
'''

import ast

class loops_mixin:
    def gen_ast_For_default(self, node):
        '''
        Generate speech for ast.For. Style "default"
        Read as "for loop with target" + target + “to loop over, " + iter + "The loop body is" + body + "The code after loop ends is" + orelse.
        E.g.,
        1. for i in list_x: return;: "for loop with target i, to loop over, list_x. The loop body is. return." 
        '''

        style_name = "default"

        # get the target
        target = node.target.jvox_speech["selected_style"]
        
        # get the iter
        iters = node.iter.jvox_speech["selected_style"]
        
        # get the body.
        body = ""
        if ((node.body is not None) and (len(node.body) > 0) and
            (node.body[0] is not None)):
            body = " The loop body is. "
            for stmt in node.body:
                body += stmt.jvox_speech["selected_style"] + '. '

        # get the orelse
        orelse = ""
        if (node.orelse is not None) and (len(node.orelse) > 0):
            orelse = " The code after loop ends is. "
            for stmt in node.orelse:
                orelse += stmt.jvox_speech["selected_style"] + '. '

        # generate the whole speech
        speech = ("\"For\" loop with target " + target +
                  ", to loop over, " + iters + "." + 
                  body + orelse)
        
        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return

    def gen_ast_For(self, node):
        '''
        Generate speech for ast.For
        '''

        # style default
        self.gen_ast_For_default(node)

        return

    def gen_ast_While_default(self, node):
        '''
        Generate speech for ast.While. Style "default"
        Read as "While loop with test" + test + "The loop body is" + body + "The code after loop ends is" + orelse.
        E.g.,
        1. while (a>b): return;: "While loop with test, a- greater than b. The loop body is. return." 
        '''

        style_name = "default"

        # get the test
        test = node.test.jvox_speech["selected_style"]
        
        # get the body.
        body = ""
        if ((node.body is not None) and (len(node.body) > 0) and
            (node.body[0] is not None)):
            body = " The loop body is. "
            for stmt in node.body:
                body += stmt.jvox_speech["selected_style"] + '. '

        # get the orelse
        orelse = ""
        if (node.orelse is not None) and (len(node.orelse) > 0):
            orelse = " The code after loop ends is. "
            for stmt in node.orelse:
                orelse += stmt.jvox_speech["selected_style"] + '. '

        # generate the whole speech
        speech = ("While loop with test, " + test + "." + 
                  body + orelse)
        
        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return

    def gen_ast_While(self, node):
        '''
        Generate speech for ast.While
        '''

        # style default
        self.gen_ast_While_default(node)

        return
