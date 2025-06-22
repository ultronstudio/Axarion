
"""
Axarion Engine Animation System
Handles smooth animations and tweening
"""

import math
from typing import Dict, Any, Callable, Optional, List
from .game_object import GameObject

class Easing:
    """Easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return 1 - pow(-2 * t + 2, 2) / 2
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def bounce_out(t: float) -> float:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375

class Animation:
    """Single animation instance"""
    
    def __init__(self, target: GameObject, property_name: str, 
                 start_value: Any, end_value: Any, duration: float,
                 easing_func: Callable[[float], float] = Easing.linear,
                 on_complete: Optional[Callable] = None):
        self.target = target
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing_func = easing_func
        self.on_complete = on_complete
        
        self.current_time = 0.0
        self.completed = False
        
    def update(self, delta_time: float) -> bool:
        """Update animation, returns True if still running"""
        if self.completed:
            return False
            
        self.current_time += delta_time
        t = min(self.current_time / self.duration, 1.0)
        eased_t = self.easing_func(t)
        
        # Interpolate value
        if isinstance(self.start_value, tuple):
            # Handle tuples (like position)
            current_value = tuple(
                self.start_value[i] + (self.end_value[i] - self.start_value[i]) * eased_t
                for i in range(len(self.start_value))
            )
        else:
            # Handle single values
            current_value = self.start_value + (self.end_value - self.start_value) * eased_t
        
        # Set property
        if self.property_name == "position":
            self.target.position = current_value
        elif self.property_name == "rotation":
            self.target.rotation = current_value
        elif self.property_name == "scale":
            self.target.scale = current_value
        else:
            self.target.set_property(self.property_name, current_value)
        
        # Check completion
        if t >= 1.0:
            self.completed = True
            if self.on_complete:
                self.on_complete()
            return False
        
        return True

class AnimationSystem:
    """Manages all animations"""
    
    def __init__(self):
        self.animations: List[Animation] = []
        
    def animate(self, target: GameObject, property_name: str,
                end_value: Any, duration: float,
                easing_func: Callable[[float], float] = Easing.linear,
                on_complete: Optional[Callable] = None) -> Animation:
        """Create and start an animation"""
        
        # Get current value
        if property_name == "position":
            start_value = target.position
        elif property_name == "rotation":
            start_value = target.rotation
        elif property_name == "scale":
            start_value = target.scale
        else:
            start_value = target.get_property(property_name, 0)
        
        animation = Animation(
            target, property_name, start_value, end_value,
            duration, easing_func, on_complete
        )
        
        self.animations.append(animation)
        return animation
    
    def move_to(self, target: GameObject, x: float, y: float, duration: float,
                easing_func: Callable[[float], float] = Easing.ease_out_quad) -> Animation:
        """Animate object to position"""
        return self.animate(target, "position", (x, y), duration, easing_func)
    
    def rotate_to(self, target: GameObject, angle: float, duration: float,
                  easing_func: Callable[[float], float] = Easing.ease_out_quad) -> Animation:
        """Animate object rotation"""
        return self.animate(target, "rotation", angle, duration, easing_func)
    
    def scale_to(self, target: GameObject, scale_x: float, scale_y: float, duration: float,
                 easing_func: Callable[[float], float] = Easing.ease_out_quad) -> Animation:
        """Animate object scale"""
        return self.animate(target, "scale", (scale_x, scale_y), duration, easing_func)
    
    def fade_to(self, target: GameObject, alpha: float, duration: float,
                easing_func: Callable[[float], float] = Easing.linear) -> Animation:
        """Animate object opacity"""
        return self.animate(target, "alpha", alpha, duration, easing_func)
    
    def bounce(self, target: GameObject, height: float, duration: float) -> Animation:
        """Create bounce animation"""
        current_y = target.position[1]
        return self.animate(
            target, "position", 
            (target.position[0], current_y - height),
            duration / 2, Easing.ease_out_quad,
            lambda: self.animate(
                target, "position",
                (target.position[0], current_y),
                duration / 2, Easing.bounce_out
            )
        )
    
    def pulse(self, target: GameObject, scale_factor: float, duration: float) -> Animation:
        """Create pulsing animation"""
        original_scale = target.scale
        return self.animate(
            target, "scale",
            (original_scale[0] * scale_factor, original_scale[1] * scale_factor),
            duration / 2, Easing.ease_out_quad,
            lambda: self.animate(
                target, "scale", original_scale,
                duration / 2, Easing.ease_out_quad
            )
        )
    
    def stop_animations(self, target: GameObject):
        """Stop all animations for a target"""
        self.animations = [anim for anim in self.animations if anim.target != target]
    
    def update(self, delta_time: float):
        """Update all animations"""
        active_animations = []
        for animation in self.animations:
            if animation.update(delta_time):
                active_animations.append(animation)
        
        self.animations = active_animations
    
    def clear(self):
        """Clear all animations"""
        self.animations.clear()

# Global animation system
animation_system = AnimationSystem()

# Convenience functions for scripts
def animate_to(target, x: float, y: float, duration: float = 1.0):
    """Animate object to position"""
    return animation_system.move_to(target, x, y, duration)

def rotate_by(target, angle: float, duration: float = 1.0):
    """Rotate object by angle"""
    current_rotation = target.rotation
    return animation_system.rotate_to(target, current_rotation + angle, duration)

def bounce_object(target, height: float = 50, duration: float = 1.0):
    """Make object bounce"""
    return animation_system.bounce(target, height, duration)

def pulse_object(target, scale: float = 1.2, duration: float = 0.5):
    """Make object pulse"""
    return animation_system.pulse(target, scale, duration)
