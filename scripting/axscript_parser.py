"""
AXScript Parser
Parses AXScript source code into an Abstract Syntax Tree (AST)
"""

import re
from typing import List, Dict, Any, Optional, Union
from .axscript_lexer import AXScriptLexer, Token, TokenType

class ASTNode:
    """Base class for AST nodes"""
    pass

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass

class VarDeclaration(Statement):
    def __init__(self, name: str, value: Optional[Expression] = None):
        self.name = name
        self.value = value

class FunctionDeclaration(Statement):
    def __init__(self, name: str, params: List[str], body: List[Statement]):
        self.name = name
        self.params = params
        self.body = body

class IfStatement(Statement):
    def __init__(self, condition: Expression, then_stmt: Statement, else_stmt: Optional[Statement] = None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body

class ReturnStatement(Statement):
    def __init__(self, value: Optional[Expression] = None):
        self.value = value

class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

class Block(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

class Assignment(Expression):
    def __init__(self, target: str, value: Expression):
        self.target = target
        self.value = value

class FunctionCall(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

class MemberAccess(Expression):
    def __init__(self, object: Expression, member: str):
        self.object = object
        self.member = member

class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

class Literal(Expression):
    def __init__(self, value: Any, type: str):
        self.value = value
        self.type = type

class ParseError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Parse error at line {line}, column {column}: {message}")

class AXScriptParser:
    """Parser for AXScript language"""

    def __init__(self):
        self.lexer = AXScriptLexer()
        self.tokens: List[Token] = []
        self.current = 0

    def parse(self, source: str) -> Program:
        """Parse AXScript source code into AST"""
        try:
            # Tokenize source
            self.tokens = self.lexer.tokenize(source)
            self.current = 0

            # Parse program
            statements = []
            while not self.is_at_end():
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)

            return Program(statements)

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Unexpected error during parsing: {e}")

    def parse_statement(self) -> Optional[Statement]:
        """Parse a statement"""
        try:
            if self.match(TokenType.VAR):
                return self.parse_var_declaration()

            if self.match(TokenType.FUNCTION):
                return self.parse_function_declaration()

            if self.match(TokenType.IF):
                return self.parse_if_statement()

            if self.match(TokenType.WHILE):
                return self.parse_while_statement()

            if self.match(TokenType.RETURN):
                return self.parse_return_statement()

            if self.match(TokenType.LEFT_BRACE):
                return self.parse_block()

            return self.parse_expression_statement()

        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Error parsing statement: {e}", self.get_current_line())

    def parse_var_declaration(self) -> VarDeclaration:
        """Parse variable declaration"""
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value

        value = None
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDeclaration(name, value)

    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration"""
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value

        self.consume(TokenType.LEFT_PAREN, "Expected '(' after function name")

        # Parse parameters
        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after function parameters")

        # Parse function body
        if not self.check(TokenType.LEFT_BRACE):
            raise ParseError("Expected '{' before function body", self.get_current_line())

        self.advance()  # consume '{'
        body_block = self.parse_block()
        return FunctionDeclaration(name, params, body_block.statements)

    def parse_if_statement(self) -> IfStatement:
        """Parse if statement"""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")

        then_stmt = self.parse_statement()
        if then_stmt is None:
            raise ParseError("Expected statement after if condition", self.get_current_line())

        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self.parse_statement()
            if else_stmt is None:
                raise ParseError("Expected statement after else", self.get_current_line())

        return IfStatement(condition, then_stmt, else_stmt)

    def parse_while_statement(self) -> WhileStatement:
        """Parse while statement"""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")

        body = self.parse_statement()
        if body is None:
            raise ParseError("Expected statement after while condition", self.get_current_line())

        return WhileStatement(condition, body)

    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement"""
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.parse_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReturnStatement(value)

    def parse_block(self) -> Block:
        """Parse block statement"""
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                # Try to synchronize and continue parsing
                print(f"Parse error in block: {e}")
                self.synchronize()
                break

        if not self.check(TokenType.RIGHT_BRACE):
            if self.is_at_end():
                raise ParseError("Unexpected end of input, expected '}'", self.get_current_line())
            else:
                raise ParseError("Expected '}' after block", self.get_current_line())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return Block(statements)

    def parse_expression_statement(self) -> ExpressionStatement:
        """Parse expression statement"""
        expr = self.parse_expression()

        # Check if semicolon is present, but don't require it at end of block
        if self.check(TokenType.SEMICOLON):
            self.advance()
        elif not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            self.consume(TokenType.SEMICOLON, "Expected ';' after expression")

        return ExpressionStatement(expr)

    def parse_expression(self) -> Expression:
        """Parse expression"""
        return self.parse_assignment()

    def parse_assignment(self) -> Expression:
        """Parse assignment expression"""
        expr = self.parse_logical_or()

        if self.match(TokenType.ASSIGN):
            value = self.parse_assignment()
            if isinstance(expr, Identifier):
                return Assignment(expr.name, value)
            else:
                raise ParseError("Invalid assignment target", self.get_current_line())

        return expr

    def parse_logical_or(self) -> Expression:
        """Parse logical OR expression"""
        expr = self.parse_logical_and()

        while self.match(TokenType.OR):
            operator = self.previous().value
            right = self.parse_logical_and()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_logical_and(self) -> Expression:
        """Parse logical AND expression"""
        expr = self.parse_equality()

        while self.match(TokenType.AND):
            operator = self.previous().value
            right = self.parse_equality()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_equality(self) -> Expression:
        """Parse equality expression"""
        expr = self.parse_comparison()

        while self.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            operator = self.previous().value
            right = self.parse_comparison()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_comparison(self) -> Expression:
        """Parse comparison expression"""
        expr = self.parse_term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                         TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous().value
            right = self.parse_term()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_term(self) -> Expression:
        """Parse term expression (+ -)"""
        expr = self.parse_factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous().value
            right = self.parse_factor()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_factor(self) -> Expression:
        """Parse factor expression (* /)"""
        expr = self.parse_unary()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.previous().value
            right = self.parse_unary()
            expr = BinaryOp(expr, operator, right)

        return expr

    def parse_unary(self) -> Expression:
        """Parse unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous().value
            right = self.parse_unary()
            return UnaryOp(operator, right)

        return self.parse_call()

    def parse_call(self) -> Expression:
        """Parse function call or member access"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'")
                expr = MemberAccess(expr, name.value)
            else:
                break

        return expr

    def finish_call(self, callee: Expression) -> FunctionCall:
        """Finish parsing function call"""
        args = []

        if not self.check(TokenType.RIGHT_PAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after function arguments")

        if isinstance(callee, Identifier):
            return FunctionCall(callee.name, args)
        else:
            raise ParseError("Invalid function call", self.get_current_line())

    def parse_primary(self) -> Expression:
        """Parse primary expression"""
        if self.match(TokenType.TRUE):
            return Literal(True, "boolean")

        if self.match(TokenType.FALSE):
            return Literal(False, "boolean")

        if self.match(TokenType.NULL):
            return Literal(None, "null")

        if self.match(TokenType.NUMBER):
            value = self.previous().value
            return Literal(float(value) if '.' in value else int(value), "number")

        if self.match(TokenType.STRING):
            return Literal(self.previous().value[1:-1], "string")  # Remove quotes

        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        if self.match(TokenType.LEFT_BRACE):
            return self.parse_object_literal()

        raise ParseError(f"Unexpected token: {self.peek().value}", self.get_current_line())

    def parse_object_literal(self) -> Expression:
        """Parse object literal { key: value, ... }"""
        properties = {}

        if not self.check(TokenType.RIGHT_BRACE):
            while True:
                # Parse key (identifier or string)
                if self.match(TokenType.IDENTIFIER):
                    key = self.previous().value
                elif self.match(TokenType.STRING):
                    key = self.previous().value[1:-1]  # Remove quotes
                else:
                    raise ParseError("Expected property name", self.get_current_line())

                self.consume(TokenType.COLON, "Expected ':' after property name")
                value = self.parse_expression()
                properties[key] = value

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after object literal")
        return Literal(properties, "object")

    # Utility methods
    def match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        """Consume current token and return it"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """Check if we're at end of tokens"""
        return self.current >= len(self.tokens) or self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """Return current token without advancing"""
        if self.current >= len(self.tokens):
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Return previous token"""
        if self.current <= 0:
            return Token(TokenType.EOF, "", 0, 0)
        return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of given type or raise error"""
        if self.check(token_type):
            return self.advance()

        current_token = self.peek()
        raise ParseError(message, current_token.line, current_token.column)

    def get_current_line(self) -> int:
        """Get current line number"""
        if self.current < len(self.tokens):
            return self.tokens[self.current].line
        return 0

    def synchronize(self):
        """Synchronize after parse error"""
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in [TokenType.CLASS, TokenType.FUNCTION, TokenType.VAR,
                                   TokenType.FOR, TokenType.IF, TokenType.WHILE,
                                   TokenType.RETURN]:
                return

            self.advance()