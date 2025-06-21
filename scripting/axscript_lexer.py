"""
AXScript Lexer
Tokenizes AXScript source code
"""

import re
from enum import Enum, auto
from typing import List, NamedTuple, Optional

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # Keywords
    VAR = auto()
    FUNCTION = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    DO = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    THIS = auto()
    SUPER = auto()
    NEW = auto()
    CLASS = auto()
    EXTENDS = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    IMPORT = auto()
    EXPORT = auto()
    FROM = auto()
    AS = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    TYPEOF = auto()
    INSTANCEOF = auto()
    IN = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    
    # Punctuation
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    DOT = auto()
    COLON = auto()
    QUESTION = auto()
    
    # Special
    EOF = auto()
    NEWLINE = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class AXScriptLexer:
    """Lexer for AXScript language"""
    
    def __init__(self):
        self.keywords = {
            'var': TokenType.VAR,
            'function': TokenType.FUNCTION,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'do': TokenType.DO,
            'return': TokenType.RETURN,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'null': TokenType.NULL,
            'this': TokenType.THIS,
            'super': TokenType.SUPER,
            'new': TokenType.NEW,
            'class': TokenType.CLASS,
            'extends': TokenType.EXTENDS,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'finally': TokenType.FINALLY,
            'throw': TokenType.THROW,
            'import': TokenType.IMPORT,
            'export': TokenType.EXPORT,
            'from': TokenType.FROM,
            'as': TokenType.AS,
            'switch': TokenType.SWITCH,
            'case': TokenType.CASE,
            'default': TokenType.DEFAULT,
            'typeof': TokenType.TYPEOF,
            'instanceof': TokenType.INSTANCEOF,
            'in': TokenType.IN,
        }
    
    def tokenize(self, source: str) -> List[Token]:
        """Tokenize source code"""
        tokens = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 0
            i = 0
            
            while i < len(line):
                # Skip whitespace
                if line[i].isspace():
                    i += 1
                    column += 1
                    continue
                
                # Skip comments
                if i < len(line) - 1 and line[i:i+2] == '//':
                    break
                
                # Multi-character operators
                if i < len(line) - 1:
                    two_char = line[i:i+2]
                    if two_char == '++':
                        tokens.append(Token(TokenType.INCREMENT, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '--':
                        tokens.append(Token(TokenType.DECREMENT, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '==':
                        tokens.append(Token(TokenType.EQUAL, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '!=':
                        tokens.append(Token(TokenType.NOT_EQUAL, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '<=':
                        tokens.append(Token(TokenType.LESS_EQUAL, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '>=':
                        tokens.append(Token(TokenType.GREATER_EQUAL, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '&&':
                        tokens.append(Token(TokenType.AND, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '||':
                        tokens.append(Token(TokenType.OR, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '+=':
                        tokens.append(Token(TokenType.PLUS_ASSIGN, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '-=':
                        tokens.append(Token(TokenType.MINUS_ASSIGN, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '*=':
                        tokens.append(Token(TokenType.MULTIPLY_ASSIGN, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                    elif two_char == '/=':
                        tokens.append(Token(TokenType.DIVIDE_ASSIGN, two_char, line_num, column))
                        i += 2
                        column += 2
                        continue
                
                # Single character tokens
                char = line[i]
                
                if char == '+':
                    tokens.append(Token(TokenType.PLUS, char, line_num, column))
                elif char == '-':
                    tokens.append(Token(TokenType.MINUS, char, line_num, column))
                elif char == '*':
                    tokens.append(Token(TokenType.MULTIPLY, char, line_num, column))
                elif char == '/':
                    tokens.append(Token(TokenType.DIVIDE, char, line_num, column))
                elif char == '%':
                    tokens.append(Token(TokenType.MODULO, char, line_num, column))
                elif char == '=':
                    tokens.append(Token(TokenType.ASSIGN, char, line_num, column))
                elif char == '<':
                    tokens.append(Token(TokenType.LESS, char, line_num, column))
                elif char == '>':
                    tokens.append(Token(TokenType.GREATER, char, line_num, column))
                elif char == '!':
                    tokens.append(Token(TokenType.NOT, char, line_num, column))
                elif char == '(':
                    tokens.append(Token(TokenType.LEFT_PAREN, char, line_num, column))
                elif char == ')':
                    tokens.append(Token(TokenType.RIGHT_PAREN, char, line_num, column))
                elif char == '{':
                    tokens.append(Token(TokenType.LEFT_BRACE, char, line_num, column))
                elif char == '}':
                    tokens.append(Token(TokenType.RIGHT_BRACE, char, line_num, column))
                elif char == '[':
                    tokens.append(Token(TokenType.LEFT_BRACKET, char, line_num, column))
                elif char == ']':
                    tokens.append(Token(TokenType.RIGHT_BRACKET, char, line_num, column))
                elif char == ',':
                    tokens.append(Token(TokenType.COMMA, char, line_num, column))
                elif char == ';':
                    tokens.append(Token(TokenType.SEMICOLON, char, line_num, column))
                elif char == '.':
                    tokens.append(Token(TokenType.DOT, char, line_num, column))
                elif char == ':':
                    tokens.append(Token(TokenType.COLON, char, line_num, column))
                elif char == '?':
                    tokens.append(Token(TokenType.QUESTION, char, line_num, column))
                
                # String literals
                elif char in ['"', "'"]:
                    quote_char = char
                    start_col = column
                    i += 1
                    column += 1
                    string_val = ""
                    
                    while i < len(line) and line[i] != quote_char:
                        if line[i] == '\\' and i + 1 < len(line):
                            # Handle escape sequences
                            i += 1
                            column += 1
                            escape_char = line[i]
                            if escape_char == 'n':
                                string_val += '\n'
                            elif escape_char == 't':
                                string_val += '\t'
                            elif escape_char == 'r':
                                string_val += '\r'
                            elif escape_char == '\\':
                                string_val += '\\'
                            elif escape_char == quote_char:
                                string_val += quote_char
                            else:
                                string_val += escape_char
                        else:
                            string_val += line[i]
                        i += 1
                        column += 1
                    
                    if i < len(line) and line[i] == quote_char:
                        tokens.append(Token(TokenType.STRING, quote_char + string_val + quote_char, line_num, start_col))
                        i += 1
                        column += 1
                    else:
                        raise Exception(f"Unterminated string at line {line_num}, column {start_col}")
                
                # Numbers
                elif char.isdigit() or char == '.':
                    start_col = column
                    num_str = ""
                    has_dot = False
                    
                    while i < len(line) and (line[i].isdigit() or (line[i] == '.' and not has_dot)):
                        if line[i] == '.':
                            has_dot = True
                        num_str += line[i]
                        i += 1
                        column += 1
                    
                    tokens.append(Token(TokenType.NUMBER, num_str, line_num, start_col))
                    continue
                
                # Identifiers and keywords
                elif char.isalpha() or char == '_':
                    start_col = column
                    identifier = ""
                    
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        identifier += line[i]
                        i += 1
                        column += 1
                    
                    token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                    tokens.append(Token(token_type, identifier, line_num, start_col))
                    continue
                
                else:
                    raise Exception(f"Unexpected character '{char}' at line {line_num}, column {column}")
                
                i += 1
                column += 1
        
        tokens.append(Token(TokenType.EOF, "", len(lines), 0))
        return tokens

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
    IMPORT = auto()
    EXPORT = auto()
    FROM = auto()
    AS = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()
    EXTENDS = auto()
    STATIC = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    IN = auto()
    OF = auto()
    DO = auto()
    BREAK = auto()
    CONTINUE = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    TYPEOF = auto()
    INSTANCEOF = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    MULTIPLY_ASSIGN = auto()
    DIVIDE_ASSIGN = auto()
    INCREMENT = auto()
    DECREMENT = auto()

    # Comparison
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    STRICT_EQUAL = auto()
    STRICT_NOT_EQUAL = auto()

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
    QUESTION = auto()
    ARROW = auto()

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
            'import': TokenType.IMPORT,
            'export': TokenType.EXPORT,
            'from': TokenType.FROM,
            'as': TokenType.AS,
            'new': TokenType.NEW,
            'this': TokenType.THIS,
            'super': TokenType.SUPER,
            'extends': TokenType.EXTENDS,
            'static': TokenType.STATIC,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'finally': TokenType.FINALLY,
            'throw': TokenType.THROW,
            'in': TokenType.IN,
            'of': TokenType.OF,
            'do': TokenType.DO,
            'break': TokenType.BREAK,
            'continue': TokenType.CONTINUE,
            'switch': TokenType.SWITCH,
            'case': TokenType.CASE,
            'default': TokenType.DEFAULT,
            'typeof': TokenType.TYPEOF,
            'instanceof': TokenType.INSTANCEOF,
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
            '?': TokenType.QUESTION,
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
            '===': TokenType.STRICT_EQUAL,
            '!==': TokenType.STRICT_NOT_EQUAL,
            '++': TokenType.INCREMENT,
            '--': TokenType.DECREMENT,
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.MULTIPLY_ASSIGN,
            '/=': TokenType.DIVIDE_ASSIGN,
            '=>': TokenType.ARROW,
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

                # Three character tokens
                if i + 2 < len(line):
                    three_char = line[i:i+3]
                    if three_char in ['===', '!==']:
                        token_type = TokenType.STRICT_EQUAL if three_char == '===' else TokenType.STRICT_NOT_EQUAL
                        tokens.append(Token(token_type, three_char, line_num, column))
                        column += 3
                        i += 3
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