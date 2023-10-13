'''
This file defines additional member functions for the class
pyastvox_speech_generator, These functions handles,
ast.Subscript
ast.Slice
'''

import ast

class subscript_mixin:
    def gen_ast_Subscript_default(self, node):
        '''
        Generate speech for ast.Subscript. Style: default
        Examples:
        1. a[1]: list item index 1 of list a
        2. a[i, "new"]: list items with indices i and string new of list a
        '''

        style_name = "default"

        # get the name of the list or dict
        list_name = node.value.jvox_speech["selected_style"]
	      # a small tweak if the list name is "a". Variable "a" is generated
        # as "a-" for ast.Name so that the text2speech won't read it as an
        # article. However, for the speech generate here, we will add "\'s"
        # after it, which text2speech reads as "a s". So we need to remove
        # the dash after a
        if list_name == "a-":
            list_name = "a"

        # get the speeches for the indices
        idx_speeches = []
        if not isinstance(node.slice, ast.Tuple):
            # just one index
            if isinstance(node.slice, ast.BinOp):
                idx_speeches.append(", expression " +
                                    node.slice.jvox_speech["selected_style"])
            else:
                idx_speeches.append(node.slice.jvox_speech["selected_style"])
        else:
            # more one indices
            for e in node.slice.elts:
                idx_speeches.append(e.jvox_speech["selected_style"])

        # combine and generate the speech
        if len(idx_speeches) == 1:
            speech = f"{list_name}\'s item with index {idx_speeches[0]}"
        else:
            speech = f"{list_name}\'s items with indices {idx_speeches[0]}"
            for i in range(1, len(idx_speeches)-1):
                speech += f", {idx_speeches[i]}"
            speech += f", and {idx_speeches[-1]}"

        # add the speech to jvox_speech
        if hasattr(node, "jvox_speech"):
            node.jvox_speech[style_name] = speech
        else:
            node.jvox_speech = {style_name: speech}
            
        return speech

    def gen_ast_Subscript_reversed(self, node):
        '''
        Generate speech for ast.Subscript. Style: indirect
        Examples:
        1. a[1]: list item index 1 of list a
        2. a[i, "new"]: list items with indices i and string new of list a
        '''

        style_name = "reversed"

        # get the name of the list or dict
        list_name = node.value.jvox_speech["selected_style"]

        # get the speeches for the indices
        idx_speeches = []
        if not isinstance(node.slice, ast.Tuple):
            # just one index
            if isinstance(node.slice, ast.BinOp):
                idx_speeches.append(", expression " +
                                    node.slice.jvox_speech["selected_style"])
            else:
                idx_speeches.append(node.slice.jvox_speech["selected_style"])
        else:
            # more one indices
            for e in node.slice.elts:
                idx_speeches.append(e.jvox_speech["selected_style"])

        # combine and generate the speech
        if len(idx_speeches) == 1:
            speech = f"list item with index {idx_speeches[0]}, of list {list_name}"
        else:
            speech = f"list item with indices of {idx_speeches[0]}"
            for i in range(1, len(idx_speeches)-1):
                speech += f", {idx_speeches[i]}"
            speech += f", and {idx_speeches[-1]}"
            # if the index is a tuple, than the object has to be a dictionary
            speech += f", of dictionary {list_name}"

        # add the speech to jvox_speech
        if hasattr(node, "jvox_speech"):
            node.jvox_speech[style_name] = speech
        else:
            node.jvox_speech = {style_name: speech}
            
        return speech

    def gen_ast_Subscript(self, node):
        '''
        Generate speech for ast.Subscript
        '''

        # style default
        self.gen_ast_Subscript_default(node)
        # style indirect
        self.gen_ast_Subscript_reversed(node)
            
