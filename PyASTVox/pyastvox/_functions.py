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
    Read "call" function_name "with" arguments.
    E.g.,
    1. func1(): call func1 with no arguments
    2. func1(a): "call func1 with argument, a-"
    3. func1(b=c): "call func1 with argument, b equals c"
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
    valid_args = arguments + keywords
    if len(valid_args) == 0: # no arguments
      arg_speech = "no arguments"
    elif len(valid_args) == 1: # one argument
      arg_speech = f"argument, {valid_args[0]}"
    else: # more than one arguments
      arg_speech = ("arguments, " + ", ".join(valid_args[:-1]) + ", and " +
                valid_args[-1])

    speech = f"call {func_name} with {arg_speech}"
    
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
      speech = f"{arg} equals {val}"
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

  def gen_ast_arg_default(self, node):
    '''
    Generate speech for ast.arg. Style "default"
    Read arg "with annotation" annotation "of type".
    Note that I am not sure how to get AST to generate type_comment.
    E.g.,
    1. a: int: "a with annotation int"
    '''

    style_name = "default"

    speech = self.var_name_special_processing(node.arg)
    if node.annotation is not None:
      speech += (" with annotation " +
                 node.annotation.jvox_speech["selected_style"])
    if node.type_comment is not None:
      speech += "with type of " + arg.type_comment
    
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_arg(self, node):
    '''
    Generate speech for ast.arg
    '''
    
    # style default
    self.gen_ast_arg_default(node)
    
    return

  def gen_ast_arguments_default(self, node):
    '''
    Generate speech for ast.arguments. Style "default"
    Read arguments one by one.
    E.g.,
    1. (a: 'annotation', m: str,  b=1, c=2, *d, e, f=3, **g): "with arguments, a- with annotation "string" annotation, m with annotation str, b with default value 1, c with default value 2, starred d, e, f with default value 3, and doubled-starred g"
    2. (): with no arguments
    '''

    style_name = "default"

    # generate speech for normal arguments
    args = []
    for arg in node.args:
      args.append(arg.jvox_speech["selected_style"])
    
    # adjust args with default values. list visit order is reversed
    # i goes from -1, -2 ... -len(node.defaults)
    for i in range(-1, -len(node.defaults)-1 ,-1):
      args[i] = (args[i] + " with default value " +
                 node.defaults[i].jvox_speech["selected_style"])
    
    # generate speech for variable arguments
    vararg = []
    if node.vararg is not None:
      vararg.append("starred " + node.vararg.jvox_speech["selected_style"])

    # generate speech for keyword-only arguments
    kwonlyargs = []
    for i in range(len(node.kwonlyargs)):
      arg_speech = node.kwonlyargs[i].jvox_speech["selected_style"]
      if node.kw_defaults[i] is not None:
        arg_speech += (" with default value " +
                       node.kw_defaults[i].jvox_speech["selected_style"])
      kwonlyargs.append(arg_speech)

    # generate speech for kwarg (double-starred keyword argument)
    kwarg = []
    if node.kwarg is not None:
      kwarg.append("doubled-starred " +
                   node.kwarg.jvox_speech["selected_style"])

    # construct the whole speech
    valid_args = args + vararg + kwonlyargs + kwarg
    
    if len(valid_args) == 0: # no arguments
      speech = "no arguments"
    elif len(valid_args) == 1: # one argument
      speech = f"argument, {valid_args[0]}"
    else: # more than one arguments
      speech = ("arguments, " + ", ".join(valid_args[:-1]) + ", and " +
                valid_args[-1])
    
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_arguments(self, node):
    '''
    Generate speech for ast.arg
    '''
    
    # style default
    self.gen_ast_arguments_default(node)
    
    return

  def gen_ast_FunctionDef_default(self, node):
    '''
    Generate speech for ast.arg. Style "default"
    Read: "Define function" + func_name + "with arguments" + args +
          "The function body is" + body
    E.g.,
    1. def f(a: 'annotation', m: str,  b=1, c=2, *d, e, f=3, **g): a+b; return y: Define function f with arguments, a- with annotation "string" annotation, m with annotation str, b with default value 1, c with default value 2, starred d, e, f with default value 3, and doubled-starred g. The function body is. a- plus b. return, y."
    2 def f(): return; : "Define function f with no arguments. The function body is. return." 
    '''

    style_name = "default"

    # generate speech for function name
    func_name = self.var_name_special_processing(node.name)
    speech = f"Define function {func_name}"

    # arguments
    speech += " with " + node.args.jvox_speech["selected_style"] + '.'

    # body.
    if node.body is not None:
      speech += " The function body is. "
      for stmt in node.body:
        speech += stmt.jvox_speech["selected_style"] + '. '
    
    # add the speech to jvox_speech
    if not hasattr(node, "jvox_speech"):
      node.jvox_speech = {}
      node.jvox_speech[style_name] = speech
      
      return

  def gen_ast_FunctionDef(self, node):
    '''
    Generate speech for ast.FunctionDef
    '''
    
    # style default
    self.gen_ast_FunctionDef_default(node)
    
    return
