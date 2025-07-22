
"""
Advanced Level Editor for Axarion Engine
Visual level creation and editing tools
"""

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from .game_object import GameObject
from .scene import Scene
from .tilemap import Tilemap
from .camera import Camera

class LevelEditor:
    """Advanced visual level editor"""
    
    def __init__(self, engine):
        self.engine = engine
        self.active = False
        self.current_scene = None
        
        # Editor state
        self.mode = "select"  # select, place, paint, terrain
        self.selected_objects = []
        self.clipboard = []
        self.undo_stack = []
        self.redo_stack = []
        
        # Tools
        self.current_tool = "select"
        self.brush_size = 1
        self.snap_to_grid = True
        self.grid_size = 32
        self.show_grid = True
        
        # Object templates
        self.object_templates = {}
        self.current_template = None
        
        # UI state
        self.ui_visible = True
        self.property_panel_open = True
        self.layer_panel_open = True
        self.tileset_panel_open = True
        
        # Editor camera
        self.editor_camera = Camera(0, 0, engine.width, engine.height)
        self.camera_speed = 300
        
        # Tilemap editing
        self.current_tilemap = None
        self.current_tile_id = 1
        self.tile_palette = []
        
        # Layers
        self.layers = {
            "background": {"visible": True, "locked": False, "objects": []},
            "main": {"visible": True, "locked": False, "objects": []},
            "foreground": {"visible": True, "locked": False, "objects": []},
            "collision": {"visible": True, "locked": False, "objects": []}
        }
        self.current_layer = "main"
        
        # Load default templates
        self._create_default_templates()
        
        # Editor settings
        self.settings = {
            "auto_save": True,
            "auto_save_interval": 300,  # 5 minutes
            "show_collision_bounds": True,
            "show_object_names": True,
            "highlight_selected": True
        }
        
        # Initialize fonts
        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
    
    def _create_default_templates(self):
        """Create default object templates"""
        # Platform template
        platform = GameObject("Platform", "rectangle")
        platform.set_property("width", 200)
        platform.set_property("height", 32)
        platform.set_property("color", (100, 100, 100))
        platform.is_static = True
        platform.add_tag("platform")
        self.object_templates["Platform"] = platform.serialize()
        
        # Player spawn template
        spawn = GameObject("PlayerSpawn", "circle")
        spawn.set_property("radius", 16)
        spawn.set_property("color", (0, 255, 0))
        spawn.add_tag("spawn")
        spawn.add_tag("player")
        self.object_templates["PlayerSpawn"] = spawn.serialize()
        
        # Enemy spawn template
        enemy_spawn = GameObject("EnemySpawn", "circle")
        enemy_spawn.set_property("radius", 16)
        enemy_spawn.set_property("color", (255, 0, 0))
        enemy_spawn.add_tag("spawn")
        enemy_spawn.add_tag("enemy")
        self.object_templates["EnemySpawn"] = enemy_spawn.serialize()
        
        # Collectible template
        collectible = GameObject("Collectible", "star")
        collectible.set_property("outer_radius", 12)
        collectible.set_property("inner_radius", 6)
        collectible.set_property("color", (255, 255, 0))
        collectible.add_tag("collectible")
        self.object_templates["Collectible"] = collectible.serialize()
        
        # Trigger zone template
        trigger = GameObject("TriggerZone", "rectangle")
        trigger.set_property("width", 64)
        trigger.set_property("height", 64)
        trigger.set_property("color", (0, 255, 255))
        trigger.collision_enabled = False
        trigger.visible = False
        trigger.add_tag("trigger")
        self.object_templates["TriggerZone"] = trigger.serialize()
    
    def activate(self, scene: Scene):
        """Activate level editor for scene"""
        self.active = True
        self.current_scene = scene
        self.editor_camera = Camera(0, 0, self.engine.width, self.engine.height)
        
        # Organize objects by layer
        self._organize_objects_by_layer()
        
        print("Level Editor activated")
    
    def deactivate(self):
        """Deactivate level editor"""
        self.active = False
        self.selected_objects.clear()
        print("Level Editor deactivated")
    
    def _organize_objects_by_layer(self):
        """Organize scene objects by layer"""
        # Clear layers
        for layer in self.layers.values():
            layer["objects"].clear()
        
        # Categorize objects
        for obj in self.current_scene.get_all_objects():
            layer_name = self._get_object_layer(obj)
            if layer_name in self.layers:
                self.layers[layer_name]["objects"].append(obj)
    
    def _get_object_layer(self, obj: GameObject) -> str:
        """Determine object layer based on tags and properties"""
        if obj.has_tag("background"):
            return "background"
        elif obj.has_tag("foreground"):
            return "foreground"
        elif obj.has_tag("collision") or obj.has_tag("platform"):
            return "collision"
        else:
            return "main"
    
    def update(self, delta_time: float):
        """Update level editor"""
        if not self.active:
            return
        
        self._handle_input(delta_time)
        self._update_camera(delta_time)
        
        # Auto-save
        if self.settings["auto_save"]:
            # TODO: Implement auto-save timer
            pass
    
    def _handle_input(self, delta_time: float):
        """Handle editor input"""
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Camera movement
        camera_moved = False
        if keys[pygame.K_w]:
            self.editor_camera.position = (self.editor_camera.position[0], 
                                         self.editor_camera.position[1] - self.camera_speed * delta_time)
            camera_moved = True
        if keys[pygame.K_s]:
            self.editor_camera.position = (self.editor_camera.position[0], 
                                         self.editor_camera.position[1] + self.camera_speed * delta_time)
            camera_moved = True
        if keys[pygame.K_a]:
            self.editor_camera.position = (self.editor_camera.position[0] - self.camera_speed * delta_time, 
                                         self.editor_camera.position[1])
            camera_moved = True
        if keys[pygame.K_d]:
            self.editor_camera.position = (self.editor_camera.position[0] + self.camera_speed * delta_time, 
                                         self.editor_camera.position[1])
            camera_moved = True
        
        if camera_moved:
            self.engine.renderer.camera = self.editor_camera
        
        # Tool shortcuts
        if keys[pygame.K_1]:
            self.current_tool = "select"
        elif keys[pygame.K_2]:
            self.current_tool = "place"
        elif keys[pygame.K_3]:
            self.current_tool = "paint"
        elif keys[pygame.K_4]:
            self.current_tool = "terrain"
        
        # Grid toggle
        if keys[pygame.K_g]:
            if not hasattr(self, '_g_pressed') or not self._g_pressed:
                self.show_grid = not self.show_grid
                self._g_pressed = True
        else:
            self._g_pressed = False
        
        # Snap to grid toggle
        if keys[pygame.K_x]:
            if not hasattr(self, '_x_pressed') or not self._x_pressed:
                self.snap_to_grid = not self.snap_to_grid
                self._x_pressed = True
        else:
            self._x_pressed = False
        
        # Handle mouse input based on current tool
        world_pos = self._screen_to_world(mouse_pos)
        
        if self.current_tool == "select":
            self._handle_select_tool(mouse_pos, world_pos, mouse_buttons)
        elif self.current_tool == "place":
            self._handle_place_tool(mouse_pos, world_pos, mouse_buttons)
        elif self.current_tool == "paint":
            self._handle_paint_tool(mouse_pos, world_pos, mouse_buttons)
        elif self.current_tool == "terrain":
            self._handle_terrain_tool(mouse_pos, world_pos, mouse_buttons)
    
    def _handle_select_tool(self, mouse_pos: Tuple[int, int], world_pos: Tuple[float, float], 
                           mouse_buttons: Tuple[bool, bool, bool]):
        """Handle selection tool"""
        if mouse_buttons[0]:  # Left click
            if not hasattr(self, '_left_clicked') or not self._left_clicked:
                # Find object at position
                clicked_object = self._get_object_at_position(world_pos)
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LCTRL]:
                    # Multi-select
                    if clicked_object and clicked_object not in self.selected_objects:
                        self.selected_objects.append(clicked_object)
                    elif clicked_object in self.selected_objects:
                        self.selected_objects.remove(clicked_object)
                else:
                    # Single select
                    self.selected_objects.clear()
                    if clicked_object:
                        self.selected_objects.append(clicked_object)
                
                self._left_clicked = True
        else:
            self._left_clicked = False
        
        # Delete selected objects
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DELETE] or keys[pygame.K_x]:
            if not hasattr(self, '_delete_pressed') or not self._delete_pressed:
                self._delete_selected_objects()
                self._delete_pressed = True
        else:
            self._delete_pressed = False
    
    def _handle_place_tool(self, mouse_pos: Tuple[int, int], world_pos: Tuple[float, float], 
                          mouse_buttons: Tuple[bool, bool, bool]):
        """Handle object placement tool"""
        if mouse_buttons[0] and self.current_template:  # Left click
            if not hasattr(self, '_place_clicked') or not self._place_clicked:
                self._place_object_at_position(world_pos)
                self._place_clicked = True
        else:
            self._place_clicked = False
    
    def _handle_paint_tool(self, mouse_pos: Tuple[int, int], world_pos: Tuple[float, float], 
                          mouse_buttons: Tuple[bool, bool, bool]):
        """Handle tile painting tool"""
        if self.current_tilemap and mouse_buttons[0]:  # Left click
            self._paint_tile_at_position(world_pos)
        elif self.current_tilemap and mouse_buttons[2]:  # Right click
            self._erase_tile_at_position(world_pos)
    
    def _handle_terrain_tool(self, mouse_pos: Tuple[int, int], world_pos: Tuple[float, float], 
                            mouse_buttons: Tuple[bool, bool, bool]):
        """Handle terrain editing tool"""
        # TODO: Implement terrain editing
        pass
    
    def _screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen position to world position"""
        cam_x, cam_y = self.editor_camera.position
        world_x = screen_pos[0] + cam_x
        world_y = screen_pos[1] + cam_y
        
        if self.snap_to_grid:
            world_x = round(world_x / self.grid_size) * self.grid_size
            world_y = round(world_y / self.grid_size) * self.grid_size
        
        return (world_x, world_y)
    
    def _get_object_at_position(self, world_pos: Tuple[float, float]) -> Optional[GameObject]:
        """Find object at world position"""
        for obj in self.current_scene.get_all_objects():
            if obj.contains_point(world_pos[0], world_pos[1]):
                return obj
        return None
    
    def _place_object_at_position(self, world_pos: Tuple[float, float]):
        """Place object template at position"""
        if not self.current_template:
            return
        
        # Create object from template
        template_data = self.object_templates[self.current_template]
        obj = GameObject("temp", "rectangle")
        obj.deserialize(template_data)
        
        # Set position
        obj.position = world_pos
        
        # Generate unique name
        base_name = self.current_template
        counter = 1
        while f"{base_name}_{counter}" in [o.name for o in self.current_scene.get_all_objects()]:
            counter += 1
        obj.name = f"{base_name}_{counter}"
        
        # Add to scene
        self.current_scene.add_object(obj)
        
        # Add to current layer
        self.layers[self.current_layer]["objects"].append(obj)
        
        # Add to undo stack
        self._add_to_undo_stack("place", {"object": obj})
        
        print(f"Placed {obj.name} at {world_pos}")
    
    def _paint_tile_at_position(self, world_pos: Tuple[float, float]):
        """Paint tile at position"""
        if not self.current_tilemap:
            return
        
        tile_x, tile_y = self.current_tilemap.world_to_tile(world_pos[0], world_pos[1])
        
        # Paint in brush area
        for dy in range(-self.brush_size // 2, self.brush_size // 2 + 1):
            for dx in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                self.current_tilemap.set_tile(tile_x + dx, tile_y + dy, self.current_tile_id)
    
    def _erase_tile_at_position(self, world_pos: Tuple[float, float]):
        """Erase tile at position"""
        if not self.current_tilemap:
            return
        
        tile_x, tile_y = self.current_tilemap.world_to_tile(world_pos[0], world_pos[1])
        
        # Erase in brush area
        for dy in range(-self.brush_size // 2, self.brush_size // 2 + 1):
            for dx in range(-self.brush_size // 2, self.brush_size // 2 + 1):
                self.current_tilemap.set_tile(tile_x + dx, tile_y + dy, 0)
    
    def _delete_selected_objects(self):
        """Delete selected objects"""
        if not self.selected_objects:
            return
        
        deleted_objects = []
        for obj in self.selected_objects:
            # Remove from scene
            self.current_scene.remove_object(obj.name)
            
            # Remove from layers
            for layer in self.layers.values():
                if obj in layer["objects"]:
                    layer["objects"].remove(obj)
            
            deleted_objects.append(obj)
        
        # Add to undo stack
        self._add_to_undo_stack("delete", {"objects": deleted_objects})
        
        self.selected_objects.clear()
        print(f"Deleted {len(deleted_objects)} objects")
    
    def _update_camera(self, delta_time: float):
        """Update editor camera"""
        # Handle zoom with mouse wheel
        # TODO: Implement zoom functionality
        pass
    
    def render(self):
        """Render level editor UI"""
        if not self.active:
            return
        
        renderer = self.engine.renderer
        
        # Render grid
        if self.show_grid:
            self._render_grid(renderer)
        
        # Render layer indicators
        self._render_layer_indicators(renderer)
        
        # Render selection highlights
        self._render_selection_highlights(renderer)
        
        # Render object bounds for collision objects
        if self.settings["show_collision_bounds"]:
            self._render_collision_bounds(renderer)
        
        # Render object names
        if self.settings["show_object_names"]:
            self._render_object_names(renderer)
        
        # Render UI panels
        if self.ui_visible:
            self._render_ui_panels(renderer)
        
        # Render tool cursor
        self._render_tool_cursor(renderer)
    
    def _render_grid(self, renderer):
        """Render editor grid"""
        cam_x, cam_y = self.editor_camera.position
        
        # Calculate grid lines in view
        start_x = int(cam_x // self.grid_size) * self.grid_size
        end_x = start_x + renderer.width + self.grid_size
        start_y = int(cam_y // self.grid_size) * self.grid_size
        end_y = start_y + renderer.height + self.grid_size
        
        grid_color = (80, 80, 80)
        
        # Vertical lines
        for x in range(start_x, end_x, self.grid_size):
            screen_x = x - cam_x
            if 0 <= screen_x <= renderer.width:
                renderer.draw_line((screen_x, 0), (screen_x, renderer.height), grid_color)
        
        # Horizontal lines
        for y in range(start_y, end_y, self.grid_size):
            screen_y = y - cam_y
            if 0 <= screen_y <= renderer.height:
                renderer.draw_line((0, screen_y), (renderer.width, screen_y), grid_color)
    
    def _render_selection_highlights(self, renderer):
        """Render selection highlights"""
        for obj in self.selected_objects:
            bounds = obj.get_bounds()
            cam_x, cam_y = self.editor_camera.position
            
            screen_x = bounds[0] - cam_x - 2
            screen_y = bounds[1] - cam_y - 2
            width = bounds[2] - bounds[0] + 4
            height = bounds[3] - bounds[1] + 4
            
            # Draw selection border
            selection_color = (255, 255, 0)
            renderer.draw_rect(screen_x, screen_y, width, height, selection_color, filled=False)
            
            # Draw corner handles
            handle_size = 6
            handles = [
                (screen_x - handle_size//2, screen_y - handle_size//2),
                (screen_x + width - handle_size//2, screen_y - handle_size//2),
                (screen_x - handle_size//2, screen_y + height - handle_size//2),
                (screen_x + width - handle_size//2, screen_y + height - handle_size//2)
            ]
            
            for handle_x, handle_y in handles:
                renderer.draw_rect(handle_x, handle_y, handle_size, handle_size, selection_color)
    
    def _render_collision_bounds(self, renderer):
        """Render collision bounds for objects"""
        for obj in self.current_scene.get_all_objects():
            if not obj.collision_enabled:
                continue
            
            bounds = obj.get_bounds()
            cam_x, cam_y = self.editor_camera.position
            
            screen_x = bounds[0] - cam_x
            screen_y = bounds[1] - cam_y
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            
            # Draw collision bounds
            collision_color = (0, 255, 0) if obj.is_static else (255, 0, 255)
            renderer.draw_rect(screen_x, screen_y, width, height, collision_color, filled=False)
    
    def _render_object_names(self, renderer):
        """Render object names"""
        for obj in self.current_scene.get_all_objects():
            x, y = obj.position
            cam_x, cam_y = self.editor_camera.position
            
            screen_x = x - cam_x
            screen_y = y - cam_y - 20
            
            # Only render if on screen
            if 0 <= screen_x <= renderer.width and 0 <= screen_y <= renderer.height:
                renderer.draw_text(obj.name, screen_x, screen_y, (255, 255, 255), self.small_font)
    
    def _render_layer_indicators(self, renderer):
        """Render layer visibility indicators"""
        y_offset = 50
        for layer_name, layer_data in self.layers.items():
            color = (255, 255, 255) if layer_data["visible"] else (100, 100, 100)
            if layer_name == self.current_layer:
                color = (255, 255, 0)
            
            text = f"● {layer_name}" if layer_data["visible"] else f"○ {layer_name}"
            renderer.draw_text(text, 10, y_offset, color, self.ui_font)
            y_offset += 20
    
    def _render_ui_panels(self, renderer):
        """Render UI panels"""
        # Tool panel
        self._render_tool_panel(renderer)
        
        # Object template panel
        self._render_template_panel(renderer)
        
        # Property panel
        if self.property_panel_open:
            self._render_property_panel(renderer)
    
    def _render_tool_panel(self, renderer):
        """Render tool selection panel"""
        panel_x = 10
        panel_y = 200
        panel_width = 120
        panel_height = 200
        
        # Panel background
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (40, 40, 40))
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (80, 80, 80), filled=False)
        
        # Title
        renderer.draw_text("Tools", panel_x + 10, panel_y + 10, (255, 255, 255), self.ui_font)
        
        # Tool buttons
        tools = ["select", "place", "paint", "terrain"]
        for i, tool in enumerate(tools):
            button_y = panel_y + 40 + i * 25
            color = (255, 255, 0) if tool == self.current_tool else (200, 200, 200)
            renderer.draw_text(f"[{i+1}] {tool}", panel_x + 10, button_y, color, self.ui_font)
    
    def _render_template_panel(self, renderer):
        """Render object template panel"""
        panel_x = 150
        panel_y = 200
        panel_width = 150
        panel_height = 200
        
        # Panel background
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (40, 40, 40))
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (80, 80, 80), filled=False)
        
        # Title
        renderer.draw_text("Templates", panel_x + 10, panel_y + 10, (255, 255, 255), self.ui_font)
        
        # Template list
        y_offset = 40
        for template_name in self.object_templates.keys():
            button_y = panel_y + y_offset
            color = (255, 255, 0) if template_name == self.current_template else (200, 200, 200)
            renderer.draw_text(template_name, panel_x + 10, button_y, color, self.small_font)
            y_offset += 16
    
    def _render_property_panel(self, renderer):
        """Render property panel for selected objects"""
        if not self.selected_objects:
            return
        
        panel_x = renderer.width - 250
        panel_y = 50
        panel_width = 240
        panel_height = 300
        
        # Panel background
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (40, 40, 40))
        renderer.draw_rect(panel_x, panel_y, panel_width, panel_height, (80, 80, 80), filled=False)
        
        # Title
        obj_count = len(self.selected_objects)
        title = f"Properties ({obj_count} selected)"
        renderer.draw_text(title, panel_x + 10, panel_y + 10, (255, 255, 255), self.ui_font)
        
        if obj_count == 1:
            # Show properties for single object
            obj = self.selected_objects[0]
            y_offset = 40
            
            # Basic properties
            renderer.draw_text(f"Name: {obj.name}", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
            y_offset += 16
            renderer.draw_text(f"Type: {obj.object_type}", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
            y_offset += 16
            renderer.draw_text(f"Pos: ({obj.position[0]:.1f}, {obj.position[1]:.1f})", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
            y_offset += 16
            renderer.draw_text(f"Static: {obj.is_static}", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
            y_offset += 16
            renderer.draw_text(f"Collision: {obj.collision_enabled}", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
            y_offset += 16
            
            # Tags
            if obj.tags:
                renderer.draw_text(f"Tags: {', '.join(obj.tags)}", panel_x + 10, panel_y + y_offset, (200, 200, 200), self.small_font)
    
    def _render_tool_cursor(self, renderer):
        """Render tool-specific cursor"""
        mouse_pos = pygame.mouse.get_pos()
        
        if self.current_tool == "place" and self.current_template:
            # Show preview of object to be placed
            world_pos = self._screen_to_world(mouse_pos)
            cam_x, cam_y = self.editor_camera.position
            preview_x = world_pos[0] - cam_x
            preview_y = world_pos[1] - cam_y
            
            # Draw simple preview
            renderer.draw_rect(preview_x - 25, preview_y - 25, 50, 50, (255, 255, 255, 100))
        
        elif self.current_tool == "paint":
            # Show brush size
            brush_size_pixels = self.brush_size * self.grid_size
            renderer.draw_circle(mouse_pos[0], mouse_pos[1], brush_size_pixels // 2, (255, 255, 0), filled=False)
    
    # UNDO/REDO SYSTEM
    def _add_to_undo_stack(self, action_type: str, data: Dict):
        """Add action to undo stack"""
        action = {
            "type": action_type,
            "data": data,
            "timestamp": pygame.time.get_ticks()
        }
        
        self.undo_stack.append(action)
        
        # Limit undo stack size
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
        
        # Clear redo stack
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            return
        
        action = self.undo_stack.pop()
        
        if action["type"] == "place":
            # Remove placed object
            obj = action["data"]["object"]
            self.current_scene.remove_object(obj.name)
            
            # Remove from layers
            for layer in self.layers.values():
                if obj in layer["objects"]:
                    layer["objects"].remove(obj)
        
        elif action["type"] == "delete":
            # Restore deleted objects
            for obj in action["data"]["objects"]:
                self.current_scene.add_object(obj)
                layer_name = self._get_object_layer(obj)
                self.layers[layer_name]["objects"].append(obj)
        
        # Add to redo stack
        self.redo_stack.append(action)
        
        print(f"Undid action: {action['type']}")
    
    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            return
        
        action = self.redo_stack.pop()
        
        if action["type"] == "place":
            # Re-add object
            obj = action["data"]["object"]
            self.current_scene.add_object(obj)
            layer_name = self._get_object_layer(obj)
            self.layers[layer_name]["objects"].append(obj)
        
        elif action["type"] == "delete":
            # Re-delete objects
            for obj in action["data"]["objects"]:
                self.current_scene.remove_object(obj.name)
                for layer in self.layers.values():
                    if obj in layer["objects"]:
                        layer["objects"].remove(obj)
        
        # Add back to undo stack
        self.undo_stack.append(action)
        
        print(f"Redid action: {action['type']}")
    
    # LEVEL SAVING/LOADING
    def save_level(self, filename: str) -> bool:
        """Save current level"""
        try:
            level_data = {
                "scene": self.current_scene.serialize(),
                "layers": self.layers,
                "tilemap": self.current_tilemap.serialize() if self.current_tilemap else None,
                "editor_settings": self.settings,
                "templates": self.object_templates
            }
            
            with open(filename, 'w') as f:
                json.dump(level_data, f, indent=2)
            
            print(f"Level saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to save level: {e}")
            return False
    
    def load_level(self, filename: str) -> bool:
        """Load level from file"""
        try:
            with open(filename, 'r') as f:
                level_data = json.load(f)
            
            # Load scene
            if "scene" in level_data:
                self.current_scene.deserialize(level_data["scene"])
            
            # Load layers
            if "layers" in level_data:
                self.layers = level_data["layers"]
            
            # Load tilemap
            if level_data.get("tilemap"):
                # TODO: Create and load tilemap
                pass
            
            # Load settings
            if "editor_settings" in level_data:
                self.settings.update(level_data["editor_settings"])
            
            # Load templates
            if "templates" in level_data:
                self.object_templates.update(level_data["templates"])
            
            # Reorganize objects by layer
            self._organize_objects_by_layer()
            
            print(f"Level loaded from {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to load level: {e}")
            return False
    
    # PUBLIC INTERFACE
    def set_current_template(self, template_name: str):
        """Set current object template for placement"""
        if template_name in self.object_templates:
            self.current_template = template_name
            self.current_tool = "place"
    
    def add_custom_template(self, name: str, game_object: GameObject):
        """Add custom object template"""
        self.object_templates[name] = game_object.serialize()
    
    def set_current_layer(self, layer_name: str):
        """Set current editing layer"""
        if layer_name in self.layers:
            self.current_layer = layer_name
    
    def toggle_layer_visibility(self, layer_name: str):
        """Toggle layer visibility"""
        if layer_name in self.layers:
            self.layers[layer_name]["visible"] = not self.layers[layer_name]["visible"]
    
    def set_brush_size(self, size: int):
        """Set tile brush size"""
        self.brush_size = max(1, size)
    
    def set_grid_size(self, size: int):
        """Set grid size"""
        self.grid_size = max(8, size)
