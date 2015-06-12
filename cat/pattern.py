#!/usr/bin/env python
# coding: utf-8

import re
from enum import Enum
from collections import namedtuple

__all__ = ['lex', 'parse']

Token = namedtuple('Token', ['type', 'match'])


class TokenEnum(Enum):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)


class DefaultContextToken(TokenEnum):
    LBRACE = r'{'
    OTHER = '.'


class RegexDefinitionContextToken(TokenEnum):
    RBRACE = r'}'
    IDENT = r'[A-Za-z_]\w*(?=:)'
    COLON = ':'


class RegexContextToken(TokenEnum):
    LBRACE, RBRACE = r'{', r'}'
    REGEXCHAR = '.'


class State(Enum):
    """
    The state of the lexer
    """

    def __init__(self, token_set):
        self.token_set = token_set

    DEFAULT = DefaultContextToken            # Outside braces
    REGEX_DEF = RegexDefinitionContextToken  # Between opening brace and colon
    REGEX = RegexContextToken                # Between colon and closing brace


def lex(s):
    """
    Chop a given string into tokens to match a semi regular
    expression pattern
    """

    tokens = []
    braces_opened = 0
    regex_def_tokens = 0
    state = State.DEFAULT

    while s:
        if state == State.DEFAULT:
            for t in state.token_set:
                m = t.pattern.match(s)

                if m is not None:
                    s = s[m.end():]

                    if t == state.token_set.LBRACE:
                        state = State.REGEX_DEF
                        break

                    token = Token(t, m)
                    tokens.append(token)
                    break

        elif state == State.REGEX_DEF:
            regex_def_tokens += 1

            for t in state.token_set:
                m = t.pattern.match(s)

                if m is not None:
                    s = s[m.end():]

                    if t == state.token_set.COLON:
                        state = State.REGEX
                        regex_def_tokens = 0

                    token = Token(t, m)
                    tokens.append(token)
                    break

        elif state == State.REGEX:
            for t in state.token_set:
                m = t.pattern.match(s)

                if m is not None:
                    # Pop out the matched string
                    s = s[m.end():]

                    if t == state.token_set.LBRACE:
                        braces_opened += 1
                        t = RegexContextToken.REGEXCHAR

                    elif t == state.token_set.RBRACE:
                        if not braces_opened:
                            state = State.DEFAULT
                            break
                        else:
                            braces_opened -= 1
                            t = RegexContextToken.REGEXCHAR

                    token = Token(t, m)
                    tokens.append(token)
                    break

    if state != State.DEFAULT:
        raise SyntaxError("Unbalanced braces")

    return tokens


def parse(s):
    """
    Transform a simple string into a regular expression
    """

    tokens = lex(s)
    pattern = ''

    while tokens:
        try:
            literal = ''
            while tokens[0].type == DefaultContextToken.OTHER:
                literal += tokens.pop(0).match.group(0)
            pattern += re.escape(literal)

            if tokens[0].type == RegexDefinitionContextToken.IDENT and\
               tokens[1].type == RegexDefinitionContextToken.COLON:

                group_name = tokens.pop(0).match.group(0)
                tokens.pop(0)

                regex = ''
                while tokens[0].type == RegexContextToken.REGEXCHAR:
                    regex += tokens.pop(0).match.group(0)

                    # Needed because otherwise IndexError is raised,
                    # interrupting the whole loop
                    if not tokens:
                        break
                pattern += '(?P<{name}>{regex})'.format(name=group_name, regex=regex)

            else:
                tokens.pop(0)
                regex = ''
                while tokens[0].type == RegexContextToken.REGEXCHAR:
                    regex += tokens.pop(0).match.group(0)

                    # Needed because otherwise IndexError is raised,
                    # interrupting the whole loop
                    if not tokens:
                        break
                pattern += regex

        except IndexError:
            break

    return re.compile(pattern)
