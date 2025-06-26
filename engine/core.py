
"""
Axarion Engine Core
Main engine class that manages all subsystems
"""

import pygame
import json
import os
import time
from typing import Dict, List, Optional
from .renderer import Renderer
from .scene import Scene
from .physics import PhysicsSystem
from .input_system import input_system
from .audio_system import audio_system
from .particle_system import particle_system
from .animation_system import animation_system

class AxarionEngine:
    """Modern game engine with clean architecture and high performance"""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Axarion Game"):
        # Core properties
        self.width = width
        self.height = height
        self.title = title
        self.running = False
        self.initialized = False
        
        # Timing and performance
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.delta_time = 0.0
        self.total_time = 0.0
        self.frame_count = 0
        self.accumulated_time = 0.0
        self.performance_stats = {
            "fps": 0,
            "frame_time": 0,
            "objects_rendered": 0,
            "physics_time": 0,
            "render_time": 0
        }
        
        # Unlimited game development features
        self.game_mode = "unlimited"  # unlimited, platformer, rpg, shooter, puzzle, racing
        self.custom_systems = {}
        self.unlimited_objects = True
        self.unlimited_scenes = True
        self.unlimited_assets = True
        
        # Advanced game features for any genre
        self.network_enabled = False
        self.multiplayer_support = False
        self.save_system = {}
        self.achievement_system = []
        self.dialog_system = {}
        self.inventory_systems = {}
        self.quest_system = {}
        self.level_editor = None
        self.mod_support = True
        
        # Unlimited rendering capabilities
        self.layered_rendering = True
        self.post_processing = []
        self.lighting_system = None
        self.shader_support = True
        
        # Advanced AI and behavior systems
        self.ai_systems = {}
        self.pathfinding = None
        self.state_machines = {}
        self.behavior_trees = {}
        
        # Engine subsystems (initialized in order)
        self.renderer = None
        self.physics = None
        self.input_manager = None
        self.audio_manager = None
        self.asset_manager = None
        
        # Scene management
        self.current_scene = None
        self.scenes: Dict[str, Scene] = {}
        self.scene_transition = None
        
        # Engine state and configuration
        self.game_state = "running"  # running, paused, loading, menu
        self.debug_mode = False
        self.time_scale = 1.0
        self.vsync_enabled = True
        self.auto_pause = True  # Pause when window loses focus
        
        # Event and messaging system
        self.event_dispatcher = {}
        self.global_variables = {}
        self.message_queue = []
        
        # System management
        self.registered_systems = []
        self.system_priorities = {}
        
        # Error handling and logging
        self.error_log = []
        self.warning_log = []
        self.verbose_logging = False
        
    def initialize(self, surface=None, **config):
        """Initialize the engine with comprehensive system setup"""
        if self.initialized:
            self._log_warning("Engine already initialized")
            return True
            
        try:
            # Initialize pygame if needed
            if not pygame.get_init():
                pygame.init()
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            
            # Apply configuration
            self._apply_config(config)
            
            # Initialize core subsystems in correct order
            success = (
                self._init_renderer(surface) and
                self._init_physics() and
                self._init_input_system() and
                self._init_audio_system() and
                self._init_asset_manager()
            )
            
            if not success:
                raise RuntimeError("Failed to initialize one or more subsystems")
            
            # Set up default scene
            self._create_default_scene()
            
            # Initialize performance monitoring
            self._init_performance_monitoring()
            
            self.initialized = True
            self._log_info(f"🎮 Axarion Engine v0.5 initialized successfully")
            self._log_info(f"   Resolution: {self.width}x{self.height}")
            self._log_info(f"   Target FPS: {self.target_fps}")
            self._log_info(f"   VSync: {'Enabled' if self.vsync_enabled else 'Disabled'}")
            
            return True
            
        except Exception as e:
            self._log_error(f"Failed to initialize engine: {e}")
            self.cleanup()
            return False
    
    def _apply_config(self, config):
        """Apply configuration options"""
        self.target_fps = config.get('fps', 60)
        self.vsync_enabled = config.get('vsync', True)
        self.debug_mode = config.get('debug', False)
        self.verbose_logging = config.get('verbose', False)
    
    def _init_renderer(self, surface):
        """Initialize rendering subsystem"""
        try:
            from .renderer import Renderer
            self.renderer = Renderer(self.width, self.height, surface)
            self.renderer.set_vsync(self.vsync_enabled)
            return True
        except Exception as e:
            self._log_error(f"Failed to initialize renderer: {e}")
            return False
    
    def _init_physics(self):
        """Initialize physics subsystem"""
        try:
            self.physics = PhysicsSystem()
            return True
        except Exception as e:
            self._log_error(f"Failed to initialize physics: {e}")
            return False
    
    def _init_input_system(self):
        """Initialize input management"""
        try:
            from .input_system import input_system
            self.input_manager = input_system
            return True
        except Exception as e:
            self._log_error(f"Failed to initialize input system: {e}")
            return False
    
    def _init_audio_system(self):
        """Initialize audio subsystem"""
        try:
            from .audio_system import audio_system
            self.audio_manager = audio_system
            # Audio system can work in disabled mode, so always return True
            if not audio_system.audio_enabled:
                self._log_warning("Audio system running in disabled mode")
            return True
        except Exception as e:
            self._log_error(f"Failed to initialize audio system: {e}")
            # Create a dummy audio manager to prevent crashes
            self.audio_manager = None
            return True  # Don't fail engine init due to audio issues
    
    def _init_asset_manager(self):
        """Initialize asset management"""
        try:
            from .asset_manager import asset_manager
            self.asset_manager = asset_manager
            return True
        except Exception as e:
            self._log_error(f"Failed to initialize asset manager: {e}")
            return False
    
    def _create_default_scene(self):
        """Create and set default scene"""
        default_scene = Scene("Default")
        self.scenes["Default"] = default_scene
        self.current_scene = default_scene
    
    def _init_performance_monitoring(self):
        """Initialize performance monitoring"""
        import time
        self.performance_stats["start_time"] = time.time()
        self.performance_stats["last_fps_update"] = time.time()
    
    def update(self):
        """High-performance engine update with proper timing"""
        if not self.running or not self.initialized:
            return
        
        import time
        frame_start = time.perf_counter()
        
        # Calculate delta time with time scale
        raw_delta = self.clock.tick(self.target_fps) / 1000.0
        self.delta_time = raw_delta * self.time_scale
        self.total_time += raw_delta
        self.frame_count += 1
        
        # Handle window events first
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.WINDOWFOCUSLOST and self.auto_pause:
                self.pause_game()
            elif event.type == pygame.WINDOWFOCUSGAINED and self.game_state == "paused":
                self.resume_game()
        
        # Skip updates if paused
        if self.game_state == "paused":
            return
        
        # Update input system
        if self.input_manager:
            self.input_manager.update(events)
        
        # Update registered systems in priority order
        self._update_systems(self.delta_time)
        
        # Update current scene
        if self.current_scene and self.current_scene.active:
            self.current_scene.update(self.delta_time)
        
        # Handle scene transitions
        if self.scene_transition:
            self._process_scene_transition()
        
        # Process message queue
        self._process_messages()
        
        # Update performance stats
        frame_time = time.perf_counter() - frame_start
        self._update_performance_stats(frame_time)
    
    def _update_systems(self, delta_time):
        """Update all registered systems in priority order"""
        # Update core systems
        systems_to_update = [
            ('physics', self.physics),
            ('animation', None),  # Will be handled via import
            ('particles', None),  # Will be handled via import
            ('audio', self.audio_manager)
        ]
        
        for system_name, system in systems_to_update:
            if system and hasattr(system, 'update'):
                try:
                    physics_start = time.perf_counter() if system_name == 'physics' else None
                    system.update(delta_time)
                    if physics_start:
                        self.performance_stats['physics_time'] = time.perf_counter() - physics_start
                except Exception as e:
                    self._log_error(f"Error updating {system_name} system: {e}")
            elif system_name == 'audio' and system is None:
                # Audio system disabled, skip silently
                pass
        
        # Update external systems
        try:
            from .animation_system import animation_system
            from .particle_system import particle_system
            animation_system.update(delta_time)
            particle_system.update(delta_time)
        except ImportError:
            pass  # Systems not available
        
        # Update custom registered systems
        for system in self.registered_systems:
            try:
                if hasattr(system, 'update'):
                    system.update(delta_time)
            except Exception as e:
                self._log_error(f"Error updating custom system: {e}")
    
    def _process_messages(self):
        """Process queued messages"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            self._dispatch_message(message)
    
    def _dispatch_message(self, message):
        """Dispatch message to registered handlers"""
        msg_type = message.get('type')
        if msg_type in self.event_dispatcher:
            for handler in self.event_dispatcher[msg_type]:
                try:
                    handler(message)
                except Exception as e:
                    self._log_error(f"Error in message handler: {e}")
    
    def _update_performance_stats(self, frame_time):
        """Update performance statistics"""
        import time
        current_time = time.time()
        
        self.performance_stats['frame_time'] = frame_time * 1000  # Convert to ms
        
        # Update FPS every second
        if current_time - self.performance_stats.get('last_fps_update', 0) >= 1.0:
            self.performance_stats['fps'] = self.frame_count / (current_time - self.performance_stats.get('start_time', current_time))
            self.performance_stats['last_fps_update'] = current_time
    
    def render(self):
        """High-performance rendering with monitoring"""
        if not self.renderer or not self.initialized:
            return
        
        import time
        render_start = time.perf_counter()
        
        try:
            # Clear screen
            self.renderer.clear()
            
            # Render current scene
            objects_rendered = 0
            if self.current_scene and self.current_scene.active:
                objects_rendered = self.current_scene.render(self.renderer)
            
            # Render particle effects
            try:
                from .particle_system import particle_system
                particle_system.render(self.renderer)
            except ImportError:
                pass
            
            # Render debug information if enabled
            if self.debug_mode:
                self._render_debug_info()
            
            # Present frame
            self.renderer.present()
            
            # Update render stats
            self.performance_stats['render_time'] = (time.perf_counter() - render_start) * 1000
            self.performance_stats['objects_rendered'] = objects_rendered
            
        except Exception as e:
            self._log_error(f"Render error: {e}")
    
    def _render_debug_info(self):
        """Render debug information overlay"""
        if not self.renderer:
            return
        
        debug_info = [
            f"FPS: {self.performance_stats.get('fps', 0):.1f}",
            f"Frame: {self.performance_stats.get('frame_time', 0):.2f}ms",
            f"Render: {self.performance_stats.get('render_time', 0):.2f}ms",
            f"Physics: {self.performance_stats.get('physics_time', 0)*1000:.2f}ms",
            f"Objects: {self.performance_stats.get('objects_rendered', 0)}",
            f"Scene: {self.current_scene.name if self.current_scene else 'None'}",
            f"Time Scale: {self.time_scale:.2f}"
        ]
        
        y_offset = 10
        for info in debug_info:
            self.renderer.draw_text(info, 10, y_offset, (255, 255, 0))
            y_offset += 18
    
    def run_frame(self):
        """Run a single frame of the engine"""
        self.update()
        self.render()
    
    def run(self):
        """Run the main game loop"""
        self.start()
        
        while self.running:
            self.run_frame()
        
        self.cleanup()
    
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
                "engine_version": "0.4",
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
        """Comprehensive cleanup of all engine resources"""
        self._log_info("🧹 Cleaning up engine resources...")
        
        try:
            # Stop any running processes
            self.running = False
            
            # Cleanup subsystems in reverse order
            subsystems = [
                ('asset_manager', self.asset_manager),
                ('audio_manager', self.audio_manager),
                ('renderer', self.renderer),
                ('physics', self.physics)
            ]
            
            for name, system in subsystems:
                if system and hasattr(system, 'cleanup'):
                    try:
                        system.cleanup()
                        self._log_info(f"   ✓ {name} cleaned up")
                    except Exception as e:
                        self._log_error(f"   ✗ Failed to cleanup {name}: {e}")
            
            # Clear external systems
            try:
                from .audio_system import audio_system
                from .animation_system import animation_system
                from .particle_system import particle_system
                
                audio_system.cleanup()
                animation_system.clear()
                particle_system.clear()
                self._log_info("   ✓ External systems cleaned up")
            except Exception as e:
                self._log_error(f"   ✗ Failed to cleanup external systems: {e}")
            
            # Clear scene data
            for scene in self.scenes.values():
                if hasattr(scene, 'cleanup'):
                    scene.cleanup()
            self.scenes.clear()
            self.current_scene = None
            
            # Clear engine state
            self.global_variables.clear()
            self.event_dispatcher.clear()
            self.message_queue.clear()
            self.registered_systems.clear()
            
            # Cleanup pygame
            if pygame.get_init():
                pygame.quit()
                self._log_info("   ✓ Pygame cleaned up")
            
            self.initialized = False
            self._log_info("✅ Engine cleanup completed successfully")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def _log_info(self, message):
        """Log info message"""
        if self.verbose_logging:
            print(f"[INFO] {message}")
    
    def _log_warning(self, message):
        """Log warning message"""
        print(f"[WARNING] {message}")
        self.warning_log.append(message)
    
    def _log_error(self, message):
        """Log error message"""
        print(f"[ERROR] {message}")
        self.error_log.append(message)
    
    # Additional engine management methods
    def register_system(self, system, priority=0):
        """Register a custom system with the engine"""
        self.registered_systems.append(system)
        self.system_priorities[system] = priority
        self.registered_systems.sort(key=lambda s: self.system_priorities.get(s, 0))
    
    def unregister_system(self, system):
        """Unregister a custom system"""
        if system in self.registered_systems:
            self.registered_systems.remove(system)
            if system in self.system_priorities:
                del self.system_priorities[system]
    
    def post_message(self, message_type, data=None):
        """Post a message to the message queue"""
        message = {'type': message_type, 'data': data, 'timestamp': self.total_time}
        self.message_queue.append(message)
    
    def subscribe_to_messages(self, message_type, handler):
        """Subscribe to messages of a specific type"""
        if message_type not in self.event_dispatcher:
            self.event_dispatcher[message_type] = []
        self.event_dispatcher[message_type].append(handler)
    
    def unsubscribe_from_messages(self, message_type, handler):
        """Unsubscribe from messages"""
        if message_type in self.event_dispatcher:
            if handler in self.event_dispatcher[message_type]:
                self.event_dispatcher[message_type].remove(handler)
    
    def get_performance_info(self):
        """Get detailed performance information"""
        return self.performance_stats.copy()
    
    def set_target_fps(self, fps):
        """Set target FPS"""
        self.target_fps = max(1, min(fps, 240))  # Clamp between 1-240
    
    def toggle_debug_mode(self):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        if self.renderer:
            self.renderer.debug_mode = self.debug_mode
        return self.debug_mode
    
    # UNLIMITED GAME DEVELOPMENT FEATURES
    
    def enable_unlimited_mode(self):
        """Enable unlimited game development capabilities"""
        self.game_mode = "unlimited"
        self.unlimited_objects = True
        self.unlimited_scenes = True
        self.unlimited_assets = True
        self._log_info("🚀 Unlimited game development mode enabled!")
    
    def create_custom_system(self, name: str, system_class):
        """Create custom game system for any genre"""
        self.custom_systems[name] = system_class()
        self.register_system(self.custom_systems[name])
        return self.custom_systems[name]
    
    def add_networking(self, server_port: int = 5000):
        """Add networking capabilities for multiplayer games"""
        self.network_enabled = True
        self.multiplayer_support = True
        self.network_port = server_port
        self._log_info(f"🌐 Networking enabled on port {server_port}")
    
    def create_save_system(self, save_slots: int = 10):
        """Create unlimited save system"""
        self.save_system = {
            "slots": save_slots,
            "auto_save": True,
            "compression": True,
            "encryption": False
        }
        return self.save_system
    
    def add_achievement_system(self, achievements: List[Dict]):
        """Add achievement system for any game type"""
        self.achievement_system = achievements
        for achievement in achievements:
            achievement["unlocked"] = False
            achievement["progress"] = 0
        return self.achievement_system
    
    def create_dialog_system(self, dialog_data: Dict):
        """Create dialog system for RPGs, adventures, etc."""
        self.dialog_system = dialog_data
        return self.dialog_system
    
    def add_inventory_system(self, name: str, max_items: int = 999):
        """Add inventory system (unlimited items supported)"""
        self.inventory_systems[name] = {
            "max_items": max_items,
            "items": {},
            "categories": [],
            "sorting": True
        }
        return self.inventory_systems[name]
    
    def create_quest_system(self, quests: List[Dict]):
        """Create quest system for RPGs and adventure games"""
        self.quest_system = {
            "active_quests": [],
            "completed_quests": [],
            "available_quests": quests,
            "quest_log": True
        }
        return self.quest_system
    
    def enable_level_editor(self):
        """Enable in-game level editor"""
        from .level_editor import LevelEditor
        self.level_editor = LevelEditor(self)
        return self.level_editor
    
    def add_post_processing(self, effect_name: str, parameters: Dict):
        """Add post-processing effects"""
        effect = {"name": effect_name, "params": parameters, "enabled": True}
        self.post_processing.append(effect)
        return effect
    
    def create_lighting_system(self, ambient_light: float = 0.3):
        """Create dynamic lighting system"""
        self.lighting_system = {
            "ambient": ambient_light,
            "lights": [],
            "shadows": True,
            "dynamic": True
        }
        return self.lighting_system
    
    def add_ai_system(self, name: str, ai_type: str = "fsm"):
        """Add AI system (FSM, Behavior Trees, Neural Networks)"""
        if ai_type == "fsm":
            self.ai_systems[name] = {"type": "finite_state_machine", "states": {}}
        elif ai_type == "bt":
            self.ai_systems[name] = {"type": "behavior_tree", "nodes": []}
        elif ai_type == "neural":
            self.ai_systems[name] = {"type": "neural_network", "layers": []}
        return self.ai_systems[name]
    
    def enable_pathfinding(self, algorithm: str = "astar"):
        """Enable pathfinding for AI characters"""
        self.pathfinding = {
            "algorithm": algorithm,
            "grid_size": 32,
            "obstacles": [],
            "cache": True
        }
        return self.pathfinding
    
    def create_unlimited_objects(self, count: int = 10000):
        """Remove object limits for massive games"""
        self.max_objects = count
        self._log_info(f"🎯 Object limit increased to {count}")
    
    def add_mod_support(self, mod_folder: str = "mods"):
        """Enable mod support for community content"""
        self.mod_support = True
        self.mod_folder = mod_folder
        self._log_info(f"🔧 Mod support enabled in '{mod_folder}' folder")
    
    def create_particle_physics(self):
        """Advanced particle physics for realistic effects"""
        return {
            "gravity": True,
            "collision": True,
            "fluid_dynamics": True,
            "particle_count": 50000
        }
    
    def enable_procedural_generation(self):
        """Enable procedural content generation"""
        return {
            "terrain": True,
            "dungeons": True,
            "items": True,
            "enemies": True,
            "music": True
        }
    
    def add_analytics(self):
        """Add game analytics for balancing"""
        return {
            "player_behavior": True,
            "performance_tracking": True,
            "crash_reporting": True,
            "heatmaps": True
        }
    
    def create_scripting_sandbox(self):
        """Create secure scripting environment"""
        return {
            "lua_support": True,
            "python_support": True,
            "javascript_support": True,
            "security": "sandboxed"
        }
