"""
Axarion Engine Renderer
Handles 2D rendering operations using Pygame
"""

import pygame
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
        self.background_color = (50, 50, 50)  # Dark gray
        
        # Fonts
        pygame.font.init()
        self.default_font = pygame.font.Font(None, 24)
    
    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear the screen with specified color"""
        if color is None:
            color = self.background_color
        self.screen.fill(color)
    
    def present(self):
        """Present the rendered frame"""
        pygame.display.flip()
    
    def draw_rect(self, x: float, y: float, width: float, height: float, 
                  color: Tuple[int, int, int], filled: bool = True):
        """Draw a rectangle"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        rect = pygame.Rect(screen_x, screen_y, int(width), int(height))
        
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 2)
    
    def draw_circle(self, x: float, y: float, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True):
        """Draw a circle"""
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        
        if filled:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(radius))
        else:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), int(radius), 2)
    
    def draw_line(self, x1: float, y1: float, x2: float, y2: float, 
                  color: Tuple[int, int, int], width: int = 1):
        """Draw a line"""
        start_pos = (int(x1 - self.camera_x), int(y1 - self.camera_y))
        end_pos = (int(x2 - self.camera_x), int(y2 - self.camera_y))
        pygame.draw.line(self.screen, color, start_pos, end_pos, width)
    
    def draw_text(self, text: str, x: float, y: float, 
                  color: Tuple[int, int, int] = (255, 255, 255),
                  font=None):
        """Draw text"""
        if font is None:
            font = self.default_font
        
        text_surface = font.render(text, True, color)
        screen_x = int(x - self.camera_x)
        screen_y = int(y - self.camera_y)
        self.screen.blit(text_surface, (screen_x, screen_y))
    
    def draw_game_object(self, game_object: GameObject):
        """Draw a game object"""
        if not game_object.visible:
            return
        
        x, y = game_object.position
        
        # Draw based on object type
        if game_object.object_type == "rectangle":
            width = game_object.properties.get("width", 50)
            height = game_object.properties.get("height", 50)
            color = game_object.properties.get("color", (255, 255, 255))
            self.draw_rect(x, y, width, height, color)
            
        elif game_object.object_type == "circle":
            radius = game_object.properties.get("radius", 25)
            color = game_object.properties.get("color", (255, 255, 255))
            self.draw_circle(x, y, radius, color)
            
        elif game_object.object_type == "sprite":
            # For now, draw as rectangle
            width = game_object.properties.get("width", 32)
            height = game_object.properties.get("height", 32)
            color = game_object.properties.get("color", (100, 150, 255))
            self.draw_rect(x, y, width, height, color)
        
        # Draw object name if in debug mode
        if hasattr(game_object, 'show_debug') and game_object.show_debug:
            self.draw_text(game_object.name, x, y - 20, (255, 255, 0))
    
    def set_camera(self, x: float, y: float):
        """Set camera position"""
        self.camera_x = x
        self.camera_y = y
    
    def get_camera(self) -> Tuple[float, float]:
        """Get camera position"""
        return (self.camera_x, self.camera_y)
    
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
    
    def cleanup(self):
        """Clean up renderer resources"""
        pass
