# this file covers the translation of the non-terminals/terminals that
# are simple and do not need separate source files

#antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

#PyAST package
import ast

# other translation functions
# from antlr2pyast import *
import antlr2pyast


# convert_name: convert a Name node to ast.Name
def convert_name(node):
    # name has three terminal options: variable name/id, "_", and "match"

    # should have only one child
    if node.getChildCount() != 1:
      raise ValueError("Name node has more than one child, count is" +
                       str(node.getChildCount()))

    # child should be terminal
    child = node.children[0]
    if not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
      raise TypeError("Child of Name node is not a terminal type.")

    # potential error: not sure how to determine if the operation is
    # store or del.
    id = child.getText()
    ast_node = ast.Name(id, ast.Load())

    return ast_node;

# convert_atom: Atom node to AST node
def convert_atom(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Atom node has more than three children, count is " +
                         str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom node at the moment")
    
    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_atom_expr(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Atom_expr node has more than three children, " +
                         "count is " + str(node.getChildCount()))
    
    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom_expr node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

# generate AST node based on operator type
def gen_ast_operator(op_text):
    if op_text == "+":
        ast_node = ast.Add()
    elif op_text == "-":
        ast_node = ast.Sub()
    elif op_text == "*":
        ast_node = ast.Mult()
    elif op_text == "/":
        ast_node = ast.Div()
    elif op_text == "%":
        ast_node = ast.Mod()
    elif op_text == "@":
        ast_node = ast.MatMult()
    elif op_text == "//":
        ast_node = ast.FloorDiv()
    elif op_text == "**":
        ast_node = ast.Pow()
    elif op_text == "<<":
        ast_node = ast.LShift()
    elif op_text == ">>":
        ast_node = ast.RShift()
    elif op_text == "&":
        ast_node = ast.BitAnd()
    elif op_text == "^":
        ast_node = ast.BitXor()
    elif op_text == "|":
        ast_node = ast.BitOr()
    else:
        raise ValueError("Unknown operator in expression:" + op_text)
    
    return ast_node

#
def convert_expr(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Expr node has more than three children, count is " +
                         str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() == 1:
        # one child => rule expr => atom_expr
        return antlr2pyast.convert_tree(node.getChild(0))
    elif node.getChildCount() == 3:
        # three children typically is binary operation

        # generate the node for left and right children (operands) first
        left_opr = antlr2pyast.convert_tree(node.getChild(0))
        right_opr = antlr2pyast.convert_tree(node.getChild(2))

        # generat the operation node
        operator = gen_ast_operator(node.getChild(1).getText())
        
        # generate the tree node
        binop_node = ast.BinOp(left_opr, operator, right_opr)
        return binop_node
    else:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Expr node at the moment, count is " +
                                  str(node.getChildCount()))

#
def convert_comparison(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Comparison node has more than three children, "
                         + "count is " + str(node.getChildCount()))
    
    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Comparison node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_not_test(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Not_test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Not_test node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_and_test(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("And_test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "And_test node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_or_test(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Or_test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Or_test node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_test(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Test node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Test node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_testlist_star_expr(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Testlist_star_expr node has more than three children"
                         + ", count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
      raise NotImplementedError("More than one child is not supported for " +
                                "Testlist_star_expr node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_expr_stmt(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Expr_stmt node has more than three children, "
                         + "count is " + str(node.getChildCount()))
    
    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Expr_stmt node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_simple_stmt(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Simple_stmt node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Simple_stmt node at the moment")
    
    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_simple_stmts(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Simple_stmts node has more than three children, "
                         + "count is " + str(node.getChildCount()))

    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Simple_stmts node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))

#
def convert_single_input(node):
    # should have no more than 3 child
    if node.getChildCount() > 3:
        raise ValueError("Single_input node has more than three children, "
                         + "count is " + str(node.getChildCount()))
    
    # only handles one the case with one child now
    if node.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Single_input node at the moment")

    return antlr2pyast.convert_tree(node.getChild(0))
