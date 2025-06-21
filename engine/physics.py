
"""
SnowFox Engine Physics System
Basic 2D physics simulation
"""

import math
from typing import List, Tuple, Optional
from .game_object import GameObject

class PhysicsSystem:
    """Basic 2D physics system for the engine"""
    
    def __init__(self):
        self.gravity: Tuple[float, float] = (0.0, 800.0)  # pixels/second^2
        self.enabled = True
        self.collision_enabled = True
        
        # Physics constants
        self.min_velocity = 0.5  # Minimum velocity threshold
        self.restitution = 0.3  # Bounce factor
        self.air_resistance = 0.98  # Air resistance factor
        
        # Collision layers
        self.collision_layers: Dict[str, List[GameObject]] = {}
        
        # World bounds
        self.world_bounds = (0, 0, 800, 600)  # left, top, right, bottom
        self.constrain_to_world = True
        
    def update(self, delta_time: float):
        """Update physics simulation"""
        if not self.enabled:
            return
        
        # Physics updates are handled in GameObject.update_physics()
        # This method handles global physics effects and cleanup
        
        # Clean up collision layers
        for layer_name in self.collision_layers:
            self.collision_layers[layer_name] = [
                obj for obj in self.collision_layers[layer_name] 
                if obj.active and not obj.destroyed
            ]
    
    def apply_gravity(self, game_object: GameObject, delta_time: float):
        """Apply gravity to a game object"""
        if not self.enabled or game_object.is_static or game_object.gravity_scale <= 0:
            return
        
        gx, gy = self.gravity
        ax, ay = game_object.acceleration
        
        # Add gravity to acceleration
        game_object.acceleration = (
            ax + gx * game_object.gravity_scale,
            ay + gy * game_object.gravity_scale
        )
    
    def check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """Check if two objects are colliding"""
        if not self.collision_enabled:
            return False
        
        if not obj1.collision_enabled or not obj2.collision_enabled:
            return False
        
        if obj1 == obj2:
            return False
        
        return obj1.is_colliding_with(obj2)
    
    def resolve_collision(self, obj1: GameObject, obj2: GameObject, delta_time: float):
        """Resolve collision between two objects"""
        if not self.check_collision(obj1, obj2):
            return
        
        bounds1 = obj1.get_bounds()
        bounds2 = obj2.get_bounds()
        
        # Calculate overlap
        overlap_x = min(bounds1[2], bounds2[2]) - max(bounds1[0], bounds2[0])
        overlap_y = min(bounds1[3], bounds2[3]) - max(bounds1[1], bounds2[1])
        
        if overlap_x <= 0 or overlap_y <= 0:
            return
        
        # Calculate centers
        center1_x = (bounds1[0] + bounds1[2]) / 2
        center1_y = (bounds1[1] + bounds1[3]) / 2
        center2_x = (bounds2[0] + bounds2[2]) / 2
        center2_y = (bounds2[1] + bounds2[3]) / 2
        
        # Determine collision direction and separate objects
        if overlap_x < overlap_y:
            # Horizontal collision
            separation = overlap_x / 2
            if center1_x < center2_x:
                # obj1 is left of obj2
                if not obj1.is_static:
                    obj1.position = (obj1.position[0] - separation, obj1.position[1])
                    obj1.velocity = (-abs(obj1.velocity[0]) * obj1.bounce * 0.5, obj1.velocity[1])
                if not obj2.is_static:
                    obj2.position = (obj2.position[0] + separation, obj2.position[1])
                    obj2.velocity = (abs(obj2.velocity[0]) * obj2.bounce * 0.5, obj2.velocity[1])
            else:
                # obj1 is right of obj2
                if not obj1.is_static:
                    obj1.position = (obj1.position[0] + separation, obj1.position[1])
                    obj1.velocity = (abs(obj1.velocity[0]) * obj1.bounce * 0.5, obj1.velocity[1])
                if not obj2.is_static:
                    obj2.position = (obj2.position[0] - separation, obj2.position[1])
                    obj2.velocity = (-abs(obj2.velocity[0]) * obj2.bounce * 0.5, obj2.velocity[1])
        else:
            # Vertical collision
            separation = overlap_y / 2
            if center1_y < center2_y:
                # obj1 is above obj2 (landing on platform)
                if not obj1.is_static:
                    obj1.position = (obj1.position[0], obj1.position[1] - separation)
                    # Stop falling completely and enable ground flag
                    if obj1.velocity[1] > 10:  # Only if falling with significant speed
                        obj1.velocity = (obj1.velocity[0] * 0.8, 0)  # Stop vertical movement
                        obj1._on_ground = True
                    else:
                        obj1.velocity = (obj1.velocity[0], min(0, obj1.velocity[1]))
                if not obj2.is_static:
                    obj2.position = (obj2.position[0], obj2.position[1] + separation)
                    obj2.velocity = (obj2.velocity[0], abs(obj2.velocity[1]) * obj2.bounce * 0.3)
            else:
                # obj1 is below obj2 (hitting from below)
                if not obj1.is_static:
                    obj1.position = (obj1.position[0], obj1.position[1] + separation)
                    obj1.velocity = (obj1.velocity[0], abs(obj1.velocity[1]) * obj1.bounce * 0.5)
                if not obj2.is_static:
                    obj2.position = (obj2.position[0], obj2.position[1] - separation)
                    obj2.velocity = (obj2.velocity[0], -abs(obj2.velocity[1]) * obj2.bounce * 0.5)
    
    def check_all_collisions(self, objects: List[GameObject], delta_time: float):
        """Check and resolve all collisions between objects"""
        if not self.collision_enabled:
            return
        
        active_objects = [obj for obj in objects if obj.active and not obj.destroyed and obj.collision_enabled]
        
        for i, obj1 in enumerate(active_objects):
            for j, obj2 in enumerate(active_objects[i+1:], i+1):
                if self.check_collision(obj1, obj2):
                    self.resolve_collision(obj1, obj2, delta_time)
    
    def check_bounds_collision(self, game_object: GameObject, 
                              bounds: Tuple[float, float, float, float] = None) -> bool:
        """Check if object is colliding with bounds"""
        if bounds is None:
            bounds = self.world_bounds
        
        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds
        
        return (obj_bounds[0] < min_x or obj_bounds[2] > max_x or
                obj_bounds[1] < min_y or obj_bounds[3] > max_y)
    
    def constrain_to_bounds(self, game_object: GameObject, 
                           bounds: Tuple[float, float, float, float] = None):
        """Constrain object to bounds"""
        if not self.constrain_to_world:
            return
        
        if bounds is None:
            bounds = self.world_bounds
        
        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds
        x, y = game_object.position
        
        obj_width = obj_bounds[2] - obj_bounds[0]
        obj_height = obj_bounds[3] - obj_bounds[1]
        
        # Calculate new position
        new_x = x
        new_y = y
        
        # Check horizontal bounds
        if obj_bounds[0] < min_x:
            new_x = min_x
        elif obj_bounds[2] > max_x:
            new_x = max_x - obj_width
        
        # Check vertical bounds
        if obj_bounds[1] < min_y:
            new_y = min_y
        elif obj_bounds[3] > max_y:
            new_y = max_y - obj_height
        
        # Apply position changes and velocity corrections
        vx, vy = game_object.velocity
        
        if new_x != x:
            game_object.velocity = (-vx * self.restitution, vy)
        if new_y != y:
            game_object.velocity = (vx, -vy * self.restitution)
        
        game_object.position = (new_x, new_y)
    
    def apply_force(self, game_object: GameObject, force_x: float, force_y: float):
        """Apply force to game object"""
        if game_object.mass <= 0 or game_object.is_static:
            return
        
        # F = ma, so a = F/m
        ax, ay = game_object.acceleration
        game_object.acceleration = (ax + force_x / game_object.mass,
                                   ay + force_y / game_object.mass)
    
    def apply_impulse(self, game_object: GameObject, impulse_x: float, impulse_y: float):
        """Apply impulse to game object (immediate velocity change)"""
        if game_object.mass <= 0 or game_object.is_static:
            return
        
        # J = mv, so v = J/m
        vx, vy = game_object.velocity
        game_object.velocity = (vx + impulse_x / game_object.mass,
                               vy + impulse_y / game_object.mass)
    
    def set_gravity(self, gx: float, gy: float):
        """Set gravity vector"""
        self.gravity = (gx, gy)
    
    def set_world_bounds(self, left: float, top: float, right: float, bottom: float):
        """Set world bounds"""
        self.world_bounds = (left, top, right, bottom)
    
    def enable_physics(self, enabled: bool):
        """Enable or disable physics"""
        self.enabled = enabled
    
    def enable_collision(self, enabled: bool):
        """Enable or disable collision detection"""
        self.collision_enabled = enabled
    
    def enable_world_bounds(self, enabled: bool):
        """Enable or disable world bounds constraint"""
        self.constrain_to_world = enabled
    
    def add_to_collision_layer(self, layer_name: str, game_object: GameObject):
        """Add object to collision layer"""
        if layer_name not in self.collision_layers:
            self.collision_layers[layer_name] = []
        
        if game_object not in self.collision_layers[layer_name]:
            self.collision_layers[layer_name].append(game_object)
        
        game_object.collision_layer = layer_name
    
    def remove_from_collision_layer(self, layer_name: str, game_object: GameObject):
        """Remove object from collision layer"""
        if layer_name in self.collision_layers:
            if game_object in self.collision_layers[layer_name]:
                self.collision_layers[layer_name].remove(game_object)
    
    def get_objects_in_layer(self, layer_name: str) -> List[GameObject]:
        """Get all objects in collision layer"""
        return self.collision_layers.get(layer_name, [])
    
    def check_layer_collisions(self, layer1: str, layer2: str, delta_time: float):
        """Check collisions between two layers"""
        objects1 = self.get_objects_in_layer(layer1)
        objects2 = self.get_objects_in_layer(layer2)
        
        for obj1 in objects1:
            for obj2 in objects2:
                if self.check_collision(obj1, obj2):
                    self.resolve_collision(obj1, obj2, delta_time)
    
    def get_objects_in_range(self, center_x: float, center_y: float, 
                            radius: float, objects: List[GameObject]) -> List[GameObject]:
        """Get all objects within a certain range"""
        result = []
        for obj in objects:
            if not obj.active or obj.destroyed:
                continue
            
            x, y = obj.position
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= radius:
                result.append(obj)
        return result
    
    def raycast(self, start_x: float, start_y: float, 
                end_x: float, end_y: float, 
                objects: List[GameObject]) -> Optional[GameObject]:
        """Simple raycast to find first object hit"""
        # This is a simplified raycast implementation
        steps = 100
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        for i in range(steps):
            x = start_x + dx * i
            y = start_y + dy * i
            
            for obj in objects:
                if obj.active and not obj.destroyed and obj.contains_point(x, y):
                    return obj
        
        return None
    
    def circle_cast(self, start_x: float, start_y: float, 
                   end_x: float, end_y: float, radius: float,
                   objects: List[GameObject]) -> List[GameObject]:
        """Cast a circle along a path and return all hit objects"""
        hits = []
        steps = int(math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2) / 5) + 1
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        for i in range(steps):
            x = start_x + dx * i
            y = start_y + dy * i
            
            nearby = self.get_objects_in_range(x, y, radius, objects)
            for obj in nearby:
                if obj not in hits:
                    hits.append(obj)
        
        return hits
    
    def apply_explosion_force(self, center_x: float, center_y: float, 
                            force: float, radius: float, objects: List[GameObject]):
        """Apply explosion force to objects in range"""
        affected_objects = self.get_objects_in_range(center_x, center_y, radius, objects)
        
        for obj in affected_objects:
            if obj.is_static:
                continue
            
            x, y = obj.position
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance == 0:
                continue
            
            # Calculate force based on distance (inverse square law)
            force_magnitude = force * (1.0 - distance / radius)
            if force_magnitude <= 0:
                continue
            
            # Normalize direction and apply force
            nx = dx / distance
            ny = dy / distance
            
            self.apply_impulse(obj, nx * force_magnitude, ny * force_magnitude)
    
    def step_simulation(self, objects: List[GameObject], delta_time: float):
        """Step the physics simulation for all objects"""
        if not self.enabled:
            return
        
        # Apply physics to all objects
        for obj in objects:
            if obj.active and not obj.destroyed and not obj.is_static:
                # Apply gravity
                self.apply_gravity(obj, delta_time)
                
                # Apply air resistance
                vx, vy = obj.velocity
                obj.velocity = (vx * self.air_resistance, vy * self.air_resistance)
                
                # Constrain to world bounds
                self.constrain_to_bounds(obj)
        
        # Check all collisions
        self.check_all_collisions(objects, delta_time)
