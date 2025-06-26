
"""
Axarion Engine Game Object
Base class for all game entities
"""

import math
import time
from typing import Dict, Any, List, Tuple, Optional

class GameObject:
    """Base class for all game objects in Axarion Engine"""
    
    def __init__(self, name: str, object_type: str = "rectangle"):
        self.name = name
        self.object_type = object_type
        self.position = (0.0, 0.0)
        self.velocity = (0.0, 0.0)
        self.acceleration = (0.0, 0.0)
        self.rotation = 0.0
        self.scale = (1.0, 1.0)
        
        # Visual properties
        self.visible = True
        self.active = True
        self.destroyed = False
        
        # UNLIMITED GAME OBJECT FEATURES
        self.unlimited_properties = {}
        self.components = {}  # Component system for unlimited functionality
        self.behaviors = []   # Unlimited behaviors
        self.triggers = {}    # Event triggers
        self.data_storage = {}  # Unlimited data storage
        
        # Advanced rendering
        self.layer = 0
        self.z_order = 0
        self.opacity = 1.0
        self.blend_mode = "normal"
        self.post_effects = []
        
        # Networking
        self.network_id = None
        self.replicated = False
        self.owner_id = None
        
        # AI and behavior
        self.ai_controller = None
        self.decision_tree = None
        self.learning_enabled = False
        
        # Genre-specific features
        self.rpg_data = {"level": 1, "xp": 0, "skills": {}}
        self.platformer_data = {"jump_count": 0, "wall_slide": False}
        self.shooter_data = {"ammo": 100, "weapon": "default"}
        self.racing_data = {"speed": 0, "lap_time": 0}
        self.puzzle_data = {"solved": False, "hints": []}
        self.strategy_data = {"resources": {}, "units": []}
        
        # Physics properties
        self.mass = 1.0
        self.friction = 0.1
        self.bounce = 0.8
        self.gravity_scale = 1.0
        self.is_static = False
        self.collision_enabled = True
        self.collision_layer = "default"
        
        # Custom properties
        self.properties: Dict[str, Any] = {}
        self.tags: List[str] = []
        
        # Parent scene reference
        self.scene = None
        
        # Scripting
        self.script_code = ""
        self.script_context = {}
        
        # Timers
        self.timers: Dict[str, float] = {}
        
        # Stats (for RPG objects)
        self.stats: Dict[str, float] = {
            "health": 100.0,
            "max_health": 100.0,
            "mana": 50.0,
            "max_mana": 50.0,
            "attack": 10.0,
            "defense": 5.0,
            "speed": 100.0
        }
        
        # Inventory (for RPG objects)
        self.inventory: List[Dict[str, Any]] = []
        self.equipment: Dict[str, Dict[str, Any]] = {}
        
        # AI properties
        self.ai_state = "idle"
        self.target = None
        self.patrol_points: List[Tuple[float, float]] = []
        self.current_patrol_index = 0
        
        # Asset properties
        self.sprite_name = None
        self.animation_name = None
        self.current_frame = 0
        self.animation_speed = 1.0
        self.animation_time = 0.0
        self.animation_playing = True
        self.animation_loop = True
        
        # Initialize default properties based on type
        self._init_default_properties()
    
    def _init_default_properties(self):
        """Initialize default properties based on object type"""
        if self.object_type == "rectangle":
            self.properties.update({
                "width": 50,
                "height": 50,
                "color": (255, 255, 255)
            })
        elif self.object_type == "circle":
            self.properties.update({
                "radius": 25,
                "color": (255, 255, 255)
            })
        elif self.object_type == "sprite":
            self.properties.update({
                "width": 32,
                "height": 32,
                "color": (100, 150, 255),
                "texture": None
            })
    
    def update(self, delta_time: float):
        """Update the game object"""
        if not self.active or self.destroyed:
            return
        
        # Update timers
        for timer_name in list(self.timers.keys()):
            self.timers[timer_name] -= delta_time
            if self.timers[timer_name] <= 0:
                del self.timers[timer_name]
        
        # Apply physics if not static
        if not self.is_static:
            self.update_physics(delta_time)
        
        # Update animation
        if self.animation_name:
            self.update_animation(delta_time)
        
        # Execute script if present
        if self.script_code:
            self.execute_script()
    
    def update_physics(self, delta_time: float):
        """Update physics simulation"""
        # Don't update physics if static
        if self.is_static:
            return
            
        # Reset ground flag at start of frame
        if hasattr(self, '_on_ground'):
            self._on_ground = False
        
        # Apply gravity through acceleration (not directly to velocity)
        if self.gravity_scale > 0 and self.scene:
            physics = getattr(self.scene, 'physics', None)
            if physics and hasattr(physics, 'gravity'):
                gx, gy = physics.gravity
                # Add gravity to acceleration
                ax, ay = self.acceleration
                self.acceleration = (ax + gx * self.gravity_scale, ay + gy * self.gravity_scale)
        
        # Update velocity from acceleration
        vx, vy = self.velocity
        ax, ay = self.acceleration
        self.velocity = (vx + ax * delta_time, vy + ay * delta_time)
        
        # Apply friction
        if self.friction > 0:
            platforms = []
            if self.scene:
                platforms = [obj for obj in self.scene.objects.values() 
                           if obj != self and (obj.has_tag("platform") or obj.is_static)]
            
            on_ground = self.is_on_ground(platforms)
            
            if on_ground:
                # Ground friction - stronger, only horizontal
                friction_factor = max(0.0, 1.0 - (self.friction * 12.0 * delta_time))
                vx, vy = self.velocity
                self.velocity = (vx * friction_factor, vy)
            else:
                # Air resistance - much weaker
                friction_factor = max(0.0, 1.0 - (self.friction * 2.0 * delta_time))
                vx, vy = self.velocity
                self.velocity = (vx * friction_factor, vy * 0.999)
        
        # Limit maximum velocities to prevent crazy physics
        vx, vy = self.velocity
        max_vel = 600.0
        if abs(vx) > max_vel:
            vx = max_vel if vx > 0 else -max_vel
        if abs(vy) > max_vel:
            vy = max_vel if vy > 0 else -max_vel
        self.velocity = (vx, vy)
        
        # Update position from velocity
        x, y = self.position
        vx, vy = self.velocity
        self.position = (x + vx * delta_time, y + vy * delta_time)
        
        # Reset acceleration for next frame
        self.acceleration = (0.0, 0.0)
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box (left, top, right, bottom)"""
        x, y = self.position
        
        if self.object_type == "rectangle" or self.object_type == "sprite":
            width = self.properties.get("width", 50)
            height = self.properties.get("height", 50)
            return (x, y, x + width, y + height)
        
        elif self.object_type == "circle":
            radius = self.properties.get("radius", 25)
            return (x - radius, y - radius, x + radius, y + radius)
        
        else:
            # Default rectangle
            return (x, y, x + 50, y + 50)
    
    def contains_point(self, px: float, py: float) -> bool:
        """Check if point is inside object"""
        if self.object_type == "circle":
            x, y = self.position
            radius = self.properties.get("radius", 25)
            distance = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            return distance <= radius
        else:
            bounds = self.get_bounds()
            return (bounds[0] <= px <= bounds[2] and 
                   bounds[1] <= py <= bounds[3])
    
    def is_colliding_with(self, other: 'GameObject') -> bool:
        """Check collision with another object"""
        if not self.collision_enabled or not other.collision_enabled:
            return False
        
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()
        
        # AABB collision detection
        return (bounds1[0] < bounds2[2] and bounds1[2] > bounds2[0] and
                bounds1[1] < bounds2[3] and bounds1[3] > bounds2[1])
    
    def is_on_ground(self, objects=None) -> bool:
        """Check if object is on ground or platform"""
        if not objects and self.scene:
            objects = [obj for obj in self.scene.objects.values() 
                      if obj != self and (obj.has_tag("platform") or obj.is_static)]
        elif not objects:
            return False
        
        my_bounds = self.get_bounds()
        
        # Don't consider grounded if moving upward
        if self.velocity[1] < -10:  # Moving upward
            return False
        
        for obj in objects:
            if obj == self or not obj.is_static:
                continue
                
            obj_bounds = obj.get_bounds()
            
            # Check horizontal overlap with some margin
            horizontal_overlap = (my_bounds[0] < obj_bounds[2] - 3 and my_bounds[2] > obj_bounds[0] + 3)
            
            # Check if we're very close to the top of this object
            vertical_distance = my_bounds[3] - obj_bounds[1]
            
            # We're on ground if:
            # 1. Horizontally overlapping
            # 2. Bottom of this object is very close to top of platform
            # 3. Not moving up
            if (horizontal_overlap and 
                vertical_distance >= -3 and 
                vertical_distance <= 8 and
                self.velocity[1] >= -10):
                # Set ground flag when detected
                self._on_ground = True
                return True
        
        # Clear ground flag if not on any platform
        self._on_ground = False
        return False
    
    def resolve_collision_with(self, other: 'GameObject', delta_time: float):
        """Resolve collision with another object"""
        if not self.is_colliding_with(other):
            return
        
        # Don't resolve if both objects are static
        if self.is_static and other.is_static:
            return
        
        bounds1 = self.get_bounds()
        bounds2 = other.get_bounds()
        
        # Calculate overlap
        overlap_x = min(bounds1[2], bounds2[2]) - max(bounds1[0], bounds2[0])
        overlap_y = min(bounds1[3], bounds2[3]) - max(bounds1[1], bounds2[1])
        
        if overlap_x <= 0 or overlap_y <= 0:
            return
        
        # Determine collision direction based on previous positions
        center1_x = (bounds1[0] + bounds1[2]) / 2
        center1_y = (bounds1[1] + bounds1[3]) / 2
        center2_x = (bounds2[0] + bounds2[2]) / 2
        center2_y = (bounds2[1] + bounds2[3]) / 2
        
        # Resolve based on smallest overlap
        if overlap_x < overlap_y:
            # Horizontal collision
            if center1_x < center2_x:
                # Move left object to the left
                if not self.is_static:
                    self.position = (bounds2[0] - (bounds1[2] - bounds1[0]), self.position[1])
                    self.velocity = (-abs(self.velocity[0]) * self.bounce, self.velocity[1])
                if not other.is_static:
                    other.position = (bounds1[2], other.position[1])
                    other.velocity = (abs(other.velocity[0]) * other.bounce, other.velocity[1])
            else:
                # Move right object to the right
                if not self.is_static:
                    self.position = (bounds2[2], self.position[1])
                    self.velocity = (abs(self.velocity[0]) * self.bounce, self.velocity[1])
                if not other.is_static:
                    other.position = (bounds1[0] - (bounds2[2] - bounds2[0]), other.position[1])
                    other.velocity = (-abs(other.velocity[0]) * other.bounce, other.velocity[1])
        else:
            # Vertical collision
            if center1_y < center2_y:
                # Move top object up (landing on platform)
                if not self.is_static:
                    self.position = (self.position[0], bounds2[1] - (bounds1[3] - bounds1[1]))
                    self.velocity = (self.velocity[0], 0)  # Stop falling
                    self._on_ground = True  # Set ground flag when landing
                if not other.is_static:
                    other.position = (other.position[0], bounds1[3])
                    other.velocity = (other.velocity[0], abs(other.velocity[1]) * other.bounce)
            else:
                # Move bottom object down (hitting from below)
                if not self.is_static:
                    self.position = (self.position[0], bounds2[3])
                    self.velocity = (self.velocity[0], abs(self.velocity[1]) * self.bounce)
                if not other.is_static:
                    other.position = (other.position[0], bounds1[1] - (bounds2[3] - bounds2[1]))
                    other.velocity = (other.velocity[0], 0)
                    other._on_ground = True  # Set ground flag when landing
    
    def set_property(self, name: str, value: Any):
        """Set a property"""
        if name == "position":
            if isinstance(value, dict) and "x" in value and "y" in value:
                self.position = (value["x"], value["y"])
            elif isinstance(value, (list, tuple)) and len(value) >= 2:
                self.position = (value[0], value[1])
        elif name == "velocity":
            if isinstance(value, dict) and "x" in value and "y" in value:
                self.velocity = (value["x"], value["y"])
            elif isinstance(value, (list, tuple)) and len(value) >= 2:
                self.velocity = (value[0], value[1])
        elif name == "visible":
            self.visible = bool(value)
        elif name == "active":
            self.active = bool(value)
        else:
            self.properties[name] = value
    
    def get_property(self, name: str, default=None):
        """Get a property"""
        if name == "position":
            return {"x": self.position[0], "y": self.position[1]}
        elif name == "velocity":
            return {"x": self.velocity[0], "y": self.velocity[1]}
        elif name == "visible":
            return self.visible
        elif name == "active":
            return self.active
        else:
            return self.properties.get(name, default)
    
    def add_tag(self, tag: str):
        """Add a tag"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if object has tag"""
        return tag in self.tags
    
    def start_timer(self, name: str, duration: float):
        """Start a timer"""
        self.timers[name] = duration
    
    def get_timer(self, name: str) -> float:
        """Get remaining time on timer"""
        return self.timers.get(name, 0.0)
    
    def is_timer_finished(self, name: str) -> bool:
        """Check if timer is finished"""
        return name not in self.timers
    
    def move_towards(self, target_pos: Tuple[float, float], speed: float):
        """Move towards target position"""
        tx, ty = target_pos
        x, y = self.position
        
        dx = tx - x
        dy = ty - y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed
            self.velocity = (vx, vy)
    
    def look_at(self, target_pos: Tuple[float, float]):
        """Look at target position"""
        tx, ty = target_pos
        x, y = self.position
        
        dx = tx - x
        dy = ty - y
        
        self.rotation = math.degrees(math.atan2(dy, dx))
    
    def apply_force(self, fx: float, fy: float):
        """Apply force to object"""
        if self.mass > 0:
            ax, ay = self.acceleration
            self.acceleration = (ax + fx / self.mass, ay + fy / self.mass)
    
    def take_damage(self, damage: float) -> bool:
        """Take damage and return if destroyed"""
        self.stats["health"] -= damage
        if self.stats["health"] <= 0:
            self.stats["health"] = 0
            self.destroyed = True
            return True
        return False
    
    def heal(self, amount: float):
        """Heal object"""
        self.stats["health"] = min(self.stats["max_health"], 
                                  self.stats["health"] + amount)
    
    def get_stat(self, stat_name: str) -> float:
        """Get stat value"""
        return self.stats.get(stat_name, 0.0)
    
    def add_item(self, item: Dict[str, Any]):
        """Add item to inventory"""
        # Check if item already exists
        for existing_item in self.inventory:
            if existing_item["name"] == item["name"]:
                existing_item["quantity"] = existing_item.get("quantity", 1) + item.get("quantity", 1)
                return
        
        # Add new item
        self.inventory.append(item)
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory"""
        for i, item in enumerate(self.inventory):
            if item["name"] == item_name:
                quantity = item.get("quantity", 1)
                if quantity > 1:
                    item["quantity"] = quantity - 1
                else:
                    del self.inventory[i]
                return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        """Check if has item"""
        for item in self.inventory:
            if item["name"] == item_name:
                return True
        return False
    
    def equip_item(self, slot: str, item: Dict[str, Any]):
        """Equip item"""
        self.equipment[slot] = item
    
    def set_patrol_route(self, points: List[Tuple[float, float]]):
        """Set patrol route"""
        self.patrol_points = points
        self.current_patrol_index = 0
    
    def get_next_patrol_point(self) -> Optional[Tuple[float, float]]:
        """Get next patrol point"""
        if not self.patrol_points:
            return None
        
        point = self.patrol_points[self.current_patrol_index]
        self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        return point
    
    def set_sprite(self, sprite_name: str):
        """Set sprite for this object"""
        from engine.asset_manager import asset_manager
        if asset_manager.get_image(sprite_name):
            self.sprite_name = sprite_name
            self.object_type = "sprite"
            return True
        return False
    
    def set_animation(self, animation_name: str, speed: float = 1.0, loop: bool = True):
        """Set animation for this object"""
        from engine.asset_manager import asset_manager
        if asset_manager.get_animation(animation_name):
            self.animation_name = animation_name
            self.animation_speed = speed
            self.animation_loop = loop
            self.current_frame = 0
            self.animation_time = 0.0
            self.animation_playing = True
            self.object_type = "animated_sprite"
            return True
        return False
    
    def play_animation(self, animation_name: str = None):
        """Play animation"""
        if animation_name:
            self.set_animation(animation_name)
        self.animation_playing = True
    
    def stop_animation(self):
        """Stop animation"""
        self.animation_playing = False
    
    def pause_animation(self):
        """Pause animation"""
        self.animation_playing = False
    
    def resume_animation(self):
        """Resume animation"""
        self.animation_playing = True
    
    def update_animation(self, delta_time: float):
        """Update animation frame"""
        if not self.animation_playing or not self.animation_name:
            return
        
        from engine.asset_manager import asset_manager
        animation = asset_manager.get_animation(self.animation_name)
        if not animation:
            return
        
        # Update animation time
        self.animation_time += delta_time * self.animation_speed
        
        # Get frame duration from asset info
        asset_info = asset_manager.get_asset_info(self.animation_name)
        frame_duration = asset_info.get('frame_duration', 0.1) if asset_info else 0.1
        
        # Calculate current frame
        total_frames = len(animation)
        frame_index = int(self.animation_time / frame_duration)
        
        if self.animation_loop:
            self.current_frame = frame_index % total_frames
        else:
            if frame_index >= total_frames:
                self.current_frame = total_frames - 1
                self.animation_playing = False
            else:
                self.current_frame = frame_index
    
    def get_current_sprite(self):
        """Get current sprite surface"""
        from engine.asset_manager import asset_manager
        
        if self.animation_name:
            return asset_manager.get_animation_frame(self.animation_name, self.current_frame)
        elif self.sprite_name:
            return asset_manager.get_image(self.sprite_name)
        return None
    
    def play_sound(self, sound_name: str):
        """Play sound effect"""
        from engine.asset_manager import asset_manager
        return asset_manager.play_sound(sound_name)
    
    def execute_script(self):
        """Execute attached script"""
        if not self.script_code:
            return
        
        try:
            from scripting.axscript_interpreter import AXScriptInterpreter
            interpreter = AXScriptInterpreter()
            result = interpreter.execute(self.script_code, self)
            
            if not result["success"] and result["error"]:
                print(f"Script error in {self.name}: {result['error']}")
        except Exception as e:
            print(f"Failed to execute script for {self.name}: {e}")
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize object to dictionary"""
        return {
            "name": self.name,
            "type": self.object_type,
            "position": self.position,
            "velocity": self.velocity,
            "rotation": self.rotation,
            "scale": self.scale,
            "visible": self.visible,
            "active": self.active,
            "mass": self.mass,
            "friction": self.friction,
            "bounce": self.bounce,
            "gravity_scale": self.gravity_scale,
            "is_static": self.is_static,
            "collision_enabled": self.collision_enabled,
            "collision_layer": self.collision_layer,
            "properties": self.properties,
            "tags": self.tags,
            "script_code": self.script_code,
            "stats": self.stats,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "ai_state": self.ai_state,
            "patrol_points": self.patrol_points
        }
    
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize object from dictionary"""
        self.name = data.get("name", "Unknown")
        self.object_type = data.get("type", "rectangle")
        self.position = tuple(data.get("position", (0, 0)))
        self.velocity = tuple(data.get("velocity", (0, 0)))
        self.rotation = data.get("rotation", 0.0)
        self.scale = tuple(data.get("scale", (1.0, 1.0)))
        self.visible = data.get("visible", True)
        self.active = data.get("active", True)
        self.mass = data.get("mass", 1.0)
        self.friction = data.get("friction", 0.1)
        self.bounce = data.get("bounce", 0.8)
        self.gravity_scale = data.get("gravity_scale", 1.0)
        self.is_static = data.get("is_static", False)
        self.collision_enabled = data.get("collision_enabled", True)
        self.collision_layer = data.get("collision_layer", "default")
        self.properties = data.get("properties", {})
        self.tags = data.get("tags", [])
        self.script_code = data.get("script_code", "")
        self.stats = data.get("stats", self.stats)
        self.inventory = data.get("inventory", [])
        self.equipment = data.get("equipment", {})
        self.ai_state = data.get("ai_state", "idle")
        self.patrol_points = data.get("patrol_points", [])
        
        # Load unlimited features
        self.unlimited_properties = data.get("unlimited_properties", {})
        self.components = data.get("components", {})
        self.behaviors = data.get("behaviors", [])
        self.triggers = data.get("triggers", {})
        self.data_storage = data.get("data_storage", {})
    
    # UNLIMITED GAME OBJECT METHODS
    
    def add_component(self, component_name: str, component_data: Dict):
        """Add unlimited components for any game genre"""
        self.components[component_name] = component_data
        return self.components[component_name]
    
    def get_component(self, component_name: str):
        """Get component data"""
        return self.components.get(component_name)
    
    def remove_component(self, component_name: str):
        """Remove component"""
        if component_name in self.components:
            del self.components[component_name]
    
    def add_behavior(self, behavior_function):
        """Add custom behavior for unlimited gameplay"""
        self.behaviors.append(behavior_function)
    
    def set_unlimited_property(self, key: str, value: Any):
        """Set unlimited custom properties"""
        self.unlimited_properties[key] = value
    
    def get_unlimited_property(self, key: str, default=None):
        """Get unlimited custom property"""
        return self.unlimited_properties.get(key, default)
    
    def store_data(self, key: str, data: Any):
        """Store unlimited custom data"""
        self.data_storage[key] = data
    
    def get_stored_data(self, key: str, default=None):
        """Get stored custom data"""
        return self.data_storage.get(key, default)
    
    def add_trigger(self, trigger_name: str, condition, action):
        """Add event trigger for unlimited interactivity"""
        self.triggers[trigger_name] = {"condition": condition, "action": action}
    
    def check_triggers(self):
        """Check and execute triggers"""
        for trigger_name, trigger in self.triggers.items():
            try:
                if trigger["condition"](self):
                    trigger["action"](self)
            except Exception as e:
                print(f"Trigger error in {trigger_name}: {e}")
    
    def enable_networking(self, replicated: bool = True):
        """Enable networking for multiplayer games"""
        self.replicated = replicated
        self.network_id = f"{self.name}_{id(self)}"
    
    def set_ai_controller(self, ai_type: str, parameters: Dict = None):
        """Set AI controller for unlimited AI behaviors"""
        self.ai_controller = {
            "type": ai_type,
            "parameters": parameters or {},
            "active": True
        }
    
    def add_post_effect(self, effect_name: str, parameters: Dict):
        """Add post-processing effect to object"""
        effect = {"name": effect_name, "params": parameters}
        self.post_effects.append(effect)
    
    def set_layer(self, layer: int, z_order: int = 0):
        """Set rendering layer for unlimited layering"""
        self.layer = layer
        self.z_order = z_order
    
    def enable_learning(self, learning_type: str = "reinforcement"):
        """Enable machine learning for adaptive behavior"""
        self.learning_enabled = True
        self.learning_type = learning_type
        self.learning_data = {"experiences": [], "rewards": []}
    
    def create_for_genre(self, genre: str, genre_data: Dict = None):
        """Configure object for specific game genre"""
        if genre == "rpg":
            self.rpg_data.update(genre_data or {})
            self.add_component("RPGComponent", self.rpg_data)
        elif genre == "platformer":
            self.platformer_data.update(genre_data or {})
            self.add_component("PlatformerComponent", self.platformer_data)
        elif genre == "shooter":
            self.shooter_data.update(genre_data or {})
            self.add_component("ShooterComponent", self.shooter_data)
        elif genre == "racing":
            self.racing_data.update(genre_data or {})
            self.add_component("RacingComponent", self.racing_data)
        elif genre == "puzzle":
            self.puzzle_data.update(genre_data or {})
            self.add_component("PuzzleComponent", self.puzzle_data)
        elif genre == "strategy":
            self.strategy_data.update(genre_data or {})
            self.add_component("StrategyComponent", self.strategy_data)
    
    def unlimited_update(self, delta_time: float):
        """Unlimited update with all features"""
        # Standard update
        self.update(delta_time)
        
        # Update components
        for component_name, component in self.components.items():
            if hasattr(component, 'update'):
                component.update(delta_time)
        
        # Execute behaviors
        for behavior in self.behaviors:
            try:
                behavior(self, delta_time)
            except Exception as e:
                print(f"Behavior error: {e}")
        
        # Check triggers
        self.check_triggers()
        
        # Update AI
        if self.ai_controller and self.ai_controller["active"]:
            self.update_ai(delta_time)
        
        # Learning update
        if self.learning_enabled:
            self.update_learning(delta_time)
    
    def update_ai(self, delta_time: float):
        """Update AI behavior"""
        ai_type = self.ai_controller["type"]
        params = self.ai_controller["parameters"]
        
        if ai_type == "pathfinding":
            self.update_pathfinding(delta_time, params)
        elif ai_type == "state_machine":
            self.update_state_machine(delta_time, params)
        elif ai_type == "behavior_tree":
            self.update_behavior_tree(delta_time, params)
    
    def update_pathfinding(self, delta_time: float, params: Dict):
        """Update pathfinding AI"""
        if "target" in params and "speed" in params:
            target = params["target"]
            speed = params["speed"]
            self.move_towards(target, speed)
    
    def update_state_machine(self, delta_time: float, params: Dict):
        """Update finite state machine"""
        current_state = params.get("current_state", "idle")
        states = params.get("states", {})
        
        if current_state in states:
            state_func = states[current_state]
            if callable(state_func):
                new_state = state_func(self, delta_time)
                if new_state and new_state != current_state:
                    params["current_state"] = new_state
    
    def update_behavior_tree(self, delta_time: float, params: Dict):
        """Update behavior tree"""
        tree = params.get("tree")
        if tree and hasattr(tree, 'execute'):
            tree.execute(self, delta_time)
    
    def update_learning(self, delta_time: float):
        """Update machine learning"""
        if self.learning_type == "reinforcement":
            # Simple Q-learning update
            experience = {
                "state": self.get_state_vector(),
                "action": self.get_last_action(),
                "reward": self.get_reward(),
                "next_state": self.get_state_vector()
            }
            self.learning_data["experiences"].append(experience)
    
    def get_state_vector(self):
        """Get state vector for learning"""
        return [self.position[0], self.position[1], self.velocity[0], self.velocity[1]]
    
    def get_last_action(self):
        """Get last action performed"""
        return getattr(self, '_last_action', 0)
    
    def get_reward(self):
        """Calculate reward for learning"""
        return getattr(self, '_reward', 0.0)
