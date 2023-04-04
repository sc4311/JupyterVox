# This file defines additional member functions for the Class astparser, These
# functions parse the functions

import ast

from speech import Speech

class functions_mixin:
    # parse an ast.Return statment
    # current probably only handles returning a variable or a number
    def emit_Return(self, node, level):
        speech = Speech()
        
        # generate speech for return value
        if not node.value is None:
            ret_val_speech = self.emit(node.value)
            speech.text = "return value " + ret_val_speech.text
        else:
            speech.text = "return none"

        
        return speech

    # parse an ast.Call, i.e., function invocation, statement
    def emit_Call(self, node, level):
        speech = Speech()

        # get function name
        func_name = self.emit(node.func)

        if func_name.text == "len": # builtin func len
            speech = self.emit_builtin_func_len(node.args)
        elif func_name.text == "range": # builtin func range
            speech = self.emit_builtin_func_range(node.args)
        else: # generic functions
            args = []
            for arg in node.args:
                body = self.emit(arg)
                args.append(body.text)
            args_text = ", ".join(args)
                 
            speech.text = ("function invocation, function name is " +
                           func_name.text + ", with parameters are " +
                           args_text)                
        return speech

    # generate speech for built-in function, len
    def emit_builtin_func_len(self, args):

        speech = Speech()
        
        body_speech = self.emit(args[0])
        #length = str(len(body_speech.text.split()[-1]))
        #speech_text += f"{body_speech.text} ({length})"
        speech.text = "the length of " + body_speech.text

        return speech

    # generate speech for built-in function, range
    def emit_builtin_func_range(self, args):
        speech_text = "the range from "

        speech = Speech()
        
        if len(args) == 3: # has start, stop, and step args
            start = self.emit(args[0])
            stop = self.emit(args[1])
            step = self.emit(args[2])
            speech_text += (f"{start.text} to {stop.text} with a step of " \
                            f"{step.text}")
        elif len(args) == 2: # only has start and stop
            start = self.emit(args[0])
            stop = self.emit(args[1])
            speech_text += f"{start.text} to {stop.text}"
        elif len(args) == 1: # only has stop
            stop = self.emit(args[0])
            speech_text += f"0 to {stop.text}"
        else: # should not reach here
            raise Exception("Range function call with more than 3 parameters!")

        speech.text = speech_text

        return speech
