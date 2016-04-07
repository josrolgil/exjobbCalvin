# -*- coding: utf-8 -*-

# Copyright (c) 2015 Ericsson AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ply.lex as lex

keywords = {'component': 'COMPONENT', 'define': 'DEFINE'}

tokens = [
    'IDENTIFIER', 'STRING', 'NUMBER',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACK', 'RBRACK',
    'DOT', 'COMMA', 'COLON',
    'GT', 'EQ',
    'RARROW',
    'DOCSTRING',
    'FALSE', 'TRUE', 'NULL'

] + list(keywords.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_DOT = r'\.'
t_COMMA = r','
t_COLON = r':'
t_GT = r'>'
t_EQ = r'='
t_RARROW = r'->'
# t_FALSE = r'false'
# t_TRUE = r'true'
# t_NULL = r'null'


def t_COMMENT(t):
    # FIXME: // is deprecated as line-comment
    r'(/\*(.|\n)*?\*/)|(//.*)|(\#.*)'
    t.lexer.lineno += t.value.count('\n')


def t_DOCSTRING(t):
    r'"""(.|\n)*?"""'
    t.lexer.lineno += t.value.count('\n')
    t.value = t.value.strip('"')
    t.value = t.value.strip(' \n\t')
    return t

# FIXME: Strings need a better definition
def t_STRING(t):
    r'!?".*?"'
    is_raw = False
    if t.value.startswith('!'):
        # Keep as raw string
        is_raw = True
        t.value = t.value[1:]
    # Remove the double quotes
    t.value = t.value.strip('"')
    if not is_raw:
        t.value = t.value.decode('string_escape')
    return t


def t_NUMBER(t):
    r'-?\d+(?:\.\d*)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_TRUE(t):
    r'true'
    return t

def t_FALSE(t):
    r'false'
    return t

def t_NULL(t):
    r'null'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t

# Track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.zerocol = t.lexpos

t_ignore = ' \t'

# Error handling rule


def t_error(t):
    # Error output format: "<Informative text> (line:<line>, col:<col>)"
    # e.g. "Expected token of type '=', found ')' (line:1, col:10)"
    raise Exception("Illegal character '%s' (line:%d, col:%d)" %
                    (t.value[0], t.lexer.lineno, t.lexpos - t.lexer.zerocol))
