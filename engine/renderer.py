
"""
Axarion Engine Renderer
Handles 2D rendering operations using Pygame
"""

import pygame
import math
from typing import Tuple, Optional, List
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
        """Draw a game object"""
        if not game_object.visible or game_object.destroyed:
            return
        
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
            
        elif game_object.object_type == "circle":
            radius = game_object.properties.get("radius", 25)
            border_width = game_object.properties.get("border_width", 0)
            self.draw_circle(x, y, radius, color, True, border_width)
            
        elif game_object.object_type == "sprite" or game_object.object_type == "animated_sprite":
            # Get sprite surface
            sprite_surface = game_object.get_current_sprite()
            
            if sprite_surface:
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
    
    def cleanup(self):
        """Clean up renderer resources"""
        pass
