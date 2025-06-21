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
        self.global_env.define_function("keyPressed", self.builtin_key_pressed)
        self.global_env.define_function("keyJustPressed", self.builtin_key_just_pressed)
        self.global_env.define_function("mouseClicked", self.builtin_mouse_clicked)
        self.global_env.define_function("mousePressed", self.builtin_mouse_pressed)
        self.global_env.define_function("getMousePos", self.builtin_get_mouse_pos)
        self.global_env.define_function("getAxis", self.builtin_get_axis)
        self.global_env.define_function("getMovement", self.builtin_get_movement)

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
                # Parse the code first
                ast = self.parser.parse(code_or_node)
                self.visit(ast)
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

        except (RuntimeError, AXScriptError, Exception) as e:
            error_info = {
                "success": False,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": str(e),
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
        elif isinstance(obj, Literal) and isinstance(obj.value, dict):
            # Handle object literals
            return obj.value.get(node.member)
        else:
            raise RuntimeError(f"Cannot access property '{node.member}' on {type(obj)}")

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
                    fall_through = False
                    break

        return result

    def visit_ArrayExpression(self, node: ArrayExpression) -> Any:
        """Visit array expression"""
        return [self.visit(element) for element in node.elements]

    def visit_IndexAccess(self, node: IndexAccess) -> Any:
        """Visit index access"""
        obj = self.visit(node.object)
        index = self.visit(node.index)

        if isinstance(obj, (list, tuple)):
            if isinstance(index, int):
                if 0 <= index < len(obj):
                    return obj[index]
                else:
                    # Return undefined instead of throwing for out of bounds
                    return None
            else:
                raise RuntimeError("Array index must be a number")
        elif isinstance(obj, dict):
            return obj.get(str(index))
        elif isinstance(obj, str):
            if isinstance(index, int) and 0 <= index < len(obj):
                return obj[index]
            else:
                raise RuntimeError("String index out of bounds")
        else:
            raise RuntimeError("Object is not indexable")

    def visit_ConditionalExpression(self, node: ConditionalExpression) -> Any:
        """Visit conditional (ternary) expression"""
        test = self.visit(node.test)
        if self.is_truthy(test):
            return self.visit(node.consequent)
        else:
            return self.visit(node.alternate)

    def visit_UpdateExpression(self, node: UpdateExpression) -> Any:
        """Visit update expression (++/--)"""
        if isinstance(node.operand, Identifier):
            current_value = self.environment.get(node.operand.name)
            if not isinstance(current_value, (int, float)):
                raise RuntimeError("Update operators can only be applied to numbers")

            if node.operator == "++":
                new_value = current_value + 1
            else:  # "--"
                new_value = current_value - 1

            self.environment.set(node.operand.name, new_value)

            if node.prefix:
                return new_value
            else:
                return current_value
        else:
            raise RuntimeError("Update operators can only be applied to variables")

    def visit_TypeofExpression(self, node: TypeofExpression) -> Any:
        """Visit typeof expression"""
        try:
            value = self.visit(node.operand)
            return self.get_typeof(value)
        except RuntimeError:
            return "undefined"

    def visit_InstanceofExpression(self, node: InstanceofExpression) -> Any:
        """Visit instanceof expression"""
        obj = self.visit(node.left)
        cls = self.visit(node.right)

        if isinstance(obj, AXScriptInstance) and isinstance(cls, AXScriptClass):
            current_class = obj.cls
            while current_class:
                if current_class== cls:
                    return True
                current_class = current_class.superclass
            return False

        # Built-in type checking
        if cls == list:
            return isinstance(obj, list)
        elif cls == dict:
            return isinstance(obj, dict)
        elif cls == str:
            return isinstance(obj, str)
        elif cls == (int, float):
            return isinstance(obj, (int, float))
        elif cls == bool:
            return isinstance(obj, bool)

        return False

    # Enhanced utility methods
    def get_typeof(self, value: Any) -> str:
        """Get the type of a value as a string"""
        if value is None:
            return "undefined"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif callable(value):
            return "function"
        elif isinstance(value, AXScriptInstance):
            return "object"
        elif isinstance(value, AXScriptClass):
            return "function"
        else:
            return "object"

    def is_truthy(self, value: Any) -> bool:
        """Enhanced truthiness check"""
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        return True

    # Enhanced built-in functions
    def builtin_typeof(self, value: Any) -> str:
        """Get type of value"""
        return self.get_typeof(value)

    def builtin_is_number(self, value: Any) -> bool:
        """Check if value is a number"""
        return isinstance(value, (int, float))

    def builtin_is_string(self, value: Any) -> bool:
        """Check if value is a string"""
        return isinstance(value, str)

    def builtin_is_boolean(self, value: Any) -> bool:
        """Check if value is a boolean"""
        return isinstance(value, bool)

    def builtin_is_array(self, value: Any) -> bool:
        """Check if value is an array"""
        return isinstance(value, list)

    def builtin_is_object(self, value: Any) -> bool:
        """Check if value is an object"""
        return isinstance(value, (dict, AXScriptInstance))

    def builtin_is_function(self, value: Any) -> bool:
        """Check if value is a function"""
        return callable(value)

    def builtin_throw(self, message: str) -> None:
        """Throw an error"""
        raise AXScriptError(str(message))

    def builtin_risky_function(self, x=None) -> int:
        """Risky function that throws an error for testing"""
        if x is not None and x < 0:
            raise AXScriptError("Negative number not allowed!")
        return x * 2 if x is not None else 10

    # Keep all the existing built-in functions from before...
    def builtin_print(self, *args) -> None:
        """Print function"""
        message = " ".join(str(arg) for arg in args)
        self.output_buffer.append(message)
        print(message)

    def builtin_move(self, dx: float, dy: float = 0) -> None:
        """Move the current object"""
        if not self.context_object:
            raise RuntimeError("move() can only be called in object context")

        x, y = self.context_object.position
        self.context_object.position = (x + dx, y + dy)

    def builtin_rotate(self, angle: float) -> None:
        """Rotate the current object"""
        if not self.context_object:
            raise RuntimeError("rotate() can only be called in object context")

        self.context_object.rotation += angle

    def builtin_set_property(self, name: str, value: Any) -> None:
        """Set property on current object"""
        if not self.context_object:
            raise RuntimeError("setProperty() can only be called in object context")

        if name == "position":
            if isinstance(value, dict) and "x" in value and "y" in value:
                self.context_object.position = (value["x"], value["y"])
            else:
                raise RuntimeError("Position must be an object with x and y properties")
        elif name == "visible":
            self.context_object.visible = bool(value)
        elif name == "active":
            self.context_object.active = bool(value)
        elif name == "color":
            # Parse color string "r,g,b" or use tuple
            if isinstance(value, str):
                try:
                    rgb = [int(x.strip()) for x in value.split(",")]
                    if len(rgb) == 3:
                        self.context_object.set_property("color", tuple(rgb))
                    else:
                        raise ValueError("Invalid color format")
                except ValueError:
                    raise RuntimeError("Color must be in format 'r,g,b' or a tuple")
            else:
                self.context_object.set_property(name, value)
        else:
            self.context_object.set_property(name, value)

    def builtin_get_property(self, name: str) -> Any:
        """Get property from current object"""
        if not self.context_object:
            raise RuntimeError("getProperty() can only be called in object context")

        if name == "position":
            return {"x": self.context_object.position[0], "y": self.context_object.position[1]}
        elif name == "name":
            return self.context_object.name
        elif name == "visible":
            return self.context_object.visible
        elif name == "active":
            return self.context_object.active
        elif name == "type":
            return self.context_object.object_type
        else:
            return self.context_object.get_property(name)

    # Math functions
    def builtin_sin(self, x: float) -> float:
        """Sine function"""
        return math.sin(x)

    def builtin_cos(self, x: float) -> float:
        """Cosine function"""
        return math.cos(x)

    def builtin_sqrt(self, x: float) -> float:
        """Square root function"""
        if x < 0:
            raise RuntimeError("Cannot take square root of negative number")
        return math.sqrt(x)

    def builtin_abs(self, x: float) -> float:
        """Absolute value function"""
        return abs(x)

    def builtin_min(self, *args) -> float:
        """Minimum function"""
        if not args:
            raise RuntimeError("min() requires at least one argument")
        return min(args)

    def builtin_max(self, *args) -> float:
        """Maximum function"""
        if not args:
            raise RuntimeError("max() requires at least one argument")
        return max(args)

    def builtin_random(self) -> float:
        """Random number function (0-1)"""
        import random
        return random.random()

    def builtin_time(self) -> float:
        """Current time in seconds"""
        return time.time()

    # Input functions (keeping existing implementations)
    def builtin_key_pressed(self, key: str) -> bool:
        """Check if key is currently pressed"""
        try:
            from engine.input_system import key_pressed
            return key_pressed(str(key))
        except:
            return False

    def builtin_key_just_pressed(self, key: str) -> bool:
        """Check if key was just pressed this frame"""
        try:
            from engine.input_system import key_just_pressed
            return key_just_pressed(str(key))
        except:
            return False

    def builtin_mouse_clicked(self, button: int = 0) -> bool:
        """Check if mouse button was just clicked"""
        try:
            from engine.input_system import mouse_clicked
            return mouse_clicked(button)
        except:
            return False

    def builtin_mouse_pressed(self, button: int = 0) -> bool:
        """Check if mouse button is currently pressed"""
        try:
            from engine.input_system import mouse_pressed
            return mouse_pressed(button)
        except:
            return False

    def builtin_get_mouse_pos(self) -> Dict[str, int]:
        """Get current mouse position"""
        try:
            from engine.input_system import get_mouse_pos
            x, y = get_mouse_pos()
            return {"x": x, "y": y}
        except:
            return {"x": 0, "y": 0}

    def builtin_get_axis(self, axis_name: str) -> float:
        """Get axis value for movement"""
        try:
            from engine.input_system import get_axis
            return get_axis(str(axis_name))
        except:
            return 0.0

    def builtin_get_movement(self) -> Dict[str, float]:
        """Get movement vector from input"""
        try:
            from engine.input_system import get_movement
            x, y = get_movement()
            return {"x": x, "y": y}
        except:
            return {"x": 0.0, "y": 0.0}

    # Utility functions
    def builtin_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance between two points"""
        try:
            dx = x2 - x1
            dy = y2 - y1
            return math.sqrt(dx * dx + dy * dy)
        except:
            return 0.0

    def builtin_clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))

    def builtin_lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between two values"""
        return a + (b - a) * t

    def builtin_floor(self, x: float) -> int:
        """Floor function"""
        return math.floor(x)

    def builtin_ceil(self, x: float) -> int:
        """Ceiling function"""
        return math.ceil(x)

    def builtin_round(self, x: float) -> int:
        """Round function"""
        return round(x)

    # Audio functions
    def builtin_play_sound(self, sound_name: str, loops: int = 0) -> bool:
        """Play sound effect"""
        try:
            from engine.audio_system import play_sound
            return play_sound(sound_name, loops)
        except:
            return False

    def builtin_play_music(self, file_path: str, loops: int = -1) -> bool:
        """Play background music"""
        try:
            from engine.audio_system import play_music
            return play_music(file_path, loops)
        except:
            return False

    def builtin_stop_music(self) -> None:
        """Stop background music"""
        try:
            from engine.audio_system import stop_music
            stop_music()
        except:
            pass

    def builtin_set_volume(self, music_vol: float, sfx_vol: float) -> None:
        """Set audio volumes"""
        try:
            from engine.audio_system import set_volume
            set_volume(music_vol, sfx_vol)
        except:
            pass

    # Animation functions
    def builtin_animate_to(self, x: float, y: float, duration: float = 1.0) -> None:
        """Animate object to position"""
        if not self.context_object:
            raise RuntimeError("animateTo() can only be called in object context")

        try:
            from engine.animation_system import animate_to
            animate_to(self.context_object, x, y, duration)
        except:
            pass

    def builtin_rotate_to(self, angle: float, duration: float = 1.0) -> None:
        """Rotate object to angle"""
        if not self.context_object:
            raise RuntimeError("rotateTo() can only be called in object context")

        try:
            from engine.animation_system import animation_system
            animation_system.rotate_to(self.context_object, angle, duration)
        except:
            pass

    def builtin_scale_to(self, scale_x: float, scale_y: float, duration: float = 1.0) -> None:
        """Scale object"""
        if not self.context_object:
            raise RuntimeError("scaleTo() can only be called in object context")

        try:
            from engine.animation_system import animation_system
            animation_system.scale_to(self.context_object, scale_x, scale_y, duration)
        except:
            pass

    def builtin_bounce(self, height: float = 50, duration: float = 1.0) -> None:
        """Make object bounce"""
        if not self.context_object:
            raise RuntimeError("bounce() can only be called in object context")

        try:
            from engine.animation_system import bounce_object
            bounce_object(self.context_object, height, duration)
        except:
            pass

    def builtin_pulse(self, scale: float = 1.2, duration: float = 0.5) -> None:
        """Make object pulse"""
        if not self.context_object:
            raise RuntimeError("pulse() can only be called in object context")

        try:
            from engine.animation_system import pulse_object
            pulse_object(self.context_object, scale, duration)
        except:
            pass

    # Particle effect functions
    def builtin_create_explosion(self, x: float, y: float, intensity: int = 50) -> None:
        """Create explosion particle effect"""
        try:
            from engine.particle_system import particle_system
            particle_system.create_explosion(x, y, intensity)
        except:
            pass

    def builtin_create_fire(self, x: float, y: float) -> None:
        """Create fire particle effect"""
        try:
            from engine.particle_system import particle_system
            particle_system.create_fire(x, y)
        except:
            pass

    def builtin_create_smoke(self, x: float, y: float) -> None:
        """Create smoke particle effect"""
        try:
            from engine.particle_system import particle_system
            particle_system.create_smoke(x, y)
        except:
            pass

    # GameObject management functions
    def builtin_destroy(self) -> None:
        """Destroy current object"""
        if self.context_object:
            self.context_object.destroyed = True

    def builtin_instantiate(self, object_type: str, x: float, y: float) -> str:
        """Create new object and add to scene"""
        if not self.context_object or not self.context_object.scene:
            return ""

        from engine.game_object import GameObject
        new_obj = GameObject(f"New_{object_type}", object_type)
        new_obj.position = (x, y)
        return self.context_object.scene.add_object(new_obj)

    def builtin_find_object_by_name(self, name: str):
        """Find object by name in current scene"""
        if not self.context_object or not self.context_object.scene:
            return None

        objects = self.context_object.scene.get_objects_by_name(name)
        return objects[0] if objects else None

    def builtin_find_objects_by_tag(self, tag: str) -> List:
        """Find all objects with tag"""
        if not self.context_object or not self.context_object.scene:
            return []

        results = []
        for obj in self.context_object.scene.get_all_objects():
            if obj.has_tag(tag):
                results.append(obj)
        return results

    def builtin_add_tag(self, tag: str) -> None:
        """Add tag to current object"""
        if self.context_object:
            self.context_object.add_tag(tag)

    def builtin_has_tag(self, tag: str) -> bool:
        """Check if current object has tag"""
        if self.context_object:
            return self.context_object.has_tag(tag)
        return False

    def builtin_look_at(self, x: float, y: float) -> None:
        """Make object look at position"""
        if self.context_object:
            self.context_object.look_at((x, y))

    def builtin_move_towards(self, x: float, y: float, speed: float) -> None:
        """Move towards position"""
        if self.context_object:
            self.context_object.move_towards((x, y), speed * 0.016)

    # Combat and RPG functions
    def builtin_take_damage(self, damage: float) -> bool:
        """Take damage"""
        if self.context_object:
            return self.context_object.take_damage(damage)
        return False

    def builtin_heal(self, amount: float) -> None:
        """Heal object"""
        if self.context_object:
            self.context_object.heal(amount)

    def builtin_add_item(self, item_name: str, quantity: int = 1) -> None:
        """Add item to inventory"""
        if self.context_object:
            item = {"name": item_name, "quantity": quantity}
            self.context_object.add_item(item)

    def builtin_remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        if self.context_object:
            return self.context_object.remove_item(item_name)
        return False

    def builtin_has_item(self, item_name: str) -> bool:
        """Check if has item"""
        if self.context_object:
            return self.context_object.has_item(item_name)
        return False

    def builtin_equip_item(self, slot: str, item_name: str) -> None:
        """Equip item"""
        if self.context_object and self.context_object.has_item(item_name):
            item = {"name": item_name}
            self.context_object.equip_item(slot, item)

    def builtin_get_stat(self, stat_name: str) -> float:
        """Get stat value"""
        if self.context_object:
            return self.context_object.get_stat(stat_name)
        return 0.0

    def builtin_set_stat(self, stat_name: str, value: float) -> None:
        """Set stat value"""
        if self.context_object:
            self.context_object.stats[stat_name] = value

    # AI and behavior functions
    def builtin_set_state(self, state: str) -> None:
        """Set AI state"""
        if self.context_object:
            self.context_object.ai_state = state

    def builtin_get_state(self) -> str:
        """Get AI state"""
        if self.context_object:
            return self.context_object.ai_state
        return "idle"

    def builtin_set_target(self, target_name: str) -> None:
        """Set target object"""
        if self.context_object and self.context_object.scene:
            targets = self.context_object.scene.get_objects_by_name(target_name)
            self.context_object.target = targets[0] if targets else None

    def builtin_get_target(self):
        """Get target object"""
        if self.context_object:
            return self.context_object.target
        return None

    def builtin_set_patrol_route(self, points: List) -> None:
        """Set patrol route"""
        if self.context_object:
            patrol_points = [(p["x"], p["y"]) for p in points if "x" in p and "y" in p]
            self.context_object.set_patrol_route(patrol_points)

    def builtin_get_next_patrol_point(self):
        """Get next patrol point"""
        if self.context_object:
            point = self.context_object.get_next_patrol_point()
            if point:
                return {"x": point[0], "y": point[1]}
        return None

    # Timer functions
    def builtin_start_timer(self, timer_name: str, duration: float) -> None:
        """Start timer"""
        if self.context_object:
            self.context_object.start_timer(timer_name, duration)

    def builtin_get_timer(self, timer_name: str) -> float:
        """Get timer remaining time"""
        if self.context_object:
            return self.context_object.get_timer(timer_name)
        return 0.0

    def builtin_is_timer_finished(self, timer_name: str) -> bool:
        """Check if timer finished"""
        if self.context_object:
            return self.context_object.is_timer_finished(timer_name)
        return True

    # Collision functions
    def builtin_is_colliding_with(self, object_name: str) -> bool:
        """Check collision with named object"""
        if not self.context_object or not self.context_object.scene:
            return False

        objects = self.context_object.scene.get_objects_by_name(object_name)
        for obj in objects:
            if self.context_object.is_colliding_with(obj):
                return True
        return False

    def builtin_get_colliding_objects(self) -> List[str]:
        """Get list of colliding object names"""
        if not self.context_object or not self.context_object.scene:
            return []

        colliding = []
        for obj in self.context_object.scene.get_all_objects():
            if obj != self.context_object and self.context_object.is_colliding_with(obj):
                colliding.append(obj.name)
        return colliding

    def builtin_set_collision_layer(self, layer: str) -> None:
        """Set collision layer"""
        if self.context_object:
            self.context_object.collision_layer = layer

    # Global variables and events
    def builtin_set_global(self, name: str, value) -> None:
        """Set global variable"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.set_global_variable(name, value)
        except:
            pass

    def builtin_get_global(self, name: str, default=None):
        """Get global variable"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                return engine_instance.get_global_variable(name, default)
        except:
            pass
        return default

    def builtin_emit_event(self, event_name: str, data=None) -> None:
        """Emit global event"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.emit_event(event_name, data)
        except:
            pass

    def builtin_subscribe_event(self, event_name: str, callback_name: str) -> None:
        """Subscribe to global event"""
        # This would need more complex implementation for script callbacks
        pass

    # Scene functions
    def builtin_change_scene(self, scene_name: str) -> None:
        """Change to different scene"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.load_scene(scene_name)
        except:
            pass

    def builtin_pause_game(self) -> None:
        """Pause the game"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.pause_game()
        except:
            pass

    def builtin_resume_game(self) -> None:
        """Resume the game"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.resume_game()
        except:
            pass

    def builtin_set_time_scale(self, scale: float) -> None:
        """Set time scale"""
        try:
            from engine.core import engine_instance
            if engine_instance:
                engine_instance.set_time_scale(scale)
        except:
            pass

    # Genre-specific functions
    def builtin_jump(self, force: float = 300.0) -> None:
        """Jump (platformer)"""
        if self.context_object:
            vel_x, vel_y = self.context_object.velocity
            self.context_object.velocity = (vel_x, -force)

    def builtin_is_on_ground(self) -> bool:
        """Check if on ground (platformer)"""
        if not self.context_object or not self.context_object.scene:
            return False

        # Simple ground check - could be improved
        bounds = self.context_object.get_bounds()
        ground_y = 450  # Hardcoded for now
        return abs(bounds[3] - ground_y) < 5

    def builtin_set_gravity(self, gravity: float) -> None:
        """Set gravity scale"""
        if self.context_object:
            self.context_object.gravity_scale = gravity

    def builtin_create_bullet(self, target_x: float, target_y: float, speed: float = 400.0) -> str:
        """Create bullet (shooter)"""
        if not self.context_object or not self.context_object.scene:
            return ""

        from engine.game_object import GameObject
        import math

        bullet = GameObject("Bullet", "circle")
        bullet.position = self.context_object.position
        bullet.set_property("radius", 3)
        bullet.set_property("color", (255, 255, 0))
        bullet.add_tag("bullet")

        # Calculate velocity
        dx = target_x - self.context_object.position[0]
        dy = target_y - self.context_object.position[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            bullet.velocity = ((dx / distance) * speed, (dy / distance) * speed)

        return self.context_object.scene.add_object(bullet)

    def builtin_create_explosion_at(self, x: float, y: float, intensity: int = 50) -> None:
        """Create explosion at position"""
        try:
            from engine.particle_system import particle_system
            particle_system.create_explosion(x, y, intensity)
        except:
            pass

    def builtin_apply_force(self, force_x: float, force_y: float) -> None:
        """Apply force (racing/physics)"""
        if self.context_object:
            vel_x, vel_y = self.context_object.velocity
            self.context_object.velocity = (vel_x + force_x * 0.016, vel_y + force_y * 0.016)

    def builtin_set_brake(self, brake_force: float) -> None:
        """Apply brakes (racing)"""
        if self.context_object:
            vel_x, vel_y = self.context_object.velocity
            factor = max(0, 1 - brake_force * 0.016)
            self.context_object.velocity = (vel_x * factor, vel_y * factor)

    def builtin_snap_to_grid(self, grid_size: int = 32) -> None:
        """Snap to grid (puzzle)"""
        if self.context_object:
            x, y = self.context_object.position
            snapped_x = round(x / grid_size) * grid_size
            snapped_y = round(y / grid_size) * grid_size
            self.context_object.position = (snapped_x, snapped_y)

    def builtin_get_grid_position(self, grid_size: int = 32) -> Dict[str, int]:
        """Get grid position (puzzle)"""
        if self.context_object:
            x, y = self.context_object.position
            return {"x": int(x // grid_size), "y": int(y // grid_size)}
        return {"x": 0, "y": 0}

    def reset(self):
        """Reset interpreter state"""
        self.environment = Environment()
        self.environment.parent = self.global_env
        self.context_object = None
        self.output_buffer = []
        self.type_checker.clear_errors()
        self.exports = {}