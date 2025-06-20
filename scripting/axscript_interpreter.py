"""
AXScript Interpreter
Executes AXScript AST nodes and provides runtime environment
"""

import math
import time
from typing import Dict, Any, List, Optional, Callable, Union
from .axscript_parser import (
    AXScriptParser, ASTNode, Program, Statement, Expression,
    VarDeclaration, FunctionDeclaration, IfStatement, WhileStatement,
    ReturnStatement, ExpressionStatement, Block, BinaryOp, UnaryOp,
    Assignment, FunctionCall, MemberAccess, Identifier, Literal
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

class Environment:
    """Runtime environment for variable and function storage"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
    
    def define(self, name: str, value: Any):
        """Define a variable in this environment"""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get a variable value"""
        if name in self.variables:
            return self.variables[name]
        
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

class AXScriptFunction:
    """User-defined AXScript function"""
    
    def __init__(self, declaration: FunctionDeclaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter: 'AXScriptInterpreter', arguments: List[Any]) -> Any:
        """Call the function"""
        # Create new environment for function execution
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        if len(arguments) != len(self.declaration.params):
            raise RuntimeError(f"Expected {len(self.declaration.params)} arguments but got {len(arguments)}")
        
        for i, param in enumerate(self.declaration.params):
            environment.define(param, arguments[i])
        
        # Execute function body
        previous_env = interpreter.environment
        interpreter.environment = environment
        
        try:
            for stmt in self.declaration.body:
                interpreter.execute(stmt)
        except ReturnException as ret:
            return ret.value
        finally:
            interpreter.environment = previous_env
        
        return None

class AXScriptInterpreter:
    """Interpreter for AXScript language"""
    
    def __init__(self):
        self.parser = AXScriptParser()
        self.global_env = Environment()
        self.environment = self.global_env
        self.context_object = None  # Current game object context
        self.output_buffer = []
        
        # Initialize built-in functions
        self.init_builtins()
    
    def init_builtins(self):
        """Initialize built-in functions and variables"""
        # Built-in functions
        self.global_env.define_function("print", self.builtin_print)
        self.global_env.define_function("move", self.builtin_move)
        self.global_env.define_function("rotate", self.builtin_rotate)
        self.global_env.define_function("setProperty", self.builtin_set_property)
        self.global_env.define_function("getProperty", self.builtin_get_property)
        self.global_env.define_function("sin", self.builtin_sin)
        self.global_env.define_function("cos", self.builtin_cos)
        self.global_env.define_function("sqrt", self.builtin_sqrt)
        self.global_env.define_function("abs", self.builtin_abs)
        self.global_env.define_function("min", self.builtin_min)
        self.global_env.define_function("max", self.builtin_max)
        self.global_env.define_function("random", self.builtin_random)
        self.global_env.define_function("time", self.builtin_time)
        
        # Input functions
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
    
    def execute(self, code_or_node: Union[str, ASTNode], context_object=None) -> Dict[str, Any]:
        """Execute AXScript code or AST node"""
        self.context_object = context_object
        self.output_buffer = []
        
        try:
            if isinstance(code_or_node, str):
                # Parse the code first
                ast = self.parser.parse(code_or_node)
                self.visit(ast)
            else:
                # Execute AST node directly
                self.visit(code_or_node)
            
            return {
                "success": True,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": None
            }
            
        except (RuntimeError, Exception) as e:
            return {
                "success": False,
                "output": "\n".join(self.output_buffer) if self.output_buffer else None,
                "error": str(e)
            }
    
    def parse(self, code: str) -> Dict[str, Any]:
        """Parse AXScript code and return result"""
        try:
            ast = self.parser.parse(code)
            return {
                "success": True,
                "ast": ast,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "ast": None,
                "error": str(e)
            }
    
    def visit(self, node: ASTNode) -> Any:
        """Visit an AST node"""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Any:
        """Default visitor for unhandled node types"""
        raise RuntimeError(f"No visit method for {type(node).__name__}")
    
    def visit_Program(self, node: Program) -> Any:
        """Visit program node"""
        result = None
        for statement in node.statements:
            result = self.visit(statement)
        return result
    
    def visit_Block(self, node: Block) -> Any:
        """Visit block statement"""
        # Create new environment for block scope
        previous_env = self.environment
        self.environment = Environment(previous_env)
        
        try:
            result = None
            for statement in node.statements:
                result = self.visit(statement)
            return result
        finally:
            self.environment = previous_env
    
    def visit_VarDeclaration(self, node: VarDeclaration) -> Any:
        """Visit variable declaration"""
        value = None
        if node.value:
            value = self.visit(node.value)
        
        self.environment.define(node.name, value)
        return value
    
    def visit_FunctionDeclaration(self, node: FunctionDeclaration) -> Any:
        """Visit function declaration"""
        function = AXScriptFunction(node, self.environment)
        self.environment.define_function(node.name, function)
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
        while self.is_truthy(self.visit(node.condition)):
            result = self.visit(node.body)
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
            # Handle string concatenation
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
        self.environment.set(node.target, value)
        return value
    
    def visit_FunctionCall(self, node: FunctionCall) -> Any:
        """Visit function call"""
        # Evaluate arguments
        args = [self.visit(arg) for arg in node.args]
        
        # Get function
        try:
            func = self.environment.get_function(node.name)
        except RuntimeError:
            raise RuntimeError(f"Undefined function: {node.name}")
        
        # Call function
        if callable(func) and hasattr(func, '__self__'):
            # Built-in function (method)
            return func(*args)
        elif hasattr(func, 'call'):
            # User-defined AXScript function
            return func.call(self, args)
        else:
            # Other callable
            return func(*args)
    
    def visit_MemberAccess(self, node: MemberAccess) -> Any:
        """Visit member access"""
        obj = self.visit(node.object)
        
        # Handle special case for 'this' object
        if isinstance(node.object, Identifier) and node.object.name == "this":
            if self.context_object:
                return self.get_object_property(self.context_object, node.member)
            else:
                raise RuntimeError("'this' is not available in this context")
        
        # For other objects, try to access as dictionary
        if isinstance(obj, dict) and node.member in obj:
            return obj[node.member]
        
        raise RuntimeError(f"Cannot access property '{node.member}' on object")
    
    def visit_Identifier(self, node: Identifier) -> Any:
        """Visit identifier"""
        if node.name == "this":
            if self.context_object:
                return self.create_object_proxy(self.context_object)
            else:
                raise RuntimeError("'this' is not available in this context")
        
        return self.environment.get(node.name)
    
    def visit_Literal(self, node: Literal) -> Any:
        """Visit literal"""
        return node.value
    
    def is_truthy(self, value: Any) -> bool:
        """Check if value is truthy"""
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        return True
    
    def create_object_proxy(self, game_object) -> Dict[str, Any]:
        """Create a proxy object for game object access"""
        return {
            "position": {"x": game_object.position[0], "y": game_object.position[1]},
            "name": game_object.name,
            "visible": game_object.visible,
            "active": game_object.active,
            "type": game_object.object_type
        }
    
    def get_object_property(self, game_object, property_name: str) -> Any:
        """Get property from game object"""
        if property_name == "position":
            return {"x": game_object.position[0], "y": game_object.position[1]}
        elif property_name == "name":
            return game_object.name
        elif property_name == "visible":
            return game_object.visible
        elif property_name == "active":
            return game_object.active
        elif property_name == "type":
            return game_object.object_type
        else:
            return game_object.get_property(property_name)
    
    # Built-in functions
    def builtin_print(self, *args) -> None:
        """Print function"""
        message = " ".join(str(arg) for arg in args)
        self.output_buffer.append(message)
        print(message)  # Also print to console
    
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
        
        # Handle special properties
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
        
        return self.get_object_property(self.context_object, name)
    
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
    
    # Input functions for game control
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
    
    # Utility functions for game development
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
    
    def reset(self):
        """Reset interpreter state"""
        self.environment = Environment()
        self.environment.parent = self.global_env
        self.context_object = None
        self.output_buffer = []
