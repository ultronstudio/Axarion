
"""
Axarion Engine Advanced Renderer
Sprite batching, lighting system, and Z-ordering
"""

import pygame
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from .game_object import GameObject
from .renderer import Renderer

@dataclass
class Light:
    """Light source definition"""
    position: Tuple[float, float]
    color: Tuple[int, int, int]
    intensity: float
    radius: float
    light_type: str = "point"  # point, directional, spot
    enabled: bool = True
    angle: float = 0  # For directional/spot lights
    cone_angle: float = 90  # For spot lights

@dataclass
class RenderBatch:
    """Batch of similar objects for efficient rendering"""
    object_type: str
    texture_id: Optional[str]
    objects: List[GameObject]
    z_order: int = 0

class LayerManager:
    """Manages rendering layers and Z-ordering"""
    
    def __init__(self):
        self.layers: Dict[str, int] = {}  # layer_name -> z_order
        self.default_layer = "default"
        self.max_z_order = 1000
        
        # Default layers
        self.layers["background"] = -100
        self.layers["ground"] = -50
        self.layers["default"] = 0
        self.layers["objects"] = 50
        self.layers["effects"] = 100
        self.layers["ui"] = 200
    
    def add_layer(self, layer_name: str, z_order: int):
        """Add rendering layer"""
        self.layers[layer_name] = z_order
    
    def get_z_order(self, layer_name: str) -> int:
        """Get Z order for layer"""
        return self.layers.get(layer_name, 0)
    
    def sort_objects(self, objects: List[GameObject]) -> List[GameObject]:
        """Sort objects by Z order"""
        def get_sort_key(obj):
            layer_z = self.get_z_order(obj.render_layer)
            object_z = getattr(obj, 'z_order', 0)
            return layer_z + object_z
        
        return sorted(objects, key=get_sort_key)

class SpriteBatcher:
    """Batches sprites for efficient rendering"""
    
    def __init__(self):
        self.batches: List[RenderBatch] = []
        self.current_batch: Optional[RenderBatch] = None
        self.max_batch_size = 100
    
    def begin_batch(self):
        """Begin batching"""
        self.batches.clear()
        self.current_batch = None
    
    def add_object(self, obj: GameObject):
        """Add object to appropriate batch"""
        texture_id = None
        if obj.object_type in ["sprite", "animated_sprite"]:
            texture_id = getattr(obj, 'current_sprite_name', None)
        
        # Find existing batch or create new one
        batch = self._find_compatible_batch(obj.object_type, texture_id)
        if not batch or len(batch.objects) >= self.max_batch_size:
            batch = RenderBatch(
                object_type=obj.object_type,
                texture_id=texture_id,
                objects=[],
                z_order=getattr(obj, 'z_order', 0)
            )
            self.batches.append(batch)
        
        batch.objects.append(obj)
        self.current_batch = batch
    
    def end_batch(self):
        """End batching and sort"""
        self.batches.sort(key=lambda b: b.z_order)
    
    def _find_compatible_batch(self, object_type: str, texture_id: Optional[str]) -> Optional[RenderBatch]:
        """Find compatible batch for object"""
        for batch in self.batches:
            if (batch.object_type == object_type and 
                batch.texture_id == texture_id and
                len(batch.objects) < self.max_batch_size):
                return batch
        return None

class LightingSystem:
    """Dynamic lighting system"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.lights: List[Light] = []
        self.ambient_color = (50, 50, 80)  # Dark blue ambient
        self.ambient_intensity = 0.3
        
        # Lighting surfaces
        self.light_surface = pygame.Surface((width, height))
        self.shadow_surface = pygame.Surface((width, height))
        
        # Performance settings
        self.enabled = True
        self.quality = "medium"  # low, medium, high
        self.max_lights = 20
    
    def add_light(self, x: float, y: float, color: Tuple[int, int, int], 
                  intensity: float = 1.0, radius: float = 100.0, 
                  light_type: str = "point") -> Light:
        """Add light source"""
        if len(self.lights) >= self.max_lights:
            return None
        
        light = Light(
            position=(x, y),
            color=color,
            intensity=intensity,
            radius=radius,
            light_type=light_type
        )
        
        self.lights.append(light)
        return light
    
    def remove_light(self, light: Light):
        """Remove light source"""
        if light in self.lights:
            self.lights.remove(light)
    
    def update_light(self, light: Light, x: float, y: float):
        """Update light position"""
        light.position = (x, y)
    
    def render_lighting(self, camera_x: float, camera_y: float) -> pygame.Surface:
        """Render lighting to surface"""
        if not self.enabled:
            return None
        
        # Clear lighting surface with ambient
        ambient_r = int(self.ambient_color[0] * self.ambient_intensity)
        ambient_g = int(self.ambient_color[1] * self.ambient_intensity)
        ambient_b = int(self.ambient_color[2] * self.ambient_intensity)
        self.light_surface.fill((ambient_r, ambient_g, ambient_b))
        
        # Render each light
        for light in self.lights:
            if not light.enabled:
                continue
            
            self._render_light(light, camera_x, camera_y)
        
        return self.light_surface
    
    def _render_light(self, light: Light, camera_x: float, camera_y: float):
        """Render individual light"""
        screen_x = int(light.position[0] - camera_x)
        screen_y = int(light.position[1] - camera_y)
        
        # Skip lights outside screen
        if (screen_x < -light.radius or screen_x > self.width + light.radius or
            screen_y < -light.radius or screen_y > self.height + light.radius):
            return
        
        if light.light_type == "point":
            self._render_point_light(light, screen_x, screen_y)
        elif light.light_type == "directional":
            self._render_directional_light(light, screen_x, screen_y)
        elif light.light_type == "spot":
            self._render_spot_light(light, screen_x, screen_y)
    
    def _render_point_light(self, light: Light, screen_x: int, screen_y: int):
        """Render point light"""
        radius = int(light.radius)
        
        # Create light gradient surface
        light_size = radius * 2
        light_surf = pygame.Surface((light_size, light_size), pygame.SRCALPHA)
        
        # Draw gradient circles
        steps = 20 if self.quality == "high" else 10
        for i in range(steps):
            t = i / steps
            current_radius = int(radius * (1 - t))
            alpha = int(255 * light.intensity * (1 - t * t))
            
            if alpha > 0 and current_radius > 0:
                color = (*light.color, alpha)
                pygame.draw.circle(light_surf, color, (radius, radius), current_radius)
        
        # Blit to lighting surface with additive blending
        blend_rect = light_surf.get_rect()
        blend_rect.center = (screen_x, screen_y)
        self.light_surface.blit(light_surf, blend_rect, special_flags=pygame.BLEND_ADD)
    
    def _render_directional_light(self, light: Light, screen_x: int, screen_y: int):
        """Render directional light"""
        # Simplified directional light as large gradient
        angle_rad = math.radians(light.angle)
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        
        # Create directional light effect
        for y in range(self.height):
            for x in range(self.width):
                # Calculate light contribution based on direction
                dot = dx * (x - screen_x) + dy * (y - screen_y)
                if dot > 0:
                    intensity = min(1.0, dot / light.radius) * light.intensity
                    if intensity > 0:
                        current_color = self.light_surface.get_at((x, y))
                        new_r = min(255, current_color[0] + int(light.color[0] * intensity))
                        new_g = min(255, current_color[1] + int(light.color[1] * intensity))
                        new_b = min(255, current_color[2] + int(light.color[2] * intensity))
                        self.light_surface.set_at((x, y), (new_r, new_g, new_b))
    
    def _render_spot_light(self, light: Light, screen_x: int, screen_y: int):
        """Render spot light"""
        # Similar to point light but with cone constraint
        angle_rad = math.radians(light.angle)
        cone_rad = math.radians(light.cone_angle / 2)
        
        radius = int(light.radius)
        light_size = radius * 2
        light_surf = pygame.Surface((light_size, light_size), pygame.SRCALPHA)
        
        for y in range(light_size):
            for x in range(light_size):
                # Calculate angle from light center
                dx = x - radius
                dy = y - radius
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= radius:
                    # Check if point is within cone
                    point_angle = math.atan2(dy, dx)
                    angle_diff = abs(point_angle - angle_rad)
                    
                    if angle_diff <= cone_rad:
                        intensity = (1.0 - distance / radius) * light.intensity
                        cone_falloff = 1.0 - (angle_diff / cone_rad)
                        final_intensity = intensity * cone_falloff
                        
                        alpha = int(255 * final_intensity)
                        if alpha > 0:
                            light_surf.set_at((x, y), (*light.color, alpha))
        
        # Blit to lighting surface
        blend_rect = light_surf.get_rect()
        blend_rect.center = (screen_x, screen_y)
        self.light_surface.blit(light_surf, blend_rect, special_flags=pygame.BLEND_ADD)

class AdvancedRenderer(Renderer):
    """Advanced renderer with batching and lighting"""
    
    def __init__(self, width: int, height: int, surface=None):
        super().__init__(width, height, surface)
        
        # Advanced systems
        self.layer_manager = LayerManager()
        self.sprite_batcher = SpriteBatcher()
        self.lighting_system = LightingSystem(width, height)
        
        # Rendering modes
        self.use_batching = True
        self.use_lighting = True
        self.use_z_ordering = True
        
        # Performance tracking
        self.batch_count = 0
        self.draw_calls_saved = 0
    
    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear screen and reset counters"""
        super().clear(color)
        self.batch_count = 0
        self.draw_calls_saved = 0
    
    def render_scene(self, objects: List[GameObject]):
        """Render entire scene with advanced features"""
        if not objects:
            return
        
        # Filter visible objects
        visible_objects = [obj for obj in objects 
                          if obj.visible and not obj.destroyed and self.is_on_screen(obj)]
        
        # Sort by Z-order if enabled
        if self.use_z_ordering:
            visible_objects = self.layer_manager.sort_objects(visible_objects)
        
        # Batch rendering if enabled
        if self.use_batching:
            self._render_batched(visible_objects)
        else:
            self._render_individual(visible_objects)
        
        # Apply lighting if enabled
        if self.use_lighting:
            self._apply_lighting()
    
    def _render_batched(self, objects: List[GameObject]):
        """Render objects using batching"""
        self.sprite_batcher.begin_batch()
        
        # Add objects to batches
        for obj in objects:
            self.sprite_batcher.add_object(obj)
        
        self.sprite_batcher.end_batch()
        
        # Render each batch
        individual_calls = 0
        for batch in self.sprite_batcher.batches:
            if batch.object_type in ["sprite", "animated_sprite"] and batch.texture_id:
                # Batch render sprites with same texture
                self._render_sprite_batch(batch)
                self.batch_count += 1
                individual_calls += len(batch.objects)
            else:
                # Render individually for non-batchable objects
                for obj in batch.objects:
                    self.draw_game_object(obj)
                    individual_calls += 1
        
        self.draw_calls_saved = individual_calls - self.batch_count
    
    def _render_individual(self, objects: List[GameObject]):
        """Render objects individually"""
        for obj in objects:
            self.draw_game_object(obj)
    
    def _render_sprite_batch(self, batch: RenderBatch):
        """Render batch of sprites efficiently"""
        if not batch.objects:
            return
        
        # Get shared texture
        first_obj = batch.objects[0]
        sprite_surface = first_obj.get_current_sprite()
        
        if not sprite_surface:
            # Fallback to individual rendering
            for obj in batch.objects:
                self.draw_game_object(obj)
            return
        
        # Render all sprites with same texture in one call
        for obj in batch.objects:
            x, y = obj.position
            rotation = obj.rotation
            scale = getattr(obj, 'scale', (1.0, 1.0))
            
            self.draw_sprite(x, y, sprite_surface, rotation, scale)
    
    def _apply_lighting(self):
        """Apply lighting to rendered scene"""
        light_surface = self.lighting_system.render_lighting(self.camera_x, self.camera_y)
        
        if light_surface:
            # Apply lighting with multiply blend mode
            self.screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def add_light(self, x: float, y: float, color: Tuple[int, int, int], 
                  intensity: float = 1.0, radius: float = 100.0) -> Light:
        """Add light to scene"""
        return self.lighting_system.add_light(x, y, color, intensity, radius)
    
    def remove_light(self, light: Light):
        """Remove light from scene"""
        self.lighting_system.remove_light(light)
    
    def set_ambient_lighting(self, color: Tuple[int, int, int], intensity: float = 0.3):
        """Set ambient lighting"""
        self.lighting_system.ambient_color = color
        self.lighting_system.ambient_intensity = intensity
    
    def add_render_layer(self, layer_name: str, z_order: int):
        """Add rendering layer"""
        self.layer_manager.add_layer(layer_name, z_order)
    
    def enable_batching(self, enabled: bool):
        """Enable sprite batching"""
        self.use_batching = enabled
    
    def enable_lighting(self, enabled: bool):
        """Enable lighting system"""
        self.use_lighting = enabled
        self.lighting_system.enabled = enabled
    
    def enable_z_ordering(self, enabled: bool):
        """Enable Z-ordering"""
        self.use_z_ordering = enabled
    
    def set_lighting_quality(self, quality: str):
        """Set lighting quality (low, medium, high)"""
        self.lighting_system.quality = quality
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Get rendering statistics"""
        stats = {
            "objects_rendered": self.objects_rendered,
            "render_calls": self.render_calls,
            "batch_count": self.batch_count,
            "draw_calls_saved": self.draw_calls_saved,
            "lights_active": len([l for l in self.lighting_system.lights if l.enabled]),
            "batching_enabled": self.use_batching,
            "lighting_enabled": self.use_lighting
        }
        return stats
