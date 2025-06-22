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
        
        # GameObject functions
        self.global_env.define_function("destroy", self.builtin_destroy)
        self.global_env.define_function("instantiate", self.builtin_instantiate)
        self.global_env.define_function("findObjectByName", self.builtin_find_object_by_name)
        self.global_env.define_function("findObjectsByTag", self.builtin_find_objects_by_tag)
        self.global_env.define_function("addTag", self.builtin_add_tag)
        self.global_env.define_function("hasTag", self.builtin_has_tag)
        self.global_env.define_function("lookAt", self.builtin_look_at)
        self.global_env.define_function("moveTowards", self.builtin_move_towards)
        
        # Combat and RPG functions
        self.global_env.define_function("takeDamage", self.builtin_take_damage)
        self.global_env.define_function("heal", self.builtin_heal)
        self.global_env.define_function("addItem", self.builtin_add_item)
        self.global_env.define_function("removeItem", self.builtin_remove_item)
        self.global_env.define_function("hasItem", self.builtin_has_item)
        self.global_env.define_function("equipItem", self.builtin_equip_item)
        self.global_env.define_function("getStat", self.builtin_get_stat)
        self.global_env.define_function("setStat", self.builtin_set_stat)
        
        # AI and behavior functions
        self.global_env.define_function("setState", self.builtin_set_state)
        self.global_env.define_function("getState", self.builtin_get_state)
        self.global_env.define_function("setTarget", self.builtin_set_target)
        self.global_env.define_function("getTarget", self.builtin_get_target)
        self.global_env.define_function("setPatrolRoute", self.builtin_set_patrol_route)
        self.global_env.define_function("getNextPatrolPoint", self.builtin_get_next_patrol_point)
        
        # Timer functions
        self.global_env.define_function("startTimer", self.builtin_start_timer)
        self.global_env.define_function("getTimer", self.builtin_get_timer)
        self.global_env.define_function("isTimerFinished", self.builtin_is_timer_finished)
        
        # Collision functions
        self.global_env.define_function("isCollidingWith", self.builtin_is_colliding_with)
        self.global_env.define_function("getCollidingObjects", self.builtin_get_colliding_objects)
        self.global_env.define_function("setCollisionLayer", self.builtin_set_collision_layer)
        
        # Global variables and events
        self.global_env.define_function("setGlobal", self.builtin_set_global)
        self.global_env.define_function("getGlobal", self.builtin_get_global)
        self.global_env.define_function("emitEvent", self.builtin_emit_event)
        self.global_env.define_function("subscribeEvent", self.builtin_subscribe_event)
        
        # Scene functions
        self.global_env.define_function("changeScene", self.builtin_change_scene)
        self.global_env.define_function("pauseGame", self.builtin_pause_game)
        self.global_env.define_function("resumeGame", self.builtin_resume_game)
        self.global_env.define_function("setTimeScale", self.builtin_set_time_scale)
        
        # Platformer functions
        self.global_env.define_function("jump", self.builtin_jump)
        self.global_env.define_function("isOnGround", self.builtin_is_on_ground)
        self.global_env.define_function("setGravity", self.builtin_set_gravity)
        
        # Shooter functions
        self.global_env.define_function("createBullet", self.builtin_create_bullet)
        self.global_env.define_function("createExplosion", self.builtin_create_explosion_at)
        
        # Racing functions
        self.global_env.define_function("applyForce", self.builtin_apply_force)
        self.global_env.define_function("setBrake", self.builtin_set_brake)
        
        # Puzzle functions
        self.global_env.define_function("snapToGrid", self.builtin_snap_to_grid)
        self.global_env.define_function("getGridPosition", self.builtin_get_grid_position)
        
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
        
        # Audio functions
        self.global_env.define_function("playSound", self.builtin_play_sound)
        self.global_env.define_function("playMusic", self.builtin_play_music)
        self.global_env.define_function("stopMusic", self.builtin_stop_music)
        self.global_env.define_function("setVolume", self.builtin_set_volume)
        
        # Animation functions
        self.global_env.define_function("animateTo", self.builtin_animate_to)
        self.global_env.define_function("rotateTo", self.builtin_rotate_to)
        self.global_env.define_function("scaleTo", self.builtin_scale_to)
        self.global_env.define_function("bounce", self.builtin_bounce)
        self.global_env.define_function("pulse", self.builtin_pulse)
        
        # Particle effects
        self.global_env.define_function("createExplosion", self.builtin_create_explosion)
        self.global_env.define_function("createFire", self.builtin_create_fire)
        self.global_env.define_function("createSmoke", self.builtin_create_smoke)
        
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
