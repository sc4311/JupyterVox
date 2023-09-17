# Antlr4 to Python AST
# Conversion function for tokens related to classdef, including
#   arguments
#   arglist
#   classdef

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# convert arglist to a list
def convert_arglist(listener, ctx:Python3Parser.ArglistContext):
  '''
  convert arglist to a list
  Rue: arglist: argument (',' argument)* ','?;
  '''

  args= []
  for child in ctx.children:
    if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
      continue # skip ','

    args.append(child.pyast_tree)

  ctx.pyast_tree = args

  return

# convert argument to the corresponding Python AST node
def convert_argument(listener, ctx:Python3Parser.ArgumentContext):
  '''
  convert argument to the corresponding Python AST node
  Rule: argument: ( test comp_for? |
                    test '=' test |
                    '**' test |
                    '*' test );
  Five cases:
  1. test: pass on the child's pyast_tree
  2. test comp_for: convert to an ast.GeneratorExp
  3. test = test: convert to ast.keyword
  4. ** test: convert to ast.keyword
  5. * test: convert to ast.Starred
  '''

  if ctx.getChildCount() == 1:
    # case 1, rule: argument: test
    # pass on the child's pyast_tree
    ctx.pyast_tree = ctx.children[0].pyast_tree
  elif isinstance(ctx.children[-1], Python3Parser.Comp_forContext):
    # case 2, rule: argument: test comp_for
    # convert to an ast.GeneratorExp
    elt = ctx.children[0].pyast_tree
    generators = ctx.children[1].pyast_tree["comprehensions"]
    ctx.pyast_tree = ast.GeneratorExp(elt, generators)
  elif (ctx.getChildCount() == 3 and
        isinstance(ctx.children[1], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[1].getText() == '='):
    # case 3, rule: argument: test = test, convert to ast.keyword
    arg = ctx.children[0].getText() # this could be an issue for Antlr4 grammar
                                    # which allows (17==17)=1
    value = ctx.children[2].pyast_tree
    ctx.pyast_tree = ast.keyword(arg, value)
  elif (ctx.getChildCount() == 2 and
        isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == '**'):
    # case 4, rule: argument: ** test, convert to ast.keyword
    arg = None
    value = ctx.children[1].pyast_tree
    ctx.pyast_tree = ast.keyword(arg, value)
  elif (ctx.getChildCount() == 2 and
        isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == '*'):
    # case 4, rule: argument: * test, convert to ast.Starred
    value = ctx.children[1].pyast_tree
    ctx.pyast_tree = ast.Starred(value, ast.Load())
  else:
    raise ValueError("Unknown argument composition.")

  return

# convert classdef to ast.ClassDef
def convert_classdef(listener, ctx:Python3Parser.ClassdefContext):
  '''
  convert classdef to ast.ClassDef
  rule: lassdef: 'class' name ('(' arglist? ')')? ':' block;
  '''

  name = ctx.children[1].getText() # class name
  decorator_list = [] # empty for now
  body = ctx.children[-1].pyast_tree # body

  # go over the arglist to extract base classes and keywords (metaclasses)
  bases = []
  keywords = []
  if (ctx.getChildCount() > 5 and
      isinstance(ctx.children[3], Python3Parser.ArglistContext)):
    # has arglist
    for n in ctx.children[3].pyast_tree:
      if isinstance(n, ast.keyword):
        keywords.append(n)
      elif isinstance(n, ast.Starred):
        bases.append(n)
      elif isinstance(n, ast.GeneratorExp):
        # Antlr4 allows class a (a for a in b): pass, but not in Python AST
        raise ValueError("Cannot have comprehensions in class def")
      else: # all other nodes
        bases.append(n)
        

  ctx.pyast_tree = ast.ClassDef(name, bases, keywords, body, decorator_list)

  return
  
