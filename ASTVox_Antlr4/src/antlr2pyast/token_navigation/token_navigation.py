'''
Class for navigating through the tokens within a statement. 
'''

# antlr4 packages
import antlr4
from antlr_parser.Python3Lexer import Python3Lexer
from antlr_parser.Python3Parser import Python3Parser



# tokenize a statement (i.e., lexical analysis)
def tokenize(stmt: str):
    '''
    Tokenize a statement through lexical analysis.

    Input parameter:
    1. stmt: the statement to tokenize

    Return value:
    The list of tokens (list of Antlr4 CommonToken-typed items)
    '''

    input_stream = antlr4.InputStream(stmt)
    lexer = Python3Lexer(input_stream)

    tokens = lexer.getAllTokens()

    return tokens

# print tokens for debugging
def print_tokens(tokens: list):
    for t in tokens:
        print(t)

    return

# find the current token index
def current_token_index(tokens: list, cur_pos: int):
    '''
    Determine the index of current token within a list of tokens given the
    current cursor position

    Input parameters:
    1. tokens: a list of tokens (CommonToken type)
    2. cur_pos: current (cursor) position

    Return value:
    The list index of current token. If the cur_pos is wrong, then return None.
    '''

    for i in range(len(tokens)):
        t = tokens[i]
        if (t.start <= cur_pos) and (cur_pos <= t.stop):
            return i

    return None

# determine the start position (col) of next token
def next_token(stmt: str, cur_pos: int, verbose: bool):
    '''
    Determine the position (col) of next token given a statement and
    the current token (where the current position is at).

    Input parameters:
    1. stmt: the statement
    2. cur_pos: the current (cursor) position (col).
    3. verbose: verbose output

    Return value:
    a dictionary: {"next_token": start of next token}.
    If current token is the last, then returns -1
    '''

    if verbose:
        print(f"find next token in {stmt} from current position {cur_pos}")

    # tokenize the stmt
    tokens = tokenize(stmt)
    if verbose:
        print("Tokens are:")
        print_tokens(tokens)

    # get the current token position
    cur_idx = current_token_index(tokens, cur_pos)
    if verbose:
        print(f"Current token is {tokens[cur_idx]} (index {cur_idx})")

    # find the start of next token
    if cur_idx == len(tokens)-1:
        # no next token, current token is the last, return -1
        ret_val = {"next_start": -1,
                   "next_stop": -1,
                   "next_text": "",
                   "next_type": -1}
    else:
        # there is a next token
        # there is a next token
        ret_val = {"next_start": tokens[cur_idx+1].start,
                   "next_stop": tokens[cur_idx+1].start,
                   "next_text": tokens[cur_idx+1].text,
                   "next_type": tokens[cur_idx+1].type}
    
    if verbose:
        print(f"Next token start is at {ret_val} (-1 means no next token).")

    return ret_val
    
# determine the start position (col) of the previous token
def previous_token(stmt: str, cur_pos: int, verbose: bool):
    '''
    Determine the position (col) of next token given a statement and
    the current token (where the current position is at).

    Input parameters:
    1. stmt: the statement
    2. cur_pos: the current (cursor) position (col).
    3. verbose: verbose output

    Return value:
    a dictionary: {"previous_token": start of next token}.
    If current token is the first, then returns -1
    '''

    if verbose:
        print(f"find the previous token in {stmt} from current position "
              f"{cur_pos}")

    # tokenize the stmt
    tokens = tokenize(stmt)
    if verbose:
        print("Tokens are:")
        print_tokens(tokens)

    # get the current token position
    cur_idx = current_token_index(tokens, cur_pos)
    if verbose:
        print(f"Current token is {tokens[cur_idx]} (index {cur_idx})")

    # find the start of the previous token
    if cur_idx == 0:
        # no previous token, current token is the first, return -1
        ret_val = {"pre_start": -1,
                   "pre_stop": -1,
                   "pre_text": "",
                   "pre_type": -1}
    else:
        # there is a next token
        ret_val = {"pre_start": tokens[cur_idx-1].start,
                   "pre_stop": tokens[cur_idx-1].start,
                   "pre_text": tokens[cur_idx-1].text,
                   "pre_type": tokens[cur_idx-1].type}
    
    if verbose:
        print(f"Previous token start is at {ret_val} (-1 means no previous "
              "token).")

    return ret_val

# determine the start and stop position (col) of current token
def current_token_start_stop(stmt: str, cur_pos: int, verbose: bool):
    '''
    Determine the start and stop (end) position (col) of the current token (i.e,
    the token where the cursor is at).

    Input parameters:
    1. stmt: the statement
    2. cur_pos: the current (cursor) position (col).
    3. verbose: verbose output

    Return value:
    a dictionary: {"start": start of the token, "stop": stop of the token,
    "text": text of the token}.
    '''

    if verbose:
        print(f"find the start/stop of the current token in {stmt} at current "
              f"position {cur_pos}")

    # tokenize the stmt
    tokens = tokenize(stmt)
    if verbose:
        print("Tokens are:")
        print_tokens(tokens)

    # get the current token position
    cur_idx = current_token_index(tokens, cur_pos)
    if verbose:
        print(f"Current token is {tokens[cur_idx]} (index {cur_idx})")

    # find the start and stop
    ret_val = {"start": tokens[cur_idx].start,
               "stop": tokens[cur_idx].start,
               "text": tokens[cur_idx].text,
               "type": tokens[cur_idx].type}
    if verbose:
        print(f"Current token start and stop are {ret_val}")

    return ret_val    
