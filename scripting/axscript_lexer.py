"""
AXScript Lexer
Tokenizes AXScript source code
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional

class TokenType(Enum):
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Keywords
    VAR = auto()
    FUNCTION = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    CLASS = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()

    # Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Assignment
    ASSIGN = auto()

    # Punctuation
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()
    COLON = auto()

    # Special
    EOF = auto()
    NEWLINE = auto()
    COMMENT = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class LexError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexical error at line {line}, column {column}: {message}")

class AXScriptLexer:
    """Lexical analyzer for AXScript"""

    def __init__(self):
        # Keywords mapping
        self.keywords = {
            'var': TokenType.VAR,
            'function': TokenType.FUNCTION,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'null': TokenType.NULL,
            'class': TokenType.CLASS,
        }

        # Single character tokens
        self.single_char_tokens = {
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
        }

        # Two character tokens
        self.two_char_tokens = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '&&': TokenType.AND,
            '||': TokenType.OR,
        }

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize AXScript source code"""
        tokens = []
        lines = source.split('\n')

        for line_num, line in enumerate(lines, 1):
            column = 1
            i = 0

            while i < len(line):
                char = line[i]

                # Skip whitespace
                if char.isspace():
                    if char == '\t':
                        column += 4  # Tab counts as 4 spaces
                    else:
                        column += 1
                    i += 1
                    continue

                # Comments
                if char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    # Single line comment - skip rest of line
                    break

                # String literals
                if char == '"':
                    string_value, new_i = self.scan_string(line, i, line_num, column)
                    tokens.append(Token(TokenType.STRING, string_value, line_num, column))
                    column += new_i - i
                    i = new_i
                    continue

                # Number literals
                if char.isdigit():
                    number_value, new_i = self.scan_number(line, i, line_num, column)
                    tokens.append(Token(TokenType.NUMBER, number_value, line_num, column))
                    column += new_i - i
                    i = new_i
                    continue

                # Identifiers and keywords
                if char.isalpha() or char == '_':
                    identifier, new_i = self.scan_identifier(line, i, line_num, column)
                    token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                    tokens.append(Token(token_type, identifier, line_num, column))
                    column += new_i - i
                    i = new_i
                    continue

                # Two character tokens
                if i + 1 < len(line):
                    two_char = line[i:i+2]
                    if two_char in self.two_char_tokens:
                        tokens.append(Token(self.two_char_tokens[two_char], two_char, line_num, column))
                        column += 2
                        i += 2
                        continue

                # Single character tokens
                if char in self.single_char_tokens:
                    tokens.append(Token(self.single_char_tokens[char], char, line_num, column))
                    column += 1
                    i += 1
                    continue

                # Handle single character operators that might be part of two-char tokens
                if char == '=':
                    tokens.append(Token(TokenType.ASSIGN, char, line_num, column))
                    column += 1
                    i += 1
                    continue

                if char == '<':
                    tokens.append(Token(TokenType.LESS, char, line_num, column))
                    column += 1
                    i += 1
                    continue

                if char == '>':
                    tokens.append(Token(TokenType.GREATER, char, line_num, column))
                    column += 1
                    i += 1
                    continue

                if char == '!':
                    tokens.append(Token(TokenType.NOT, char, line_num, column))
                    column += 1
                    i += 1
                    continue

                # Unexpected character
                raise LexError(f"Unexpected character: '{char}'", line_num, column)

        # Add EOF token
        tokens.append(Token(TokenType.EOF, "", len(lines), 1))
        return tokens

    def scan_string(self, line: str, start: int, line_num: int, column: int) -> tuple:
        """Scan a string literal"""
        i = start + 1  # Skip opening quote
        value = '"'

        while i < len(line):
            char = line[i]

            if char == '"':
                value += char
                return value, i + 1

            if char == '\\' and i + 1 < len(line):
                # Handle escape sequences
                next_char = line[i + 1]
                if next_char in ['"', '\\', 'n', 't', 'r']:
                    value += char + next_char
                    i += 2
                else:
                    value += char
                    i += 1
            else:
                value += char
                i += 1

        raise LexError("Unterminated string literal", line_num, column)

    def scan_number(self, line: str, start: int, line_num: int, column: int) -> tuple:
        """Scan a number literal"""
        i = start
        value = ""
        has_dot = False

        while i < len(line):
            char = line[i]

            if char.isdigit():
                value += char
                i += 1
            elif char == '.' and not has_dot:
                has_dot = True
                value += char
                i += 1
            else:
                break

        return value, i

    def scan_identifier(self, line: str, start: int, line_num: int, column: int) -> tuple:
        """Scan an identifier or keyword"""
        i = start
        value = ""

        while i < len(line):
            char = line[i]

            if char.isalnum() or char == '_':
                value += char
                i += 1
            else:
                break

        return value, i

    def is_keyword(self, text: str) -> bool:
        """Check if text is a keyword"""
        return text in self.keywords

    def get_token_type_name(self, token_type: TokenType) -> str:
        """Get human-readable name for token type"""
        return token_type.name.lower().replace('_', ' ')