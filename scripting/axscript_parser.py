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
    def __init__(self, name: str, params: List[str], body: List[Statement], 
                 return_type: Optional[str] = None, param_types: Optional[List[str]] = None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
        self.param_types = param_types or []

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
    def __init__(self, target: Union[str, Expression], value: Expression):
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

class ClassDeclaration(Statement):
    def __init__(self, name: str, superclass: Optional[str], methods: List['FunctionDeclaration']):
        self.name = name
        self.superclass = superclass
        self.methods = methods

class NewExpression(Expression):
    def __init__(self, class_name: str, args: List[Expression]):
        self.class_name = class_name
        self.args = args

class ThisExpression(Expression):
    def __init__(self):
        pass

class SuperExpression(Expression):
    def __init__(self, method: str):
        self.method = method

class ForStatement(Statement):
    def __init__(self, init: Optional[Statement], condition: Optional[Expression], 
                 update: Optional[Expression], body: Statement):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class ForInStatement(Statement):
    def __init__(self, variable: str, iterable: Expression, body: Statement):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class DoWhileStatement(Statement):
    def __init__(self, body: Statement, condition: Expression):
        self.body = body
        self.condition = condition

class TryStatement(Statement):
    def __init__(self, try_block: Block, catch_clause: Optional['CatchClause'], finally_block: Optional[Block]):
        self.try_block = try_block
        self.catch_clause = catch_clause
        self.finally_block = finally_block

class CatchClause(ASTNode):
    def __init__(self, param: str, body: Block):
        self.param = param
        self.body = body

class ThrowStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

class BreakStatement(Statement):
    def __init__(self):
        pass

class ContinueStatement(Statement):
    def __init__(self):
        pass

class ImportStatement(Statement):
    def __init__(self, module_name: str, imports: Optional[List[str]] = None, alias: Optional[str] = None):
        self.module_name = module_name
        self.imports = imports  # None means import all
        self.alias = alias

class ExportStatement(Statement):
    def __init__(self, declaration: Statement):
        self.declaration = declaration

class SwitchStatement(Statement):
    def __init__(self, discriminant: Expression, cases: List['CaseClause']):
        self.discriminant = discriminant
        self.cases = cases

class CaseClause(ASTNode):
    def __init__(self, test: Optional[Expression], consequent: List[Statement]):
        self.test = test  # None for default case
        self.consequent = consequent

class ArrayExpression(Expression):
    def __init__(self, elements: List[Expression]):
        self.elements = elements

class IndexAccess(Expression):
    def __init__(self, object: Expression, index: Expression):
        self.object = object
        self.index = index

class ConditionalExpression(Expression):
    def __init__(self, test: Expression, consequent: Expression, alternate: Expression):
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

class UpdateExpression(Expression):
    def __init__(self, operator: str, operand: Expression, prefix: bool):
        self.operator = operator
        self.operand = operand
        self.prefix = prefix

class TypeofExpression(Expression):
    def __init__(self, operand: Expression):
        self.operand = operand

class InstanceofExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

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

            if self.match(TokenType.CLASS):
                return self.parse_class_declaration()

            if self.match(TokenType.IF):
                return self.parse_if_statement()

            if self.match(TokenType.WHILE):
                return self.parse_while_statement()

            if self.match(TokenType.FOR):
                return self.parse_for_statement()

            if self.match(TokenType.DO):
                return self.parse_do_while_statement()

            if self.match(TokenType.TRY):
                return self.parse_try_statement()

            if self.match(TokenType.THROW):
                return self.parse_throw_statement()

            if self.match(TokenType.RETURN):
                return self.parse_return_statement()

            if self.match(TokenType.BREAK):
                self.consume(TokenType.SEMICOLON, "Expected ';' after break")
                return BreakStatement()

            if self.match(TokenType.CONTINUE):
                self.consume(TokenType.SEMICOLON, "Expected ';' after continue")
                return ContinueStatement()

            if self.match(TokenType.IMPORT):
                return self.parse_import_statement()

            if self.match(TokenType.EXPORT):
                return self.parse_export_statement()

            if self.match(TokenType.SWITCH):
                return self.parse_switch_statement()

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
        """Parse if statement with robust error recovery"""
        # Store starting position for recovery
        start_pos = self.current

        try:
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        except ParseError:
            # Skip problematic tokens and try to find opening paren
            self.recover_to_token([TokenType.LEFT_PAREN, TokenType.IDENTIFIER, TokenType.NUMBER])

        # Parse condition with multiple fallback strategies
        condition = None
        try:
            condition = self.parse_expression()
        except ParseError as e:
            # Try to recover by finding the next meaningful token
            print(f"Warning: Error in if condition: {e.message}")
            condition = Literal(True, "boolean")  # Safe fallback

            # Advanced recovery: skip to next ) or {
            self.recover_to_token([TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE])

        # Handle closing paren with recovery
        try:
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition")
        except ParseError:
            # Try to find closing paren or continue to statement
            self.recover_to_token([TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE, TokenType.IDENTIFIER])

        # Parse then statement with error protection
        then_stmt = None
        try:
            then_stmt = self.parse_statement()
        except ParseError:
            # Create a simple block as fallback
            then_stmt = Block([])

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
            except ParseError:
                # Skip problematic tokens until we find a synchronization point
                self.advance()
                continue

        # Consume closing brace if present
        if self.check(TokenType.RIGHT_BRACE):
            self.advance()

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
        """Parse expression with proper error recovery"""
        try:
            return self.parse_assignment()
        except ParseError as e:
            # Forcefully advance to prevent infinite loops
            if not self.is_at_end():
                self.advance()
            return Literal(None, "null")

    def parse_assignment(self) -> Expression:
        """Parse assignment expression"""
        expr = self.parse_conditional()

        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, 
                     TokenType.MULTIPLY_ASSIGN, TokenType.DIVIDE_ASSIGN):
            operator = self.previous().value
            value = self.parse_assignment()

            if isinstance(expr, Identifier):
                if operator != "=":
                    # Convert compound assignment to regular assignment
                    op = operator[:-1]  # Remove '=' from '+=', '-=', etc.
                    value = BinaryOp(expr, op, value)
                return Assignment(expr.name, value)
            elif isinstance(expr, MemberAccess):
                if operator != "=":
                    # Convert compound assignment to regular assignment
                    op = operator[:-1]  # Remove '=' from '+=', '-=', etc.
                    value = BinaryOp(expr, op, value)
                return Assignment(expr, value)
            elif isinstance(expr, IndexAccess):
                if operator != "=":
                    # Convert compound assignment to regular assignment
                    op = operator[:-1]  # Remove '=' from '+=', '-=', etc.
                    value = BinaryOp(expr, op, value)
                return Assignment(expr, value)

        return expr

    def parse_conditional(self) -> Expression:
        """Parse conditional (ternary) expression"""
        expr = self.parse_logical_or()

        if self.match(TokenType.QUESTION):
            then_expr = self.parse_expression()
            self.consume(TokenType.COLON, "Expected ':' after '?' in conditional")
            else_expr = self.parse_conditional()
            return ConditionalExpression(expr, then_expr, else_expr)

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

        if self.match(TokenType.INCREMENT, TokenType.DECREMENT):
            operator = self.previous().value
            operand = self.parse_unary()
            return UpdateExpression(operator, operand, True)  # prefix

        expr = self.parse_call()

        # Postfix increment/decrement
        if self.match(TokenType.INCREMENT, TokenType.DECREMENT):
            operator = self.previous().value
            return UpdateExpression(operator, expr, False)  # postfix

        return expr

    def parse_call(self) -> Expression:
        """Parse function call, member access, or array access"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'")
                expr = MemberAccess(expr, name.value)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.parse_expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array index")
                expr = IndexAccess(expr, index)
            else:
                break

        # Handle instanceof
        if self.match(TokenType.INSTANCEOF):
            right = self.parse_unary()
            expr = InstanceofExpression(expr, right)

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
        elif isinstance(callee, MemberAccess):
            # Handle method calls like obj.method()
            return FunctionCall(f"{callee.object.name}.{callee.member}", args)
        else:
            raise ParseError("Invalid function call", self.get_current_line())

    def parse_primary(self) -> Expression:
        """Parse primary expression with simple error recovery"""
        # Skip problematic tokens silently
        while not self.is_at_end() and self.check(TokenType.RIGHT_PAREN):
            self.advance()

        if self.match(TokenType.TRUE):
            return Literal(True, "boolean")

        if self.match(TokenType.FALSE):
            return Literal(False, "boolean")

        if self.match(TokenType.NULL):
            return Literal(None, "null")

        if self.match(TokenType.THIS):
            return ThisExpression()

        if self.match(TokenType.SUPER):
            self.consume(TokenType.DOT, "Expected '.' after 'super'")
            method = self.consume(TokenType.IDENTIFIER, "Expected method name").value
            return SuperExpression(method)

        if self.match(TokenType.NEW):
            class_name = self.consume(TokenType.IDENTIFIER, "Expected class name").value
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after class name")
            args = []
            if not self.check(TokenType.RIGHT_PAREN):
                args.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_expression())
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
            return NewExpression(class_name, args)

        if self.match(TokenType.TYPEOF):
            operand = self.parse_unary()
            return TypeofExpression(operand)

        if self.match(TokenType.NUMBER):
            value = self.previous().value
            return Literal(float(value) if '.' in value else int(value), "number")

        if self.match(TokenType.STRING):
            return Literal(self.previous().value[1:-1], "string")  # Remove quotes

        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)

        if self.match(TokenType.LEFT_PAREN):
            try:
                expr = self.parse_expression()
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
                return expr
            except ParseError as e:
                # Better error handling for parenthesized expressions
                raise ParseError(f"Error in parenthesized expression: {e.message}", self.get_current_line())

        if self.match(TokenType.LEFT_BRACKET):
            return self.parse_array_literal()

        # Handle object literals
        if self.check(TokenType.LEFT_BRACE):
            self.advance()  # consume '{'
            return self.parse_object_literal()

        # If we get here, just advance and return a safe literal
        if not self.is_at_end():
            self.advance()
        return Literal(None, "null")

    def parse_array_literal(self) -> ArrayExpression:
        """Parse array literal [a, b, c]"""
        elements = []
        if not self.check(TokenType.RIGHT_BRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                elements.append(self.parse_expression())
        self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after array elements")
        return ArrayExpression(elements)

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

    def parse_class_declaration(self) -> ClassDeclaration:
        """Parse class declaration"""
        name_token = self.consume(TokenType.IDENTIFIER, "Expected class name")
        name = name_token.value

        superclass = None
        if self.match(TokenType.EXTENDS):
            superclass_token = self.consume(TokenType.IDENTIFIER, "Expected superclass name")
            superclass = superclass_token.value

        self.consume(TokenType.LEFT_BRACE, "Expected '{' before class body")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.match(TokenType.FUNCTION):
                methods.append(self.parse_function_declaration())
            else:
                raise ParseError("Expected method declaration in class body", self.get_current_line())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after class body")
        return ClassDeclaration(name, superclass, methods)

    def parse_for_statement(self) -> Statement:
        """Parse for statement"""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        # Check for for-in loop
        if self.check(TokenType.VAR):
            checkpoint = self.current
            try:
                self.advance()  # consume 'var'
                var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
                if self.match(TokenType.IN):
                    iterable = self.parse_expression()
                    self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for-in")
                    body = self.parse_statement()
                    return ForInStatement(var_name, iterable, body)
                else:
                    # Reset and parse as regular for loop
                    self.current = checkpoint
            except:
                self.current = checkpoint

        # Regular for loop
        init = None
        if not self.check(TokenType.SEMICOLON):
            if self.match(TokenType.VAR):
                name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
                name = name_token.value
                value = None
                if self.match(TokenType.ASSIGN):
                    value = self.parse_expression()
                self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
                init = VarDeclaration(name, value)
            else:
                expr = self.parse_expression()
                self.consume(TokenType.SEMICOLON, "Expected ';' after for loop initializer")
                init = ExpressionStatement(expr)
        else:
            self.advance()  # consume semicolon

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after for loop condition")

        update = None
        if not self.check(TokenType.RIGHT_PAREN):
            update = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")

        body = self.parse_statement()
        return ForStatement(init, condition, update, body)

    def parse_do_while_statement(self) -> DoWhileStatement:
        """Parse do-while statement"""
        body = self.parse_statement()
        self.consume(TokenType.WHILE, "Expected 'while' after do body")
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after while condition")
        self.consume(TokenType.SEMICOLON, "Expected ';' after do-while")
        return DoWhileStatement(body, condition)

    def parse_try_statement(self) -> TryStatement:
        """Parse try-catch-finally statement"""
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'try'")
        try_block = self.parse_block()

        catch_clause = None
        if self.match(TokenType.CATCH):
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'catch'")
            param = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after catch parameter")
            self.consume(TokenType.LEFT_BRACE, "Expected '{' after catch clause")
            catch_body = self.parse_block()
            catch_clause = CatchClause(param, catch_body)

        finally_block = None
        if self.match(TokenType.FINALLY):
            self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'finally'")
            finally_block = self.parse_block()

        if catch_clause is None and finally_block is None:
            raise ParseError("Missing catch or finally after try", self.get_current_line())

        return TryStatement(try_block, catch_clause, finally_block)

    def parse_throw_statement(self) -> ThrowStatement:
        """Parse throw statement"""
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after throw")
        return ThrowStatement(expr)

    def parse_import_statement(self) -> ImportStatement:
        """Parse import statement"""
        if self.match(TokenType.LEFT_BRACE):
            # Named imports: import { a, b } from "module"
            imports = []
            imports.append(self.consume(TokenType.IDENTIFIER, "Expected import name").value)
            while self.match(TokenType.COMMA):
                imports.append(self.consume(TokenType.IDENTIFIER, "Expected import name").value)
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' after imports")
            self.consume(TokenType.FROM, "Expected 'from' after imports")
            module_name = self.consume(TokenType.STRING, "Expected module name").value
            self.consume(TokenType.SEMICOLON, "Expected ';' after import")
            return ImportStatement(module_name, imports)
        else:
            # Default import: import module or import module as alias
            if self.check(TokenType.STRING):
                module_name = self.consume(TokenType.STRING, "Expected module name").value
                alias = None
                if self.match(TokenType.AS):
                    alias = self.consume(TokenType.IDENTIFIER, "Expected alias name").value
                self.consume(TokenType.SEMICOLON, "Expected ';' after import")
                return ImportStatement(module_name, None, alias)
            else:
                # import ModuleName
                module_name = self.consume(TokenType.IDENTIFIER, "Expected module name").value
                alias = None
                if self.match(TokenType.AS):
                    alias = self.consume(TokenType.IDENTIFIER, "Expected alias name").value
                self.consume(TokenType.SEMICOLON, "Expected ';' after import")
                return ImportStatement(module_name, None, alias)

    def parse_export_statement(self) -> ExportStatement:
        """Parse export statement"""
        declaration = self.parse_statement()
        return ExportStatement(declaration)

    def parse_switch_statement(self) -> SwitchStatement:
        """Parse switch statement"""
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'switch'")
        discriminant = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after switch expression")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before switch body")

        cases = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.match(TokenType.CASE):
                test = self.parse_expression()
                self.consume(TokenType.COLON, "Expected ':' after case")
                consequent = []
                while not self.check(TokenType.CASE) and not self.check(TokenType.DEFAULT) and not self.check(TokenType.RIGHT_BRACE):
                    stmt = self.parse_statement()
                    if stmt:
                        consequent.append(stmt)
                cases.append(CaseClause(test, consequent))
            elif self.match(TokenType.DEFAULT):
                self.consume(TokenType.COLON, "Expected ':' after default")
                consequent = []
                while not self.check(TokenType.CASE) and not self.check(TokenType.DEFAULT) and not self.check(TokenType.RIGHT_BRACE):
                    stmt = self.parse_statement()
                    if stmt:
                        consequent.append(stmt)
                cases.append(CaseClause(None, consequent))
            else:
                raise ParseError("Expected 'case' or 'default' in switch", self.get_current_line())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after switch body")
        return SwitchStatement(discriminant, cases)

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
                                   TokenType.RETURN, TokenType.RIGHT_BRACE]:
                return

            self.advance()

    def synchronize_to_token(self, target_token: TokenType):
        """Synchronize to a specific token type"""
        while not self.is_at_end() and not self.check(target_token):
            self.advance()

        if self.check(target_token):
            self.advance()  # consume the target token

    def recover_to_token(self, token_list: List[TokenType]):
        """Recover by skipping to the next meaningful token"""
        while not self.is_at_end():
            if self.peek().type in token_list:
                return  # Found a synchronization point
            self.advance()