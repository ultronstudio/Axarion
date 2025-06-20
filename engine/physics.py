"""
Axarion Engine Physics System
Basic 2D physics simulation
"""

import math
from typing import List, Tuple, Optional
from .game_object import GameObject

class PhysicsSystem:
    """Basic 2D physics system for the engine"""
    
    def __init__(self):
        self.gravity: Tuple[float, float] = (0.0, 981.0)  # pixels/second^2
        self.enabled = True
        self.collision_enabled = True
        
        # Physics constants
        self.min_velocity = 0.1  # Minimum velocity threshold
        self.restitution = 0.8  # Bounce factor
        
    def update(self, delta_time: float):
        """Update physics simulation"""
        if not self.enabled:
            return
        
        # Physics is handled per-object in GameObject.update()
        # This method can be used for global physics effects
        pass
    
    def apply_gravity(self, game_object: GameObject, delta_time: float):
        """Apply gravity to a game object"""
        if not self.enabled:
            return
        
        gx, gy = self.gravity
        ax, ay = game_object.acceleration
        
        # Add gravity to acceleration
        game_object.acceleration = (ax + gx, ay + gy)
    
    def check_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """Check if two objects are colliding"""
        if not self.collision_enabled:
            return False
        
        bounds1 = obj1.get_bounds()
        bounds2 = obj2.get_bounds()
        
        # AABB collision detection
        return (bounds1[0] < bounds2[2] and bounds1[2] > bounds2[0] and
                bounds1[1] < bounds2[3] and bounds1[3] > bounds2[1])
    
    def resolve_collision(self, obj1: GameObject, obj2: GameObject):
        """Resolve collision between two objects"""
        if not self.check_collision(obj1, obj2):
            return
        
        # Simple collision response - reverse velocities
        v1x, v1y = obj1.velocity
        v2x, v2y = obj2.velocity
        
        # Calculate collision normal (simplified)
        x1, y1 = obj1.position
        x2, y2 = obj2.position
        
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Normalize
        nx = dx / distance
        ny = dy / distance
        
        # Relative velocity
        dvx = v2x - v1x
        dvy = v2y - v1y
        
        # Relative velocity in collision normal direction
        dvn = dvx * nx + dvy * ny
        
        # Do not resolve if velocities are separating
        if dvn > 0:
            return
        
        # Collision impulse
        impulse = 2 * dvn / (obj1.mass + obj2.mass)
        
        # Update velocities
        obj1.velocity = (v1x + impulse * obj2.mass * nx, 
                        v1y + impulse * obj2.mass * ny)
        obj2.velocity = (v2x - impulse * obj1.mass * nx, 
                        v2y - impulse * obj1.mass * ny)
        
        # Apply restitution
        obj1.velocity = (obj1.velocity[0] * self.restitution,
                        obj1.velocity[1] * self.restitution)
        obj2.velocity = (obj2.velocity[0] * self.restitution,
                        obj2.velocity[1] * self.restitution)
    
    def check_bounds_collision(self, game_object: GameObject, 
                              bounds: Tuple[float, float, float, float]) -> bool:
        """Check if object is colliding with bounds"""
        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds
        
        return (obj_bounds[0] < min_x or obj_bounds[2] > max_x or
                obj_bounds[1] < min_y or obj_bounds[3] > max_y)
    
    def constrain_to_bounds(self, game_object: GameObject, 
                           bounds: Tuple[float, float, float, float]):
        """Constrain object to bounds"""
        obj_bounds = game_object.get_bounds()
        min_x, min_y, max_x, max_y = bounds
        x, y = game_object.position
        
        obj_width = obj_bounds[2] - obj_bounds[0]
        obj_height = obj_bounds[3] - obj_bounds[1]
        
        # Constrain position
        new_x = max(min_x, min(x, max_x - obj_width))
        new_y = max(min_y, min(y, max_y - obj_height))
        
        # If position changed, reverse velocity
        if new_x != x:
            game_object.velocity = (-game_object.velocity[0] * self.restitution,
                                   game_object.velocity[1])
        if new_y != y:
            game_object.velocity = (game_object.velocity[0],
                                   -game_object.velocity[1] * self.restitution)
        
        game_object.position = (new_x, new_y)
    
    def apply_force(self, game_object: GameObject, force_x: float, force_y: float):
        """Apply force to game object"""
        if game_object.mass <= 0:
            return
        
        # F = ma, so a = F/m
        ax, ay = game_object.acceleration
        game_object.acceleration = (ax + force_x / game_object.mass,
                                   ay + force_y / game_object.mass)
    
    def set_gravity(self, gx: float, gy: float):
        """Set gravity vector"""
        self.gravity = (gx, gy)
    
    def enable_physics(self, enabled: bool):
        """Enable or disable physics"""
        self.enabled = enabled
    
    def enable_collision(self, enabled: bool):
        """Enable or disable collision detection"""
        self.collision_enabled = enabled
    
    def get_objects_in_range(self, center_x: float, center_y: float, 
                            radius: float, objects: List[GameObject]) -> List[GameObject]:
        """Get all objects within a certain range"""
        result = []
        for obj in objects:
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
                if obj.contains_point(x, y):
                    return obj
        
        return None
