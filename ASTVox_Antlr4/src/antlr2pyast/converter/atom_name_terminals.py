# ANTLR4 to Python AST
# Conversion functions for the ATOM* rules, NAME rules and terminals

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser
from antlr_parser.Python3ParserListener import Python3ParserListener

# PyAST package
import ast

# sibling packages
from . import tools

# convert a NUMBER to ast.Constant
def gen_ast_num_constant(ctx:antlr4.tree.Tree.TerminalNodeImpl):
    # extract the value, a bit hacky
    try:
        value = int(ctx.getText())
    except ValueError:
        value = float(ctx.getText())

    # generate the AST node
    ast_node = ast.Constant(value)

    return ast_node

# It seems ANTLR4 will pass on the string with the quote marks, I will
# remove them here. However, there may be other preprocessing need, 
# hence the separate function
def atom_string_processing(text:str):
  if text[0] == '\"':
    return text.lstrip('\"').rstrip('\"')
  elif text[0] == '\'':
    return text.lstrip('\'').rstrip('\'')
  else:
    return text # should not reach here

# convert a list of strings (STRING+) to one string ast.Constant node
# note that, the strings will also be saved into a list and add to the
# ast.Constant node. The name of the string is "original_string"
def convert_atom_strings(listener, ctx:Python3Parser.AtomContext):
  
  combined_string=""
  original_strings=[]

  for child in ctx.children:
    # check if child is STRING
    if not (isinstance(child, antlr4.tree.Tree.TerminalNodeImpl) and
          child.getSymbol().type == Python3Lexer.STRING):
      raise ValueError("")

    # combine and insert the strings.
    combined_string += atom_string_processing(child.getText())
    original_strings.append(child.getText())

  ast_node = ast.Constant(value = combined_string)
  ast_node.original_strings = original_strings

  return ast_node

# convert atom to ast.List or ast.ListComp
def convert_atom_list_listcomp(listener, ctx:Python3Parser.AtomContext):
    '''
    convert atom to ast.List or ast.ListComp
        
    rule: atom: '[' testlist_comp? ']'
    testlist_comp has two potential values, a list of items or a dict for
    list comprehension
    case1: list of items => ast.List()
    case2: list comprehension => ast.LisComp()
    case3: nothing => return empty list
    '''
    if ctx.getChildCount() == 2:
        # empty list
        ctx.pyast_tree = ast.List([], ast.Load())
    elif type(ctx.children[1].pyast_tree) is list:
        # creating list with items
        # returns an ast.List node
        ctx.pyast_tree = ast.List(ctx.children[1].pyast_tree, ast.Load())
    else:
        # creating list with comprehensions
        # returns an ast.LitComp node
        ctx.pyast_tree = ast.ListComp(ctx.children[1].pyast_tree["elt"],
                                      ctx.children[1].pyast_tree["generators"])

    return

# convert atom that has a parenthesis-ed statement
def convert_atom_paren_stmt(listener, ctx:Python3Parser.AtomContext):
    '''
    convert atom that has a parenthesis-ed statement
    Rule: atom: '(' (yield_expr|testlist_comp)? ')'
    handles the testlist_comp, yield_expr unimplemented yet
    Three cases:
    case 1: testlist_comp is a list => return a simple node if testlist_comp
            has only one item, otherwise returns a tuple
    case 2: testlist_comp is a dict => return a ast.GeneratorExp
    case 3: yield_expr: unhandled
    case 4: nothing: a tuple with empty list
    '''

    if isinstance(ctx.children[0], Python3Parser.Yield_exprContext):
        raise NotImplementedError("yield_expr not handled in atom")

    if ctx.getChildCount() == 2:
        # empty list
        ctx.pyast_tree = ast.Tuple([], ast.Load())
    elif type(ctx.children[1].pyast_tree) is list:
        # testlist_comp is a list => return a simple node if testlist_comp
        # has only one item, otherwise returns a tuple
        ctx.pyast_tree = tools.list_to_node_or_tuple(ctx.children[1].pyast_tree,
                                                     is_load=True)
    else:
        # testlist_comp is a dict => return a ast.GeneratorExp
        ctx.pyast_tree = ast.GeneratorExp(ctx.children[1].pyast_tree["elt"],
                                      ctx.children[1].pyast_tree["generators"])

    return
        
# convert an atom node from Anltr4 tree to Python AST tree
def convert_atom(listener, ctx:Python3Parser.AtomContext):
    # should have more than one child and the type of the first child
    # can help determine what rule it is and what to do
    first_child = ctx.children[0]

    # process based on rules/first_child
    if isinstance(first_child, Python3Parser.NameContext):
        # rule 1: atom: name
        # child is a name node, just copy the child's AST tree
        ctx.pyast_tree = first_child.pyast_tree
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.NUMBER):
        # rule 2: atom: NUMBER
        # child a is NUMER type, convert it to ast.Constant
        ctx.pyast_tree = gen_ast_num_constant(first_child)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.STRING):
        # rule 3: atom: STRING+
        # child a is String type, convert it to list of strings
        ctx.pyast_tree = convert_atom_strings(listener, ctx)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.TRUE):
        # rule 4: atom: "True"
        # child a is True, convert it to ast.Constant
        # implement here => ast.Constant
        ctx.pyast_tree = ast.Constant(True)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.FALSE):
        # rule 4: atom: "False"
        # child a is False, convert it to ast.Constant
        # implement here => ast.Constant
        ctx.pyast_tree = ast.Constant(False)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.OPEN_PAREN):
        # rule 5: atom: '(' (testlist_comp)? ')'
        # handles the testlist_comp, yield_expr unimplemented yet
        # return a simple node if testlist_comp has only one item,
        # otherwise returns a tuple
        convert_atom_paren_stmt(listener, ctx)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.OPEN_BRACK):
        # rule 6: atom: '[' testlist_comp? ']'
        # testlist_comp has two potential values, a list of items or
        # a dict for list comprehension
        convert_atom_list_listcomp(listener, ctx)
    elif (isinstance(first_child, antlr4.tree.Tree.TerminalNodeImpl) and
          first_child.getSymbol().type == Python3Lexer.OPEN_BRACE):
        # rule 7: atom: '{' dictorsetmaker? '}'
        if ctx.getChildCount() == 2:
            # if dictorsetmaker does not exit, return empty dict
            ctx.pyast_tree = ast.Dict([], [])
        else:
            # dictorsetmaker exists, return child's pyast_tree
            ctx.pyast_tree = ctx.children[1].pyast_tree
    else:
        raise NotImplementedError("Other rules not implemented for " +
                                  "Atom node at the moment")
    return

# convert an name node from Anltr4 tree to Python AST tree
def convert_name(listener, ctx:Python3Parser.NameContext):
    # should have only one child
    if ctx.getChildCount() != 1:
        raise ValueError("Name node has more than one child, count is" +
                         str(ctx.getChildCount()))

    # child should be terminal
    child = ctx.children[0]
    if not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
        raise TypeError("Child of Name node is not a terminal type.")

    # generate the Python AST tree node
    # name : NAME | '_' | 'match' ; not sure what to do with '_'
    # and 'match'
    id = child.getText()
    # potential error: not sure how to determine if the operation is
    # store or del.
    ast_node = ast.Name(id, ast.Load())

    # save the node/tree
    # listener.pyast_trees[ctx] = ast_node
    ctx.pyast_tree = ast_node

    return

# Grammar: atom_expr: AWAIT? atom trailer*;
def convert_atom_expr(listener, ctx:Python3Parser.Atom_exprContext):
    '''
    Convert atom_expr to ast.Await, or ast.Call, or pass on child's node
    '''
    # should have no more than 3 child
    if ctx.getChildCount() > 3:
        raise ValueError("Atom_expr node has more than three children, " +
                         "count is " + str(ctx.getChildCount()))

    # only handles one the case with one child now
    if ctx.getChildCount() != 1:
        raise NotImplementedError("More than one child is not supported for " +
                                  "Atom_expr node at the moment")

    # copy child's AST node
    child = ctx.children[0]
    #listener.pyast_trees[ctx] = listener.pyast_trees[child]
    ctx.pyast_tree = child.pyast_tree
    return

# convert dictorsetmaker to a dict of keys and values for making a dictionary
def gen_dict_keys_values(ctx:Python3Parser.DictorsetmakerContext):
    '''
    Convert dictorsetmaker to a dict of keys and values for dictionary
    construction.
    Rule: dictorsetmaker: ( ((test ':' test | '**' expr)
                   (comp_for | (',' (test ':' test | '**' expr))* ','?))
    Comp_for is not handles at the moment.
    Returns {"keys":[...], "values":[...]} for dict construction
    '''

    keys = []
    values = []

    # process each part of the comma-separated dict list to get keys and values
    i = 0
    while i < ctx.getChildCount():
        if isinstance(ctx.children[i], Python3Parser.TestContext):
            # this dict item is test ':' test
            keys.append(ctx.children[i].pyast_tree)
            values.append(ctx.children[i+2].pyast_tree)
            i += 4 # advance to next dict item, skip 4, including ','
        elif (isinstance(ctx.children[i],
                         antlr4.tree.Tree.TerminalNodeImpl) and
              ctx.children[i].getSymbol().type == Python3Lexer.POWER):
            # this dict item is "**" expr
            keys.append(None)
            values.append(ctx.children[i+1].pyast_tree)
            i += 3 # advance to next dict item, skip 3, including ','
        else:
            raise ValueError("Unknown dictionary item type for Dictorsetmaker" +
                             " node is type " +
                             ctx.children[i].__class__.__name__ )

    # create the ast.Dict node
    ast_node = ast.Dict(keys, values)
    
    return ast_node

# convert dictorsetmaker to a dict of keys and values for making a set
def gen_set_values(ctx:Python3Parser.DictorsetmakerContext):
    '''
    Convert dictorsetmaker to a dict of keys and values for making a set
    Rule: dictorsetmaker: (
                  ((test | star_expr)
                   (comp_for | (',' (test | star_expr))* ','?)) );
    Comp_for is not handles at the moment.
    Returns {"keys":None, "values":[...]} for set construction
    '''
    elts = []

    for child in ctx.children:
        if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
            continue # skip ','

        elts.append(child.pyast_tree)

    # create the ast.Set node
    ast_node = ast.Set(elts)
    
    return ast_node

# convert dictorsetmaker to a dict of keys and values for dictionary or set
def convert_dictorsetmaker(listener, ctx:Python3Parser.DictorsetmakerContext):
    '''
    Convert dictorsetmaker to a dict of keys and values
    Rule: dictorsetmaker: ( ((test ':' test | '**' expr)
                   (comp_for | (',' (test ':' test | '**' expr))* ','?)) |
                  ((test | star_expr)
                   (comp_for | (',' (test | star_expr))* ','?)) );
    This rule allows for set construction, where there are not keys;
    or allows for dict construction, where there are keys;
    or dict/set comprehension, where there are comp_for.

    Four cases;
    1. dict construction:
       dictorsetmaker: 
       (test ':' test | '**' expr)  (',' (test ':' test | '**' expr))* ','?)
    2. set construction:
       dictorsetmaker: 
       (test | star_expr) (',' (test | star_expr))* ','?
    3. dict comprehension:
       dictorsetmaker: 
       (test ':' test | '**' expr)  comp_for
    4. set comprehension:
       dictorsetmaker: 
       (test ':' test | '**' expr)  comp_for
    
    Conversion results:
    case 1: ast.Dict
    case 2: ast.Set
    case 3: ast.DictComp
    case 4: ast.SetComp

    Note, this, "{**x for x in numbers}", is valid for Antlr4 grammar,
    not PyAST grammar
    '''

    if (ctx.getChildCount() == 4 and
        isinstance(ctx.children[-1], Python3Parser.Comp_forContext)):
        # case 3, making a dict comprehension, create an ast.DictComp node
        key = ctx.children[0].pyast_tree
        value = ctx.children[2].pyast_tree
        generators = ctx.children[3].pyast_tree["comprehensions"]
        ctx.pyast_tree = ast.DictComp(key, value, generators)
        
    elif (ctx.getChildCount() == 2 and
        isinstance(ctx.children[-1], Python3Parser.Comp_forContext)):
        # case 4,  making a set comprehension, create an ast.SetComp node
        elt = ctx.children[0].pyast_tree
        generators = ctx.children[1].pyast_tree["comprehensions"]
        ctx.pyast_tree = ast.SetComp(elt, generators)
        
    elif (ctx.getChildCount() > 2 and
          isinstance(ctx.children[1], antlr4.tree.Tree.TerminalNodeImpl) and
          ctx.children[1].getText() == ':'):
        # case 1, making a dictionary, starting with test:test
        ctx.pyast_tree = gen_dict_keys_values(ctx)
        
    elif (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
          ctx.children[0].getSymbol().type == Python3Lexer.POWER):
        # case 1, making a dictionary, starting with **expr
        ctx.pyast_tree = gen_dict_keys_values(ctx)
        
    else:
        # case 2, making a set
        ctx.pyast_tree = gen_set_values(ctx)

# 
def exitTrailer(self, ctx:Python3Parser.TrailerContext):
    raise NotImplementedError("Working in progress")
    
        
        
