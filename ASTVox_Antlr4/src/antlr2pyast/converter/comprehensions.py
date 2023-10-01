# Antlr4 to Python AST
# Conversion function for comprehension statements, including
#   comp_iter
#   comp_if
#   comp_for

import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# Convert comp_iter to a dictionary with two lists, "ifs" and "comprehensions".
def convert_comp_iter(listener, ctx:Python3Parser.Comp_iterContext):
  '''
  Convert comp_if to a dictionary with two lists, "ifs" and "comprehensions".
  Rule: comp_iter: comp_for | comp_if;

  Basically pass on the child's pyast_tree, which is a dict of two lists,
  i.e., {"ifs":[...], "comprehensions":[...]}
  '''

  # pass on child's pyast_tree
  ctx.pyast_tree = ctx.children[0].pyast_tree

  return
  
# Convert comp_for to a dictionary with two lists, "ifs" and "comprehensions".
def convert_comp_for(listener, ctx:Python3Parser.Comp_forContext):
  '''
  Convert comp_for to a dictionary with two lists, "ifs" and "comprehensions".
  That is, the pyast_tree is a dict of two lists,
  i.e., {"ifs":[...], "comprehensions":[...]}.
  Nonetheless, the "ifs" list should be empty, please see the following for
  the reason.
  
  Rule: comp_for: ASYNC? 'for' exprlist 'in' or_test comp_iter?;

  The "ASYNC? 'for' exprlist 'in' or_test" creates an new item in the
  "comprehensions" list. This new item is an object of type ast.comprehension.
  This creation will consume the "ifs" list from "comp_iter",
  if "comp_iter" exist.
  
  If there is a comp_iter, its "comprehensions" list is passed on. Because the
  "ifs" list is consumed when generating the ast.comprehension, the ifs list is
  not passed on. Hence the "ifs" list will be empty in the end.

  This implementation is due to Antlr4's grammar nested comp_iters, even though
  they should be the on the same level.
  '''

  #### construct the ast.Comprehension node
  # if there is ASYNC, then the comprehension is async
  if (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
      ctx.children[0].getText() == "async"):
    is_async = 1
  else:
    is_async = 0

  # get the for in the list
  if is_async:
    target = tools.list_to_node_or_tuple(ctx.children[2].pyast_tree,
                                         is_load=False)
    iter = ctx.children[4].pyast_tree
  else:
    target = tools.list_to_node_or_tuple(ctx.children[1].pyast_tree,
                                         is_load=False)
    iter = ctx.children[3].pyast_tree

  new_comprehension = ast.comprehension(target, iter, [], is_async)

  # get the ifs from the comp_iter, if it exists
  if isinstance(ctx.children[-1], Python3Parser.Comp_iterContext):
    new_comprehension.ifs = ctx.children[-1].pyast_tree["ifs"]

  # get the comprehensions list from the comp_iter, if it exists
  # if no comp_iter, create a new empty list
  if isinstance(ctx.children[-1], Python3Parser.Comp_iterContext):
    comprehensions = ctx.children[-1].pyast_tree["comprehensions"]
  else:
    comprehensions = []

  # add the new ast.comprehension node, and return the dict
  # need to add to the beginning of the list
  comprehensions.insert(0, new_comprehension)
  ctx.pyast_tree = {"ifs":[], "comprehensions":comprehensions}

  return

  

# Convert comp_if to a dictionary with two lists, "ifs" and "comprehensions".
def convert_comp_if(listener, ctx:Python3Parser.Comp_ifContext):
  '''
  Convert comp_if to a dictionary with two lists, "ifs" and "comprehensions".
  That is, the pyast_tree is a dict of two lists,
  i.e., {"ifs":[...], "comprehensions":[...]}.
  
  Rule: comp_if: 'if' test_nocond comp_iter?;

  The "if test_nocond" creates an new item in the "ifs" list.
  If there is a comp_iter, its "ifs" and "comprehensions" lists are passed on.
  This implementation is due to Antlr4's grammar nested comp_iters, even though
  they should be the on the same level.
  '''

  # get the new if from test_nocond
  new_if = ctx.children[1].pyast_tree

  # get the ifs and comprehensions lists from comp_iter, if it exist.
  # if no comp_iter, create new list
  if ctx.getChildCount() == 3:
    ifs = ctx.children[2].pyast_tree["ifs"]
    comprehensions = ctx.children[2].pyast_tree["comprehensions"]
  else:
    ifs = []
    comprehensions = []

  # insert new_if to the beginning of the list, and return the dict
  ifs.insert(0, new_if)
  ctx.pyast_tree = {"ifs":ifs, "comprehensions":comprehensions}

  return


  
  
