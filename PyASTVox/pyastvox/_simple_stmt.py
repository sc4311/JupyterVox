'''
This file defines additional member functions for the Class astparser, These
functions parse some simple Python statements, including,
return
pass
continue
break
import
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
        Generate speech for ast.Pass. Style "default".
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

    def gen_ast_Import_default(self, node):
        '''
        Generate speech for ast.Import. Style "default".
        Reads "import", then follows with package names
        Example:
        1. import a.c: import a dot c
        2. import numpy as np: import numpy as np
        '''

        style_name = "default"

        # generate speeches with packages
        speech = "import"
        for p in node.names:
            speech += ", " + p.jvox_speech["selected_style"]

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return
    
    def gen_ast_Import(self, node):
        '''
        Generate speech for ast.Import
        '''

        # style default
        self.gen_ast_Import_default(node)

        return

    def gen_ast_alias_default(self, node):
        '''
        Generate speech for ast.alias. Style "default".
        Reads the package name. If there is as name, also reads "as" + the
        asname. "." is replaced as "dot".
        Example:
        1. numpy: "numpy"
        2. numpy as np: "numpy as np"
        3. package1.a as pa: "package1 dot a as pa"
        '''

        style_name = "default"

        # generate speeches with packages
        speech = node.name.replace(".", " dot ")
        if node.asname is not None:
            speech += " as " + node.asname.replace(".", " dot ")

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return
    
    def gen_ast_alias(self, node):
        '''
        Generate speech for ast.alias
        '''

        # style default
        self.gen_ast_alias_default(node)

        return

    def gen_ast_ImportFrom_default(self, node):
        '''
        Generate speech for ast.ImportFrom. Style "default".
        Reads "from" + module name +  "import" + package names.
        If level is not 0, then level will also be read out after the module
        name.
        Examples:
        1. from a.x import b, c: "from a dot x import b, c"
        2. from ..a import b, c: "from a (relative level 2) import b"
        3. form .. import x: "form directory (relative level 2) import x"
        '''

        style_name = "default"

        # generate speeches with packages
        if node.module is not None:
            speech = "from " + node.module.replace(".", " dot ")
        else:
            speech = "from directory"
        if node.level != 0:
            speech += f" (relative level {node.level})"
        speech += " import"
        for p in node.names:
            speech += ", " + p.jvox_speech["selected_style"]

        # add the speech to jvox_speech
        if not hasattr(node, "jvox_speech"):
            node.jvox_speech = {}
            node.jvox_speech[style_name] = speech

        return
    
    def gen_ast_ImportFrom(self, node):
        '''
        Generate speech for ast.Import
        '''

        # style default
        self.gen_ast_ImportFrom_default(node)

        return
        
