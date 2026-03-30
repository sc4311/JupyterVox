#
# classes to add JVox custom AI magics
# Adapted from https://github.com/jupyter-ai-contrib/jupyter-ai-magic-commands/tree/main
#

import base64
import json
import os
import re
import sys
import warnings
from typing import Any, Optional
import io
import tokenize

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import HTML, JSON, Markdown, Math

import logging

#from .jvox_ai_backend import jvox_gemini_interface as ai_interface
from jupytervox.commons.ai_backend import get_ai_interface

#from jvox_server_commons import jvox_logging
from jupytervox.commons import jvox_logging

from .jvox_ai_settings_comm import get_ai_client, get_api_key

@magics_class
class JVoxAiMagics(Magics):

    def __init__(self, shell):
        super().__init__(shell) 

    @cell_magic
    def jvoxAI(self, line: str, cell: str) -> Any:
        """
        Defines "%%jvoxAI" cell magic.

        Currently only support generating a new code cell.

        It will take the whole cell input as prompts, and use an AI to gnerate 
        a new cell of code. 
        """
        logger = jvox_logging("ipython", log_to_stderr=False)
        
        logger.debug(f"cell text: {cell}")

        self.run_ai_cell(cell)
        #self.run_ai_cell_with_added_error(cell)

    def run_ai_cell(self, cell_text):
        logger = jvox_logging("ipython", log_to_stderr=False)

        # generate the prompt to send to AI
        # prompt = self.prepare_prompt_with_error(cell_text)
        prompt = self.prepare_prompt(cell_text)

        logger.debug(f"prompt is: {prompt}")

        ai_interface = get_ai_interface(get_ai_client())
        response = ai_interface.generate(prompt, api_key=get_api_key())

        logger.debug(f"response is: {response}")

        self.shell.set_next_input(response, replace=False)
        return HTML("AI generated code inserted below &#11015;&#65039;")

    def prepare_prompt(self, cell_text):

        prefix = "Write Python code for:"

        postfix = "Provide raw code only. No explanations, no preamble, and no markdown backticks."

        prompt = f"{prefix}, {cell_text}. {postfix}"

        return prompt

    def prepare_prompt_with_error(self, cell_text):

        prefix = "Write Python code for:"

        postfix = """Intentionally include one subtle logic or runtime error commonly found in AI-generated code. 
        Provide raw code only. No explanations, no preamble, and no markdown backticks."""

        prompt = f"{prefix}, {cell_text}. {postfix}"

        return prompt

    def prepare_conversation_with_error(self, cell_text):
        prefix = "Write Python code for:"

        postfix = """Intentionally include one subtle syntax or logic error commonly found in AI-generated code. 
        Provide raw code only. No comments, no explanations, no preamble, and no markdown backticks."""

        prompt1 = f"{prefix}, {cell_text}. {postfix}"

        prompt2 = "Please explain the error you hav added."

        prompts = [prompt1, prompt2]

        return prompts

    def run_ai_cell_with_added_error(self, cell_text):
        logger = jvox_logging("ipython", log_to_stderr=False)

        prompts = self.prepare_conversation_with_error(cell_text)
        logger.debug(f"Prompts to send: {prompts}")

        responses = ai_interface.converse(prompts)

        logger.debug(f"responses are: {responses}")

        self.shell.set_next_input(responses[0], replace=False)
        
        return HTML("AI generated code inserted below &#11015;&#65039;")

    def _remove_comments_from_line(line):
        # Strip inline comments, but not hashes in string literals
        result = ''
        prev_toktype = tokenize.INDENT
        last_col = 0
        sio = io.StringIO(line)
        try:
            for tok in tokenize.generate_tokens(sio.readline):
                token_type = tok.type
                token_string = tok.string
                start_col = tok.start[1]

                if token_type == tokenize.COMMENT:
                    # If first token is comment, skip whole line
                    if start_col == 0:
                        return ''
                    # Else, discard the comment but keep code before
                    else:
                        break
                elif token_type != tokenize.NL and token_type != tokenize.ENDMARKER:
                    result += token_string
                last_col = tok.end[1]
        except tokenize.TokenError:
            # Return the line as is if it cannot be tokenized
            return line
        return result.rstrip()

    def remove_comments(self, python_code):
        """
        Remove all comments from Python code (both full-line and trailing comments).
        Preserves code and strings with '#' in them.
        """
        output_lines = []
        sio = io.StringIO(python_code)
        try:
            for tok in tokenize.generate_tokens(sio.readline):
                if tok.type == tokenize.COMMENT:
                    continue
                elif tok.type == tokenize.NL or tok.type == tokenize.ENDMARKER:
                    output_lines.append('\n')
                else:
                    output_lines.append(tok.string)
        except tokenize.TokenError:
            # As fallback, use linewise filter
            lines = python_code.splitlines()
            cleaned = [_remove_comments_from_line(line) for line in lines]
            return '\n'.join(cleaned)
        # Reconstruct source from tokens (avoiding formatting issues)
        cleaned_code = ''.join(output_lines)
        # Remove potentially introduced blank lines
        cleaned_lines = [line.rstrip() for line in cleaned_code.splitlines()]
        return '\n'.join(line for line in cleaned_lines if line.strip())

