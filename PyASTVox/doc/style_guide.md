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
