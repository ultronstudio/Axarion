"""
Axarion Engine Core
Main engine class that manages all subsystems
"""

import pygame
import json
import os
from typing import Dict, List, Optional
from .renderer import Renderer
from .scene import Scene
from .physics import PhysicsSystem
from .input_system import input_system

class AxarionEngine:
    """Main engine class that coordinates all subsystems"""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize subsystems
        self.renderer = None
        self.physics = PhysicsSystem()
        self.current_scene = None
        self.scenes: Dict[str, Scene] = {}
        
        # Engine state
        self.delta_time = 0.0
        self.total_time = 0.0
        
    def initialize(self, surface=None):
        """Initialize the engine with optional surface"""
        try:
            if not pygame.get_init():
                pygame.init()
            
            # Initialize renderer
            self.renderer = Renderer(self.width, self.height, surface)
            
            # Create default scene
            default_scene = Scene("Default")
            self.scenes["Default"] = default_scene
            self.current_scene = default_scene
            
            print("Axarion Engine initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize engine: {e}")
            return False
    
    def update(self):
        """Update engine state"""
        if not self.running:
            return
            
        # Calculate delta time
        self.delta_time = self.clock.tick(self.fps) / 1000.0
        self.total_time += self.delta_time
        
        # Handle pygame events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.stop()
        
        # Update input system
        input_system.update(events)
        
        # Update current scene
        if self.current_scene:
            self.current_scene.update(self.delta_time)
            
        # Update physics
        self.physics.update(self.delta_time)
    
    def render(self):
        """Render the current frame"""
        if not self.renderer:
            return
            
        self.renderer.clear()
        
        if self.current_scene:
            self.current_scene.render(self.renderer)
            
        self.renderer.present()
    
    def run_frame(self):
        """Run a single frame of the engine"""
        self.update()
        self.render()
    
    def start(self):
        """Start the engine main loop"""
        self.running = True
        
    def stop(self):
        """Stop the engine"""
        self.running = False
    
    def load_scene(self, scene_name: str) -> bool:
        """Load a scene by name"""
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            return True
        return False
    
    def create_scene(self, scene_name: str) -> Scene:
        """Create a new scene"""
        scene = Scene(scene_name)
        self.scenes[scene_name] = scene
        return scene
    
    def get_scene(self, scene_name: str) -> Optional[Scene]:
        """Get a scene by name"""
        return self.scenes.get(scene_name)
    
    def save_project(self, file_path: str) -> bool:
        """Save the current project to file"""
        try:
            project_data = {
                "engine_version": "1.0",
                "scenes": {}
            }
            
            # Save all scenes
            for name, scene in self.scenes.items():
                project_data["scenes"][name] = scene.serialize()
            
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save project: {e}")
            return False
    
    def load_project(self, file_path: str) -> bool:
        """Load a project from file"""
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            
            # Clear existing scenes
            self.scenes.clear()
            
            # Load scenes
            for name, scene_data in project_data.get("scenes", {}).items():
                scene = Scene(name)
                scene.deserialize(scene_data)
                self.scenes[name] = scene
            
            # Set first scene as current
            if self.scenes:
                self.current_scene = next(iter(self.scenes.values()))
            
            return True
        except Exception as e:
            print(f"Failed to load project: {e}")
            return False
    
    def cleanup(self):
        """Clean up engine resources"""
        if self.renderer:
            self.renderer.cleanup()
        pygame.quit()
