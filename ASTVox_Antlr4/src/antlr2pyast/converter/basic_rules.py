# this file covers the translation of the non-terminals/terminals that
# are simple and do not need separate source files

#antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

#PyAST package
import ast

# Grammar:
#   comparison: expr (comp_op expr)*;
def convert_comparison(listener, ctx:Python3Parser.ComparisonContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Comparison node has more than three children, "
                         + "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Comparison node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    #listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# Grammar:
# expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
#                     ('=' (yield_expr|testlist_star_expr))*);
def convert_expr_stmt(listener, ctx:Python3Parser.Expr_stmtContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Expr_stmt node has more than three children, "
                         + "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Expr_stmt node at the moment")

    # generate an ast.Expr node
    child = ctx.children[0]
    # ast_node = ast.Expr(listener.pyast_trees[child])
    # listener.pyast_trees[ctx] = ast_node
    ast_node = ast.Expr(child.pyast_tree)
    ctx.pyast_tree = ast_node
    return

# Grammar:
#    simple_stmt: (expr_stmt | del_stmt | pass_stmt | flow_stmt |
#             import_stmt | global_stmt | nonlocal_stmt | assert_stmt);
def convert_simple_stmt(listener, ctx:Python3Parser.Simple_stmtContext):
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Simple_stmt node has more than three children, "
                         + "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Simple_stmt node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    #listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    
    return

# grammar:
#    simple_stmts: simple_stmt (';' simple_stmt)* ';'? NEWLINE;
def convert_simple_stmts(listener, ctx:Python3Parser.Simple_stmtsContext):
    # can have one or more simple statement with ';' and NEWLINE
    if ctx.getChildCount() < 1: # this should never happen...
        raise ValueError("Simple_stmts node has less than one children? "
                         + "count is " + str(ctx.getChildCount()))

    # in Python AST, statements are stored in a list, as the "body"
    # of ast.Module
    ast_stmts = []
    # process each children
    for i in range(ctx.getChildCount()):
      child = ctx.children[i];
      if (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.NEWLINE):
        # ignore new line character
        continue;
      elif (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.SEMI_COLON):
        # ignore semi colon character
        continue;
      elif isinstance(child, Python3Parser.Simple_stmtContext):
        # a statement, add to the list
        #ast_stmts.append(listener.pyast_trees[child])
        ast_stmts.append(child.pyast_tree)
      else:
        # should never reach here
        raise TypeError("Unknow child type for Simple_Statments, " +
                        "type is " + str(type(child)))

    # copy child's AST node
    # listener.pyast_trees[ctx] = ast_stmts
    ctx.pyast_tree = ast_stmts
    
    return

# grammar
# single_input: NEWLINE | simple_stmts | compound_stmt NEWLINE;
def convert_single_input(listener, ctx:Python3Parser.Single_inputContext):
    # should have no more than 2 child
    if ctx.getChildCount() > 2:
        raise ValueError("Single_input node has more than two children, "
                         + "count is " + str(ctx.getChildCount()))

    # based on the grammar on the first child matter
    child = ctx.children[0]
    if (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.NEWLINE):
        # just a new line, return empty list
        body = []
    elif isinstance(child, Python3Parser.Simple_stmtsContext):
        # statements, get the statement node list from the child
        #body = listener.pyast_trees[child]
        body = child.pyast_tree
    elif isinstance(child, Python3Parser.Compound_stmtContext):
      raise NotImplementedError("Compound_stmt child not implemented for" +
                                " simple_input")


    # create an ast.Module node to hotd the statements
    # not sure what "type_ignores" is, ignoring "type_ignores"
    ast_node = ast.Module(body, type_ignores=[])
    #listener.pyast_trees[ctx] = ast_node
    ctx.pyast_tree = ast_node
    
    return
