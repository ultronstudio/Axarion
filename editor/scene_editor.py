"""
Axarion Engine Scene Editor
Visual scene editing interface with Pygame integration
"""

import tkinter as tk
from tkinter import ttk
import pygame
import os
import sys

class SceneEditor:
    """Visual scene editor using Pygame embedded in Tkinter"""

    def __init__(self, parent, main_editor):
        self.parent = parent
        self.main_editor = main_editor
        self.selected_object = None

        # Pygame setup
        self.pygame_initialized = False
        self.surface = None
        self.screen_width = 800
        self.screen_height = 600

        # Mouse state
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.drag_offset = (0, 0)

        # Setup UI
        self.setup_ui()
        self.init_pygame()

        # Start update loop
        self.update_scene()

    def setup_ui(self):
        """Setup the scene editor UI"""
        # Scene controls
        controls_frame = ttk.Frame(self.parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(controls_frame, text="Center View", 
                  command=self.center_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Fit View", 
                  command=self.fit_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Reset Zoom", 
                  command=self.reset_zoom).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Open Scene Window",
                  command=self.open_scene_window).pack(side=tk.LEFT, padx=2)

        # Scene info frame instead of pygame
        self.scene_info_frame = ttk.LabelFrame(self.parent, text="Scene View")
        self.scene_info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scene info display
        info_text = tk.Text(self.scene_info_frame, wrap=tk.WORD, height=15, 
                           font=("Arial", 10), bg='#f0f0f0', state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Store reference for updates
        self.scene_info_text = info_text
        
        # Update scene info
        self.update_scene_info()

    def init_pygame(self):
        """Initialize scene info display instead of pygame"""
        self.pygame_initialized = True
        print("Scene editor initialized with text display")

    def update_scene(self):
        """Update the scene info display"""
        if not self.pygame_initialized:
            self.parent.after(1000, self.update_scene)
            return

        # Update scene info
        self.update_scene_info()

        # Schedule next update
        self.parent.after(1000, self.update_scene)  # Update every second

    def draw_grid(self):
        """Draw a grid for easier object placement"""
        if not self.main_editor.engine.renderer:
            return

        renderer = self.main_editor.engine.renderer
        grid_size = 50
        grid_color = (70, 70, 70)

        # Draw vertical lines
        for x in range(0, self.screen_width, grid_size):
            renderer.draw_line(x, 0, x, self.screen_height, grid_color)

        # Draw horizontal lines
        for y in range(0, self.screen_height, grid_size):
            renderer.draw_line(0, y, self.screen_width, y, grid_color)

    def draw_selection_highlight(self):
        """Draw highlight around selected object"""
        if not self.selected_object or not self.main_editor.engine.renderer:
            return

        renderer = self.main_editor.engine.renderer
        bounds = self.selected_object.get_bounds()

        # Draw selection rectangle
        x1, y1, x2, y2 = bounds
        width = x2 - x1
        height = y2 - y1

        # Convert to screen coordinates
        screen_x, screen_y = renderer.world_to_screen(x1, y1)

        # Draw selection outline
        selection_color = (255, 255, 0)  # Yellow
        renderer.draw_rect(screen_x - 2, screen_y - 2, width + 4, height + 4, 
                          selection_color, filled=False)

        # Draw corner handles
        handle_size = 6
        handle_color = (255, 255, 255)

        corners = [
            (screen_x - handle_size//2, screen_y - handle_size//2),
            (screen_x + width - handle_size//2, screen_y - handle_size//2),
            (screen_x - handle_size//2, screen_y + height - handle_size//2),
            (screen_x + width - handle_size//2, screen_y + height - handle_size//2)
        ]

        for corner_x, corner_y in corners:
            renderer.draw_rect(corner_x, corner_y, handle_size, handle_size, handle_color)

    def on_mouse_down(self, event):
        """Handle mouse button press - simplified for info display"""
        pass

    def on_mouse_drag(self, event):
        """Handle mouse drag - simplified for info display"""
        pass

    def on_mouse_up(self, event):
        """Handle mouse button release - simplified for info display"""
        pass

    def on_mouse_move(self, event):
        """Handle mouse movement - simplified for info display"""
        pass

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        if self.main_editor.engine.renderer:
            return self.main_editor.engine.renderer.screen_to_world(screen_x, screen_y)
        return (screen_x, screen_y)

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        if self.main_editor.engine.renderer:
            return self.main_editor.engine.renderer.world_to_screen(world_x, world_y)
        return (int(world_x), int(world_y))

    def set_selected_object(self, obj):
        """Set the selected object"""
        self.selected_object = obj

    def center_view(self):
        """Center the view on all objects"""
        if not self.main_editor.engine.current_scene:
            return

        bounds = self.main_editor.engine.current_scene.get_bounds()
        if bounds != (0, 0, 0, 0):
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2

            # Set camera to center the view
            camera_x = center_x - self.screen_width / 2
            camera_y = center_y - self.screen_height / 2

            if self.main_editor.engine.current_scene:
                self.main_editor.engine.current_scene.camera_x = camera_x
                self.main_editor.engine.current_scene.camera_y = camera_y

    def fit_view(self):
        """Fit all objects in view"""
        # TODO: Implement zoom to fit functionality
        self.center_view()

    def reset_zoom(self):
        """Reset zoom to 100%"""
        pass  # TODO: Implement zoom functionality

    def update_scene_info(self):
        """Update scene information display"""
        if not hasattr(self, 'scene_info_text'):
            return
            
        info_lines = []
        
        if self.main_editor.engine.current_scene:
            scene = self.main_editor.engine.current_scene
            info_lines.append(f"📋 Scene: {scene.name}")
            info_lines.append(f"📦 Objects: {len(scene.game_objects)}")
            info_lines.append("")
            
            if scene.game_objects:
                info_lines.append("🎯 Objects in Scene:")
                for obj in scene.get_all_objects():
                    status_icons = []
                    if obj.active:
                        status_icons.append("✅")
                    if obj.visible:
                        status_icons.append("👁️")
                    if obj.script_code.strip():
                        status_icons.append("📜")
                    
                    status = " ".join(status_icons) if status_icons else "⚪"
                    pos_x, pos_y = obj.position
                    info_lines.append(f"  {status} {obj.name} ({obj.object_type}) at ({pos_x:.0f}, {pos_y:.0f})")
                
                info_lines.append("")
                
                if self.selected_object:
                    obj = self.selected_object
                    info_lines.append(f"🎯 Selected: {obj.name}")
                    info_lines.append(f"   Type: {obj.object_type}")
                    info_lines.append(f"   Position: ({obj.position[0]:.1f}, {obj.position[1]:.1f})")
                    info_lines.append(f"   Active: {'Yes' if obj.active else 'No'}")
                    info_lines.append(f"   Visible: {'Yes' if obj.visible else 'No'}")
                    
                    if obj.script_code.strip():
                        lines = obj.script_code.strip().split('\n')
                        info_lines.append(f"   Script: {len(lines)} lines")
                    else:
                        info_lines.append("   Script: None")
            else:
                info_lines.append("📭 No objects in scene")
                info_lines.append("")
                info_lines.append("💡 Tips:")
                info_lines.append("• Use Quick Start buttons to create template games")
                info_lines.append("• Add objects with the buttons below")
                info_lines.append("• Click 'Run Scene' to test your game")
        else:
            info_lines.append("❌ No scene loaded")
        
        # Update text
        self.scene_info_text.config(state=tk.NORMAL)
        self.scene_info_text.delete(1.0, tk.END)
        self.scene_info_text.insert(1.0, "\n".join(info_lines))
        self.scene_info_text.config(state=tk.DISABLED)

    def open_scene_window(self):
        """Open separate Pygame window for scene view"""
        try:
            # Initialize pygame for separate window
            if not pygame.get_init():
                pygame.init()
            
            # Create new window
            screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Axarion Scene View")
            
            # Initialize engine with this surface
            self.main_editor.engine.initialize(screen)
            
            print("Opened separate scene window")
            
            # Simple render loop for the window
            clock = pygame.time.Clock()
            running = True
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                
                # Clear and render
                screen.fill((50, 50, 50))
                
                if self.main_editor.engine.current_scene:
                    # Simple rendering without full engine
                    scene = self.main_editor.engine.current_scene
                    for obj in scene.get_all_objects():
                        if obj.visible:
                            x, y = obj.position
                            if obj.object_type == "rectangle":
                                width = obj.get_property("width", 50)
                                height = obj.get_property("height", 50)
                                color = obj.get_property("color", (100, 100, 255))
                                pygame.draw.rect(screen, color, (x, y, width, height))
                            elif obj.object_type == "circle":
                                radius = obj.get_property("radius", 25)
                                color = obj.get_property("color", (255, 100, 100))
                                pygame.draw.circle(screen, color, (int(x), int(y)), int(radius))
                
                pygame.display.flip()
                clock.tick(60)
            
            pygame.quit()
            
        except Exception as e:
            print(f"Failed to open scene window: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Window Error", f"Could not open scene window: {e}")