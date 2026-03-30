#!/usr/bin/python3

# system packages
import traceback
import types
import io

# packages for AST parsing
import ast
# packages for Text2Speech and audio manipulation
from gtts import gTTS

# import sibling directories
import sys
from pathlib import Path

# from jupytervox.jupytervox import screenreader

# generate the path to JVox packages
# BASE_DIR = Path(__file__).resolve().parent
# sys.path.append(f"{BASE_DIR}/../../pyastvox/")
# sys.path.append(f"{BASE_DIR}/../../../ASTVox_Antlr4/src/antlr2pyast/")

# load the Vox parser utilities
from ..screenreader import utils

# import JVox speech generator
from ..screenreader import jvox_screenreader

# import token/lexeme navigation packages
from ..parser.token_navigation import token_navigation
from ..parser.token_navigation import lexeme_navigation as lex_nav

# import single line parsing checking packages
from ..parser.debug_support import single_line_check as one_chk
from ..parser.debug_support import code_snippet_check as snippet_chk
from ..parser.debug_support.runtime_error_support import entry_point as rt_support

# import chunked reading packages
from ..parser.statement_chunking import statement_chunking as stmt_chunk

# from ..commons.ai_backend import gemini_interface as ai_interface
# from ..commons.ai_backend import llama_cpp_interface as ai_interface
from ..commons.ai_backend import get_ai_interface
#from jvox_server_commons import jvox_llama_cpp_interface as ai_interface

class jvox_interface:
    vox_gen = None;
    jvox = None;
    style = "default";

    # constructor    
    def __init__(self, style="default"):
        self.jvox =  jvox_screenreader()

    # generate the speech for one statement
    def gen_speech_for_one(self, stmt, verbose):
        speech = self.jvox.generate_for_one(stmt, verbose)

        return speech

    # generate the mp3 file
    def gen_mp3_from_speech(self, speech, file_name):
        tts = gTTS(speech, slow=False)
        tts.save(file_name)
        print("jvox created mp3 file at", file_name)

        return

    # generate the audio MP3 bytes from Google TTS
    def gen_mp3_bytes_from_speech_gtts(self, speech):
        # Generate speech using gTTS
        tts = gTTS(text=speech, lang='en')
        
        # Save to a bytes buffer instead of a file
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        
        # Seek to the beginning of the buffer to read it
        mp3_fp.seek(0)
        mp3_bytes = mp3_fp.read()

        return mp3_bytes

    # find next token
    def find_next_token_start(self, stmt, cur_pos, verbose):
        next_token = token_navigation.next_token(stmt, cur_pos, verbose)

        return {"start":next_token['next_start'],
                "stop":next_token['next_stop']}

    # find previous token
    def find_previous_token_start(self, stmt, cur_pos, verbose):
        previous_token = token_navigation.previous_token(stmt, cur_pos, verbose)

        return {"start":previous_token['pre_start'],
                "stop":previous_token['pre_stop']}

    # find current token start stop
    def find_cur_token_start_stop(self, stmt, cur_pos, verbose):
        cur_token = token_navigation.current_token_start_stop(stmt, cur_pos,
                                                               verbose)

        return {"start":cur_token['start'], "stop":cur_token['stop']}

    # find current lexeme or token
    def find_cur_lexeme_token(self, stmt, cur_pos, verbose):
        cur_token = lex_nav.find_lexeme_token_at_pos(stmt, cur_pos,
                                                     verbose)
        return {"start":cur_token['start'], "stop":cur_token['stop']}
    
    # find next lexeme or token
    def find_next_lexeme_token(self, stmt, cur_pos, verbose):
        next_token = lex_nav.find_next_lexeme_token(stmt, cur_pos,
                                            verbose)
        return {"start":next_token['start'], "stop":next_token['stop']}

    # find next lexeme or token
    def find_prev_lexeme_token(self, stmt, cur_pos, verbose):
        prev_token = lex_nav.find_prev_lexeme_token(stmt, cur_pos,
                                                    verbose)
        return {"start":prev_token['start'], "stop":prev_token['stop']}

    # check if a single statement is correct or not
    def single_line_parsing_check(self, stmt, verbose):
        # add a new line to the statement to suppress the "i want newline or ;"
        # parsing error for ANTLR4
        stmt += '\n'
        check_result = one_chk.single_line_syntax_check(stmt, verbose)

        # generate the speech to be returned to the user
        ret_val = types.SimpleNamespace()
        if check_result.error_no == 0:
            ret_val.msg = check_result.error_msg
            ret_val.offset = 1
        elif check_result.error_no == 1:
            ret_val.msg = check_result.error_msg
            ret_val.offset = 1
        elif check_result.error_no == 2:
            ret_val.msg = "Syntax error: " + check_result.error_msg
            ret_val.offset = check_result.offset
        elif check_result.error_no == 3:
            ret_val.msg = "Other parsing error: " + check_result.error_msg
            ret_val.offset = 1

        return ret_val

    # check the syntax of a code snippet
    # returns the error message, line number, and column number
    def code_snippet_parsing_check(self, stmts, verbose):
        # check the statements
        check_ret = snippet_chk.code_snippet_syntax_check(stmts, verbose)

        # create the return object
        ret_val = types.SimpleNamespace()
        ret_val.msg = check_ret.error_msg
        ret_val.line_no = check_ret.line_no
        ret_val.offset = check_ret.offset
        ret_val.error_no = check_ret.error_no

        return ret_val

    # debugging support for runtime errors
    def handle_runtime_error(self, error_msg, code, line_no, support_type,
                             extra_data, verbose):
        # pass data on to runtime error handler
        return rt_support.handle_runtime_error(error_msg, code, line_no,
                                               support_type, extra_data,
                                               verbose)

    # break a statement into chunks
    # command should be "next", "pre", "current"
    # I think chunk navigation should be merged with token navigation
    def chunkify_statement(self, stmt, cur_pos, command, chunk_len, verbose):
        # whether to read the space after or inside a chunk.
        # this is not for leading spaces/indentation, indentation will be read
        read_space = False
        
        # prepare return value
        ret_val = types.SimpleNamespace()
        ret_val.error_message = ""
        ret_val.chunk_to_read = ""
        ret_val.chunk_string = ""

        # check if current line is empty
        if stmt.lstrip() == '':
            # empty line
            ret_val.chunks = []
            ret_val.new_pos = 0
            ret_val.error_message = "Empty line."
            return ret_val

        # check if at the end of a line
        # need this when at the end of comment line
        if len(stmt) == cur_pos and command != "pre":
            # empty line
            ret_val.chunks = []
            ret_val.new_pos = cur_pos
            ret_val.error_message = "end of statement"
            return ret_val

        # check if current line is comment
        if stmt.lstrip().startswith('#'):
            # comment line
            ret_val.chunks = []
            ret_val.new_pos = len(stmt)
            ret_val.error_message = stmt.replace('#', 'hashtag, ')
            return ret_val

        # check if the line from cur_pos is comment
        if stmt[cur_pos:].lstrip().startswith('#'):
            # comment line
            ret_val.chunks = []
            ret_val.new_pos = len(stmt)
            ret_val.error_message = stmt[cur_pos:].replace('#', 'hashtag ')
            return ret_val

        # check if command is correct
        if (command != "next" and command != "pre" and
            command != "current" and command != "read_then_next"):
            ret_val.chunks = []
            ret_val.new_pos = 0
            ret_val.error_message = ("invalid command, " +
                                     "likely incorrect implementation")
            return ret_Val

        # handle indentation and white spaces
        # extract lead white space, if any
        lead_white_spaces = stmt[:len(stmt)-len(stmt.lstrip())]
        # remove white spaces
        stmt = stmt.lstrip()
        
        # break the statement into chunks and return the chunks
        # Note I set cur_pos to 0 to chuck the whole statement
        try:
            chunks = stmt_chunk.chunk_statement(stmt, cur_pos=0,
                                                chunk_len=chunk_len,
                                                verbose=verbose)
            print("Chunkify results", chunks)
        except Exception as e:
            print("Chunkify failed with exception:", e)
            print("Fallback to tokenization")
            # tokenization
            tokens = token_navigation.tokenize(stmt)
            # convert tokens to a list of strings
            chunks = []
            for token in tokens:
                chunks.append(token.text)

        # add leading white spaces back if any
        if len(lead_white_spaces) != 0:
            chunks.insert(0, lead_white_spaces)

        # find the current chuck given the cur_pos
        cur_chunk_idx = 0
        searched_chunks_len = 0
        for cur_chunk in chunks:
            searched_chunks_len += len(cur_chunk)
            if searched_chunks_len > cur_pos:
                break
            cur_chunk_idx += 1

        if verbose:
            print(f"find current chunk idx: {cur_chunk_idx}")

        # if searched_chunks_len <= cur_pos:
        #     # cur_pos is at or beyond the end of the statement,
        #     # return "end of statement"
        #     ret_val.chunks = chunks
        #     ret_val.new_pos = len(stmt) 
        #     ret_val.chunk_to_read = "end of statement"
        #     return ret_val

        # find the chunk-to-return based on the command
        if command == "next":
            ret_chunk_idx = cur_chunk_idx + 1
        elif command == "pre":
            ret_chunk_idx = cur_chunk_idx - 1
        elif command == "current":
            ret_chunk_idx = cur_chunk_idx
        elif command == "read_then_next":
            ret_chunk_idx = cur_chunk_idx

        # handle the corner cases for chunk-to return
        if ret_chunk_idx >= len(chunks):
            # chunk-to-return is beyond the end of the statement
            ret_val.chunks = chunks
            ret_val.new_pos = len(stmt)
            ret_val.error_message = "end of statement"
            ret_val.chunk_to_read = ""
            ret_val.chunk_string = ""
            return ret_val
        elif ret_chunk_idx < 0:
            # chunk-to-return is beyond the beginning of the statement
            ret_val.chunks = chunks
            ret_val.new_pos = 0
            ret_val.error_message = "beginning of statement"
            ret_val.chunk_to_read = ""
            ret_val.chunk_string = ""
            return ret_val

        # handle the common case, where chunk-to-return is in the middle of
        # the statement
        ret_val.chunks = chunks
        ret_val.error_message = ""
        ret_val.new_pos = 0
        for i in range(0, ret_chunk_idx):
            ret_val.new_pos += len(chunks[i])

        if command == "read_then_next":
            # in the case of command "read then jump to next", we need to
            # move the cursor behind current chunk as well
            ret_val.new_pos += len(chunks[ret_chunk_idx])

        # if current chunk is leading indentation (white spaces)
        # read the white spaces count
        if len(chunks[ret_chunk_idx].lstrip()) == 0:
            ret_val.chunk_to_read = f'{len(chunks[ret_chunk_idx])} white spaces.'
            ret_val.chunk_string = chunks[ret_chunk_idx]
            return ret_val

        # current chunk is 
        # make statement readable, we need help from tokenization
        # to generate the reading for each token correctly
        chunk_string = chunks[ret_chunk_idx]
        tokens = token_navigation.tokenize(chunk_string)
        if verbose:
            print("Tokens of chunk are:",)    
            for t in tokens:
                print(t)
                
        # convert the statement chunk into a list of tokens and spaces
        chunk_items = []
        str_idx = 0
        token_idx = 0
        while (str_idx < len(chunk_string)):
            # if current character is space
            if chunk_string[str_idx] == ' ' :
                chunk_items.append(chunk_string[str_idx])
                str_idx += 1
                continue
            
            # if current character is the start of a token
            if str_idx == tokens[token_idx].start:
                chunk_items.append(tokens[token_idx].text)
                str_idx = tokens[token_idx].stop + 1
                token_idx += 1
                continue

        # replace chunk items with readable strings
        for i in range(len(chunk_items)):
            chunk_items[i] = utils.make_token_readable(chunk_items[i],
                                                       read_space)

        if verbose:
            print("Tokens and spaces of chunk are:")
            print(chunk_items)

        # return the reading and original string of the chunk    
        ret_val.chunk_to_read = ', '.join(chunk_items)
        ret_val.chunk_string = chunk_string

        return ret_val

    # --------------------------------------------------------------
    # ai_explain_code: Use an AI model to explain a Python statement
    #
    # Args:
    #   statement (str): The Python code statement to be explained.
    #
    # Returns:
    #   str: A succinct, beginner-friendly explanation of the code statement,
    #        generated by an AI text model. The explanation does not repeat
    #        the statement and attempts to clearly describe its meaning.
    #
    # Description:
    #   This function takes in a Python code statement as a string and sends
    #   a prompt to an AI backend (via ai_interface), requesting a one-sentence,
    #   succinct, human-understandable explanation. It is intended to help
    #   beginner programmers understand the meaning of code, including
    #   variable names, without echoing the original code back to the user.
    # --------------------------------------------------------------
    def ai_explain_code(self, statement, ai_client=None, api_key=None):
        print(f"Explaining statement with AI: {statement}")

        prompt = f"""please explain the literal meaning of the following Python 
        statement in one short sentence for beginners, please do not repeat the 
        statement, please be succinct. Make sure you read variable names. 
        Statement is: {statement}"""

        ai_interface = get_ai_interface(ai_client)
        response = ai_interface.generate(prompt, api_key=api_key)
        if isinstance(response, str):
            response = response.replace('`', '"')

        print(f"AI Explanation Response: {response}")

        return response

    def ai_explain_nested_code(self, statement, ai_client=None, api_key=None):
        print(f"Explaining nested statement with AI: {statement}")

        prompt = f"""please explain the nested operations of the following Python 
        statement for beginners in one or two sentences. Please be concise.
        Input code: {statement}"""

        ai_interface = get_ai_interface(ai_client)
        response = ai_interface.generate(prompt, api_key=api_key)
        if isinstance(response, str):
            response = response.replace('`', '"')
        print(f"AI Explanation Response: {response}")

        return response
