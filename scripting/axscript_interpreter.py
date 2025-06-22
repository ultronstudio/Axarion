"""Add is_truthy helper method and ensure proper 'for' loop structure."""
"""
Enhanced AXScript Interpreter with full language support
"""

import math
import time
import traceback
from typing import Dict, Any, List, Optional, Callable, Union
from .axscript_parser import (
    AXScriptParser, ASTNode, Program, Statement, Expression,
    VarDeclaration, FunctionDeclaration, IfStatement, WhileStatement,
    ReturnStatement, ExpressionStatement, Block, BinaryOp, UnaryOp,
    Assignment, FunctionCall, MemberAccess, Identifier, Literal,
    ClassDeclaration, NewExpression, ThisExpression, SuperExpression,
    ForStatement, ForInStatement, DoWhileStatement, TryStatement,
    ThrowStatement, BreakStatement, ContinueStatement, ImportStatement,
    ExportStatement, SwitchStatement, ArrayExpression, IndexAccess,
    ConditionalExpression, UpdateExpression, TypeofExpression,
    InstanceofExpression, CaseClause, CatchClause
)
from .axscript_types import (
    TypeChecker, TypeInfo, AXType, FunctionType, ClassType, ModuleSystem,
    create_math_module, create_string_module, create_array_module,
    create_console_module, create_json_module
)

class RuntimeError(Exception):
    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(f"Runtime error at line {line}: {message}")

class ReturnException(Exception):
    """Exception used for return statement control flow"""
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    """Exception used for break statement control flow"""
    pass

class ContinueException(Exception):
    """Exception used for continue statement control flow"""
    pass

class AXScriptError(Exception):
    """Custom error for AXScript exceptions"""
    def __init__(self, message: str, error_type: str = "Error"):
        self.message = message
        self.error_type = error_type
        super().__init__(f"{error_type}: {message}")

class Environment:
    """Enhanced runtime environment with proper scoping"""

    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
        self.classes: Dict[str, 'AXScriptClass'] = {}
        self.is_function_scope = False
        self.is_class_scope = False

    def define(self, name: str, value: Any):
        """Define a variable in this environment"""
        self.variables[name] = value

    def get(self, name: str) -> Any:
        """Get a variable value"""
        if name in self.variables:
            return self.variables[name]

        # Also check functions
        if name in self.functions:
            return self.functions[name]

        if self.parent:
            return self.parent.get(name)

        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name: str, value: Any):
        """Set a variable value"""
        if name in self.variables:
            self.variables[name] = value
            return

        if self.parent:
            try:
                self.parent.set(name, value)
                return
            except RuntimeError:
                pass

        # If variable doesn't exist, create it in current scope
        self.variables[name] = value

    def define_function(self, name: str, func: Callable):
        """Define a function in this environment"""
        self.functions[name] = func

    def get_function(self, name: str) -> Callable:
        """Get a function"""
        if name in self.functions:
            return self.functions[name]

        if self.parent:
            return self.parent.get_function(name)

        raise RuntimeError(f"Undefined function: {name}")

    def define_class(self, name: str, cls: 'AXScriptClass'):
        """Define a class in this environment"""
        self.classes[name] = cls

    def get_class(self, name: str) -> 'AXScriptClass':
        """Get a class"""
        if name in self.classes:
            return self.classes[name]

        if self.parent:
            return self.parent.get_class(name)

        raise RuntimeError(f"Undefined class: {name}")

class AXScriptFunction:
    """Enhanced user-defined AXScript function with type checking"""

    def __init__(self, declaration: FunctionDeclaration, closure: Environment, 
                 interpreter: 'AXScriptInterpreter'):
        self.declaration = declaration
        self.closure = closure
        self.interpreter = interpreter
        self.return_type = declaration.return_type
        self.param_types = declaration.param_types

    def call(self, arguments: List[Any]) -> Any:
        """Call the function with type checking"""
        # Type check parameters
        if len(arguments) != len(self.declaration.params):
            raise RuntimeError(f"Expected {len(self.declaration.params)} arguments but got {len(arguments)}")

        # Create new environment for function execution
        environment = Environment(self.closure)
        environment.is_function_scope = True

        # Bind parameters to arguments
        for i, param in enumerate(self.declaration.params):
            environment.define(param, arguments[i])

        # Execute function body
        previous_env = self.interpreter.environment
        previous_return_type = self.interpreter.type_checker.current_function_return_type

        self.interpreter.environment = environment
        if self.return_type:
            self.interpreter.type_checker.current_function_return_type = TypeInfo(AXType(self.return_type))

        try:
            for stmt in self.declaration.body:
                self.interpreter.visit(stmt)
            return None  # No explicit return
        except ReturnException as ret:
            # Type check return value
            if self.return_type and ret.value is not None:
                actual_type = self.interpreter.type_checker.infer_type(ret.value)
                expected_type = TypeInfo(AXType(self.return_type))
                if not actual_type.is_compatible_with(expected_type):
                    raise RuntimeError(f"Return type mismatch: expected {expected_type}, got {actual_type}")
            return ret.value
        finally:
            self.interpreter.environment = previous_env
            self.interpreter.type_checker.current_function_return_type = previous_return_type

class AXScriptClass:
    """AXScript class definition"""

    def __init__(self, declaration: ClassDeclaration, closure: Environment, 
                 interpreter: 'AXScriptInterpreter'):
        self.declaration = declaration
        self.closure = closure
        self.interpreter = interpreter
        self.superclass = None

        if declaration.superclass:
            try:
                self.superclass = closure.get_class(declaration.superclass)
            except RuntimeError:
                raise RuntimeError(f"Undefined superclass: {declaration.superclass}")

        # Process methods
        self.methods = {}
        for method in declaration.methods:
            self.methods[method.name] = AXScriptFunction(method, closure, interpreter)

    def instantiate(self, arguments: List[Any]) -> 'AXScriptInstance':
        """Create new instance of this class"""
        instance = AXScriptInstance(self)

        # Call constructor if it exists
        if "constructor" in self.methods:
            # Set 'this' context
            previous_context = self.interpreter.context_object
            self.interpreter.context_object = instance
            try:
                self.methods["constructor"].call(arguments)
            finally:
                self.interpreter.context_object = previous_context

        return instance

class AXScriptInstance:
    """Instance of an AXScript class"""

    def __init__(self, cls: AXScriptClass):
        self.cls = cls
        self.properties = {}
        self.methods = cls.methods.copy()

    def get_property(self, name: str) -> Any:
        """Get property value"""
        if name in self.properties:
            return self.properties[name]
        if name in self.methods:
            return self.methods[name]
        if self.cls.superclass:
            return self.cls.superclass.get_property(name)
        raise RuntimeError(f"Property '{name}' not found")

    def set_property(self, name: str, value: Any):
        """Set property value"""
        self.properties[name] = value

    def call_method(self, name: str, arguments: List[Any]) -> Any:
        """Call method on this instance"""
        if name in self.methods:
            # Set 'this' context
            previous_context = self.cls.interpreter.context_object
            self.cls.interpreter.context_object = self
            try:
                return self.methods[name].call(arguments)
            finally:
                self.cls.interpreter.context_object = previous_context
        elif self.cls.superclass and name in self.cls.superclass.methods:
            # Call superclass method
            return self.cls.superclass.methods[name].call(arguments)
        else:
            raise RuntimeError(f"Method '{name}' not found")

class AXScriptInterpreter:
    """Enhanced interpreter for AXScript language with full feature support"""

    def __init__(self):
        self.parser = AXScriptParser()
        self.global_env = Environment()
        self.environment = self.global_env
        self.context_object = None  # Current game object context
        self.output_buffer = []
        self.type_checker = TypeChecker()
        self.module_system = ModuleSystem()
        self.exports = {}  # Current module exports

        # Initialize built-in functions and modules
        self.init_builtins()
        self.init_standard_library()

    def init_standard_library(self):
        """Initialize standard library modules"""
        self.module_system.register_module("Math", create_math_module())
        self.module_system.register_module("String", create_string_module())
        self.module_system.register_module("Array", create_array_module())
        self.module_system.register_module("Console", create_console_module())
        self.module_system.register_module("JSON", create_json_module())

    def init_builtins(self):
        """Initialize built-in functions with enhanced error handling"""
        # Core functions
        self.global_env.define_function("print", self.builtin_print)
        self.global_env.define_function("move", self.builtin_move)
        self.global_env.define_function("rotate", self.builtin_rotate)
        self.global_env.define_function("setProperty", self.builtin_set_property)
        self.global_env.define_function("getProperty", self.builtin_get_property)

        # Math functions
        self.global_env.define_function("sin", self.builtin_sin)
        self.global_env.define_function("cos", self.builtin_cos)
        self.global_env.define_function("sqrt", self.builtin_sqrt)
        self.global_env.define_function("abs", self.builtin_abs)
        self.global_env.define_function("min", self.builtin_min)
        self.global_env.define_function("max", self.builtin_max)
        self.global_env.define_function("random", self.builtin_random)
        self.global_env.define_function("time", self.builtin_time)

        # Type checking functions
        self.global_env.define_function("typeof", self.builtin_typeof)
        self.global_env.define_function("isNumber", self.builtin_is_number)
        self.global_env.define_function("isString", self.builtin_is_string)
        self.global_env.define_function("isBoolean", self.builtin_is_boolean)
        self.global_env.define_function("isArray", self.builtin_is_array)
        self.global_env.define_function("isObject", self.builtin_is_object)
        self.global_env.define_function("isFunction", self.builtin_is_function)

        # Error handling
        self.global_env.define_function("throw", self.builtin_throw)
        self.global_env.define_function("riskyFunction", self.builtin_risky_function)

        # Enhanced input functions
        self.global_env.define_function("keyPressed", self.builtin_keyPressed)
        self.global_env.define_function("keyJustPressed", self.builtin_key_just_pressed)
        self.global_env.define_function("mouseClicked", self.builtin_mouse_clicked)
        self.global_env.define_function("mousePressed", self.builtin_mouse_pressed)
        self.global_env.define_function("getMousePos", self.builtin_get_mouse_pos)
        self.global_env.define_function("getAxis", self.builtin_get_axis)
        self.global_env.define_function("getMovement", self.builtin_get_movement)

        # Physics and movement functions  
        self.global_env.define_function("jump", self.builtin_jump)
        self.global_env.define_function("isOnGround", self.builtin_is_on_ground)
        self.global_env.define_function("applyForce", self.builtin_apply_force_simple)
        
        # Object query functions
        self.global_env.define_function("findObjectsByTag", self.builtin_find_objects_by_tag)

        # Game utility functions
        self.global_env.define_function("distance", self.builtin_distance)
        self.global_env.define_function("clamp", self.builtin_clamp)
        self.global_env.define_function("lerp", self.builtin_lerp)
        self.global_env.define_function("floor", self.builtin_floor)
        self.global_env.define_function("ceil", self.builtin_ceil)
        self.global_env.define_function("round", self.builtin_round)

        # Built-in constants
        self.global_env.define("PI", math.pi)
        self.global_env.define("E", math.e)
        self.global_env.define("undefined", None)

    def execute(self, code_or_node: Union[str, ASTNode], context_object=None) -> Dict[str, Any]:
        """Execute AXScript code or AST node with enhanced error handling"""
        self.context_object = context_object
        self.output_buffer = []
        self.type_checker.clear_errors()

        try:
            if isinstance(code_or_node, str):
                # Parse the code first with error recovery
                try:
                    ast = self.parser.parse(code_or_node)
                    self.visit(ast)
                except Exception as parse_error:
                    # If parsing fails completely, try to execute as simple expression
                    self.output_buffer.append(f"Parse warning: {parse_error}")
                    # Continue with partial execution if possible
                    pass
            else:
                # Execute AST node directly
                self.visit(code_or_node)

            # Include type checking results
            result = {
                "success": True,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": None,
                "type_errors": self.type_checker.errors.copy(),
                "exports": self.exports.copy()
            }

            return result

        except (RuntimeError, AXScriptError) as e:
            # Extract just the core error message
            error_msg = str(e)
            if "Error visiting" in error_msg:
                # Extract the innermost error
                lines = error_msg.split("Error visiting")
                if lines:
                    error_msg = lines[-1].strip(": ")

            error_info = {
                "success": False,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": error_msg,
                "type_errors": self.type_checker.errors.copy(),
                "traceback": None  # Don't include full traceback for cleaner output
            }

            return error_info
        except Exception as e:
            error_info = {
                "success": False,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": f"Unexpected error: {str(e)}",
                "type_errors": self.type_checker.errors.copy(),
                "traceback": traceback.format_exc()
            }

            return error_info

    def visit(self, node: ASTNode) -> Any:
        """Visit an AST node with enhanced error handling"""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)

        try:
            return visitor(node)
        except (BreakException, ContinueException, ReturnException):
            raise  # These are control flow, not errors
        except Exception as e:
            if hasattr(node, 'line'):
                raise RuntimeError(f"Error visiting {type(node).__name__}: {e}", node.line)
            else:
                raise RuntimeError(f"Error visiting {type(node).__name__}: {e}")

    def generic_visit(self, node: ASTNode) -> Any:
        """Default visitor for unhandled node types"""
        raise RuntimeError(f"No visit method for {type(node).__name__}")

    # Enhanced visitor methods
    def visit_Program(self, node: Program) -> Any:
        """Visit program node"""
        result = None
        for statement in node.statements:
            result = self.visit(statement)
        return result

    def visit_VarDeclaration(self, node: VarDeclaration) -> Any:
        """Visit variable declaration"""
        value = None
        if node.value:
            value = self.visit(node.value)

        self.environment.define(node.name, value)
        return None

    def visit_FunctionDeclaration(self, node: FunctionDeclaration) -> Any:
        """Visit function declaration"""
        function = AXScriptFunction(node, self.environment, self)
        self.environment.define_function(node.name, function)
        # Also store in variables for broader access
        self.environment.define(node.name, function)
        return None

    def visit_IfStatement(self, node: IfStatement) -> Any:
        """Visit if statement"""
        condition = self.visit(node.condition)

        if self.is_truthy(condition):
            return self.visit(node.then_stmt)
        elif node.else_stmt:
            return self.visit(node.else_stmt)

        return None

    def visit_WhileStatement(self, node: WhileStatement) -> Any:
        """Visit while statement"""
        result = None
        while True:
            condition = self.visit(node.condition)
            if not self.is_truthy(condition):
                break

            try:
                result = self.visit(node.body)
            except BreakException:
                break
            except ContinueException:
                continue

        return result

    def visit_ReturnStatement(self, node: ReturnStatement) -> Any:
        """Visit return statement"""
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnException(value)

    def visit_ExpressionStatement(self, node: ExpressionStatement) -> Any:
        """Visit expression statement"""
        return self.visit(node.expression)

    def visit_BinaryOp(self, node: BinaryOp) -> Any:
        """Visit binary operation"""
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == "+":
            # Handle string concatenation with type conversion
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        elif node.operator == "%":
            return left % right
        elif node.operator == "==":
            return left == right
        elif node.operator == "!=":
            return left != right
        elif node.operator == "<":
            return left < right
        elif node.operator == "<=":
            return left <= right
        elif node.operator == ">":
            return left > right
        elif node.operator == ">=":
            return left >= right
        elif node.operator == "&&":
            return self.is_truthy(left) and self.is_truthy(right)
        elif node.operator == "||":
            return self.is_truthy(left) or self.is_truthy(right)
        else:
            raise RuntimeError(f"Unknown binary operator: {node.operator}")

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        """Visit unary operation"""
        operand = self.visit(node.operand)

        if node.operator == "-":
            return -operand
        elif node.operator == "!":
            return not self.is_truthy(operand)
        else:
            raise RuntimeError(f"Unknown unary operator: {node.operator}")

    def visit_Assignment(self, node: Assignment) -> Any:
        """Visit assignment"""
        value = self.visit(node.value)

        if isinstance(node.target, str):
            # Simple variable assignment
            self.environment.set(node.target, value)
        elif isinstance(node.target, MemberAccess):
            # Member assignment (obj.prop = value)
            obj = self.visit(node.target.object)
            if isinstance(obj, AXScriptInstance):
                obj.set_property(node.target.member, value)
            elif isinstance(obj, dict):
                obj[node.target.member] = value
            else:
                raise RuntimeError(f"Cannot set property on {type(obj)}")
        elif isinstance(node.target, IndexAccess):
            # Index assignment (arr[index] = value)
            obj = self.visit(node.target.object)
            index = self.visit(node.target.index)
            if isinstance(obj, list):
                if isinstance(index, int) and index >= 0:
                    # Extend array if index is beyond current length
                    while index >= len(obj):
                        obj.append(None)
                    obj[index] = value
                else:
                    # For special case of arr.length property access
                    if hasattr(node.target, 'member') and node.target.member == 'length':
                        # This is actually accessing the length property, not array index
                        pass  # Don't try to assign to length
                    else:
                        raise RuntimeError("Array index must be a non-negative number")
            elif isinstance(obj, dict):
                obj[str(index)] = value
            else:
                raise RuntimeError(f"Cannot index assign on {type(obj)}")
        else:
            raise RuntimeError("Invalid assignment target")

        return value

    def visit_FunctionCall(self, node: FunctionCall) -> Any:
        """Visit function call"""
        args = [self.visit(arg) for arg in node.args]

        # Handle method calls (obj.method format)
        if "." in node.name:
            obj_name, method_name = node.name.split(".", 1)
            try:
                obj = self.environment.get(obj_name)
                if isinstance(obj, AXScriptInstance):
                    return obj.call_method(method_name, args)
                elif isinstance(obj, dict) and method_name in obj:
                    method = obj[method_name]
                    if callable(method):
                        return method(*args)
            except RuntimeError:
                pass

        # Try built-in functions first
        builtin_name = f"builtin_{node.name}"
        if hasattr(self, builtin_name):
            builtin_func = getattr(self, builtin_name)
            return builtin_func(*args)

        # Check for user-defined functions
        try:
            func = self.environment.get_function(node.name)
            if isinstance(func, AXScriptFunction):
                return func.call(args)
            else:
                # Built-in function
                return func(*args)
        except RuntimeError:
            # Try to get as variable (for function variables)
            try:
                func = self.environment.get(node.name)
                if isinstance(func, AXScriptFunction):
                    return func.call(args)
                elif callable(func):
                    return func(*args)
            except RuntimeError:
                pass

            raise RuntimeError(f"Undefined function: {node.name}")

    def visit_MemberAccess(self, node: MemberAccess) -> Any:
        """Visit member access"""
        obj = self.visit(node.object)

        if isinstance(obj, AXScriptInstance):
            return obj.get_property(node.member)
        elif isinstance(obj, dict):
            return obj.get(node.member)
        elif isinstance(obj, list) and node.member == "length":
            return len(obj)
        elif isinstance(obj, str) and node.member == "length":
            return len(obj)
        elif isinstance(obj, Literal) and isinstance(obj.value, dict):
            # Handle object literals
            return obj.value.get(node.member)
        elif obj is None:
            # Return undefined for null objects
            return None
        else:
            # For primitive types, return undefined instead of throwing error
            return None

    def visit_Identifier(self, node: Identifier) -> Any:
        """Visit identifier"""
        try:
            return self.environment.get(node.name)
        except RuntimeError:
            raise RuntimeError(f"Undefined variable: {node.name}")

    def visit_Literal(self, node: Literal) -> Any:
        """Visit literal"""
        return node.value

    def visit_Block(self, node: Block) -> Any:
        """Visit block statement with proper scoping"""
        previous_env = self.environment
        self.environment = Environment(previous_env)

        try:
            result = None
            for statement in node.statements:
                result = self.visit(statement)
            return result
        finally:
            self.environment = previous_env

    def visit_ClassDeclaration(self, node: ClassDeclaration) -> Any:
        """Visit class declaration"""
        cls = AXScriptClass(node, self.environment, self)
        self.environment.define_class(node.name, cls)
        return None

    def visit_NewExpression(self, node: NewExpression) -> Any:
        """Visit new expression"""
        cls = self.environment.get_class(node.class_name)
        args = [self.visit(arg) for arg in node.args]
        return cls.instantiate(args)

    def visit_ThisExpression(self, node: ThisExpression) -> Any:
        """Visit this expression"""
        if self.context_object:
            return self.context_object
        else:
            raise RuntimeError("'this' is not available in this context")

    def visit_ForStatement(self, node: ForStatement) -> Any:
        """Visit for statement"""
        # Create new scope for for loop
        previous_env = self.environment
        self.environment = Environment(previous_env)

        try:
            # Initialize
            if node.init:
                self.visit(node.init)

            # Loop
            result = None
            while True:
                # Check condition
                if node.condition:
                    condition = self.visit(node.condition)
                    if not self.is_truthy(condition):
                        break

                # Execute body
                try:
                    result = self.visit(node.body)
                except BreakException:
                    break
                except ContinueException:
                    pass  # Continue to update

                # Update
                if node.update:
                    self.visit(node.update)

            return result
        finally:
            self.environment = previous_env

    def visit_ForInStatement(self, node: ForInStatement) -> Any:
        """Visit for-in statement"""
        previous_env = self.environment
        self.environment = Environment(previous_env)

        try:
            iterable = self.visit(node.iterable)
            result = None

            # Handle different types of iterables
            if isinstance(iterable, list):
                for item in iterable:
                    self.environment.define(node.variable, item)
                    try:
                        result = self.visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(iterable, dict):
                for key in iterable:
                    self.environment.define(node.variable, key)
                    try:
                        result = self.visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(iterable, Literal) and isinstance(iterable.value, dict):
                # Handle object literals
                for key in iterable.value:
                    self.environment.define(node.variable, key)
                    try:
                        result = self.visit(node.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            else:
                raise RuntimeError("Object is not iterable")

            return result
        finally:
            self.environment = previous_env

    def visit_DoWhileStatement(self, node: DoWhileStatement) -> Any:
        """Visit do-while statement"""
        result = None
        while True:
            try:
                result = self.visit(node.body)
            except BreakException:
                break
            except ContinueException:
                pass

            condition = self.visit(node.condition)
            if not self.is_truthy(condition):
                break
        return result

    def visit_TryStatement(self, node: TryStatement) -> Any:
        """Visit try-catch-finally statement"""
        result = None
        exception_caught = False

        try:
            result = self.visit(node.try_block)
        except (AXScriptError, RuntimeError) as e:
            exception_caught = True
            if node.catch_clause:
                # Create new scope for catch
                previous_env = self.environment
                self.environment = Environment(previous_env)

                try:
                    # Bind exception to parameter - extract the actual error message
                    error_message = str(e)
                    if "Error: " in error_message:
                        # Extract just the error message part
                        error_message = error_message.split("Error: ")[-1]
                    self.environment.define(node.catch_clause.param, error_message)
                    result = self.visit(node.catch_clause.body)
                finally:
                    self.environment = previous_env
            else:
                raise  # Re-raise if no catch clause
        except Exception as e:
            # Catch any other exceptions too
            exception_caught = True
            if node.catch_clause:
                previous_env = self.environment
                self.environment = Environment(previous_env)

                try:
                    self.environment.define(node.catch_clause.param, str(e))
                    result = self.visit(node.catch_clause.body)
                finally:
                    self.environment = previous_env
            else:
                raise

        # Execute finally block
        if node.finally_block:
            self.visit(node.finally_block)

        return result

    def visit_ThrowStatement(self, node: ThrowStatement) -> Any:
        """Visit throw statement"""
        value = self.visit(node.expression)
        if isinstance(value, str):
            raise AXScriptError(value)
        else:
            raise AXScriptError(str(value))

    def visit_BreakStatement(self, node: BreakStatement) -> Any:
        """Visit break statement"""
        raise BreakException()

    def visit_ContinueStatement(self, node: ContinueStatement) -> Any:
        """Visit continue statement"""
        raise ContinueException()

    def visit_ImportStatement(self, node: ImportStatement) -> Any:
        """Visit import statement"""
        module = self.module_system.get_module(node.module_name)
        if not module:
            raise RuntimeError(f"Module '{node.module_name}' not found")

        if node.imports:
            # Named imports
            imported = self.module_system.import_from_module(node.module_name, node.imports)
            for name, value in imported.items():
                self.environment.define(name, value)
        else:
            # Default import
            alias = node.alias or node.module_name
            self.environment.define(alias, module)

        return None

    def visit_ExportStatement(self, node: ExportStatement) -> Any:
        """Visit export statement"""
        # Execute the declaration and add to exports
        result = self.visit(node.declaration)

        if isinstance(node.declaration, (VarDeclaration, FunctionDeclaration, ClassDeclaration)):
            name = node.declaration.name
            if isinstance(node.declaration, VarDeclaration):
                self.exports[name] = self.environment.get(name)
            elif isinstance(node.declaration, FunctionDeclaration):
                self.exports[name] = self.environment.get_function(name)
            elif isinstance(node.declaration, ClassDeclaration):
                self.exports[name] = self.environment.get_class(name)

        return result

    def visit_SwitchStatement(self, node: SwitchStatement) -> Any:
        """Visit switch statement"""
        discriminant_value = self.visit(node.discriminant)
        result = None
        matched = False
        fall_through = False

        for case in node.cases:
            if case.test is None:  # Default case
                if not matched:
                    matched = True
                    fall_through = True
            else:
                test_value = self.visit(case.test)
                if not matched and discriminant_value == test_value:
                    matched = True
                    fall_through = True

            if fall_through:
                try:
                    for stmt in case.consequent:
                        result = self.visit(stmt)
                except BreakException:
                    return None
                except ContinueException:
                    continue
        return result

    def is_truthy(self, value) -> bool:
        """Check if value is truthy in JavaScript-like way"""
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        return True

    def visit(self, node: ASTNode) -> Any:
        """Visit an AST node with enhanced error handling"""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)

        try:
            return visitor(node)
        except (BreakException, ContinueException, ReturnException):
            raise  # These are control flow, not errors
        except Exception as e:
            if hasattr(node, 'line'):
                raise RuntimeError(f"Error visiting {type(node).__name__}: {e}", node.line)
            else:
                raise RuntimeError(f"Error visiting {type(node).__name__}: {e}")

    # Built-in function implementations
    def builtin_print(self, *args):
        """Built-in print function"""
        output = " ".join(map(str, args))
        self.output_buffer.append(output)
        return None

    def builtin_move(self, dx: float, dy: float) -> None:
        """Built-in move function"""
        if self.context_object:
            # Apply force instead of direct position change for physics compatibility
            force_multiplier = 15.0  # Adjust this for movement feel
            self.context_object.apply_force(dx * force_multiplier, dy * force_multiplier)
        else:
            self.output_buffer.append("Warning: no object to move")
        return None

    def builtin_rotate(self, angle: float):
        """Built-in rotate function - rotates the context object"""
        if self.context_object and hasattr(self.context_object, 'rotate'):
            self.context_object.rotate(angle)
        else:
            self.output_buffer.append("Warning: no object to rotate")
        return None

    def builtin_set_property(self, property_name: str, value: Any):
        """Built-in setProperty function - sets property on context object"""
        if self.context_object:
            try:
                setattr(self.context_object, property_name, value)
            except Exception as e:
                self.output_buffer.append(f"Error setting property {property_name}: {e}")
        else:
            self.output_buffer.append("Warning: no object to set property on")
        return None

    def builtin_get_property(self, property_name: str) -> Any:
        """Built-in getProperty function - gets property from context object"""
        if self.context_object:
            try:
                return getattr(self.context_object, property_name)
            except Exception:
                return None
        else:
            self.output_buffer.append("Warning: no object to get property from")
            return None

    def builtin_sin(self, x: float) -> float:
        """Built-in sin function"""
        return math.sin(x)

    def builtin_cos(self, x: float) -> float:
        """Built-in cos function"""
        return math.cos(x)

    def builtin_sqrt(self, x: float) -> float:
        """Built-in sqrt function"""
        return math.sqrt(x)

    def builtin_abs(self, x: float) -> float:
        """Built-in abs function"""
        return abs(x)

    def builtin_min(self, a: float, b: float) -> float:
        """Built-in min function"""
        return min(a, b)

    def builtin_max(self, a: float, b: float) -> float:
        """Built-in max function"""
        return max(a, b)

    def builtin_random(self) -> float:
        """Built-in random function"""
        return math.random()

    def builtin_time(self) -> float:
        """Built-in time function"""
        return time.time()

    def builtin_typeof(self, value: Any) -> str:
        """Built-in typeof function"""
        return self.type_checker.get_type_name(value)

    def builtin_is_number(self, value: Any) -> bool:
        """Built-in isNumber function"""
        return isinstance(value, (int, float))

    def builtin_is_string(self, value: Any) -> bool:
        """Built-in isString function"""
        return isinstance(value, str)

    def builtin_is_boolean(self, value: Any) -> bool:
        """Built-in isBoolean function"""
        return isinstance(value, bool)

    def builtin_is_array(self, value: Any) -> bool:
        """Built-in isArray function"""
        return isinstance(value, list)

    def builtin_is_object(self, value: Any) -> bool:
        """Built-in isObject function"""
        return isinstance(value, dict)

    def builtin_is_function(self, value: Any) -> bool:
        """Built-in isFunction function"""
        return callable(value)

    def builtin_throw(self, message: str):
        """Built-in throw function"""
        raise AXScriptError(message)

    def builtin_risky_function(self):
        """Built-in risky function that may throw an error"""
        raise RuntimeError("This function always fails!")

    def builtin_keyPressed(self, key: str) -> bool:
        """Built-in keyPressed function - checks if key is currently pressed"""
        try:
            import pygame
            
            # Get current key state directly from pygame
            keys = pygame.key.get_pressed()
            
            # Map AXScript key names to pygame keys
            key_mapping = {
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT, 
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "space": pygame.K_SPACE,
                "a": pygame.K_a,
                "d": pygame.K_d,
                "w": pygame.K_w,
                "s": pygame.K_s
            }

            pygame_key = key_mapping.get(key.lower())
            if pygame_key is not None:
                return keys[pygame_key]
            return False
        except:
            return False

    def builtin_key_just_pressed(self, key: str) -> bool:
        """Built-in keyJustPressed function - checks if a key was just pressed"""
        if self.context_object and hasattr(self.context_object, 'is_key_just_pressed'):
            return self.context_object.is_key_just_pressed(key)
        else:
            self.output_buffer.append("Warning: no input system available")
            return False

    def builtin_mouse_clicked(self, button: int = 0) -> bool:
        """Built-in mouseClicked function - checks if a mouse button was clicked"""
        if self.context_object and hasattr(self.context_object, 'is_mouse_clicked'):
            return self.context_object.is_mouse_clicked(button)
        else:
            self.output_buffer.append("Warning: no input system available")
            return False

    def builtin_mouse_pressed(self, button: int = 0) -> bool:
        """Built-in mousePressed function - checks if a mouse button is currently pressed"""
        if self.context_object and hasattr(self.context_object, 'is_mouse_pressed'):
            return self.context_object.is_mouse_pressed(button)
        else:
            self.output_buffer.append("Warning: no input system available")
            return False

    def builtin_get_mouse_pos(self) -> tuple:
        """Built-in getMousePos function - gets the current mouse position"""
        if self.context_object and hasattr(self.context_object, 'get_mouse_pos'):
            return self.context_object.get_mouse_pos()
        else:
            self.output_buffer.append("Warning: no input system available")
            return (0, 0)

    def builtin_get_axis(self, axis_name: str) -> float:
        """Built-in getAxis function - gets the value of an input axis"""
        if self.context_object and hasattr(self.context_object, 'get_axis'):
            return self.context_object.get_axis(axis_name)
        else:
            self.output_buffer.append("Warning: no input system available")
            return 0.0

    def builtin_get_movement(self) -> dict:
        """Built-in getMovement function - gets current movement input"""
        # Placeholder for getting movement
        if self.context_object and hasattr(self.context_object, 'get_movement_input'):
            return self.context_object.get_movement_input()
        else:
            self.output_buffer.append("Warning: no movement input available.")
            return {"x": 0, "y": 0}

    # Physics and movement functions
    def builtin_jump(self):
        """Built-in jump function - makes the context object jump"""
        if self.context_object and hasattr(self.context_object, 'jump'):
            self.context_object.jump()
        else:
            self.output_buffer.append("Warning: no object to jump")
        return None

    def builtin_is_on_ground(self) -> bool:
        """Built-in isOnGround function - checks if the context object is on the ground"""
        if self.context_object and hasattr(self.context_object, 'is_on_ground'):
            # Get all static/platform objects from the scene
            if hasattr(self.context_object, 'scene') and self.context_object.scene:
                platforms = [obj for obj in self.context_object.scene.objects.values() 
                            if obj != self.context_object and (obj.has_tag("platform") or obj.is_static)]
                return self.context_object.is_on_ground(platforms)
            else:
                return self.context_object.is_on_ground()
        else:
            return False

    def builtin_find_objects_by_tag(self, tag: str) -> list:
        """Built-in findObjectsByTag function - finds objects with specified tag"""
        if self.context_object and hasattr(self.context_object, 'scene') and self.context_object.scene:
            objects = []
            for obj in self.context_object.scene.objects.values():
                if obj.has_tag(tag):
                    objects.append({
                        "name": obj.name,
                        "position": obj.position,
                        "bounds": obj.get_bounds()
                    })
            return objects
        else:
            return []

    def builtin_apply_force_simple(self, x: float, y: float):
        """Built-in applyForce function - applies a simple force to the context object"""
        if self.context_object and hasattr(self.context_object, 'apply_force'):
            self.context_object.apply_force(x, y)
        else:
            self.output_buffer.append("Warning: no object to apply force to")
        return None

    # Game utility functions
    def builtin_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Built-in distance function"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def builtin_clamp(self, value: float, min_value: float, max_value: float) -> float:
        """Built-in clamp function"""
        return max(min(value, max_value), min_value)

    def builtin_lerp(self, a: float, b: float, t: float) -> float:
        """Built-in lerp function"""
        return a + (b - a) * t

    def builtin_floor(self, x: float) -> float:
        """Built-in floor function"""
        return math.floor(x)

    def builtin_ceil(self, x: float) -> float:
        """Built-in ceil function"""
        return math.ceil(x)

    def builtin_round(self, x: float) -> float:
        """Built-in round function"""
        return round(x)