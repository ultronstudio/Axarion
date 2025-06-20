"""
Axarion Engine Game Object
Base class for all game entities
"""

import math
from typing import Dict, List, Tuple, Any, Optional

class GameObject:
    """Base class for all game objects in the engine"""
    
    def __init__(self, name: str = "GameObject", object_type: str = "rectangle"):
        # Identity
        self.id: str = ""
        self.name: str = name
        self.object_type: str = object_type
        
        # Transform
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.rotation: float = 0.0
        self.scale: Tuple[float, float] = (1.0, 1.0)
        
        # Physics
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.acceleration: Tuple[float, float] = (0.0, 0.0)
        self.mass: float = 1.0
        self.friction: float = 0.0
        
        # State
        self.active: bool = True
        self.visible: bool = True
        
        # Properties (type-specific attributes)
        self.properties: Dict[str, Any] = {}
        
        # Script
        self.script_code: str = ""
        self.script_variables: Dict[str, Any] = {}
        
        # References
        self.scene = None
        self.children: List['GameObject'] = []
        self.parent: Optional['GameObject'] = None
        
        # Set default properties based on type
        self._set_default_properties()
    
    def _set_default_properties(self):
        """Set default properties based on object type"""
        if self.object_type == "rectangle":
            self.properties.update({
                "width": 50.0,
                "height": 50.0,
                "color": (255, 255, 255)
            })
        elif self.object_type == "circle":
            self.properties.update({
                "radius": 25.0,
                "color": (255, 255, 255)
            })
        elif self.object_type == "sprite":
            self.properties.update({
                "width": 32.0,
                "height": 32.0,
                "color": (100, 150, 255),
                "texture": None
            })
    
    def update(self, delta_time: float):
        """Update the game object"""
        # Apply physics
        if self.velocity != (0.0, 0.0) or self.acceleration != (0.0, 0.0):
            # Update velocity
            vel_x, vel_y = self.velocity
            acc_x, acc_y = self.acceleration
            
            vel_x += acc_x * delta_time
            vel_y += acc_y * delta_time
            
            # Apply friction
            if self.friction > 0:
                friction_force = self.friction * delta_time
                if abs(vel_x) > friction_force:
                    vel_x -= friction_force if vel_x > 0 else -friction_force
                else:
                    vel_x = 0
                    
                if abs(vel_y) > friction_force:
                    vel_y -= friction_force if vel_y > 0 else -friction_force
                else:
                    vel_y = 0
            
            self.velocity = (vel_x, vel_y)
            
            # Update position
            pos_x, pos_y = self.position
            pos_x += vel_x * delta_time
            pos_y += vel_y * delta_time
            self.position = (pos_x, pos_y)
        
        # Update children
        for child in self.children:
            if child.active:
                child.update(delta_time)
    
    def set_position(self, x: float, y: float):
        """Set object position"""
        self.position = (x, y)
    
    def get_position(self) -> Tuple[float, float]:
        """Get object position"""
        return self.position
    
    def move(self, dx: float, dy: float):
        """Move object by offset"""
        x, y = self.position
        self.position = (x + dx, y + dy)
    
    def set_velocity(self, vx: float, vy: float):
        """Set object velocity"""
        self.velocity = (vx, vy)
    
    def add_velocity(self, dvx: float, dvy: float):
        """Add to object velocity"""
        vx, vy = self.velocity
        self.velocity = (vx + dvx, vy + dvy)
    
    def set_property(self, key: str, value: Any):
        """Set a property value"""
        self.properties[key] = value
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value"""
        return self.properties.get(key, default)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside object bounds"""
        obj_x, obj_y = self.position
        
        if self.object_type == "rectangle":
            width = self.properties.get("width", 50)
            height = self.properties.get("height", 50)
            return (obj_x <= x <= obj_x + width and 
                   obj_y <= y <= obj_y + height)
                   
        elif self.object_type == "circle":
            radius = self.properties.get("radius", 25)
            dx = x - obj_x
            dy = y - obj_y
            return (dx * dx + dy * dy) <= (radius * radius)
            
        elif self.object_type == "sprite":
            width = self.properties.get("width", 32)
            height = self.properties.get("height", 32)
            return (obj_x <= x <= obj_x + width and 
                   obj_y <= y <= obj_y + height)
        
        return False
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get object bounding box (x1, y1, x2, y2)"""
        x, y = self.position
        
        if self.object_type == "rectangle":
            width = self.properties.get("width", 50)
            height = self.properties.get("height", 50)
            return (x, y, x + width, y + height)
            
        elif self.object_type == "circle":
            radius = self.properties.get("radius", 25)
            return (x - radius, y - radius, x + radius, y + radius)
            
        elif self.object_type == "sprite":
            width = self.properties.get("width", 32)
            height = self.properties.get("height", 32)
            return (x, y, x + width, y + height)
        
        return (x, y, x, y)
    
    def distance_to(self, other: 'GameObject') -> float:
        """Calculate distance to another object"""
        x1, y1 = self.position
        x2, y2 = other.position
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def add_child(self, child: 'GameObject'):
        """Add a child object"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
    
    def remove_child(self, child: 'GameObject'):
        """Remove a child object"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize object to dictionary"""
        return {
            "name": self.name,
            "object_type": self.object_type,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "velocity": self.velocity,
            "acceleration": self.acceleration,
            "mass": self.mass,
            "friction": self.friction,
            "active": self.active,
            "visible": self.visible,
            "properties": self.properties,
            "script_code": self.script_code,
            "script_variables": self.script_variables
        }
    
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize object from dictionary"""
        self.name = data.get("name", "GameObject")
        self.object_type = data.get("object_type", "rectangle")
        self.position = tuple(data.get("position", (0.0, 0.0)))
        self.rotation = data.get("rotation", 0.0)
        self.scale = tuple(data.get("scale", (1.0, 1.0)))
        self.velocity = tuple(data.get("velocity", (0.0, 0.0)))
        self.acceleration = tuple(data.get("acceleration", (0.0, 0.0)))
        self.mass = data.get("mass", 1.0)
        self.friction = data.get("friction", 0.0)
        self.active = data.get("active", True)
        self.visible = data.get("visible", True)
        self.properties = data.get("properties", {})
        self.script_code = data.get("script_code", "")
        self.script_variables = data.get("script_variables", {})
    
    def clone(self) -> 'GameObject':
        """Create a copy of this object"""
        clone = GameObject()
        clone.deserialize(self.serialize())
        clone.id = ""  # Will be assigned when added to scene
        return clone
    
    def __str__(self) -> str:
        return f"GameObject(id={self.id}, name={self.name}, type={self.object_type}, pos={self.position})"
