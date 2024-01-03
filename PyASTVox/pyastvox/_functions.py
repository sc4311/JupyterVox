'''
This file defines additional member functions for the Class
pyastvox_speech_generator, These functions parse the function related AST nodes,
including,
ast.Call

'''

import ast

class functions_mixin:

  def gen_ast_Call_default(self, node):
    '''
    Generate speech for ast.Call. Style "default"
    Read "call" funcation_name "with" arguments.
    E.g.,
    1. func1(): call func1 with no arguments
    2. func1(a): "call func1 with argument, a-"
    3. func1(b=c): "call func1 with argument, key b equals c"
    4. func1(a, *m, b=c, **x): call func1 with argument, key b equals c
    '''

    style_name = "default"

    # get function name
    func_name = node.func.jvox_speech["selected_style"]
    # get non-keyworded argument speeches
    arguments = []
    for arg in node.args:
      arguments.append(arg.jvox_speech["selected_style"])
    # get keyworded argument speeches
    keywords = []
    for kw in node.keywords:
      keywords.append(kw.jvox_speech["selected_style"])

    # construct the whole speech
    # Fairly cumbersome implementation to handle variable cases in a more
    # readable fashion.
    if (len(arguments) == 0) and (len(keywords) == 0):
      # no arguments at all
      speech = f"call {func_name} with no arguments"
    elif (len(keywords) == 0):
      # at least one non-keyword args, but no keyword arguments
      if (len(arguments) == 1):
        # just one non-keyworded argument
        speech = f"call {func_name} with argument, {arguments[0]}"
      else:
        # more than one non-keyworded arguments, no keyword arguments
        args_speech = ', '.join(arguments[0:-1]) # all args expect the last one
        speech = (f"call {func_name} with arguments, {args_speech}, and " + 
                  f"{arguments[-1]}")
    elif (len(arguments) == 0):
      # no non-keyword args, at least one keyword args
      if (len(keywords) == 1):
        # just one keyworded argument
        speech = f"call {func_name} with argument, {keywords[0]}"
      else:
        # more than on keyword arguments
        args_speech = ', '.join(keywords[:-1]) # all keywords but last one
        speech = (f"call {func_name} with arguments, {args_speech}, and " + 
                  f"{keywords[-1]}")
    else:
      # >=1 non-keyword args, and >=1 keyword args
      if (len(arguments) > 0) and (len(keywords) == 1):
        # has non-keyworded arguments, and only one keyword argument
        args_speech = ', '.join(arguments) # all non-keyworded args
        speech = (f"call {func_name} with arguments {args_speech}, and " + 
                  f"{keywords[-1]}")
      else:
        # more than one keyword arguments
        args_speech = ', '.join(arguments) + ", " # all non-keyworded args
        args_speech += ', '.join(keywords[:-1]) # all keywords but last one
        speech = (f"call {func_name} with arguments, {args_speech}, and " + 
                  f"{keywords[-1]}")
      
    
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_Call(self, node):
    '''
    Generate speech for ast.Call
    '''

    # style default
    self.gen_ast_Call_default(node)
    
    return

  def gen_ast_Starred_default(self, node):
    '''
    Generate speech for ast.Starred. Style "default"
    Simply read "starred" + variable name
    E.g.,
    1. *args: "starred args"
    '''

    style_name = "default"

    # generate the speech
    var_name = node.value.jvox_speech["selected_style"]
    speech = f"starred {var_name}" 
      
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_Starred(self, node):
    '''
    Generate speech for ast.Starred
    '''

    # style default
    self.gen_ast_Starred_default(node)
    
    return

  def gen_ast_keyword_default(self, node):
    '''
    Generate speech for ast.keyword. Style "default"
    For normal keyword arg, read "key" arg "equals" value
    For double stared arg, read "double-starred" arg
    E.g.,
    1. b = c: "key b equals c"
    2. **b : "double starred b"
    '''

    style_name = "default"

    # generate the speech
    if node.arg is not None:
      # normal keyword arg
      arg = self.var_name_special_processing(node.arg)
      val = node.value.jvox_speech["selected_style"]
      speech = f"key {arg} equals {val}"
    else:
      # double starred arg
      val = node.value.jvox_speech["selected_style"]
      speech = f"double-starred {val}"
      
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_keyword(self, node):
    '''
    Generate speech for ast.keyword
    '''
    
    # style default
    self.gen_ast_keyword_default(node)
    
    return
