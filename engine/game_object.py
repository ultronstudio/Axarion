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
        self.origin: Tuple[float, float] = (0.5, 0.5)  # Pivot point (0-1)
        
        # Physics
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.acceleration: Tuple[float, float] = (0.0, 0.0)
        self.mass: float = 1.0
        self.friction: float = 0.0
        self.bounce: float = 0.0
        self.gravity_scale: float = 1.0
        self.is_static: bool = False
        self.is_trigger: bool = False
        
        # State
        self.active: bool = True
        self.visible: bool = True
        self.destroyed: bool = False
        
        # Gameplay features
        self.health: float = 100.0
        self.max_health: float = 100.0
        self.damage: float = 10.0
        self.defense: float = 0.0
        self.speed: float = 100.0
        self.level: int = 1
        self.experience: float = 0.0
        
        # Inventory and items (for RPG games)
        self.inventory: List[Dict[str, Any]] = []
        self.equipment: Dict[str, Any] = {}
        self.stats: Dict[str, float] = {}
        
        # AI and behavior
        self.ai_state: str = "idle"
        self.target: Optional['GameObject'] = None
        self.patrol_points: List[Tuple[float, float]] = []
        self.current_patrol_index: int = 0
        
        # Visual effects
        self.alpha: float = 1.0
        self.tint_color: Tuple[int, int, int] = (255, 255, 255)
        self.blend_mode: str = "normal"
        
        # Collision and layers
        self.collision_layer: str = "default"
        self.collision_mask: List[str] = ["default"]
        self.tags: List[str] = []
        
        # Animation
        self.sprite_sheet: Optional[str] = None
        self.animation_frame: int = 0
        self.animation_speed: float = 1.0
        self.current_animation: str = "idle"
        self.animations: Dict[str, Dict] = {}
        
        # Properties (type-specific attributes)
        self.properties: Dict[str, Any] = {}
        
        # Script
        self.script_code: str = ""
        self.script_variables: Dict[str, Any] = {}
        self.script_functions: Dict[str, Any] = {}
        
        # References
        self.scene = None
        self.children: List['GameObject'] = []
        self.parent: Optional['GameObject'] = None
        
        # Timers and coroutines
        self.timers: Dict[str, float] = {}
        self.coroutines: List = []
        
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
        elif self.object_type == "line":
            self.properties.update({
                "end_x": 100.0,
                "end_y": 0.0,
                "width": 2,
                "color": (255, 255, 255)
            })
        elif self.object_type == "triangle":
            self.properties.update({
                "size": 50.0,
                "color": (255, 255, 255)
            })
        elif self.object_type == "star":
            self.properties.update({
                "size": 30.0,
                "color": (255, 255, 255)
            })
        elif self.object_type == "diamond":
            self.properties.update({
                "size": 40.0,
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
            
        elif self.object_type in ["triangle", "star", "diamond"]:
            # Simple bounding box for complex shapes
            size = self.properties.get("size", 40)
            return (obj_x - size <= x <= obj_x + size and 
                   obj_y - size <= y <= obj_y + size)
                   
        elif self.object_type == "line":
            # Simple line collision (check if point is near line)
            end_x = self.properties.get("end_x", obj_x + 100)
            end_y = self.properties.get("end_y", obj_y)
            width = self.properties.get("width", 2)
            
            # Distance from point to line
            line_length = ((end_x - obj_x) ** 2 + (end_y - obj_y) ** 2) ** 0.5
            if line_length == 0:
                return ((x - obj_x) ** 2 + (y - obj_y) ** 2) <= (width ** 2)
            
            t = max(0, min(1, ((x - obj_x) * (end_x - obj_x) + (y - obj_y) * (end_y - obj_y)) / (line_length ** 2)))
            projection_x = obj_x + t * (end_x - obj_x)
            projection_y = obj_y + t * (end_y - obj_y)
            
            distance = ((x - projection_x) ** 2 + (y - projection_y) ** 2) ** 0.5
            return distance <= width
            
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
    
    def add_tag(self, tag: str):
        """Add tag to object"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove tag from object"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if object has tag"""
        return tag in self.tags
    
    def take_damage(self, damage: float) -> bool:
        """Take damage and return True if destroyed"""
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        
        if self.health <= 0:
            self.health = 0
            self.destroyed = True
            return True
        return False
    
    def heal(self, amount: float):
        """Heal the object"""
        self.health = min(self.max_health, self.health + amount)
    
    def add_item(self, item: Dict[str, Any]):
        """Add item to inventory"""
        self.inventory.append(item)
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.inventory):
            if item.get("name") == item_name:
                del self.inventory[i]
                return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        """Check if has item in inventory"""
        return any(item.get("name") == item_name for item in self.inventory)
    
    def equip_item(self, slot: str, item: Dict[str, Any]):
        """Equip item in slot"""
        self.equipment[slot] = item
    
    def get_stat(self, stat_name: str, default: float = 0.0) -> float:
        """Get stat value including equipment bonuses"""
        base_value = self.stats.get(stat_name, default)
        
        # Add equipment bonuses
        for item in self.equipment.values():
            if "stats" in item and stat_name in item["stats"]:
                base_value += item["stats"][stat_name]
        
        return base_value
    
    def set_animation(self, animation_name: str):
        """Set current animation"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.animation_frame = 0
    
    def add_animation(self, name: str, frames: List[int], speed: float = 1.0, loop: bool = True):
        """Add animation definition"""
        self.animations[name] = {
            "frames": frames,
            "speed": speed,
            "loop": loop,
            "current_frame": 0
        }
    
    def start_timer(self, timer_name: str, duration: float):
        """Start a timer"""
        self.timers[timer_name] = duration
    
    def get_timer(self, timer_name: str) -> float:
        """Get remaining time on timer"""
        return self.timers.get(timer_name, 0.0)
    
    def is_timer_finished(self, timer_name: str) -> bool:
        """Check if timer is finished"""
        return self.timers.get(timer_name, 0.0) <= 0.0
    
    def set_patrol_route(self, points: List[Tuple[float, float]]):
        """Set patrol route for AI"""
        self.patrol_points = points
        self.current_patrol_index = 0
    
    def get_next_patrol_point(self) -> Optional[Tuple[float, float]]:
        """Get next patrol point"""
        if not self.patrol_points:
            return None
        
        point = self.patrol_points[self.current_patrol_index]
        self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        return point
    
    def look_at(self, target_pos: Tuple[float, float]):
        """Look at target position"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        self.rotation = math.atan2(dy, dx) * (180 / math.pi)
    
    def move_towards(self, target_pos: Tuple[float, float], speed: float):
        """Move towards target position"""
        dx = target_pos[0] - self.position[0]
        dy = target_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            move_x = (dx / distance) * speed
            move_y = (dy / distance) * speed
            self.move(move_x, move_y)
    
    def is_colliding_with(self, other: 'GameObject') -> bool:
        """Check collision with another object"""
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()
        
        return (bounds1[0] < bounds2[2] and bounds1[2] > bounds2[0] and
                bounds1[1] < bounds2[3] and bounds1[3] > bounds2[1])
    
    def clone(self) -> 'GameObject':
        """Create a copy of this object"""
        clone = GameObject()
        clone.deserialize(self.serialize())
        clone.id = ""  # Will be assigned when added to scene
        return clone
    
    def __str__(self) -> str:
        return f"GameObject(id={self.id}, name={self.name}, type={self.object_type}, pos={self.position})"
