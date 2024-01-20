# set module search path
import os
ast2pyast_path = os.path.abspath('../antlr2pyast/')
import sys
sys.path.append(ast2pyast_path)

# system packages
import argparse
import re
import traceback

# AST tree generation/conversion packages
from token_navigation import token_navigation
import ast

####### print and compare each test case
# get test case file name
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--statement', help='a single statement to test',
                    dest='stmt')
parser.add_argument('-v', '--verbose', action='store_true',
                    dest='verbose', help='enable verbose output' )
parser.add_argument('-p', '--cur-pos', help='current cursor position',
                    dest='cur_pos')
parser.add_argument('-c', '--command',
                    help=("token navigation command: \n" +
                          "\t next: start of next token;\n" +
                          "\t pre: start of previous;\n" +
                          "\t cur: start/stop of current token;\n"), 
                    dest='command')
args = parser.parse_args()

if (args.stmt is None):
    parser.print_help("Missing parameter: statement")
if (args.command is None):
    parser.print_help("Missing parameter: token navigation command")
if (args.cur_pos is None):
    parser.print_help("Missing parameter: current cursor position")

try:
    cur_pos = int(args.cur_pos)
except:
    parser.print_help("Parameter -p/-cur-pos must be an integer")
    exit(1)

if args.command == "next":
    # find the start of next token
    next_token = token_navigation.next_token(args.stmt, cur_pos,
                                             args.verbose)
    print("Next token is", next_token)
elif args.command == "pre":
    # find the start of previous token
    prev_token = token_navigation.previous_token(args.stmt, cur_pos,
                                                 args.verbose)
    print("Previous token is", prev_token)
elif args.command == "cur":
    # find the start and end of current token
    cur_token = token_navigation.current_token_start_stop(args.stmt,
                                                          cur_pos,
                                                          args.verbose)
    print("Current token is", cur_token)
else:
    parser.print_help(f"Unknown command: args.command")
    

    
