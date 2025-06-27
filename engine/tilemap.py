
"""
Tilemap System for Axarion Engine
Provides tile-based level creation and management
"""

import pygame
from typing import List, Dict, Tuple, Optional, Any
from .game_object import GameObject

class Tile:
    """Represents a single tile in a tilemap"""
    
    def __init__(self, tile_id: int, sprite_name: str = None, collision: bool = False, 
                 properties: Dict[str, Any] = None):
        self.tile_id = tile_id
        self.sprite_name = sprite_name
        self.collision = collision
        self.properties = properties or {}
        self.sprite_surface = None

class Tilemap:
    """Tile-based map system"""
    
    def __init__(self, width: int, height: int, tile_size: int = 32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        self.tile_definitions: Dict[int, Tile] = {}
        self.collision_objects: List[GameObject] = []
        
        # Optimization
        self.chunk_size = 16
        self.chunks: Dict[Tuple[int, int], List[GameObject]] = {}
        self.dirty_chunks: set = set()
        
    def register_tile(self, tile_id: int, sprite_name: str = None, 
                     collision: bool = False, properties: Dict = None):
        """Register a tile type"""
        self.tile_definitions[tile_id] = Tile(tile_id, sprite_name, collision, properties)
    
    def set_tile(self, x: int, y: int, tile_id: int):
        """Set a tile at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_id
            
            # Mark chunk as dirty for optimization
            chunk_x, chunk_y = x // self.chunk_size, y // self.chunk_size
            self.dirty_chunks.add((chunk_x, chunk_y))
    
    def get_tile(self, x: int, y: int) -> int:
        """Get tile ID at given coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return 0
    
    def get_tile_at_world_pos(self, world_x: float, world_y: float) -> int:
        """Get tile at world coordinates"""
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        return self.get_tile(tile_x, tile_y)
    
    def world_to_tile(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to tile coordinates"""
        return (int(world_x // self.tile_size), int(world_y // self.tile_size))
    
    def tile_to_world(self, tile_x: int, tile_y: int) -> Tuple[float, float]:
        """Convert tile coordinates to world coordinates"""
        return (tile_x * self.tile_size, tile_y * self.tile_size)
    
    def load_from_array(self, tile_array: List[List[int]]):
        """Load tilemap from 2D array"""
        self.height = len(tile_array)
        if self.height > 0:
            self.width = len(tile_array[0])
            self.tiles = [row[:] for row in tile_array]
        
        # Mark all chunks as dirty
        self.dirty_chunks = set()
        for chunk_x in range(0, self.width // self.chunk_size + 1):
            for chunk_y in range(0, self.height // self.chunk_size + 1):
                self.dirty_chunks.add((chunk_x, chunk_y))
    
    def generate_collision_objects(self, scene):
        """Generate collision objects for solid tiles"""
        # Clear existing collision objects
        for obj in self.collision_objects:
            if obj.name in scene.objects:
                scene.remove_object(obj.name)
        self.collision_objects.clear()
        
        # Group adjacent collision tiles into larger rectangles for optimization
        visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                if visited[y][x]:
                    continue
                
                tile_id = self.tiles[y][x]
                if tile_id in self.tile_definitions and self.tile_definitions[tile_id].collision:
                    # Find rectangular area of same collision tile
                    width, height = self._find_rect_area(x, y, tile_id, visited)
                    
                    # Create collision object
                    world_x, world_y = self.tile_to_world(x, y)
                    collision_obj = GameObject(f"tile_collision_{x}_{y}", "rectangle")
                    collision_obj.position = (world_x, world_y)
                    collision_obj.set_property("width", width * self.tile_size)
                    collision_obj.set_property("height", height * self.tile_size)
                    collision_obj.set_property("color", (100, 100, 100))
                    collision_obj.is_static = True
                    collision_obj.collision_enabled = True
                    collision_obj.visible = False  # Hidden collision object
                    collision_obj.add_tag("platform")
                    
                    scene.add_object(collision_obj)
                    self.collision_objects.append(collision_obj)
    
    def _find_rect_area(self, start_x: int, start_y: int, tile_id: int, 
                       visited: List[List[bool]]) -> Tuple[int, int]:
        """Find rectangular area of same collision tiles"""
        # Find width
        width = 0
        for x in range(start_x, self.width):
            if self.tiles[start_y][x] == tile_id and not visited[start_y][x]:
                width += 1
            else:
                break
        
        # Find height
        height = 1
        for y in range(start_y + 1, self.height):
            # Check if entire row matches
            row_matches = True
            for x in range(start_x, start_x + width):
                if x >= self.width or self.tiles[y][x] != tile_id or visited[y][x]:
                    row_matches = False
                    break
            
            if row_matches:
                height += 1
            else:
                break
        
        # Mark area as visited
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if y < self.height and x < self.width:
                    visited[y][x] = True
        
        return (width, height)
    
    def render(self, renderer, camera_x: float = 0, camera_y: float = 0):
        """Render visible tiles"""
        # Calculate visible tile range
        start_x = max(0, int(camera_x // self.tile_size) - 1)
        end_x = min(self.width, int((camera_x + renderer.width) // self.tile_size) + 2)
        start_y = max(0, int(camera_y // self.tile_size) - 1)
        end_y = min(self.height, int((camera_y + renderer.height) // self.tile_size) + 2)
        
        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tiles[y][x]
                
                if tile_id in self.tile_definitions:
                    tile_def = self.tile_definitions[tile_id]
                    if tile_def.sprite_name:
                        world_x, world_y = self.tile_to_world(x, y)
                        
                        # Get sprite from asset manager
                        from .asset_manager import asset_manager
                        sprite = asset_manager.get_image(tile_def.sprite_name)
                        
                        if sprite:
                            renderer.draw_sprite(world_x, world_y, sprite)
                        else:
                            # Fallback to colored rectangle
                            color = tile_def.properties.get("color", (128, 128, 128))
                            renderer.draw_rect(world_x, world_y, self.tile_size, 
                                             self.tile_size, color)
    
    def get_tiles_in_area(self, world_x: float, world_y: float, 
                         width: float, height: float) -> List[Tuple[int, int, int]]:
        """Get all tiles in a world area"""
        start_x, start_y = self.world_to_tile(world_x, world_y)
        end_x, end_y = self.world_to_tile(world_x + width, world_y + height)
        
        tiles = []
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                tile_id = self.get_tile(x, y)
                if tile_id != 0:
                    tiles.append((x, y, tile_id))
        
        return tiles
    
    def flood_fill(self, start_x: int, start_y: int, new_tile_id: int):
        """Flood fill algorithm for tile editing"""
        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            return
        
        original_id = self.tiles[start_y][start_x]
        if original_id == new_tile_id:
            return
        
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            
            if self.tiles[y][x] != original_id:
                continue
            
            self.tiles[y][x] = new_tile_id
            
            # Add neighbors to stack
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
    
    def save_to_file(self, filename: str):
        """Save tilemap to file"""
        import json
        
        data = {
            "width": self.width,
            "height": self.height,
            "tile_size": self.tile_size,
            "tiles": self.tiles,
            "tile_definitions": {
                str(tile_id): {
                    "sprite_name": tile.sprite_name,
                    "collision": tile.collision,
                    "properties": tile.properties
                }
                for tile_id, tile in self.tile_definitions.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load tilemap from file"""
        import json
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.width = data["width"]
        self.height = data["height"]
        self.tile_size = data["tile_size"]
        self.tiles = data["tiles"]
        
        # Load tile definitions
        self.tile_definitions.clear()
        for tile_id_str, tile_data in data["tile_definitions"].items():
            tile_id = int(tile_id_str)
            self.register_tile(
                tile_id,
                tile_data["sprite_name"],
                tile_data["collision"],
                tile_data["properties"]
            )

def create_tilemap_object(tilemap: Tilemap, name: str = "Tilemap") -> GameObject:
    """Create a GameObject wrapper for a tilemap"""
    tilemap_obj = GameObject(name, "tilemap")
    tilemap_obj.tilemap = tilemap
    tilemap_obj.set_property("tilemap", tilemap)
    
    # Override render method to use tilemap rendering
    def render_tilemap(renderer):
        camera_x, camera_y = renderer.get_camera()
        tilemap.render(renderer, camera_x, camera_y)
    
    tilemap_obj.custom_render = render_tilemap
    return tilemap_obj
