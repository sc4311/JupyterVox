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
  # remove the first and last " or '
  # text = text[1:-1]
    
  # using eval the string to remove special characters, including the beginning
  # and ending " and '
  text = eval(text)

  return text

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

# generate ast.Call, ast.Subscript, ast.Attribute based on the trailer type
def gen_node_based_on_trailer(node:ast.AST, trailer:dict):
    '''
    generate ast.Call, ast.Subscript, ast.Attribute based on the trailer type
    '''

    if trailer["type"] == "arglist":
        # function call, create ast.Call
        func = node 
        # process the arguments, put to normal args and keyword args
        args = []
        keywords = []
        for n in trailer["values"]:
            if isinstance(n, ast.keyword):
                keywords.append(n)
            elif isinstance(n, ast.Starred):
                args.append(n)
            elif isinstance(n, ast.GeneratorExp):
                args.append(n)
            else: # all other nodes
                args.append(n)
        # create the ast.Call node
        ast_node = ast.Call(func, args, keywords)
    elif trailer["type"] == "field":
        # field attribute access, create an ast.Attribute node
        value = node
        attr = trailer["values"][0].id
        ast_node = ast.Attribute(value, attr, ast.Load())
    elif trailer["type"] == "subscriptionlist":
        # subscriptionlist for list/dict access, create an ast.Subscript 
        value = node
        slice_field = tools.list_to_node_or_tuple(trailer["values"],
                                                  is_load = True,
                                                  update_children = True)
        ast_node = ast.Subscript(value, slice_field, ast.Load())
    else:
        raise NotImplementedError("Other type of trailer not implemented yet")

    return ast_node

# Grammar: atom_expr: AWAIT? atom trailer*;
def convert_atom_expr(listener, ctx:Python3Parser.Atom_exprContext):
    '''
    Convert atom_expr to corresponding Python AST node
    Rule: atom_expr: AWAIT? atom trailer*;

    Possible base cases based on trailer and AWAIT:
    1. atom_expr: AWAIT ... => ast.Await
    2. atom_expr: atom => pass on child node
    3. atom_expr: atom '(' arglist ')' => ast.Call
    4. atom_expr: atom '[' subscriptionlist ']' => ast.Subscript
    5. atom_expr: atom '.' name => ast.Attribute

    This has to be recursively processed.
    AWAIT is at the topest level.
    First atom trailer at the *lowest* level.
    Then the rest trailer gradually increase from the lowest level.
    E.g., atom trailer1 trailer2 trailer3 has the ast node for trailer3 at
    the top level, trailer2 at the 2nd level, atom trailer1 at the
    lowest level
    '''

    # This has to be recursively processed.
    # AWAIT is at the topest level
    # first atom trailer at the *lowest* level
    # then the rest trailer gradually increase from the lowest level
    # e.g., atom trailer1 trailer2 trailer3 has the ast node for trailer3 at
    # the top level, trailer2 at the 2nd level, atom trailer1 at the
    # lowest level

    # get the index i for accessing the nodes
    if (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == 'await'):
        i = 1 # skip the AWAIT
    else:
        i = 0 # no AWAIT

    # build the lowest level of AST node
    if isinstance(ctx.children[-1], Python3Parser.AtomContext):
        # there is no trailer in this atom_expr
        # children[i] should also be the last child
        ast_node = ctx.children[i].pyast_tree
        i += 1 # advance the index, skip atom, should be no more child after
    else:
        # there is at least one trailer
        ast_node = gen_node_based_on_trailer(ctx.children[i].pyast_tree,
                                             ctx.children[i+1].pyast_tree)
        
        i += 2 # advance the index, skip atom trailer, may be more children

    # recursively build higher level of AST nodes if there are more trailers
    current_top_node = ast_node
    while i < ctx.getChildCount():
        current_top_node = gen_node_based_on_trailer(current_top_node,
                                             ctx.children[i].pyast_tree)

        i += 1

    # create ast.Await node if there is AWAIT
    if (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == 'await'):
        current_top_node = ast.Await(current_top_node)

    ctx.pyast_tree = current_top_node
    
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

# convert trailer to a dict with type (arglist, sublist, field) and
# a list of values
def convert_trailer(listener, ctx:Python3Parser.TrailerContext):
    '''
    Convert trailer to a dict with type (arglist, sublist, field) and
    a list of values
    Rule:
    1. trailer: '(' arglist? ')'
       convert to dict {"type":"arglist", "values": arglist}
    2. trailer: '[' subscriptlist ']'
       convert to dict {"type":"subscriptlist", "values": subscriptlist}
    3. trailer: '.' name
       convert to dict {"type":"field", "values": [name]}
    
    '''

    if (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == '('):
        # case 1, arglist
        if ctx.getChildCount() == 2:
            # just "()"
            args = []
        else:
            # is "( arglist )"
            args = ctx.children[1].pyast_tree
        ctx.pyast_tree = {"type":"arglist",
                          "values": args}
    elif (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == '['):
        # case 2, subscriptionlist
        ctx.pyast_tree = {"type":"subscriptionlist",
                          "values": ctx.children[1].pyast_tree}
    elif (isinstance(ctx.children[0], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[0].getText() == '.'):
        # case 3, field access
        ctx.pyast_tree = {"type":"field",
                          "values": [ctx.children[1].pyast_tree]}
    else:
        raise ValueError("Unknown trailer composition\n")

    return
    
# convert_sliceop to ast.Node
def convert_sliceop(self, ctx:Python3Parser.SliceopContext):
    '''
    convert_sliceop to ast.Node
    Rule: sliceop: ':' test?;

    This is the step in the subscript slice (i.e., lower:upper:step)
    If there is test, pass on its pyast_tree
    If there is no test, pass on None
    '''

    if ctx.getChildCount() == 1:
        # no test
        ctx.pyast_tree = None
    else:
        # has test
        ctx.pyast_tree = ctx.children[1].pyast_tree

    return
    

# convert subscript_ to a ast.Slice or pass one child node
def convert_subscript_(self, ctx:Python3Parser.Subscript_Context):
    '''
    convert subscript_ to a ast.Slice or pass one child node
    Rules:
    case 1. subscript_: test, pass on child's pyast_tree
    case 2. subscript_: test ':' test sliceop;, convert to ast.Slice
                        Note that, except for ':' all other fields can be
                        missing. The fields correspond to lower:upper:step
    '''

    if (ctx.getChildCount() == 1 and
        isinstance(ctx.children[0], Python3Parser.TestContext)):
        # case 1. subscript_: test, pass on child's pyast_tree
        ctx.pyast_tree = ctx.children[0].pyast_tree
    else:
        # case 2. subscript_: test? ':' test? sliceop?;, convert to ast.Slice

        # find the lower bound
        if isinstance(ctx.children[0], Python3Parser.TestContext):
            # there is lower bound
            lower = ctx.children[0].pyast_tree
            upper_at = 2 # upper bound at children[2]
        else:
            # there is no lower bound
            lower = None
            upper_at = 1 # upper bound at children[1]

        # find the upper bound
        if upper_at >= ctx.getChildCount():
            # there is no upper bound
            upper = None
        elif isinstance(ctx.children[upper_at], Python3Parser.TestContext):
            # there is upper bound
            upper = ctx.children[upper_at].pyast_tree
        else:
            # there is no upper bound, but step
            upper = None
            

        # find the step
        if isinstance(ctx.children[-1], Python3Parser.SliceopContext):
            # has sliceop node
            step = ctx.children[-1].pyast_tree
        else:
            # no sliceop node
            step = None

        # create the ast.Slice node
        ctx.pyast_tree = ast.Slice(lower, upper, step)

    return

# convert subscriptlist to a list
def convert_subscriptlist(self, ctx:Python3Parser.SubscriptlistContext):
    '''
    convert subscriptlist to a list of substript_ pyast_trees
    Rule: subscriptlist: subscript_ (',' subscript_)* ','?;
    '''

    sublist = []

    for child in ctx.children:
        if isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
            continue # skip ','
        
        sublist.append(child.pyast_tree)

    # for the corner case subscriptlist: subscript_ ',', i.e.,
    # just one item follow by ','. We need to convert this subscriptlist
    # to ast.Tuple instead of a single node. I am adding a None item to
    # the list so that the function tools.list_to_node_or_tuple knows
    # to generate a tuple.
    if (isinstance(ctx.children[-1], antlr4.tree.Tree.TerminalNodeImpl) and
        ctx.children[-1].getText() == ','):
        sublist.append(None)

    ctx.pyast_tree = sublist

    return
        
        
