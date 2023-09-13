# 1. Terminal Tokens
## 1.1 NUMBER
1. Integer string => ast.Constant(value:int)
2. Float string => ast.Constant(value:float)

# 2. Non-terminal Tokens
## 2.1 name
### 2.1.1 name: NAME
1. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
### 2.1.2 name: '_'
1. Not sure if this is right
2. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
### 2.1.2 name: 'match'
1. Not sure if this is right
2. NameContext.pyast_tree <= ast.Name(id = NameContext.children[0].getText(), 
                                      ast.Load())
## 2.2 atom
### 2.2.1 atom: name
1. AtomContext.pyast_tree <= AtomContext.children[0].pyast_tree (copy child)
### 2.2.2 atom: NUMBER
1. AtomContext.pyast_tree <= ast.Constant(AtomContext.children[0]), see 1.1 NUMBER
### 2.2.3 atom:STRING+
1. AtomContext.pyast_tree <= ast.Constant
    1. value <= concatenated string tokens
    2. A separate list "original_strings" is also added to the ast.Constant node with individual strings in STRING+
    3. String is processes to remove leading and trailing " and '
### 2.2.3 atom:"True" | "False"
1. AtomContext.pyast_tree <= ast.Constant
    1. value <= True or False, based on the actual statement text
### 2.2.x Other not implemented yet

## 2.3 atom_expr
### 2.3.1 atom_expr: AWAIT? atom trailer*
1. atom_expr.pyast_tree <= atom_expr.children[0].pyast_tree (copy child)
2. basically rule: atom_expr: atom
3. AWAIT? and trailer* not handled yet

## 2.4 expr
### 2.4.1 expr; atom_expr
1. exprContext.pyast_tree <= exprContext.children[0].pyast_tree (copy child)
### 2.4.2 expr: expr binaryOp expr
1. ExprContext.pyast_tree <= ast.BinOp(left expr, ast.Add/ast.Mult etc., right expr)
2. Covers
> Expr:   | expr '**' expr <br/>
>    | expr ('*'|'@'|'/'|'%'|'//') expr <br/>
>    | expr ('+'|'-') expr <br/>
>    | expr ('<<' | '>>') expr <br/>
>    | expr '&' expr <br/>
>    | expr '^' expr <br/>
>    | expr '|' expr <br/>
### 2.4.3 expr: ('+'|'-'|'~')+ expr, i.e., UnaryOp 
1. ExprContext.pyast_tree <= ast.UnaryOp(ast.UAdd/USub/Invert*, right epxr)
2. \* means nested tree

## 2.5 expr_stmt:
### 2.5.1 expr_stmt: testlist_star_expr
1. Epxr_stmtContext.pyast_tree <= ast.Expr(Epxr_stmtContext.children[0].pyast_tree)
### 2.5.x Other parts of the rule not handled
Full rule:<br/>
expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) |
                     ('=' (yield_expr|testlist_star_expr))*);

## 2.6 simple_stmts
### 2.6.1 simple_stmts: simple_stmt (';' simple_stmt)* ';'? NEWLINE;
1. Simple_stmtsContext.pyast_tree = [Simple_stmtsContext.children[*].pyast_tree]
2. The tree is a list containing the trees of all simple_stmt children 
3. ';' and NEWLINE are omitted from the list

## 2.7 single_input
### 2.7.1 single_input: NEWLINE
1. single_inputContext.pyast_tree <= ast.Module(body=[]) (empty list for body)
### 2.7.2 single_input: simple_stmts
1. single_inputContext.pyast_tree <= ast.Module(body=single_inputContext.Children[0].pyast_tree)
### 2.7.3 single_input: compound_stmt NEWLINE;
1. Not handled yet

## 2.8 flow_stmt
### 2.8.1 flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt;
1. Flow_stmtContext.pyast_tree <= Flow_stmtContext.children[0].pyast_tree (child copy)
2. Flow_stmt is just a intermediate non-terminal

## 2.9 return_stmt
### 2.9.1 return_stmt: 'return' testlist?;
1. Return_stmtContext.pyast_tree <= ast.Return
2. for ast.Return.value
    1. if no return value, value <= None
    2. if return on value, value <= Return_stmtContext.children[1]
    3. if return a list of values, value <= ast.Tuple
         1. ast.Tuple.elts <= Return_stmtContext.children[1]
         2. basically copy testlist's pyast_tree, which is a list

## 2.10 testlist
### 2.10.1 testlist: test (',' test)* ','?;
1. If there is just one child
    1.  TestlistContext.pyast_tree <= TestlistContext.children[0].pyast_tree (copy_child)
2. If there are more than one child
    1. TestlistContext.pyast_tree <= [] (just a list)
    2. the pyast_tree of each child of testlistContext is an item in the list

