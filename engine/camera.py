
"""
Advanced Camera System for Axarion Engine
Provides camera controls, effects, and smooth following
"""

import math
from typing import Tuple, Optional, Dict, Any
from .game_object import GameObject

class Camera:
    """Advanced camera system with smooth following and effects"""
    
    def __init__(self, x: float = 0, y: float = 0, width: int = 800, height: int = 600):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Target following
        self.target: Optional[GameObject] = None
        self.follow_speed = 5.0
        self.follow_offset = (0, 0)
        self.deadzone = (50, 50)  # Area where camera doesn't move
        
        # Camera bounds
        self.bounds_enabled = False
        self.min_x = 0
        self.min_y = 0
        self.max_x = 1000
        self.max_y = 1000
        
        # Camera shake
        self.shake_enabled = False
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        
        # Zoom
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 2.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Camera effects
        self.effects: Dict[str, Any] = {}
        
        # Smooth movement
        self.smooth_movement = True
        self.lerp_factor = 0.1
        
    def update(self, delta_time: float):
        """Update camera"""
        # Update target following
        if self.target:
            self.update_follow(delta_time)
        
        # Update zoom
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed * delta_time
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
        
        # Update shake
        if self.shake_enabled:
            self.update_shake(delta_time)
        
        # Apply bounds
        if self.bounds_enabled:
            self.apply_bounds()
        
        # Update effects
        self.update_effects(delta_time)
    
    def update_follow(self, delta_time: float):
        """Update target following behavior"""
        if not self.target:
            return
        
        target_x, target_y = self.target.position
        target_x += self.follow_offset[0]
        target_y += self.follow_offset[1]
        
        # Calculate target camera position (centered on target)
        desired_x = target_x - self.width / (2 * self.zoom)
        desired_y = target_y - self.height / (2 * self.zoom)
        
        # Apply deadzone
        dx = desired_x - self.x
        dy = desired_y - self.y
        
        deadzone_x, deadzone_y = self.deadzone
        
        if abs(dx) > deadzone_x:
            if dx > 0:
                desired_x = self.x + deadzone_x
            else:
                desired_x = self.x - deadzone_x
        else:
            desired_x = self.x
        
        if abs(dy) > deadzone_y:
            if dy > 0:
                desired_y = self.y + deadzone_y
            else:
                desired_y = self.y - deadzone_y
        else:
            desired_y = self.y
        
        # Smooth movement
        if self.smooth_movement:
            self.x += (desired_x - self.x) * self.follow_speed * delta_time
            self.y += (desired_y - self.y) * self.follow_speed * delta_time
        else:
            self.x = desired_x
            self.y = desired_y
    
    def update_shake(self, delta_time: float):
        """Update camera shake effect"""
        self.shake_timer -= delta_time
        
        if self.shake_timer <= 0:
            self.shake_enabled = False
            self.shake_offset = (0, 0)
            return
        
        # Generate random shake offset
        import random
        angle = random.uniform(0, 2 * math.pi)
        distance = self.shake_intensity * (self.shake_timer / self.shake_duration)
        
        self.shake_offset = (
            math.cos(angle) * distance,
            math.sin(angle) * distance
        )
    
    def update_effects(self, delta_time: float):
        """Update camera effects"""
        effects_to_remove = []
        
        for effect_name, effect_data in self.effects.items():
            if effect_data["duration"] > 0:
                effect_data["duration"] -= delta_time
                
                if effect_data["duration"] <= 0:
                    effects_to_remove.append(effect_name)
                else:
                    # Update effect
                    if effect_name == "pan":
                        self.update_pan_effect(effect_data, delta_time)
                    elif effect_name == "zoom_to":
                        self.update_zoom_effect(effect_data, delta_time)
        
        for effect_name in effects_to_remove:
            del self.effects[effect_name]
    
    def update_pan_effect(self, effect_data: Dict, delta_time: float):
        """Update pan effect"""
        target_x = effect_data["target_x"]
        target_y = effect_data["target_y"]
        speed = effect_data["speed"]
        
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 1:
            move_distance = speed * delta_time
            if move_distance >= distance:
                self.x = target_x
                self.y = target_y
                effect_data["duration"] = 0  # End effect
            else:
                self.x += (dx / distance) * move_distance
                self.y += (dy / distance) * move_distance
    
    def update_zoom_effect(self, effect_data: Dict, delta_time: float):
        """Update zoom effect"""
        target_zoom = effect_data["target_zoom"]
        speed = effect_data["speed"]
        
        zoom_diff = target_zoom - self.zoom
        
        if abs(zoom_diff) > 0.01:
            zoom_change = speed * delta_time
            if abs(zoom_change) >= abs(zoom_diff):
                self.zoom = target_zoom
                effect_data["duration"] = 0
            else:
                self.zoom += zoom_change if zoom_diff > 0 else -zoom_change
    
    def apply_bounds(self):
        """Apply camera bounds"""
        # Adjust bounds for zoom
        effective_width = self.width / self.zoom
        effective_height = self.height / self.zoom
        
        self.x = max(self.min_x, min(self.max_x - effective_width, self.x))
        self.y = max(self.min_y, min(self.max_y - effective_height, self.y))
    
    def follow(self, target: GameObject, offset: Tuple[float, float] = (0, 0)):
        """Set target to follow"""
        self.target = target
        self.follow_offset = offset
    
    def stop_following(self):
        """Stop following target"""
        self.target = None
    
    def set_position(self, x: float, y: float):
        """Set camera position"""
        self.x = x
        self.y = y
    
    def move(self, dx: float, dy: float):
        """Move camera by offset"""
        self.x += dx
        self.y += dy
    
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float):
        """Set camera bounds"""
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.bounds_enabled = True
    
    def disable_bounds(self):
        """Disable camera bounds"""
        self.bounds_enabled = False
    
    def shake(self, intensity: float, duration: float):
        """Start camera shake"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration
        self.shake_enabled = True
    
    def set_zoom(self, zoom: float, smooth: bool = True):
        """Set zoom level"""
        zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
        if smooth:
            self.target_zoom = zoom
        else:
            self.zoom = zoom
            self.target_zoom = zoom
    
    def zoom_in(self, factor: float = 1.5):
        """Zoom in by factor"""
        self.set_zoom(self.zoom * factor)
    
    def zoom_out(self, factor: float = 1.5):
        """Zoom out by factor"""
        self.set_zoom(self.zoom / factor)
    
    def pan_to(self, x: float, y: float, speed: float = 200, duration: float = 0):
        """Pan camera to position"""
        if duration == 0:
            # Calculate duration based on distance and speed
            distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
            duration = distance / speed if speed > 0 else 1.0
        
        self.effects["pan"] = {
            "target_x": x,
            "target_y": y,
            "speed": speed,
            "duration": duration
        }
    
    def zoom_to(self, zoom: float, speed: float = 2.0, duration: float = 1.0):
        """Zoom to specific level over time"""
        zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
        self.effects["zoom_to"] = {
            "target_zoom": zoom,
            "speed": abs(zoom - self.zoom) / duration,
            "duration": duration
        }
    
    def get_world_position(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x / self.zoom) + self.x
        world_y = (screen_y / self.zoom) + self.y
        return (world_x, world_y)
    
    def get_screen_position(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        return (screen_x, screen_y)
    
    def get_view_bounds(self) -> Tuple[float, float, float, float]:
        """Get camera view bounds in world coordinates"""
        shake_x, shake_y = self.shake_offset
        effective_x = self.x + shake_x
        effective_y = self.y + shake_y
        
        width = self.width / self.zoom
        height = self.height / self.zoom
        
        return (effective_x, effective_y, effective_x + width, effective_y + height)
    
    def is_visible(self, world_x: float, world_y: float, width: float = 0, height: float = 0) -> bool:
        """Check if a world position/area is visible in camera"""
        view_bounds = self.get_view_bounds()
        
        return not (world_x + width < view_bounds[0] or world_x > view_bounds[2] or
                   world_y + height < view_bounds[1] or world_y > view_bounds[3])
    
    def apply_to_renderer(self, renderer):
        """Apply camera transform to renderer"""
        shake_x, shake_y = self.shake_offset
        renderer.set_camera(self.x + shake_x, self.y + shake_y)
        
        # Apply zoom if renderer supports it
        if hasattr(renderer, 'set_zoom'):
            renderer.set_zoom(self.zoom)
