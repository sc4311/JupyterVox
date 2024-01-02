# Style selection for JupyterVox.
#
# This file is used to determine what speech style will be used to generate the
# final "spoken" reading. The style selected in this file can be changed with
# pyastvox_speech_generator class' function set_speech style.
#
# Note that all styles will be generated, the selection should only happen at
# after all speech styles are generated. This is because the complex
# inter-dependency between styles. 

import ast

class pyastvox_speech_styles:
    selected_styles = {
        ast.Constant: "default",
        ast.Name: "default",
        ast.Add: "default",
        ast.Mult: "default",
        ast.Sub: "default",
        ast.Mult: "default",
        ast.Div: "default",
        ast.Mod: "default",
        ast.FloorDiv: "default",
        ast.MatMult: "default",
        ast.LShift: "default",
        ast.RShift: "default",
        ast.BitOr: "default",
        ast.BitXor: "default",
        ast.BitAnd: "default",
        ast.USub: "default",
        ast.Not: "default",
        ast.UAdd: "default",
        ast.Invert: "default",
        ast.BinOp: "alternatev2",
        ast.UnaryOp: "default",
        ast.List: "default",
        ast.Dict: "default",
        ast.Subscript: "reversed",
        ast.Assign: "indirect",
        ast.BoolOp: "alternatev2",
        ast.Continue: "default",
        ast.Pass: "default",
        ast.Break: "default",
        ast.Return: "default",
    }
    
