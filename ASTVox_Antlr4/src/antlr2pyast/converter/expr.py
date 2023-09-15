# ANTLR4 to Python AST
# Conversion functions for the Expr* rules and terminals

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# generate AST node based on operator type
def gen_ast_binary_operator(op_text):
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
        raise ValueError("Unknown binary operator: " + op_text)

    return ast_node

# generate ast.BinOp node for an expression
def gen_ast_binop(listener, ctx:Python3Parser.ExprContext):
    # get the PyAST nodes for left and right operands
    # left_opr = listener.pyast_trees[ctx.getChild(0)]
    left_opr = ctx.getChild(0).pyast_tree
    # right_opr = listener.pyast_trees[ctx.getChild(2)]
    right_opr = ctx.getChild(2).pyast_tree
    
    # generate the operator node
    operator = gen_ast_binary_operator(ctx.getChild(1).getText())
    
    # generate the tree node
    binop_node = ast.BinOp(left_opr, operator, right_opr)

    return binop_node

# generate AST node based on unary operation type
def gen_ast_unary_operations(op_text):
    if op_text == "+":
        ast_node = ast.UAdd()
    elif op_text == "-":
        ast_node = ast.USub()
    elif op_text == "~":
        ast_node = ast.Invert()
    else:
        raise ValueError("Unknown unary operator:" + op_text)

    return ast_node

# generate ast.UnaryOp node for an expression
def gen_ast_unaryop(listener, ctx:Python3Parser.ExprContext):
    # UnaryOp expression can have more than one UnaryOp
    # need to do this iteratively. I am starting for the last, which
    # should represent an operand as another ExprContext

    count = ctx.getChildCount()

    # get the last operand node
    #operand = listener.pyast_trees[ctx.getChild(count-1)]
    operand = ctx.getChild(count-1).pyast_tree
    # generate the AST node for the last unary operator
    op = gen_ast_unary_operations(ctx.getChild(count-2).getText())
    # generate the lowest ast.UnaryOp node
    cur_unaryop_node = ast.UnaryOp(op, operand)

    # iterative build other UnaryOp nodes
    for i in range(count-3, -1, -1):
        op = gen_ast_unary_operations(ctx.getChild(i).getText())
        cur_unaryop_node = ast.UnaryOp(op, cur_unaryop_node)

    return cur_unaryop_node

# Grammar:
# expr: 
#    atom_expr
#    | expr '**' expr
#    | ('+'|'-'|'~')+ expr
#    | expr ('*'|'@'|'/'|'%'|'//') expr
#    | expr ('+'|'-') expr
#    | expr ('<<' | '>>') expr
#    | expr '&' expr
#    | expr '^' expr
#    | expr '|' expr
#    ;
def convert_expr(listener, ctx:Python3Parser.ExprContext):
    # should have at least one child
    if ctx.getChildCount() == 0:
        raise ValueError("Expr node has zero child\n")

    # only handles one the case with one child now
    if ctx.getChildCount() == 1:
        # one child => rule expr => atom_expr
        # copy child's AST node
        child = ctx.children[0]
        # listener.pyast_trees[ctx] = listener.pyast_trees[child]
        ctx.pyast_tree = child.pyast_tree
        return
    elif (ctx.getChildCount() == 3 and
          isinstance(ctx.getChild(0), Python3Parser.ExprContext) and
          isinstance(ctx.getChild(2), Python3Parser.ExprContext)):
        # expr op expr is BinOp expression
        binop_node = gen_ast_binop(listener, ctx)
        #listener.pyast_trees[ctx] = binop_node
        ctx.pyast_tree = binop_node
        return
    elif isinstance(ctx.getChild(0), antlr4.tree.Tree.TerminalNodeImpl):
        # UnaryOp expression, i.e.,
        # for grammar expr ('*'|'@'|'/'|'%'|'//') expr
        unaryop_node = gen_ast_unaryop(listener, ctx)
        #listener.pyast_trees[ctx] = unaryop_node
        ctx.pyast_tree = unaryop_node
        return
    else:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Expr node at the moment, count is " +
                                  str(ctx.getChildCount()))

# Convert exprlist to Python AST node or list
def convert_exprlist(listener, ctx:Python3Parser.ExprlistContext):
    '''
    Convert exprlist to Python AST node or list
    Rule: exprlist: (expr|star_expr) (',' (expr|star_expr))* ','?;
    '''

    # if ctx.getChildCount() == 1:
    #     # just one expr, copy the child's tree node
    #     ctx.pyast_tree = ctx.children[0].pyast_tree
    # else:
    #     # more than one child, make a list
    expr_list = []
    for i in range(ctx.getChildCount()):
        if not isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl):
            # sometimes ';' is also included in the children
            expr_list.append(ctx.children[i].pyast_tree)

    ctx.pyast_tree = expr_list

    return

# Generate an ast.Expr node from expr_stmt, when it is not an assignment.
def gen_ast_expr_from_expr_stmt(ctx:Python3Parser.Expr_stmtContext):
  '''
  Generate an ast.Expr node from expr_stmt, when it is not an assignment.
  This function is only for rule: expr_stmt : testlist_star_expr
  Returns the generated ast.Expr node.
  '''
  # should have only one child, with type of Testlist_star_expr
  child = ctx.children[0]

  ast_node = ast.Expr(tools.list_to_node_or_tuple(child.pyast_tree,
                                                  is_load=True))

  return ast_node


# Generate an ast.Assign node from expr_stmt, when it is a simple assignment.
def gen_ast_assign_from_expr_stmt(ctx:Python3Parser.Expr_stmtContext):
  '''
  Generate an ast.Assign node from expr_stmt, when it is a simple assignment.
  This function is only for rule:
  expr_stmt : testlist_star_expr ('=' testlist_star_expr)+
  Returns the generated ast.Assign node.
  '''

  # generate the targets
  targets = []

  # process the statement for targets
  for i in range(0, ctx.getChildCount()-1, 2):
    node = tools.list_to_node_or_tuple(ctx.children[i].pyast_tree,
                                       is_load=False)
    targets.append(node)

  # generate the value from the last child
  value = tools.list_to_node_or_tuple(ctx.children[-1].pyast_tree, is_load=True)

  ast_node = ast.Assign(targets, value)

  return ast_node

# Convert expr_stmt to Python AST node
def convert_expr_stmt(listener, ctx:Python3Parser.Expr_stmtContext):
  '''
  Convert expr_stmt to Python AST node, could be ast.Expr or ast.Assign
  for now.
  rule:  expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
                    ('=' (yield_expr|testlist_star_expr))*);
  Only handles two cases now:
  expr_stmt : testlist_star_expr, convert to ast.Expr
  expr_stmt : testlist_star_expr '=' testlist_star_expr, convert to ast.Assign
  '''

  #print_ast_tree(ctx)

  if ctx.getChildCount() == 1:
    # for rule, expr_stmt : testlist_star_expr
    node = gen_ast_expr_from_expr_stmt(ctx)
    ctx.pyast_tree = node
  elif (ctx.getChildCount() >= 3 and
        isinstance(ctx.children[0], Python3Parser.Testlist_star_exprContext) and
        isinstance(ctx.children[1], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[1].getSymbol().type == Python3Lexer.ASSIGN and
        isinstance(ctx.children[2], Python3Parser.Testlist_star_exprContext)):
    # for rule, expr_stmt : testlist_star_expr ('=' testlist_star_expr)+
    node = gen_ast_assign_from_expr_stmt(ctx)
    ctx.pyast_tree = node
  else:
    raise NotImplementedError("Other rules not implemented for epxr_stmt")

  return

# Convert testlist_star_expr to a list of Python AST nodes
def convert_testlist_star_expr(listener,
                               ctx:Python3Parser.Testlist_star_exprContext):
    '''
    Convert testlist_star_expr to a list of Python AST nodes
    Rule: testlist_star_expr: (test|star_expr) (',' (test|star_expr))* ','?;
    Always return a list, with Python AST nodes for test or star_expr as the
    items.
    '''

    expr_list = []

    for child in ctx.children:
      if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
        continue # skip ','

      expr_list.append(child.pyast_tree)

    ctx.pyast_tree = expr_list

    return

# Convert star_expr to ast.Starred
def convert_star_expr(listener, ctx:Python3Parser.Star_exprContext):
    '''
    Convert star_expr to ast.Starred.
    Rule: star_expr: '*' expr;
    '''

    # should have two children
    ast_node = ast.Starred(ctx.children[1].pyast_tree, ast.Load())

    ctx.pyast_tree = ast_node

    return
