
"""
AXScript Type System
Provides type checking and type inference for AXScript
"""

from typing import Dict, Any, List, Optional, Union, Set
from enum import Enum

class AXType(Enum):
    """AXScript type enumeration"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    UNDEFINED = "undefined"
    OBJECT = "object"
    ARRAY = "array"
    FUNCTION = "function"
    CLASS = "class"
    ANY = "any"

class TypeInfo:
    """Type information for variables and expressions"""
    
    def __init__(self, type: AXType, subtype: Optional[str] = None, 
                 element_type: Optional['TypeInfo'] = None,
                 properties: Optional[Dict[str, 'TypeInfo']] = None):
        self.type = type
        self.subtype = subtype  # For class names
        self.element_type = element_type  # For arrays
        self.properties = properties or {}  # For objects
    
    def __str__(self):
        if self.type == AXType.ARRAY and self.element_type:
            return f"{self.element_type}[]"
        elif self.type == AXType.CLASS and self.subtype:
            return self.subtype
        else:
            return self.type.value
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Check if this type is compatible with another type"""
        if self.type == AXType.ANY or other.type == AXType.ANY:
            return True
        
        if self.type == other.type:
            if self.type == AXType.CLASS:
                return self.subtype == other.subtype
            return True
        
        # Number and string can be converted
        if (self.type == AXType.NUMBER and other.type == AXType.STRING) or \
           (self.type == AXType.STRING and other.type == AXType.NUMBER):
            return True
        
        return False

class FunctionType:
    """Function type information"""
    
    def __init__(self, param_types: List[TypeInfo], return_type: TypeInfo):
        self.param_types = param_types
        self.return_type = return_type

class ClassType:
    """Class type information"""
    
    def __init__(self, name: str, superclass: Optional[str] = None):
        self.name = name
        self.superclass = superclass
        self.methods: Dict[str, FunctionType] = {}
        self.properties: Dict[str, TypeInfo] = {}

class TypeChecker:
    """Type checker for AXScript"""
    
    def __init__(self):
        self.type_env: Dict[str, TypeInfo] = {}
        self.function_types: Dict[str, FunctionType] = {}
        self.class_types: Dict[str, ClassType] = {}
        self.errors: List[str] = []
        self.current_function_return_type: Optional[TypeInfo] = None
    
    def add_error(self, message: str, line: int = 0):
        """Add a type error"""
        self.errors.append(f"Type error at line {line}: {message}")
    
    def infer_type(self, value: Any) -> TypeInfo:
        """Infer type from runtime value"""
        if value is None:
            return TypeInfo(AXType.NULL)
        elif isinstance(value, bool):
            return TypeInfo(AXType.BOOLEAN)
        elif isinstance(value, (int, float)):
            return TypeInfo(AXType.NUMBER)
        elif isinstance(value, str):
            return TypeInfo(AXType.STRING)
        elif isinstance(value, list):
            element_type = TypeInfo(AXType.ANY)
            if value:
                element_type = self.infer_type(value[0])
            return TypeInfo(AXType.ARRAY, element_type=element_type)
        elif isinstance(value, dict):
            properties = {}
            for key, val in value.items():
                properties[key] = self.infer_type(val)
            return TypeInfo(AXType.OBJECT, properties=properties)
        else:
            return TypeInfo(AXType.ANY)
    
    def get_builtin_function_type(self, name: str) -> Optional[FunctionType]:
        """Get type information for built-in functions"""
        builtin_functions = {
            "print": FunctionType([TypeInfo(AXType.ANY)], TypeInfo(AXType.NULL)),
            "sin": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "cos": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "sqrt": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "abs": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "min": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "max": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
            "random": FunctionType([], TypeInfo(AXType.NUMBER)),
            "time": FunctionType([], TypeInfo(AXType.NUMBER)),
            "move": FunctionType([TypeInfo(AXType.NUMBER), TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NULL)),
            "rotate": FunctionType([TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NULL)),
            "keyPressed": FunctionType([TypeInfo(AXType.STRING)], TypeInfo(AXType.BOOLEAN)),
            "distance": FunctionType([TypeInfo(AXType.NUMBER), TypeInfo(AXType.NUMBER), 
                                    TypeInfo(AXType.NUMBER), TypeInfo(AXType.NUMBER)], TypeInfo(AXType.NUMBER)),
        }
        return builtin_functions.get(name)
    
    def clear_errors(self):
        """Clear all type errors"""
        self.errors.clear()

class ModuleSystem:
    """Module system for AXScript"""
    
    def __init__(self):
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.module_paths: Dict[str, str] = {}
    
    def register_module(self, name: str, exports: Dict[str, Any], path: str = ""):
        """Register a module"""
        self.modules[name] = exports
        self.module_paths[name] = path
    
    def get_module(self, name: str) -> Optional[Dict[str, Any]]:
        """Get module exports"""
        return self.modules.get(name)
    
    def import_from_module(self, module_name: str, imports: List[str]) -> Dict[str, Any]:
        """Import specific items from module"""
        module = self.get_module(module_name)
        if not module:
            raise RuntimeError(f"Module '{module_name}' not found")
        
        result = {}
        for import_name in imports:
            if import_name in module:
                result[import_name] = module[import_name]
            else:
                raise RuntimeError(f"'{import_name}' not found in module '{module_name}'")
        
        return result

# Standard library modules
def create_math_module():
    """Create math standard library module"""
    import math
    return {
        "PI": math.pi,
        "E": math.e,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "round": round,
        "pow": pow,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "random": __import__('random').random,
        "randint": __import__('random').randint,
        "choice": __import__('random').choice,
    }

def create_string_module():
    """Create string standard library module"""
    return {
        "toUpperCase": lambda s: s.upper(),
        "toLowerCase": lambda s: s.lower(),
        "trim": lambda s: s.strip(),
        "split": lambda s, sep=" ": s.split(sep),
        "join": lambda arr, sep="": sep.join(str(x) for x in arr),
        "replace": lambda s, old, new: s.replace(old, new),
        "indexOf": lambda s, sub: s.find(sub),
        "charAt": lambda s, i: s[i] if 0 <= i < len(s) else "",
        "length": lambda s: len(s),
        "startsWith": lambda s, prefix: s.startswith(prefix),
        "endsWith": lambda s, suffix: s.endswith(suffix),
    }

def create_array_module():
    """Create array standard library module"""
    return {
        "push": lambda arr, *items: arr.extend(items),
        "pop": lambda arr: arr.pop() if arr else None,
        "shift": lambda arr: arr.pop(0) if arr else None,
        "unshift": lambda arr, *items: [arr.insert(0, item) for item in reversed(items)],
        "slice": lambda arr, start=0, end=None: arr[start:end],
        "splice": lambda arr, start, delete_count=None, *items: arr[start:start+delete_count] if delete_count else arr[start:],
        "indexOf": lambda arr, item: arr.index(item) if item in arr else -1,
        "includes": lambda arr, item: item in arr,
        "length": lambda arr: len(arr),
        "reverse": lambda arr: arr.reverse(),
        "sort": lambda arr, key=None: arr.sort(key=key),
        "filter": lambda arr, predicate: [x for x in arr if predicate(x)],
        "map": lambda arr, func: [func(x) for x in arr],
        "reduce": lambda arr, func, initial=None: __import__('functools').reduce(func, arr, initial) if initial is not None else __import__('functools').reduce(func, arr),
        "forEach": lambda arr, func: [func(x) for x in arr],
        "find": lambda arr, predicate: next((x for x in arr if predicate(x)), None),
        "some": lambda arr, predicate: any(predicate(x) for x in arr),
        "every": lambda arr, predicate: all(predicate(x) for x in arr),
    }

def create_console_module():
    """Create console standard library module"""
    return {
        "log": print,
        "warn": lambda *args: print("WARNING:", *args),
        "error": lambda *args: print("ERROR:", *args),
        "info": lambda *args: print("INFO:", *args),
        "debug": lambda *args: print("DEBUG:", *args),
        "clear": lambda: print("\033[2J\033[H"),  # Clear screen
        "time": lambda label="default": print(f"Timer '{label}' started"),
        "timeEnd": lambda label="default": print(f"Timer '{label}' ended"),
    }

def create_json_module():
    """Create JSON standard library module"""
    import json
    return {
        "parse": json.loads,
        "stringify": json.dumps,
    }
