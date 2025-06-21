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
from .audio_system import audio_system
from .particle_system import particle_system
from .animation_system import animation_system

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
        self.frame_count = 0
        self.performance_stats = {"fps": 0, "frame_time": 0}
        
        # Advanced features
        self.global_variables = {}
        self.event_system = {}
        self.game_state = "running"  # running, paused, menu
        self.debug_mode = False
        self.collision_layers = {}
        self.time_scale = 1.0
        
        # Asset management
        self.loaded_textures = {}
        self.loaded_sounds = {}
        self.loaded_fonts = {}
        
        # Game systems
        self.game_systems = []
        self.custom_updates = []
        
        # Web display for Replit
        self.web_server = None
        self.web_port = 5000
        
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
        
        # Update animation system
        animation_system.update(self.delta_time)
        
        # Update particle system
        particle_system.update(self.delta_time)
    
    def render(self):
        """Render the current frame"""
        if not self.renderer:
            return
            
        self.renderer.clear()
        
        if self.current_scene:
            self.current_scene.render(self.renderer)
            
        # Render particle effects
        particle_system.render(self.renderer)
            
        self.renderer.present()
    
    def run_frame(self):
        """Run a single frame of the engine"""
        self.update()
        self.render()
    
    def run(self):
        """Run the main game loop"""
        self.start()
        
        # Web server disabled for desktop mode
        # self.start_web_server()
        
        while self.running:
            self.run_frame()
        
        self.cleanup()
    
    def start_web_server(self):
        """Start web server to display game in browser"""
        import threading
        import http.server
        import socketserver
        
        class GameHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>🎮 Axarion Game</title>
                        <style>
                            body { 
                                margin: 0; 
                                padding: 20px; 
                                background: #2b2b2b; 
                                color: white; 
                                font-family: Arial, sans-serif;
                                text-align: center;
                            }
                            #gameCanvas { 
                                border: 2px solid #4CAF50; 
                                background: #000;
                                margin: 20px auto;
                                display: block;
                            }
                            .info {
                                margin: 20px;
                                padding: 10px;
                                background: #3c3c3c;
                                border-radius: 5px;
                            }
                        </style>
                    </head>
                    <body>
                        <h1>🎮 Axarion Game Engine</h1>
                        <div class="info">
                            <p>✨ Vaše hra běží!</p>
                            <p>🎯 Používejte šipky pro pohyb, mezerník pro akce</p>
                        </div>
                        <canvas id="gameCanvas" width="800" height="600"></canvas>
                        
                        <script>
                            const canvas = document.getElementById('gameCanvas');
                            const ctx = canvas.getContext('2d');
                            
                            // Simple demo animation
                            let x = 400, y = 300;
                            let dx = 2, dy = 1;
                            
                            function animate() {
                                ctx.fillStyle = '#000';
                                ctx.fillRect(0, 0, 800, 600);
                                
                                // Draw bouncing ball
                                ctx.fillStyle = '#4CAF50';
                                ctx.beginPath();
                                ctx.arc(x, y, 20, 0, Math.PI * 2);
                                ctx.fill();
                                
                                // Update position
                                x += dx;
                                y += dy;
                                
                                if (x <= 20 || x >= 780) dx = -dx;
                                if (y <= 20 || y >= 580) dy = -dy;
                                
                                // Game info
                                ctx.fillStyle = '#fff';
                                ctx.font = '16px Arial';
                                ctx.fillText('🎮 Axarion Engine Demo', 10, 30);
                                ctx.fillText('Hra běží úspěšně!', 10, 55);
                                
                                requestAnimationFrame(animate);
                            }
                            
                            animate();
                            
                            // Keyboard controls
                            document.addEventListener('keydown', (e) => {
                                console.log('Key pressed:', e.key);
                            });
                        </script>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                else:
                    super().do_GET()
        
        try:
            with socketserver.TCPServer(("0.0.0.0", self.web_port), GameHandler) as httpd:
                print(f"🌐 Game server running at http://0.0.0.0:{self.web_port}")
                
                def serve():
                    httpd.serve_forever()
                
                server_thread = threading.Thread(target=serve, daemon=True)
                server_thread.start()
                self.web_server = httpd
                
        except Exception as e:
            print(f"Failed to start web server: {e}")
    
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
    
    def set_global_variable(self, name: str, value):
        """Set global variable accessible from all scripts"""
        self.global_variables[name] = value
    
    def get_global_variable(self, name: str, default=None):
        """Get global variable"""
        return self.global_variables.get(name, default)
    
    def add_game_system(self, system):
        """Add custom game system"""
        self.game_systems.append(system)
    
    def emit_event(self, event_name: str, data=None):
        """Emit global event"""
        if event_name in self.event_system:
            for callback in self.event_system[event_name]:
                callback(data)
    
    def subscribe_event(self, event_name: str, callback):
        """Subscribe to global event"""
        if event_name not in self.event_system:
            self.event_system[event_name] = []
        self.event_system[event_name].append(callback)
    
    def pause_game(self):
        """Pause the game"""
        self.game_state = "paused"
        self.time_scale = 0.0
    
    def resume_game(self):
        """Resume the game"""
        self.game_state = "running"
        self.time_scale = 1.0
    
    def set_time_scale(self, scale: float):
        """Set time scale for slow motion or fast forward"""
        self.time_scale = max(0.0, scale)
    
    def add_collision_layer(self, layer_name: str, objects: List = None):
        """Add collision layer for organized collision detection"""
        self.collision_layers[layer_name] = objects or []
    
    def get_objects_in_layer(self, layer_name: str):
        """Get all objects in collision layer"""
        return self.collision_layers.get(layer_name, [])
    
    def load_texture(self, name: str, file_path: str):
        """Load and cache texture"""
        try:
            texture = pygame.image.load(file_path)
            self.loaded_textures[name] = texture
            return True
        except:
            return False
    
    def get_texture(self, name: str):
        """Get cached texture"""
        return self.loaded_textures.get(name)
    
    def create_tilemap(self, tile_data: List[List[int]], tile_size: int = 32):
        """Create tilemap from 2D array"""
        tilemap = GameObject("Tilemap", "tilemap")
        tilemap.set_property("tile_data", tile_data)
        tilemap.set_property("tile_size", tile_size)
        return tilemap
    
    def find_objects_by_tag(self, tag: str):
        """Find all objects with specific tag across all scenes"""
        results = []
        for scene in self.scenes.values():
            for obj in scene.get_all_objects():
                if obj.get_property("tags", []) and tag in obj.get_property("tags"):
                    results.append(obj)
        return results
    
    def cleanup(self):
        """Clean up engine resources"""
        if self.renderer:
            self.renderer.cleanup()
        
        # Cleanup audio system
        audio_system.cleanup()
        
        # Clear animation and particle systems
        animation_system.clear()
        particle_system.clear()
        
        # Clear caches
        self.loaded_textures.clear()
        self.loaded_sounds.clear()
        self.loaded_fonts.clear()
        
        pygame.quit()
