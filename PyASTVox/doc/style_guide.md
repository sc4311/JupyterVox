# General Notes
1. Each node has a jvox\_speech field after the speech generation routine. The
   jvox_speech is a dictionary with speeches for different styles. There should
   always be a "default" style. 
2. Jvox\_speech should also have a "selected\_style" to help the parent nodes to
   know which speech to use if not sure. If user selected a style,
   "selected\_style" will be using that style. Otherwise, "default" is copied to
   "selected\_style."  This "selected\_style" is automatically selected by the
   set\_selected\_style\_speech\_for\_node function afer the speech is generated
   for each node (i.e., after gen_ast_XXX function is called)
   
# Per Node Style Guide
## ast.Constant
1. default:
   1. For int, Just use the string, i.e., str(), of the constant as the speech
   2. For string, process it to handle certain punctuation marks and special
      characters, then add "string" before the actual string
		1. "," is replaced with "comma" so it will be read out
## ast.Name
1. default: the id of the variable (ast.Name node)
2. Since "a/A"  is always read as the artical "a" than the letter "a/A" in gTTs,
   the speech of variable "a/A" is generated as "a-/A-".
## ast.Add
1. default: "plus"
2. indirect: "the sum of"
## ast.Mult
1. default: "multiply"
2. indirect: "the product of"
## ast.Sub
1. default: "minus"
2. indirect: "the difference of"
## ast.Div
1. default: "divide"
## ast.Mod
1. default: "modulo"
## ast.FloorDiv
1. default: "floor divide"
## ast.MatMult
1. default: "matrix multiply"
## ast.Pow
1. default: "to the power of"
## ast.LShift
1. default: "left shift by"
## ast.RShift
1. default: "right shift by"
## ast.BitOr
1. default: "bit-wise or"
## ast.BitXor
1. default: "bit-wise xor"
## ast.BitAnd
1. default: "bit-wise and"
## ast.USub
1. default: "negative"
## ast.Not
1. default: "not"
2. indirect: "the negation of"
## ast.UAdd
1. default: "positive"
2. succinct: "" (not speech)
## ast.Invert
1. default: "invert"
2. indirect: "the inversion of"
## ast.BinOp
1. default: "left op.direct right", 
    1. e.g., "a+b*c", a plus b multiply c
    2. e.g., "(a+b)*c", a plus b, then multiply c
2. indirect: "the sum/product/difference... of left and right"
    1. e.g., "a+b*c", the sum of a and the sum of b and c
    2. e.g., "(a+b)*c", the product of the sum of a and b, and c
3. alternate: alternating default and indirect styles for each level of expressions
    1. e.g., "a+b*c", a plus the product of b and c
    2. e.g., "(a+b)*c", the sum of a plus b, then multiply c
    3. jvox_data is used to hold if the speech is direct or indirect
    4. lowest level is indirect
4. semantic\_oriented: This style reads the expression based on the semantic
   order (i.e., operation precedence), instead of the text order. There is a
   still a problem reading complex expression with multiple complex
   subexpressions, e.g., (a+b)*(a-b)
    1. e.g., "a+b*c", b multiply c, then plus a
    2. e.g., "(a+b)*c", a plus b, then multiply c
5. alternatev2: Use direct/default for unit-typed right operand, use indirect for non-unit-typed right operand
    1. e.g., "a+b*c", a- plus the product of b and c
    2. e.g., "(a+b)*c", a- plus b, then multiply c
## ast.UnaryOp
1. default: "op.default left.default right.default"
    1. -3.14: negative 3.14
    2. +3.14: positive 3.14
    3. not a: not a
    4. ^ a: invert a
## ast.List
1. default: "a list with items of ..."
    1. e.g., [1, 2, a]: a list with items of 1, 2, a
## ast.Dict
1. default: "a dictionary with items of, item 1 has key of ... and value of ...,
   item 2..."
    1. e.g., {"key1":1, "key2":3}: a dictionary with items of, item 1 has key of
   a string of key1 and value of 1, and item 2 has key of a string of key2 and
   value 3
## ast.Subscript
1. default: 
    1. a[1]: a's item with index 1
    2. a[i, "new"]:  a's items with indices i and new
2. reversed:
    1. a[1]: list item index 1 of list a
    2. a[i, "new"]: list items with indices i and string new of list a
## ast.Return
1. default: 
    1. if there is value: "return, " + the selected-style speech for the value node
    2. if there is not value: "return"
## ast.Continue
1. default: "continue"
## ast.Break
1. default: "break"
## ast.Pass
1. default: "pass"
## ast.And
1. default: "and"
2. indirect: "the logical "and" of"
## ast.Or
1. default: "or"
2. indirect: "the logical "or" of"
## ast.Eq
1. default: "equal to"
## ast.NotEq
1. default: "not equal to"
## ast.Gt
1. default: "greater than"
## ast.GtE
1. default: "greater than or equal to"
## ast.Is
1. default: "the same as"
## ast.IsNot
1. default: "is not"
## ast.In
1. default: "is in"
## ast.NotIn
1. default: "is not in"
## ast.BoolOp
1. default: bascially read the expression as it is
    1. e.g., a or b or c: a or b, then or c
    2. e.g., a or b and c: a or b and c
    3. e.g., a and b or c, a and b, then or c
2. indirect: use indirect readings for And and Or operators
    1. e.g., a or b or c: the logical or of a-, b and c
    2. e.g., a or b and c: the logical or of a- "and" b and c
    3. e.g., a and b or c, a and b, then or c
2. alternatev2: use direct/default for unit-typed right operand, use indirect for non-unit-typed right operand
    1. e.g., a or b or c: a- "or" b, then "or" 
    2. e.g., a or b and c: a- "or" , the logical "and" of b and c
    3. e.g., a and b or c, a- "and" b, then "or" c
## ast.Compare
1. default:
    1. e.g., a>12, a- greater than 12
    2. e.g., a>(12\*b), a- greater than 12 multiply b
    3. e.g., a>(12\*b)+(c\*5), a- greater than 12 multiply b, then plus c multiply 5
## ast.Assign
1. default: left hand + "equals" + selected-style reading for right hand
    1. e.g., a = b * c: a equals b multiply c
    2. e.g., a = b = b * c: a equals b equals b multiply c
2. indirect: left hand + "is assigned with value" + selected-style reading for right hand
    1. e.g., a = b * c: a is assigned with value, b multiply c
    2. e.g., a = b = b * c: a and b are assigned with value, b multiply c
## ast.FromImport
1. default: Reads "from" + module name +  "import" + package names. If level is not 0, then level will also be read out after the module name.
    1. e.g., from a.x import b, c: "from a dot x import b, c"
    2. e.g., from ..a import b, c: "from a (relative level 2) import b"
    3. e.g., form .. import x: "form directory (relative level 2) import x"
## ast.Import
1. default:  Reads "import", then follows with package names
    1. e.g., import a.c: import a dot c
    2. e.g., import numpy as np: import numpy as np
## ast.alias
1. default: Reads the package name. If there is as name, also reads "as" + the asname. "." is replaced as "dot". Examples:
    1. numpy: "numpy"
    2. numpy as np: "numpy as np"
    3. package1.a as pa: "package1 dot a as pa"
## ast.keyword
1. default: For normal keyword arg, read "key" arg "equals" value. For double stared arg, read "double-starred" arg. E.g.,
    1. b = c: "key b equals c"
    2. **b : "double starred b"
## ast.Starred
1. default: Simply read "starred" + variable name. E.g.,
    1. *args: "starred args"
## ast.Call
1. default: Read "call" funcation_name "with" arguments. E.g.,
    1. func1(): call func1 with no arguments
    2. func1(a): "call func1 with argument, a-"
    3. func1(b=c): "call func1 with argument, key b equals c"
    4. func1(a, *m, b=c, **x): call func1 with argument, key b equals c
## ast.arg:
1. default: Read arg "with annotation" annotation "of type". Note that I am not sure how to get AST to generate type_comment. E.g.,
    1. a: int: "a with annotation int"
    2. a: "a"
## ast.Arguments:
1. default: Read arguments one by one. E.g.,
    1. (a: 'annotation', m: str,  b=1, c=2, *d, e, f=3, **g): "with arguments, a- with annotation "string" annotation, m with annotation str, b with default value 1, c with default value 2, starred d, e, f with default value 3, and doubled-starred g"
    2. (): with no arguments
## ast.FunctionDef:
1. Read: "Define function" + func_name + "with arguments" + args + "The function body is" + body E.g.,
    1. def f(a: 'annotation', m: str,  b=1, c=2, *d, e, f=3, **g): a+b; return y: Define function f with arguments, a- with annotation "string" annotation, m with annotation str, b with default value 1, c with default value 2, starred d, e, f with default value 3, and doubled-starred g. The function body is. a- plus b. return, y."
    2. def f(): return; : "Define function f with no arguments. The function body is. return." 
2. Note that we dont support decorator_list, returns, type_cooment, type_params yet.

