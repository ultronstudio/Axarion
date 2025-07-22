
"""
Advanced Axarion Engine Asset Manager
Handles all game assets with caching, streaming, and advanced features
"""

import pygame
import json
import os
import threading
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import zipfile
import hashlib

class AssetManager:
    """Advanced asset management with streaming, caching, and compression"""
    
    def __init__(self):
        # Core asset storage
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music: Dict[str, str] = {}  # Store file paths for music
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.gifs: Dict[str, List[pygame.Surface]] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.data_files: Dict[str, Any] = {}
        
        # Advanced features
        self.asset_metadata: Dict[str, Dict] = {}
        self.asset_dependencies: Dict[str, List[str]] = {}
        self.asset_cache: Dict[str, Any] = {}
        self.streaming_assets: Dict[str, Any] = {}
        self.compressed_packages: Dict[str, str] = {}
        
        # Performance tracking
        self.load_times: Dict[str, float] = {}
        self.memory_usage: Dict[str, int] = {}
        self.access_frequency: Dict[str, int] = {}
        
        # Async loading
        self.loading_queue: List[str] = []
        self.background_loader = None
        self.loading_thread_active = False
        
        # Asset paths
        self.base_paths = {
            "images": "assets/local/images/",
            "sounds": "assets/local/sounds/", 
            "music": "assets/local/sounds/",
            "fonts": "assets/local/fonts/",
            "data": "assets/local/other/",
            "packages": "assets/packages/"
        }
        
        # Create directories if they don't exist
        for path in self.base_paths.values():
            os.makedirs(path, exist_ok=True)
            
        # Initialize pygame font
        pygame.font.init()
    
    # CORE LOADING FUNCTIONS
    def load_image(self, name: str, file_path: str, convert_alpha: bool = True) -> bool:
        """Load image with performance optimization"""
        start_time = time.time()
        
        try:
            if os.path.exists(file_path):
                surface = pygame.image.load(file_path)
                if convert_alpha:
                    surface = surface.convert_alpha()
                else:
                    surface = surface.convert()
                
                self.images[name] = surface
                
                # Store metadata
                self.asset_metadata[name] = {
                    "type": "image",
                    "path": file_path,
                    "size": surface.get_size(),
                    "memory": surface.get_bytesize()
                }
                
                # Performance tracking
                load_time = time.time() - start_time
                self.load_times[name] = load_time
                self.memory_usage[name] = surface.get_bytesize()
                self.access_frequency[name] = 0
                
                return True
        except Exception as e:
            print(f"Failed to load image {name}: {e}")
        return False
    
    def load_sound(self, name: str, file_path: str) -> bool:
        """Load sound effect"""
        try:
            if os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.sounds[name] = sound
                
                self.asset_metadata[name] = {
                    "type": "sound",
                    "path": file_path,
                    "length": sound.get_length()
                }
                return True
        except Exception as e:
            print(f"Failed to load sound {name}: {e}")
        return False
    
    def load_music(self, name: str, file_path: str) -> bool:
        """Load background music"""
        try:
            if os.path.exists(file_path):
                self.music[name] = file_path
                
                self.asset_metadata[name] = {
                    "type": "music",
                    "path": file_path
                }
                return True
        except Exception as e:
            print(f"Failed to load music {name}: {e}")
        return False
    
    def load_animation(self, name: str, file_paths: List[str], frame_duration: float = 0.1) -> bool:
        """Load sprite animation from multiple images"""
        frames = []
        
        for path in file_paths:
            if os.path.exists(path):
                try:
                    frame = pygame.image.load(path).convert_alpha()
                    frames.append(frame)
                except Exception as e:
                    print(f"Failed to load animation frame {path}: {e}")
                    return False
            else:
                print(f"Animation frame not found: {path}")
                return False
        
        if frames:
            self.animations[name] = frames
            self.asset_metadata[name] = {
                "type": "animation",
                "frame_count": len(frames),
                "frame_duration": frame_duration,
                "paths": file_paths
            }
            return True
        return False
    
    def load_gif(self, name: str, file_path: str) -> bool:
        """Load GIF animation (simplified - loads as image sequence)"""
        try:
            if os.path.exists(file_path):
                # For now, load as single image - could be extended for true GIF support
                surface = pygame.image.load(file_path).convert_alpha()
                self.gifs[name] = [surface]  # Single frame for now
                
                self.asset_metadata[name] = {
                    "type": "gif",
                    "path": file_path,
                    "frame_count": 1
                }
                return True
        except Exception as e:
            print(f"Failed to load GIF {name}: {e}")
        return False
    
    def load_font(self, name: str, file_path: str, size: int = 24) -> bool:
        """Load custom font"""
        try:
            if os.path.exists(file_path):
                font = pygame.font.Font(file_path, size)
                self.fonts[name] = font
                
                self.asset_metadata[name] = {
                    "type": "font",
                    "path": file_path,
                    "size": size
                }
                return True
            else:
                # Try system font
                font = pygame.font.SysFont(file_path, size)
                self.fonts[name] = font
                return True
        except Exception as e:
            print(f"Failed to load font {name}: {e}")
        return False
    
    def load_data_file(self, name: str, file_path: str) -> bool:
        """Load JSON or text data file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_path.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = f.read()
                
                self.data_files[name] = data
                self.asset_metadata[name] = {
                    "type": "data",
                    "path": file_path
                }
                return True
        except Exception as e:
            print(f"Failed to load data file {name}: {e}")
        return False
    
    # ADVANCED ASSET MANAGEMENT
    def create_asset_package(self, package_name: str, asset_list: List[str], compress: bool = True) -> bool:
        """Create compressed asset package for distribution"""
        try:
            package_path = os.path.join(self.base_paths["packages"], f"{package_name}.zip")
            
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as zipf:
                package_data = {
                    "assets": {},
                    "metadata": {}
                }
                
                for asset_name in asset_list:
                    if asset_name in self.asset_metadata:
                        metadata = self.asset_metadata[asset_name]
                        original_path = metadata["path"]
                        
                        if os.path.exists(original_path):
                            # Add file to zip
                            archive_name = f"assets/{asset_name}{os.path.splitext(original_path)[1]}"
                            zipf.write(original_path, archive_name)
                            
                            # Store package data
                            package_data["assets"][asset_name] = archive_name
                            package_data["metadata"][asset_name] = metadata
                
                # Add package manifest
                zipf.writestr("manifest.json", json.dumps(package_data, indent=2))
            
            self.compressed_packages[package_name] = package_path
            print(f"Asset package '{package_name}' created successfully")
            return True
            
        except Exception as e:
            print(f"Failed to create asset package: {e}")
            return False
    
    def load_asset_package(self, package_name: str, package_path: str = None) -> bool:
        """Load assets from compressed package"""
        try:
            if package_path is None:
                package_path = os.path.join(self.base_paths["packages"], f"{package_name}.zip")
            
            with zipfile.ZipFile(package_path, 'r') as zipf:
                # Read manifest
                manifest_data = json.loads(zipf.read("manifest.json").decode('utf-8'))
                
                for asset_name, archive_path in manifest_data["assets"].items():
                    # Extract to temp location
                    temp_path = f"temp_{asset_name}"
                    zipf.extract(archive_path, "temp_assets/")
                    
                    # Load based on type
                    metadata = manifest_data["metadata"][asset_name]
                    extracted_path = os.path.join("temp_assets", archive_path)
                    
                    if metadata["type"] == "image":
                        self.load_image(asset_name, extracted_path)
                    elif metadata["type"] == "sound":
                        self.load_sound(asset_name, extracted_path)
                    elif metadata["type"] == "music":
                        self.load_music(asset_name, extracted_path)
                    
                    # Clean up temp file
                    os.remove(extracted_path)
            
            # Clean up temp directory
            if os.path.exists("temp_assets"):
                os.rmdir("temp_assets")
            
            print(f"Asset package '{package_name}' loaded successfully")
            return True
            
        except Exception as e:
            print(f"Failed to load asset package: {e}")
            return False
    
    def queue_async_load(self, asset_type: str, name: str, path: str):
        """Queue asset for background loading"""
        self.loading_queue.append({
            "type": asset_type,
            "name": name,
            "path": path
        })
        
        if not self.loading_thread_active:
            self.start_background_loading()
    
    def start_background_loading(self):
        """Start background asset loading thread"""
        if self.background_loader is None or not self.background_loader.is_alive():
            self.loading_thread_active = True
            self.background_loader = threading.Thread(target=self._background_load_worker)
            self.background_loader.daemon = True
            self.background_loader.start()
    
    def _background_load_worker(self):
        """Background thread worker for loading assets"""
        while self.loading_thread_active and self.loading_queue:
            try:
                asset_info = self.loading_queue.pop(0)
                
                if asset_info["type"] == "image":
                    self.load_image(asset_info["name"], asset_info["path"])
                elif asset_info["type"] == "sound":
                    self.load_sound(asset_info["name"], asset_info["path"])
                elif asset_info["type"] == "music":
                    self.load_music(asset_info["name"], asset_info["path"])
                
                time.sleep(0.01)  # Small delay to prevent CPU hogging
                
            except Exception as e:
                print(f"Background loading error: {e}")
        
        self.loading_thread_active = False
    
    # SMART CACHING SYSTEM
    def enable_smart_caching(self, cache_size_mb: int = 100):
        """Enable intelligent asset caching"""
        self.cache_size_limit = cache_size_mb * 1024 * 1024  # Convert to bytes
        self.caching_enabled = True
    
    def cache_frequently_used_assets(self):
        """Cache assets based on usage frequency"""
        if not hasattr(self, 'caching_enabled'):
            return
        
        # Sort assets by frequency
        sorted_assets = sorted(self.access_frequency.items(), 
                             key=lambda x: x[1], reverse=True)
        
        current_cache_size = 0
        for asset_name, frequency in sorted_assets:
            if current_cache_size >= self.cache_size_limit:
                break
            
            if asset_name not in self.asset_cache:
                asset_size = self.memory_usage.get(asset_name, 0)
                if current_cache_size + asset_size <= self.cache_size_limit:
                    self.asset_cache[asset_name] = True
                    current_cache_size += asset_size
    
    def preload_scene_assets(self, scene_name: str, asset_list: List[str]):
        """Preload assets for a specific scene"""
        print(f"Preloading assets for scene: {scene_name}")
        
        for asset_name in asset_list:
            if asset_name in self.asset_metadata:
                # Increment access frequency for caching
                self.access_frequency[asset_name] = self.access_frequency.get(asset_name, 0) + 1
        
        # Update cache based on new usage patterns
        self.cache_frequently_used_assets()
    
    # MEMORY MANAGEMENT
    def unload_unused_assets(self, keep_cached: bool = True):
        """Unload assets that haven't been used recently"""
        unused_assets = []
        
        for asset_name, frequency in self.access_frequency.items():
            if frequency == 0 and (not keep_cached or asset_name not in self.asset_cache):
                unused_assets.append(asset_name)
        
        for asset_name in unused_assets:
            self.unload_asset(asset_name)
        
        print(f"Unloaded {len(unused_assets)} unused assets")
    
    def unload_asset(self, name: str):
        """Unload specific asset from memory"""
        # Remove from all storage dictionaries
        if name in self.images:
            del self.images[name]
        if name in self.sounds:
            del self.sounds[name]
        if name in self.music:
            del self.music[name]
        if name in self.animations:
            del self.animations[name]
        if name in self.gifs:
            del self.gifs[name]
        if name in self.fonts:
            del self.fonts[name]
        if name in self.data_files:
            del self.data_files[name]
        
        # Clean up metadata
        if name in self.asset_metadata:
            del self.asset_metadata[name]
        if name in self.memory_usage:
            del self.memory_usage[name]
        if name in self.load_times:
            del self.load_times[name]
    
    def get_memory_usage_report(self) -> Dict[str, Any]:
        """Get detailed memory usage report"""
        total_memory = sum(self.memory_usage.values())
        
        report = {
            "total_memory_bytes": total_memory,
            "total_memory_mb": total_memory / (1024 * 1024),
            "asset_count": len(self.asset_metadata),
            "cached_assets": len(self.asset_cache),
            "memory_by_type": {},
            "largest_assets": []
        }
        
        # Memory by type
        type_memory = {}
        for asset_name, metadata in self.asset_metadata.items():
            asset_type = metadata["type"]
            memory = self.memory_usage.get(asset_name, 0)
            type_memory[asset_type] = type_memory.get(asset_type, 0) + memory
        
        report["memory_by_type"] = type_memory
        
        # Largest assets
        largest = sorted(self.memory_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        report["largest_assets"] = [(name, size / (1024 * 1024)) for name, size in largest]
        
        return report
    
    # ASSET STREAMING
    def enable_streaming(self, stream_distance: float = 1000.0):
        """Enable asset streaming based on distance"""
        self.streaming_enabled = True
        self.stream_distance = stream_distance
    
    def update_streaming(self, player_position: Tuple[float, float]):
        """Update streaming based on player position"""
        if not hasattr(self, 'streaming_enabled'):
            return
        
        px, py = player_position
        
        for asset_name, metadata in self.asset_metadata.items():
            if "world_position" in metadata:
                ax, ay = metadata["world_position"]
                distance = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
                
                if distance <= self.stream_distance:
                    # Load if not loaded
                    if asset_name not in self.images and metadata["type"] == "image":
                        self.queue_async_load("image", asset_name, metadata["path"])
                else:
                    # Unload if too far
                    if asset_name in self.images:
                        self.unload_asset(asset_name)
    
    # GETTER METHODS WITH TRACKING
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get image with usage tracking"""
        if name in self.images:
            self.access_frequency[name] = self.access_frequency.get(name, 0) + 1
            return self.images[name]
        return None
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get sound with usage tracking"""
        if name in self.sounds:
            self.access_frequency[name] = self.access_frequency.get(name, 0) + 1
            return self.sounds[name]
        return None
    
    def get_music_path(self, name: str) -> Optional[str]:
        """Get music file path"""
        return self.music.get(name)
    
    def get_animation(self, name: str) -> Optional[List[pygame.Surface]]:
        """Get animation frames"""
        if name in self.animations:
            self.access_frequency[name] = self.access_frequency.get(name, 0) + 1
            return self.animations[name]
        return None
    
    def get_animation_frame(self, name: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get specific animation frame"""
        if name in self.animations:
            frames = self.animations[name]
            if 0 <= frame_index < len(frames):
                self.access_frequency[name] = self.access_frequency.get(name, 0) + 1
                return frames[frame_index]
        return None
    
    def get_gif(self, name: str) -> Optional[List[pygame.Surface]]:
        """Get GIF frames"""
        return self.gifs.get(name)
    
    def get_gif_frame(self, name: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get specific GIF frame"""
        if name in self.gifs:
            frames = self.gifs[name]
            if 0 <= frame_index < len(frames):
                return frames[frame_index]
        return None
    
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Get font"""
        return self.fonts.get(name)
    
    def get_data(self, name: str) -> Optional[Any]:
        """Get data file content"""
        return self.data_files.get(name)
    
    def get_asset_info(self, name: str) -> Optional[Dict]:
        """Get asset metadata"""
        return self.asset_metadata.get(name)
    
    # CONVENIENCE METHODS
    def play_sound(self, name: str, loops: int = 0) -> bool:
        """Play sound effect"""
        sound = self.get_sound(name)
        if sound:
            try:
                sound.play(loops)
                return True
            except Exception as e:
                print(f"Failed to play sound {name}: {e}")
        return False
    
    def play_music(self, name: str, loops: int = -1, fade_in: int = 0) -> bool:
        """Play background music"""
        music_path = self.get_music_path(name)
        if music_path:
            try:
                pygame.mixer.music.load(music_path)
                if fade_in > 0:
                    pygame.mixer.music.play(loops, fade_in_ms=fade_in)
                else:
                    pygame.mixer.music.play(loops)
                return True
            except Exception as e:
                print(f"Failed to play music {name}: {e}")
        return False
    
    def stop_music(self, fade_out: int = 0):
        """Stop background music"""
        if fade_out > 0:
            pygame.mixer.music.fadeout(fade_out)
        else:
            pygame.mixer.music.stop()
    
    # BULK OPERATIONS
    def load_directory(self, directory_path: str, asset_type: str = "auto", prefix: str = ""):
        """Load all assets from a directory"""
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return
        
        loaded_count = 0
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                name = prefix + os.path.splitext(filename)[0]
                extension = os.path.splitext(filename)[1].lower()
                
                # Auto-detect type if needed
                if asset_type == "auto":
                    if extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                        detected_type = "image"
                    elif extension in ['.wav', '.ogg', '.mp3']:
                        detected_type = "sound"
                    elif extension in ['.mp3', '.ogg', '.wav']:
                        detected_type = "music"
                    elif extension in ['.ttf', '.otf']:
                        detected_type = "font"
                    elif extension in ['.json', '.txt']:
                        detected_type = "data"
                    else:
                        continue
                else:
                    detected_type = asset_type
                
                # Load based on detected type
                success = False
                if detected_type == "image":
                    success = self.load_image(name, file_path)
                elif detected_type == "sound":
                    success = self.load_sound(name, file_path)
                elif detected_type == "music":
                    success = self.load_music(name, file_path)
                elif detected_type == "font":
                    success = self.load_font(name, file_path)
                elif detected_type == "data":
                    success = self.load_data_file(name, file_path)
                
                if success:
                    loaded_count += 1
        
        print(f"Loaded {loaded_count} assets from {directory_path}")
    
    def save_asset_manifest(self, file_path: str):
        """Save manifest of all loaded assets"""
        manifest = {
            "assets": self.asset_metadata,
            "load_times": self.load_times,
            "memory_usage": self.memory_usage,
            "access_frequency": self.access_frequency
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            print(f"Asset manifest saved to {file_path}")
        except Exception as e:
            print(f"Failed to save manifest: {e}")
    
    def load_asset_manifest(self, file_path: str):
        """Load assets from manifest file"""
        try:
            with open(file_path, 'r') as f:
                manifest = json.load(f)
            
            for asset_name, metadata in manifest["assets"].items():
                asset_type = metadata["type"]
                asset_path = metadata["path"]
                
                if asset_type == "image":
                    self.load_image(asset_name, asset_path)
                elif asset_type == "sound":
                    self.load_sound(asset_name, asset_path)
                elif asset_type == "music":
                    self.load_music(asset_name, asset_path)
                elif asset_type == "font":
                    self.load_font(asset_name, asset_path, metadata.get("size", 24))
                elif asset_type == "data":
                    self.load_data_file(asset_name, asset_path)
            
            print(f"Loaded assets from manifest: {file_path}")
            
        except Exception as e:
            print(f"Failed to load manifest: {e}")
    
    def cleanup(self):
        """Clean up asset manager"""
        # Stop background loading
        self.loading_thread_active = False
        if self.background_loader and self.background_loader.is_alive():
            self.background_loader.join(timeout=1.0)
        
        # Clear all assets
        self.images.clear()
        self.sounds.clear()
        self.music.clear()
        self.animations.clear()
        self.gifs.clear()
        self.fonts.clear()
        self.data_files.clear()
        
        # Clear metadata
        self.asset_metadata.clear()
        self.asset_cache.clear()
        self.memory_usage.clear()
        self.load_times.clear()
        self.access_frequency.clear()

# Global asset manager instance
asset_manager = AssetManager()

# Convenience functions for quick access
def load_image(name: str, path: str) -> bool:
    return asset_manager.load_image(name, path)

def load_sound(name: str, path: str) -> bool:
    return asset_manager.load_sound(name, path)

def get_image(name: str) -> Optional[pygame.Surface]:
    return asset_manager.get_image(name)

def get_sound(name: str) -> Optional[pygame.mixer.Sound]:
    return asset_manager.get_sound(name)

def play_sound(name: str, loops: int = 0) -> bool:
    return asset_manager.play_sound(name, loops)
