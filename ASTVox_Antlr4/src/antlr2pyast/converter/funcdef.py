# Antlr4 to Python AST
# Conversion function for function definition statements, incluidng
#   funcdef
#   parameters
#   typedargslist
#   tfpdef

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# convert tfpdef to ast.arg
def convert_tfpdef(listener, ctx:Python3Parser.TfpdefContext):
  '''
  convert tfpdef to ast.arg
  rule: tfpdef: name (':' test)?;
  '''
  # parameter name
  arg = ctx.children[0].getText()
  # annotation of the parameter, e.g., type
  ann = None
  if ctx.getChildCount() == 3:
    # has annotation
    ann = ctx.children[2].pyast_tree

  # construct the ast.arg node
  ctx.pyast_tree = ast.arg(arg, ann)

  return

# Convert normal arguments to list of args and defaults. Normal arguments
# basically in the format arg: default_value.
# These parameters can be positional or keyword-ed, or both.
# This really interesting to know that a Python parameter can be positional
# and keyword-ed at the same time, and there are also position-only and
# keyword-only parameters.
def convert_normal_arg_list(ctx:Python3Parser.TypedargslistContext,
                            start_idx:int,
                            use_none_default:bool):
  '''
  Convert normal arguments to list of args and defaults. Normal arguments
  basically in the format arg: default_value.
  Takes three parameters:
  1. ctx: the list of typed arguments (i.e., typedargslist),
  2. start_idx: the index of the first children to process.
  3. use_none_default: if the parameter has no defaults value, should we
     use None as the default value. A keyword-only parameter must use
     None as its default value, if not specified.
  
  Rule: tfpdef ('=' test)? (',' tfpdef ('=' test)?)*
  Returns two lists: args, defaults, and an integer, representing the
  number of children processed
  '''

  i = start_idx; # index to process the children

  # process the normal args
  args = []
  defaults = []
  while i < ctx.getChildCount():
    if not isinstance(ctx.children[i], Python3Parser.TfpdefContext):
      # not an normal parameter anymore, this is either *vararg or **kwarg
      # stop the processing
      break
    
    # add the argument
    args.append(ctx.children[i].pyast_tree)
    
    # if there are default value, add them to defaults
    has_default = False
    if (ctx.getChildCount() > (i+1) and
        isinstance(ctx.children[i+1], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[i+1].getText() == '='):
      # next symbol is '=', do have default value
      has_default =  True
      defaults.append(ctx.children[i+2].pyast_tree)
    elif use_none_default:
      # there is no default specified. However, we are asked to use None
      # as the default value. This should be only applicable to keyword-only
      # arguments/parameters.
      defaults.append(None)

    # advance i to next argument
    if has_default:
      i += 4 # skip tfpdef '=' test ','
    else:
      i += 2 # skip tfpdef ','
      
  return args, defaults, i

# convert typedargslist to ast.arguments, this one is complex
def convert_typedargslist(self, ctx:Python3Parser.TypedargslistContext):
  '''
  convert typedargslist to ast.arguments, this one is complex.
  rule:
  typedargslist: (tfpdef ('=' test)? (',' tfpdef ('=' test)?)* (',' (
        '*' tfpdef? (',' tfpdef ('=' test)?)* (',' ('**' tfpdef ','? )? )?
      | '**' tfpdef ','? )? )?
  | '*' tfpdef? (',' tfpdef ('=' test)?)* (',' ('**' tfpdef ','? )? )?
  | '**' tfpdef ','?);

  This is basically four cases:
  1. normal args + *vararg + kwonly args + **kwarg
  2. normal args + **kwarg
  3. *kwarg + kwonly args + **kwarg
  4. **kwarg
  '''

  # process the normal parameters first, if they exist.
  # These parameters are positional and keyword-ed at the same time.
  args, defaults, i = convert_normal_arg_list(ctx, 0, use_none_default=False)

  # process the vararg if this is one, i.e., the *args parameters
  vararg = None
  if (i < ctx.getChildCount() and
      isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
      ctx.children[i].getText() == '*'):
    # vararg: '*' tfpdef
    vararg = ctx.children[i+1].pyast_tree

    # advance to next argument
    i += 3 # skip '*', tfpdef, ','

  # process the keyword-only arguments, if they exist
  kwonlyargs, kw_defaults, i = convert_normal_arg_list(ctx, i,
                                                       use_none_default=True)

  # process the kwarg if there is one, i.e., the **kwargs parameters
  kwarg = None
  if (i < ctx.getChildCount() and
      isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
      ctx.children[i].getText() == '**'):
    # kwarg: '**' tfpdef
    kwarg = ctx.children[i+1].pyast_tree
    
  # generate the ast.arguments node
  posonlyargs = [] # antlr4 grammar does not support position-only args
  ast_node = ast.arguments(posonlyargs, args, vararg, kwonlyargs,
                           kw_defaults, kwarg, defaults)
  ctx.pyast_tree = ast_node

  return
  
# convert parameters to its child's ast.arguments node
def convert_parameters(self, ctx:Python3Parser.ParametersContext):
  '''
  Convert parameters to its child's ast.arguments node.
  Rule: parameters: '(' typedargslist? ')';
  '''

  ctx.pyast_tree = ctx.children[1].pyast_tree

  return

# Convert funcdef to ast.FunctionDef
def convert_funcdef(self, ctx:Python3Parser.FuncdefContext):
  '''
  Convert funcdef to ast.FunctionDef
  Rule: funcdef: 'def' name parameters ('->' test)? ':' block;
  '''
  
  # get the function name and arguments
  name = ctx.children[1].getText()
  args = ctx.children[2].pyast_tree

  # get the return annotation and body
    
  if ctx.getChildCount() == 7:
    # has return annotation
    returns = ctx.children[4].pyast_tree
    body = ctx.children[6].pyast_tree
  else:
    # has no return annotation
    returns = None
    body = ctx.children[4].pyast_tree

  # nowhere to find the decorators, no support for now
  decorator_list = []

  # construct the ast.FunctionDef node
  ast_node = ast.FunctionDef(name, args, body, decorator_list, returns)
  ctx.pyast_tree = ast_node

  return
  
