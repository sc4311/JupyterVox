# this file covers the translation of the non-terminals/terminals that
# are simple and do not need separate source files

#antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser

#PyAST package
import ast

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
        # copy the child's tree and create a simple object list,
        # since the body has to be a list
        body = [child.pyast_tree]

    # create an ast.Module node to hotd the statements
    # not sure what "type_ignores" is, ignoring "type_ignores"
    ast_node = ast.Module(body, type_ignores=[])
    #listener.pyast_trees[ctx] = ast_node
    ctx.pyast_tree = ast_node
    
    return

# Convert block to its own Python AST tree
def convert_block(listener, ctx:Python3Parser.BlockContext):
    '''
    Convert block to its own Python AST tree. I simply copy the Python AST tree
    form the child simple_stmts or stmt+
    rules: block: simple_stmts | NEWLINE INDENT stmt+ DEDENT;
    '''
    # if not child, return an None node tree
    # This should only happen when we are parsing on the first line of
    # a compound statment, e.g., the "for ..." line of a for loop
    if ctx.getChildCount() == 0:
        # this branch is for line such as "for i in j:"
        ctx.pyast_tree = None
        return
    elif (ctx.getChildCount() == 1 and
          isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
          ctx.children[0].getSymbol().type == Python3Lexer.NEWLINE):
        # this branch is for line such as "for i in j:\n"
        ctx.pyast_tree = None
        return

    # check which rule we are handling to determine what to do
    if isinstance(ctx.children[0], Python3Parser.Simple_stmtsContext):
        # rule 1: block: simple_stmts
        ctx.pyast_tree = ctx.children[0].pyast_tree
    elif (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
          isinstance(ctx.children[1], antlr4.tree.Tree.TerminalNodeImpl)):
        # rule 2: block: NEWLINE INDENT stmt+ DEDENT;
        # the tree is a list
        stmt_list = []
        for i in range(2,ctx.getChildCount()):
            if not isinstance(ctx.children[i],
                              antlr4.tree.Tree.TerminalNodeImpl):
                # sometimes ';' is also included in the children
                if type(ctx.children[i].pyast_tree) is list:
                    # when a stmt is derived from simple_stmts, it may be a
                    # list itself
                    stmt_list = stmt_list + ctx.children[i].pyast_tree
                else:
                    stmt_list.append(ctx.children[i].pyast_tree)

        ctx.pyast_tree = stmt_list
    else:
        raise ValueError("unknown \"block\" node, " +
                         "do not have NEWLINE and INDENT?\n")

    return

# Convert compound_stmt to child's Python AST tree, i.e., just copy child
def convert_compound_stmt(self, ctx:Python3Parser.Compound_stmtContext):
    '''
    Convert compound_stmt to child's Python AST tree, i.e., just copy child
    Rule: compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated | async_stmt | match_stmt;
    '''

    # just copy the child's tree
    ctx.pyast_tree = ctx.children[0].pyast_tree
    
    return

# convert stmt to corresponding Python AST node
def convert_stmt(listener, ctx:Python3Parser.StmtContext):
  '''
  Convert stmt to corresponding Python AST node
  rule: stmt: simple_stmts | compound_stmt;
  Just copy the child's pyast_tree
  '''
  ctx.pyast_tree = ctx.children[0].pyast_tree

  return

# convert dotted_as_name to an ast.alias node
def convert_dotted_as_name(self, ctx:Python3Parser.Dotted_as_nameContext):
    '''
    Convert dotted_as_name to a Python ast.alias node
    rule: dotted_as_name: dotted_name ('as' name)?;

    Generates an ast.alias node, with fields,
     name <= dotted_name.getText()
     asname <= name.getText()

    Note that I am not going to have a separate conversion function for
    dotted_name since its getText() already returns what we need.
    '''

    # get the dotted name text
    ast_node = ast. alias(ctx.children[0].getText(), None)

    # if there is "as name", update the asname with the "as name" text
    if ctx.getChildCount() == 3:
        # there is "as"
        ast_node.asname = ctx.children[2].getText()

    ctx.pyast_tree = ast_node

    return 

# convert dotted_as_names to a list of ast.alias nodes
def convert_dotted_as_names(self, ctx:Python3Parser.Dotted_as_namesContext):
    '''
    Convert dotted_as_names to a list of ast.alias nodes
    rule: dotted_as_names: dotted_as_name (',' dotted_as_name)*;

    Generates a list of ast.alias nodes, where an ast.alias corresponds to
    a dotted_as_name
    '''

    aliases = []
    for child in ctx.children:
        if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
            continue # skip coma ","

        aliases.append(child.pyast_tree)

    ctx.pyast_tree = aliases

    return

# convert import_name to a Python ast.Import node
def convert_import_name(self, ctx:Python3Parser.Import_nameContext):
    '''
    Convert import_name to a Python ast.Import node
    Rule: import_name: 'import' dotted_as_names;

    Generate an ast.Import node with fields,
    names = dotted_as_names.pyast_tree (it is a list)
    '''

    ctx.pyast_tree = ast.Import(ctx.children[1].pyast_tree)

    return

# Convert import_stmt to an ast.Import node or as.ImportFrom node
def convert_import_stmt(self, ctx:Python3Parser.Import_stmtContext):
    '''
    Convert import_stmt to an ast.Import node or as.ImportFrom node
    Rule: import_stmt: import_name | import_from;

    Pass on child's pyast_tree
    '''

    ctx.pyast_tree = ctx.children[0].pyast_tree

    return

# Convert import_as_name to an ast.alias node
def convert_import_as_name(self, ctx:Python3Parser.Import_as_nameContext):
    '''
    Convert import_as_name to an ast.alias node
    rule: import_as_name: name ('as' name)?;

    Generates an ast.alias node, with fields,
     name <= first name.getText()
     asname <= 2nd name.getText()
    '''

    # get the dotted name text
    ast_node = ast. alias(ctx.children[0].getText(), None)

    # if there is "as name", update the asname with the "as name" text
    if ctx.getChildCount() == 3:
        # there is "as"
        ast_node.asname = ctx.children[2].getText()

    ctx.pyast_tree = ast_node

    return

# Convert import_as_names to a list of ast.alias nodes
def convert_import_as_names(self, ctx:Python3Parser.Import_as_namesContext):
    '''
    Convert import_as_names to a list of ast.alias nodes
    rule: import_as_names: import_as_name (',' import_as_name)* ','?;

    Generates a list with the pyast_tree of each import_as_name as the item.
    Each item should be an ast.alias node
    '''

    aliases = []
    for child in ctx.children:
        if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
            continue # skip coma ","

        aliases.append(child.pyast_tree)

    ctx.pyast_tree = aliases

    return

# Convert import_from to an ast.ImportFrom node
def convert_import_from(self, ctx:Python3Parser.Import_fromContext):
    '''
    Convert import_from to an ast.ImportFrom node
    Rule: import_from: ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
              'import' ('*' | '(' import_as_names ')' | import_as_names));

    This is another complex rule. But it basic has two parts
    "from .* dotted_name"
    and
    "import * | import_as_names"

    Generates an ast.ImportFrom node with fields
    level <= the number of dots ('.')
    module <= dotted_name.getText()
    names <= import_as_names.pyast_tree (a list) or [ast.alias(name="*")]
    '''

    # process the first part from .* dotted_name
    # process the dots to get the relative directory level
    level = 0
    i = 1 # i points the next child to process. Starting at 1 to skip "import"
    # loop if current child is '.' or '...'
    while (isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
           (ctx.children[i].getText() == '.' or
            ctx.children[i].getText() == '...')): 
        if ctx.children[i].getText() == '.':
            level += 1
        else: # "..." three dots
            level += 3

        i += 1 # go to next child

    # process the dotted_name
    if isinstance(ctx.children[i], Python3Parser.Dotted_nameContext):
        # has dotted_name
        module = ctx.children[i].getText()
        i += 1 # go to next child
    else:
        # does not have dotted_name, module is None
        module = None
    
    # process the "import ..." statement
    if (not (isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
            ctx.children[i].getText() == "import")):
        raise ValueError("Expecting keyword import in import_from")
    i += 1 # go to next child

    # three cases
    if (isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[i].getText() == '*'):
        # case 1: import *
        ast_node = ast.alias("*", None)
        names = [ast_node]
    elif (isinstance(ctx.children[i], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[i].getText() == '('):
        # case 2: import '(' import_as_names ')'
        i += 1 # goto the import_as_names child
        names = ctx.children[i].pyast_tree
    elif isinstance(ctx.children[i], Python3Parser.Import_as_namesContext):
        # case 3: import import_as_names
        names = ctx.children[i].pyast_tree
    else:
        raise ValueError("Unknown import type in import_from, node is" +
                         str(ctx.children[i]))

    # create the ast.ImportFrom node
    ast_node = ast.ImportFrom(module, names, level)
    ctx.pyast_tree = ast_node

    return 
    
    
          
          
    
        
