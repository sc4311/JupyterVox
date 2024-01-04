'''
This file defines additional member functions for the Class
pyastvox_speech_generator, These functions parse AST related to classes,
including,
ast.Attribute
'''

import ast

class class_mixin:
    def gen_ast_Attribute_default(self, node):
        '''
        Generate speech for ast.Attribute. Style "default"
        Because it is difficult to read nested attributes, here I am simply
        reading the statement literally with "dot"
        E.g.,
        1. a.b.c: "a dot b dot c"
        '''

        style_name = "default"

        # generate the speech. Nested ast.Attribute nodes are constructed
        # reversely. For example, for "a.b.c", the lower level node corresponds
        # to "a.b," the higher level node corresponds to ".c"
        speech = (node.value.jvox_speech["selected_style"] + " dot " +
                  self.var_name_special_processing(node.attr))

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return

    def gen_ast_Attribute(self, node):
        '''
        Generate speech for ast.Attribute
        '''

        # style default
        self.gen_ast_Attribute_default(node)

        return

