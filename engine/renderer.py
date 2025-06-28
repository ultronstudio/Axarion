
"""
Axarion Engine Renderer
Handles 2D rendering operations using Pygame
"""

import pygame
import math
from typing import Dict, Tuple, Optional, List
from .game_object import GameObject

class Renderer:
    """2D renderer for the Axarion Engine"""
    
    def __init__(self, width: int, height: int, surface=None):
        self.width = width
        self.height = height
        
        # Create or use provided surface
        if surface:
            self.screen = surface
        else:
            self.screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Axarion Engine")
        
        # Rendering state
        self.camera_x = 0
        self.camera_y = 0
        self.background_color = (30, 30, 40)  # Dark blue-gray
        
        # Initialize fonts
        pygame.font.init()
        try:
            self.default_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)
            self.large_font = pygame.font.Font(None, 32)
        except:
            self.default_font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 16)
            self.large_font = pygame.font.SysFont('arial', 32)
        
        # Debug rendering
        self.debug_mode = False
        self.show_bounds = False
        self.show_velocity = False
        
        # Performance tracking
        self.render_calls = 0
        self.objects_rendered = 0
        
        # Sprite batching system
        self.enable_sprite_batching = True
        self.sprite_batches = {}
        self.current_batch_size = 0
        self.max_batch_size = 100
        
        # Frustum culling
        self.enable_frustum_culling = True
        self.camera_bounds = (0, 0, width, height)
        
        # Layer system
        self.layers = {}
        self.sorted_layers = []
        
        # Quality settings
        self.enable_antialiasing = True
        self.particle_limit = 500
        
        # UNLIMITED RENDERING FEATURES
        self.unlimited_mode = True
        self.layered_rendering = True
        self.post_processing_enabled = True
        self.lighting_enabled = False
        self.shadows_enabled = False
        self.particle_rendering = True
        
        # Advanced visual features
        self.render_layers = {}
        self.post_effects = []
        self.lights = []
        self.shaders = {}
        self.framebuffers = {}
        
        # Visual effects
        self.screen_shake = {"active": False, "intensity": 0, "duration": 0}
        self.camera_effects = []
        self.transition_effects = []
        
        # Genre-specific rendering
        self.rpg_ui_elements = []
        self.hud_elements = []
        self.minimap = None
        self.dialog_boxes = []
    
    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear the screen with specified color"""
        if color is None:
            color = self.background_color
        self.screen.fill(color)
        
        # Reset counters
        self.render_calls = 0
        self.objects_rendered = 0
    
    def present(self):
        """Present the rendered frame"""
        # Draw debug info if enabled
        if self.debug_mode:
            self.draw_debug_info()
        
        pygame.display.flip()
    
    def draw_rect(self, x: float, y: float, width: float, height: float, 
                  color: Tuple[int, int, int], filled: bool = True, 
                  rotation: float = 0, border_width: int = 0):
        """Draw a rectangle"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        if rotation == 0:
            # Simple non-rotated rectangle
            rect = pygame.Rect(screen_x, screen_y, int(width), int(height))
            
            if filled:
                pygame.draw.rect(self.screen, color, rect)
            
            if border_width > 0:
                pygame.draw.rect(self.screen, color, rect, border_width)
        else:
            # Rotated rectangle
            self.draw_rotated_rect(screen_x, screen_y, width, height, color, rotation, filled)
        
        self.render_calls += 1
    
    def draw_rotated_rect(self, x: float, y: float, width: float, height: float,
                         color: Tuple[int, int, int], rotation: float, filled: bool = True):
        """Draw a rotated rectangle"""
        # Create surface for the rectangle
        rect_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if filled:
            rect_surface.fill(color)
        else:
            pygame.draw.rect(rect_surface, color, (0, 0, width, height), 2)
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(rect_surface, -rotation)
        
        # Calculate new position
        rotated_rect = rotated_surface.get_rect()
        rotated_rect.center = (x + width/2, y + height/2)
        
        # Blit to screen
        self.screen.blit(rotated_surface, rotated_rect)
    
    def draw_circle(self, x: float, y: float, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True, border_width: int = 0):
        """Draw a circle"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        if filled:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(radius))
        
        if border_width > 0:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(radius), border_width)
        
        self.render_calls += 1
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float, 
                  color: Tuple[int, int, int], width: int = 1):
        """Draw a line"""
        start_pos = (int(x1 - self.camera_x), int(y1 - self.camera_y))
        end_pos = (int(x2 - self.camera_x), int(y2 - self.camera_y))
        pygame.draw.line(self.screen, color, start_pos, end_pos, width)
        self.render_calls += 1
    
    def draw_polygon(self, points: List[Tuple[float, float]], 
                    color: Tuple[int, int, int], filled: bool = True):
        """Draw a polygon"""
        screen_points = [(int(x - self.camera_x), int(y - self.camera_y)) for x, y in points]
        
        if len(screen_points) < 3:
            return
        
        if filled:
            pygame.draw.polygon(self.screen, color, screen_points)
        else:
            pygame.draw.polygon(self.screen, color, screen_points, 2)
        
        self.render_calls += 1
    
    def draw_sprite(self, x: float, y: float, sprite_surface: pygame.Surface, 
                   rotation: float = 0, scale: Tuple[float, float] = (1.0, 1.0)):
        """Draw a sprite"""
        if not sprite_surface:
            return
        
        # Apply scaling
        if scale != (1.0, 1.0):
            new_width = int(sprite_surface.get_width() * scale[0])
            new_height = int(sprite_surface.get_height() * scale[1])
            sprite_surface = pygame.transform.scale(sprite_surface, (new_width, new_height))
        
        # Apply rotation
        if rotation != 0:
            sprite_surface = pygame.transform.rotate(sprite_surface, -rotation)
        
        # Calculate screen position
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        # Center the sprite
        sprite_rect = sprite_surface.get_rect()
        sprite_rect.center = (screen_x + sprite_surface.get_width()//2, 
                             screen_y + sprite_surface.get_height()//2)
        
        # Draw sprite
        self.screen.blit(sprite_surface, sprite_rect)
        self.render_calls += 1
    
    def draw_text(self, text: str, x: float, y: float, 
                  color: Tuple[int, int, int] = (255, 255, 255),
                  font=None, center: bool = False):
        """Draw text"""
        if font is None:
            font = self.default_font
        
        try:
            text_surface = font.render(str(text), True, color)
            screen_x = int(x - self.camera_x)
            screen_y = int(y - self.camera_y)
            
            if center:
                text_rect = text_surface.get_rect()
                text_rect.center = (screen_x, screen_y)
                self.screen.blit(text_surface, text_rect)
            else:
                self.screen.blit(text_surface, (screen_x, screen_y))
        except Exception as e:
            # Fallback text rendering
            print(f"Text rendering error: {e}")
        
        self.render_calls += 1
    
    def draw_game_object(self, game_object: GameObject):
        """Draw a game object with batching support"""
        if not game_object.visible or game_object.destroyed:
            return
        
        # Frustum culling
        if self.enable_frustum_culling and not self.is_in_camera_bounds(game_object):
            return
        
        # Get layer for rendering order
        layer = getattr(game_object, 'layer', 0)
        
        x, y = game_object.position
        rotation = game_object.rotation
        
        # Get object color with proper fallback
        color = game_object.properties.get("color", (255, 255, 255))
        if not isinstance(color, (tuple, list)) or len(color) < 3:
            color = (255, 255, 255)
        
        # Ensure color values are valid
        color = tuple(max(0, min(255, int(c))) for c in color[:3])
        
        # Draw based on object type
        if game_object.object_type == "rectangle":
            width = game_object.properties.get("width", 50)
            height = game_object.properties.get("height", 50)
            border_width = game_object.properties.get("border_width", 0)
            self.draw_rect(x, y, width, height, color, True, rotation, border_width)
            
        elif game_object.object_type == "square":
            size = game_object.properties.get("size", 50)
            border_width = game_object.properties.get("border_width", 0)
            self.draw_rect(x, y, size, size, color, True, rotation, border_width)
            
        elif game_object.object_type == "triangle":
            size = game_object.properties.get("size", 50)
            triangle_type = game_object.properties.get("triangle_type", "equilateral")
            self.draw_triangle(x, y, size, color, triangle_type, rotation)
            
        elif game_object.object_type == "ellipse":
            width = game_object.properties.get("width", 80)
            height = game_object.properties.get("height", 50)
            self.draw_ellipse(x, y, width, height, color, rotation)
            
        elif game_object.object_type == "polygon":
            points = game_object.properties.get("points", [(0, 0), (50, 0), (25, 50)])
            world_points = [(x + px, y + py) for px, py in points]
            self.draw_polygon(world_points, color, True)
            
        elif game_object.object_type == "star":
            outer_radius = game_object.properties.get("outer_radius", 30)
            inner_radius = game_object.properties.get("inner_radius", 15)
            points = game_object.properties.get("points", 5)
            self.draw_star(x, y, outer_radius, inner_radius, points, color, rotation)
            
        elif game_object.object_type == "hexagon":
            radius = game_object.properties.get("radius", 30)
            self.draw_hexagon(x, y, radius, color, rotation)
            
        elif game_object.object_type == "circle":
            radius = game_object.properties.get("radius", 25)
            border_width = game_object.properties.get("border_width", 0)
            self.draw_circle(x, y, radius, color, True, border_width)
            
        elif game_object.object_type in ["sprite", "animated_sprite", "gif"]:
            # Get sprite surface
            sprite_surface = game_object.get_current_sprite()
            
            if sprite_surface:
                if self.enable_sprite_batching:
                    self.add_to_sprite_batch(game_object, sprite_surface)
                else:
                    self.draw_sprite(x, y, sprite_surface, rotation)
            else:
                # Fallback to rectangle if sprite not found
                width = game_object.properties.get("width", 32)
                height = game_object.properties.get("height", 32)
                sprite_color = game_object.properties.get("color", (100, 150, 255))
                self.draw_rect(x, y, width, height, sprite_color, True, rotation)
                
                # Draw border to indicate missing sprite
                self.draw_rect(x, y, width, height, (255, 0, 0), False, rotation, 2)
            
        elif game_object.object_type == "line":
            end_x = game_object.properties.get("end_x", x + 50)
            end_y = game_object.properties.get("end_y", y)
            width = game_object.properties.get("line_width", 1)
            self.draw_line(x, y, end_x, end_y, color, width)
            
        elif game_object.object_type == "polygon":
            points = game_object.properties.get("points", [(x, y), (x+25, y-25), (x+50, y)])
            self.draw_polygon(points, color, True)
        
        # Debug rendering
        if self.debug_mode or self.show_bounds:
            self.draw_object_debug(game_object)
        
        self.objects_rendered += 1
    
    def is_in_camera_bounds(self, game_object: GameObject) -> bool:
        """Check if object is within camera bounds for culling"""
        bounds = game_object.get_bounds()
        cam_x, cam_y = self.camera_x, self.camera_y
        cam_right = cam_x + self.width
        cam_bottom = cam_y + self.height
        
        return not (bounds[2] < cam_x or bounds[0] > cam_right or 
                   bounds[3] < cam_y or bounds[1] > cam_bottom)
    
    def add_to_sprite_batch(self, game_object, sprite_surface):
        """Add sprite to batch for optimized rendering"""
        batch_key = id(sprite_surface)
        
        if batch_key not in self.sprite_batches:
            self.sprite_batches[batch_key] = {
                'surface': sprite_surface,
                'objects': []
            }
        
        self.sprite_batches[batch_key]['objects'].append(game_object)
        self.current_batch_size += 1
        
        # Flush batch if it's full
        if self.current_batch_size >= self.max_batch_size:
            self.flush_sprite_batches()
    
    def flush_sprite_batches(self):
        """Render all batched sprites"""
        for batch in self.sprite_batches.values():
            for obj in batch['objects']:
                x, y = obj.position
                rotation = obj.rotation
                self.draw_sprite(x, y, batch['surface'], rotation)
        
        self.sprite_batches.clear()
        self.current_batch_size = 0
    
    def add_to_layer(self, layer_id: int, game_object: GameObject):
        """Add object to rendering layer"""
        if layer_id not in self.layers:
            self.layers[layer_id] = []
            self._sort_layers()
        
        self.layers[layer_id].append(game_object)
        game_object.layer = layer_id
    
    def _sort_layers(self):
        """Sort layers by ID for proper rendering order"""
        self.sorted_layers = sorted(self.layers.keys())
    
    def render_layers(self):
        """Render all objects by layer order"""
        for layer_id in self.sorted_layers:
            for obj in self.layers[layer_id]:
                if obj.visible and not obj.destroyed:
                    self.draw_game_object(obj)
    
    def draw_object_debug(self, game_object: GameObject):
        """Draw debug information for an object"""
        bounds = game_object.get_bounds()
        
        # Draw bounding box
        if self.show_bounds:
            self.draw_rect(bounds[0], bounds[1], 
                         bounds[2] - bounds[0], bounds[3] - bounds[1],
                         (255, 0, 0), False, 0, 1)
        
        # Draw velocity vector
        if self.show_velocity:
            vx, vy = game_object.velocity
            if vx != 0 or vy != 0:
                x, y = game_object.position
                end_x = x + vx * 0.1  # Scale down velocity for visualization
                end_y = y + vy * 0.1
                self.draw_line(x, y, end_x, end_y, (0, 255, 0), 2)
        
        # Draw object name
        if hasattr(game_object, 'show_debug') and game_object.show_debug:
            x, y = game_object.position
            self.draw_text(game_object.name, x, y - 25, (255, 255, 0), self.small_font)
    
    def draw_debug_info(self):
        """Draw debug information on screen"""
        debug_y = 10
        line_height = 20
        
        debug_info = [
            f"Render calls: {self.render_calls}",
            f"Objects rendered: {self.objects_rendered}",
            f"Camera: ({self.camera_x:.1f}, {self.camera_y:.1f})",
        ]
        
        for info in debug_info:
            self.draw_text(info, 10, debug_y, (255, 255, 0), self.small_font)
            debug_y += line_height
    
    def set_camera(self, x: float, y: float):
        """Set camera position"""
        self.camera_x = x
        self.camera_y = y
    
    def move_camera(self, dx: float, dy: float):
        """Move camera by offset"""
        self.camera_x += dx
        self.camera_y += dy
    
    def get_camera(self) -> Tuple[float, float]:
        """Get camera position"""
        return (self.camera_x, self.camera_y)
    
    def follow_object(self, game_object: GameObject, offset_x: float = 0, offset_y: float = 0):
        """Make camera follow an object"""
        x, y = game_object.position
        self.camera_x = x - self.width / 2 + offset_x
        self.camera_y = y - self.height / 2 + offset_y
    
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.camera_x
        world_y = screen_y + self.camera_y
        return (world_x, world_y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_x - self.camera_x)
        screen_y = int(world_y - self.camera_y)
        return (screen_x, screen_y)
    
    def is_on_screen(self, game_object: GameObject, margin: float = 50) -> bool:
        """Check if object is visible on screen"""
        bounds = game_object.get_bounds()
        
        return (bounds[2] >= self.camera_x - margin and
                bounds[0] <= self.camera_x + self.width + margin and
                bounds[3] >= self.camera_y - margin and
                bounds[1] <= self.camera_y + self.height + margin)
    
    def set_background_color(self, color: Tuple[int, int, int]):
        """Set background color"""
        self.background_color = color
    
    def enable_debug(self, enabled: bool):
        """Enable debug rendering"""
        self.debug_mode = enabled
    
    def show_object_bounds(self, enabled: bool):
        """Show object bounding boxes"""
        self.show_bounds = enabled
    
    def show_velocity_vectors(self, enabled: bool):
        """Show velocity vectors"""
        self.show_velocity = enabled
    
    def set_vsync(self, enabled: bool):
        """Set VSync (currently not implemented in pygame)"""
        # Note: pygame doesn't have direct VSync control
        # This is a placeholder for engine compatibility
        pass
    
    def draw_triangle(self, x: float, y: float, size: float, color: Tuple[int, int, int], 
                     triangle_type: str = "equilateral", rotation: float = 0):
        """Draw a triangle"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        if triangle_type == "equilateral":
            # Equilateral triangle
            points = [
                (screen_x + size/2, screen_y),
                (screen_x, screen_y + size),
                (screen_x + size, screen_y + size)
            ]
        elif triangle_type == "right":
            # Right triangle
            points = [
                (screen_x, screen_y),
                (screen_x, screen_y + size),
                (screen_x + size, screen_y + size)
            ]
        else:  # isosceles
            points = [
                (screen_x + size/2, screen_y),
                (screen_x, screen_y + size),
                (screen_x + size, screen_y + size)
            ]
        
        if rotation != 0:
            # Apply rotation around center
            center_x = screen_x + size/2
            center_y = screen_y + size/2
            points = self._rotate_points(points, center_x, center_y, rotation)
        
        pygame.draw.polygon(self.screen, color, points)
        self.render_calls += 1
    
    def draw_ellipse(self, x: float, y: float, width: float, height: float, 
                    color: Tuple[int, int, int], rotation: float = 0):
        """Draw an ellipse"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        rect = pygame.Rect(screen_x, screen_y, int(width), int(height))
        
        if rotation == 0:
            pygame.draw.ellipse(self.screen, color, rect)
        else:
            # For rotated ellipse, we need to create a surface and rotate it
            ellipse_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(ellipse_surface, color, (0, 0, width, height))
            
            rotated_surface = pygame.transform.rotate(ellipse_surface, -rotation)
            rotated_rect = rotated_surface.get_rect()
            rotated_rect.center = (screen_x + width/2, screen_y + height/2)
            
            self.screen.blit(rotated_surface, rotated_rect)
        
        self.render_calls += 1
    
    def draw_star(self, x: float, y: float, outer_radius: float, inner_radius: float, 
                  points: int, color: Tuple[int, int, int], rotation: float = 0):
        """Draw a star"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        star_points = []
        angle_step = math.pi / points
        
        for i in range(points * 2):
            angle = i * angle_step + math.radians(rotation)
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = screen_x + math.cos(angle) * radius
            py = screen_y + math.sin(angle) * radius
            star_points.append((px, py))
        
        pygame.draw.polygon(self.screen, color, star_points)
        self.render_calls += 1
    
    def draw_hexagon(self, x: float, y: float, radius: float, 
                    color: Tuple[int, int, int], rotation: float = 0):
        """Draw a hexagon"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        points = []
        for i in range(6):
            angle = i * math.pi / 3 + math.radians(rotation)
            px = screen_x + math.cos(angle) * radius
            py = screen_y + math.sin(angle) * radius
            points.append((px, py))
        
        pygame.draw.polygon(self.screen, color, points)
        self.render_calls += 1
    
    def _rotate_points(self, points: List[Tuple[float, float]], 
                      center_x: float, center_y: float, rotation: float) -> List[Tuple[float, float]]:
        """Rotate points around a center"""
        rotated_points = []
        cos_r = math.cos(math.radians(rotation))
        sin_r = math.sin(math.radians(rotation))
        
        for px, py in points:
            # Translate to origin
            px -= center_x
            py -= center_y
            
            # Rotate
            new_x = px * cos_r - py * sin_r
            new_y = px * sin_r + py * cos_r
            
            # Translate back
            new_x += center_x
            new_y += center_y
            
            rotated_points.append((new_x, new_y))
        
        return rotated_points

    def cleanup(self):
        """Clean up renderer resources"""
        pass
    
    # UNLIMITED RENDERING METHODS
    
    def enable_unlimited_rendering(self):
        """Enable unlimited rendering capabilities"""
        self.unlimited_mode = True
        self.layered_rendering = True
        self.post_processing_enabled = True
    
    def create_render_layer(self, layer_name: str, z_order: int = 0):
        """Create rendering layer for unlimited visual organization"""
        self.render_layers[layer_name] = {
            "z_order": z_order,
            "objects": [],
            "visible": True,
            "opacity": 1.0
        }
        return self.render_layers[layer_name]
    
    def add_to_layer(self, layer_name: str, game_object):
        """Add object to specific render layer"""
        if layer_name in self.render_layers:
            self.render_layers[layer_name]["objects"].append(game_object)
    
    def render_layered(self):
        """Render all layers in z-order"""
        # Sort layers by z_order
        sorted_layers = sorted(self.render_layers.items(), 
                              key=lambda x: x[1]["z_order"])
        
        for layer_name, layer_data in sorted_layers:
            if layer_data["visible"]:
                self.render_layer(layer_name, layer_data)
    
    def render_layer(self, layer_name: str, layer_data: Dict):
        """Render specific layer"""
        for obj in layer_data["objects"]:
            if obj.visible and not obj.destroyed:
                # Apply layer opacity
                original_opacity = getattr(obj, 'opacity', 1.0)
                obj.opacity = original_opacity * layer_data["opacity"]
                
                self.draw_game_object(obj)
                
                # Restore original opacity
                obj.opacity = original_opacity
    
    def add_post_effect(self, effect_name: str, parameters: Dict):
        """Add post-processing effect"""
        effect = {
            "name": effect_name,
            "params": parameters,
            "enabled": True
        }
        self.post_effects.append(effect)
        return effect
    
    def apply_post_processing(self):
        """Apply all post-processing effects"""
        if not self.post_processing_enabled:
            return
        
        for effect in self.post_effects:
            if effect["enabled"]:
                self.apply_effect(effect)
    
    def apply_effect(self, effect: Dict):
        """Apply single post-processing effect"""
        effect_name = effect["name"]
        params = effect["params"]
        
        if effect_name == "blur":
            self.apply_blur_effect(params)
        elif effect_name == "bloom":
            self.apply_bloom_effect(params)
        elif effect_name == "chromatic_aberration":
            self.apply_chromatic_aberration(params)
        elif effect_name == "color_grading":
            self.apply_color_grading(params)
    
    def apply_blur_effect(self, params: Dict):
        """Apply blur post-processing effect"""
        intensity = params.get("intensity", 5)
        # Simplified blur effect for demonstration
        # In a real implementation, this would use proper image processing
        pass
    
    def apply_bloom_effect(self, params: Dict):
        """Apply bloom post-processing effect"""
        threshold = params.get("threshold", 0.8)
        intensity = params.get("intensity", 1.5)
        # Bloom effect implementation
        pass
    
    def apply_chromatic_aberration(self, params: Dict):
        """Apply chromatic aberration effect"""
        offset = params.get("offset", 2.0)
        # Chromatic aberration implementation
        pass
    
    def apply_color_grading(self, params: Dict):
        """Apply color grading effect"""
        brightness = params.get("brightness", 1.0)
        contrast = params.get("contrast", 1.0)
        saturation = params.get("saturation", 1.0)
        # Color grading implementation
        pass
    
    def enable_lighting(self, ambient_light: float = 0.3):
        """Enable dynamic lighting system"""
        self.lighting_enabled = True
        self.ambient_light = ambient_light
        self.lights = []
    
    def add_light(self, x: float, y: float, radius: float, 
                  color: Tuple[int, int, int] = (255, 255, 255), 
                  intensity: float = 1.0):
        """Add dynamic light source"""
        light = {
            "position": (x, y),
            "radius": radius,
            "color": color,
            "intensity": intensity,
            "enabled": True
        }
        self.lights.append(light)
        return light
    
    def render_lighting(self):
        """Render lighting system"""
        if not self.lighting_enabled:
            return
        
        # Create lighting overlay
        light_surface = pygame.Surface((self.width, self.height))
        light_surface.fill((0, 0, 0))  # Start with darkness
        
        # Add ambient light
        ambient_color = (int(255 * self.ambient_light),) * 3
        light_surface.fill(ambient_color, special_flags=pygame.BLEND_ADD)
        
        # Add each light
        for light in self.lights:
            if light["enabled"]:
                self.render_light(light_surface, light)
        
        # Apply lighting to screen
        self.screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def render_light(self, surface: pygame.Surface, light: Dict):
        """Render individual light"""
        x, y = light["position"]
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        radius = light["radius"]
        color = light["color"]
        intensity = light["intensity"]
        
        # Create light gradient
        light_color = tuple(int(c * intensity) for c in color)
        pygame.draw.circle(surface, light_color, (screen_x, screen_y), 
                          int(radius), special_flags=pygame.BLEND_ADD)
    
    def enable_shadows(self):
        """Enable shadow casting"""
        self.shadows_enabled = True
    
    def start_screen_shake(self, intensity: float, duration: float):
        """Start screen shake effect"""
        self.screen_shake = {
            "active": True,
            "intensity": intensity,
            "duration": duration,
            "time_left": duration
        }
    
    def update_screen_shake(self, delta_time: float):
        """Update screen shake effect"""
        if not self.screen_shake["active"]:
            return
        
        self.screen_shake["time_left"] -= delta_time
        
        if self.screen_shake["time_left"] <= 0:
            self.screen_shake["active"] = False
            return
        
        # Apply screen shake offset
        import random
        intensity = self.screen_shake["intensity"]
        shake_x = random.uniform(-intensity, intensity)
        shake_y = random.uniform(-intensity, intensity)
        
        self.camera_x += shake_x
        self.camera_y += shake_y
    
    def add_hud_element(self, element_type: str, position: Tuple[int, int], 
                       data: Dict):
        """Add HUD element for any game genre"""
        element = {
            "type": element_type,
            "position": position,
            "data": data,
            "visible": True
        }
        self.hud_elements.append(element)
        return element
    
    def render_hud(self):
        """Render HUD elements"""
        for element in self.hud_elements:
            if element["visible"]:
                self.render_hud_element(element)
    
    def render_hud_element(self, element: Dict):
        """Render individual HUD element"""
        element_type = element["type"]
        x, y = element["position"]
        data = element["data"]
        
        if element_type == "health_bar":
            self.render_health_bar(x, y, data)
        elif element_type == "minimap":
            self.render_minimap(x, y, data)
        elif element_type == "inventory":
            self.render_inventory(x, y, data)
        elif element_type == "dialog":
            self.render_dialog_box(x, y, data)
    
    def render_health_bar(self, x: int, y: int, data: Dict):
        """Render health bar"""
        width = data.get("width", 200)
        height = data.get("height", 20)
        current_health = data.get("current", 100)
        max_health = data.get("max", 100)
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (100, 0, 0), bg_rect)
        
        # Health bar
        health_width = int((current_health / max_health) * width)
        health_rect = pygame.Rect(x, y, health_width, height)
        pygame.draw.rect(self.screen, (0, 255, 0), health_rect)
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
    
    def render_minimap(self, x: int, y: int, data: Dict):
        """Render minimap"""
        size = data.get("size", 100)
        scale = data.get("scale", 0.1)
        
        # Minimap background
        minimap_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(self.screen, (50, 50, 50), minimap_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), minimap_rect, 2)
    
    def render_inventory(self, x: int, y: int, data: Dict):
        """Render inventory UI"""
        slots = data.get("slots", 20)
        slot_size = data.get("slot_size", 32)
        items = data.get("items", [])
        
        # Render inventory slots
        for i in range(slots):
            slot_x = x + (i % 5) * (slot_size + 2)
            slot_y = y + (i // 5) * (slot_size + 2)
            
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            pygame.draw.rect(self.screen, (100, 100, 100), slot_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), slot_rect, 1)
            
            # Render item if present
            if i < len(items) and items[i]:
                item_color = items[i].get("color", (255, 255, 0))
                pygame.draw.rect(self.screen, item_color, slot_rect)
    
    def render_dialog_box(self, x: int, y: int, data: Dict):
        """Render dialog box"""
        width = data.get("width", 400)
        height = data.get("height", 100)
        text = data.get("text", "")
        speaker = data.get("speaker", "")
        
        # Dialog background
        dialog_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), dialog_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect, 2)
        
        # Speaker name
        if speaker:
            self.draw_text(speaker, x + 10, y + 5, (255, 255, 0), self.default_font)
        
        # Dialog text
        self.draw_text(text, x + 10, y + 30, (255, 255, 255), self.default_font)
    
    def create_particle_system(self, x: float, y: float, particle_count: int = 100):
        """Create unlimited particle system"""
        return {
            "position": (x, y),
            "particles": [],
            "count": particle_count,
            "active": True
        }
    
    def add_camera_effect(self, effect_name: str, duration: float, parameters: Dict):
        """Add camera effect"""
        effect = {
            "name": effect_name,
            "duration": duration,
            "time_left": duration,
            "params": parameters
        }
        self.camera_effects.append(effect)
        return effect
    
    def update_camera_effects(self, delta_time: float):
        """Update all camera effects"""
        effects_to_remove = []
        
        for effect in self.camera_effects:
            effect["time_left"] -= delta_time
            
            if effect["time_left"] <= 0:
                effects_to_remove.append(effect)
            else:
                self.apply_camera_effect(effect, delta_time)
        
        for effect in effects_to_remove:
            self.camera_effects.remove(effect)
    
    def apply_camera_effect(self, effect: Dict, delta_time: float):
        """Apply camera effect"""
        effect_name = effect["name"]
        params = effect["params"]
        
        if effect_name == "zoom":
            self.apply_zoom_effect(params, delta_time)
        elif effect_name == "pan":
            self.apply_pan_effect(params, delta_time)
        elif effect_name == "rotation":
            self.apply_rotation_effect(params, delta_time)
    
    def apply_zoom_effect(self, params: Dict, delta_time: float):
        """Apply camera zoom effect"""
        zoom_speed = params.get("speed", 1.0)
        target_zoom = params.get("target", 1.0)
        # Camera zoom implementation
        pass
    
    def apply_pan_effect(self, params: Dict, delta_time: float):
        """Apply camera pan effect"""
        pan_speed = params.get("speed", 100.0)
        target_x = params.get("target_x", self.camera_x)
        target_y = params.get("target_y", self.camera_y)
        
        # Smooth camera movement
        dx = target_x - self.camera_x
        dy = target_y - self.camera_y
        
        move_x = dx * pan_speed * delta_time
        move_y = dy * pan_speed * delta_time
        
        self.camera_x += move_x
        self.camera_y += move_y
    
    def apply_rotation_effect(self, params: Dict, delta_time: float):
        """Apply camera rotation effect"""
        rotation_speed = params.get("speed", 90.0)
        # Camera rotation implementation
        pass
