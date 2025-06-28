
"""
Axarion Engine Asset Manager
Handles loading and management of images, sounds, animations, and other assets
"""

import pygame
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

class AssetManager:
    """Comprehensive asset management system"""
    
    def __init__(self):
        # Initialize pygame systems
        pygame.init()
        
        # Asset storage
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Asset metadata
        self.asset_info: Dict[str, Dict[str, Any]] = {}
        
        # Supported formats
        self.image_formats = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tga', '.webp', '.svg']
        self.sound_formats = ['.wav', '.mp3', '.ogg', '.m4a', '.flac', '.aac']
        self.font_formats = ['.ttf', '.otf', '.woff', '.woff2']
        self.video_formats = ['.mp4', '.avi', '.mov', '.mkv']
        
        # GIF storage for animated GIFs
        self.gifs: Dict[str, List[pygame.Surface]] = {}
        self.gif_durations: Dict[str, List[float]] = {}
        
        # Base paths
        self.assets_path = Path("assets")
        self.images_path = self.assets_path / "images"
        self.sounds_path = self.assets_path / "sounds"
        self.animations_path = self.assets_path / "animations"
        self.fonts_path = self.assets_path / "fonts"
        
        # Create directories if they don't exist
        self._create_directories()
        
        print("✅ Asset Manager initialized")
    
    def _create_directories(self):
        """Create asset directories"""
        directories = [
            self.assets_path,
            self.images_path,
            self.sounds_path,
            self.animations_path,
            self.fonts_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_image(self, name: str, file_path: str, scale: Optional[Tuple[int, int]] = None) -> bool:
        """Load an image asset"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ Image file not found: {file_path}")
                return False
            
            # Load image
            image = pygame.image.load(file_path).convert_alpha()
            
            # Scale if requested
            if scale:
                image = pygame.transform.scale(image, scale)
            
            # Store image
            self.images[name] = image
            
            # Store metadata
            self.asset_info[name] = {
                'type': 'image',
                'path': file_path,
                'size': image.get_size(),
                'scale': scale
            }
            
            print(f"✅ Loaded image: {name} ({image.get_width()}x{image.get_height()})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load image {name}: {e}")
            return False
    
    def load_sound(self, name: str, file_path: str, volume: float = 1.0) -> bool:
        """Load a sound asset"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ Sound file not found: {file_path}")
                return False
            
            # Load sound
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(volume)
            
            # Store sound
            self.sounds[name] = sound
            
            # Store metadata
            self.asset_info[name] = {
                'type': 'sound',
                'path': file_path,
                'volume': volume
            }
            
            print(f"✅ Loaded sound: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load sound {name}: {e}")
            return False
    
    def load_animation(self, name: str, folder_path: str, frame_duration: float = 0.1) -> bool:
        """Load animation from folder of images"""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                print(f"❌ Animation folder not found: {folder_path}")
                return False
            
            # Get all image files
            image_files = []
            for ext in self.image_formats:
                image_files.extend(folder.glob(f"*{ext}"))
            
            if not image_files:
                print(f"❌ No image files found in: {folder_path}")
                return False
            
            # Sort files naturally
            image_files.sort(key=lambda x: x.name)
            
            # Load frames
            frames = []
            for image_file in image_files:
                frame = pygame.image.load(str(image_file)).convert_alpha()
                frames.append(frame)
            
            # Store animation
            self.animations[name] = frames
            
            # Store metadata
            self.asset_info[name] = {
                'type': 'animation',
                'path': folder_path,
                'frame_count': len(frames),
                'frame_duration': frame_duration,
                'total_duration': len(frames) * frame_duration
            }
            
            print(f"✅ Loaded animation: {name} ({len(frames)} frames)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load animation {name}: {e}")
            return False
    
    def load_sprite_sheet(self, name: str, file_path: str, frame_width: int, frame_height: int) -> bool:
        """Load sprite sheet and split into frames"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ Sprite sheet file not found: {file_path}")
                return False
            
            # Load sprite sheet
            sprite_sheet = pygame.image.load(file_path).convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            
            # Calculate grid
            cols = sheet_width // frame_width
            rows = sheet_height // frame_height
            
            # Extract frames
            frames = []
            for row in range(rows):
                for col in range(cols):
                    x = col * frame_width
                    y = row * frame_height
                    frame = sprite_sheet.subsurface((x, y, frame_width, frame_height))
                    frames.append(frame.copy())
            
            # Store animation
            self.animations[name] = frames
            
            # Store metadata
            self.asset_info[name] = {
                'type': 'sprite_sheet',
                'path': file_path,
                'frame_size': (frame_width, frame_height),
                'grid_size': (cols, rows),
                'frame_count': len(frames)
            }
            
            print(f"✅ Loaded sprite sheet: {name} ({len(frames)} frames, {cols}x{rows} grid)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load sprite sheet {name}: {e}")
            return False
    
    def load_gif(self, name: str, file_path: str) -> bool:
        """Load animated GIF"""
        try:
            if not os.path.exists(file_path):
                print(f"❌ GIF file not found: {file_path}")
                return False
            
            # Load GIF using PIL for better GIF support
            try:
                from PIL import Image
                gif = Image.open(file_path)
                
                frames = []
                durations = []
                
                # Extract all frames
                frame_count = 0
                while True:
                    try:
                        gif.seek(frame_count)
                        
                        # Convert PIL image to pygame surface
                        mode = gif.mode
                        size = gif.size
                        data = gif.tobytes()
                        
                        # Convert to RGBA if needed
                        if mode != 'RGBA':
                            gif_rgba = gif.convert('RGBA')
                            data = gif_rgba.tobytes()
                            mode = 'RGBA'
                        
                        pygame_surface = pygame.image.fromstring(data, size, mode)
                        frames.append(pygame_surface.convert_alpha())
                        
                        # Get frame duration (in milliseconds, convert to seconds)
                        duration = gif.info.get('duration', 100) / 1000.0
                        durations.append(duration)
                        
                        frame_count += 1
                        
                    except EOFError:
                        break
                
                # Store GIF
                self.gifs[name] = frames
                self.gif_durations[name] = durations
                
                # Store metadata
                self.asset_info[name] = {
                    'type': 'gif',
                    'path': file_path,
                    'frame_count': len(frames),
                    'durations': durations,
                    'total_duration': sum(durations)
                }
                
                print(f"✅ Loaded GIF: {name} ({len(frames)} frames)")
                return True
                
            except ImportError:
                print("❌ PIL (Pillow) not available for GIF loading. Install with: pip install Pillow")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load GIF {name}: {e}")
            return False
    
    def load_texture_atlas(self, name: str, image_path: str, atlas_data: Dict) -> bool:
        """Load texture atlas with sprite definitions"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Atlas image not found: {image_path}")
                return False
            
            # Load atlas image
            atlas_image = pygame.image.load(image_path).convert_alpha()
            
            # Extract sprites based on atlas data
            sprites = {}
            for sprite_name, sprite_info in atlas_data.items():
                x = sprite_info.get('x', 0)
                y = sprite_info.get('y', 0)
                width = sprite_info.get('width', 32)
                height = sprite_info.get('height', 32)
                
                sprite_surface = atlas_image.subsurface((x, y, width, height))
                sprites[sprite_name] = sprite_surface.copy()
            
            # Store individual sprites
            for sprite_name, sprite_surface in sprites.items():
                full_name = f"{name}_{sprite_name}"
                self.images[full_name] = sprite_surface
                
                self.asset_info[full_name] = {
                    'type': 'atlas_sprite',
                    'atlas': name,
                    'sprite': sprite_name,
                    'size': sprite_surface.get_size()
                }
            
            print(f"✅ Loaded texture atlas: {name} ({len(sprites)} sprites)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load texture atlas {name}: {e}")
            return False

    def load_font(self, name: str, file_path: str, size: int = 24) -> bool:
        """Load a font asset"""
        try:
            if os.path.exists(file_path):
                font = pygame.font.Font(file_path, size)
            else:
                # Use system font
                font = pygame.font.SysFont(file_path, size)
            
            self.fonts[name] = font
            
            # Store metadata
            self.asset_info[name] = {
                'type': 'font',
                'path': file_path,
                'size': size
            }
            
            print(f"✅ Loaded font: {name} (size {size})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load font {name}: {e}")
            return False
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Get loaded image"""
        return self.images.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get loaded sound"""
        return self.sounds.get(name)
    
    def get_animation_frame(self, name: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get specific frame from animation"""
        animation = self.animations.get(name)
        if animation and 0 <= frame_index < len(animation):
            return animation[frame_index]
        return None
    
    def get_animation(self, name: str) -> Optional[List[pygame.Surface]]:
        """Get entire animation"""
        return self.animations.get(name)
    
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Get loaded font"""
        return self.fonts.get(name)
    
    def get_gif_frame(self, name: str, frame_index: int) -> Optional[pygame.Surface]:
        """Get specific frame from GIF"""
        gif = self.gifs.get(name)
        if gif and 0 <= frame_index < len(gif):
            return gif[frame_index]
        return None
    
    def get_gif(self, name: str) -> Optional[List[pygame.Surface]]:
        """Get entire GIF as frame list"""
        return self.gifs.get(name)
    
    def get_gif_frame_duration(self, name: str, frame_index: int) -> float:
        """Get duration of specific GIF frame"""
        durations = self.gif_durations.get(name)
        if durations and 0 <= frame_index < len(durations):
            return durations[frame_index]
        return 0.1  # Default duration
    
    def play_sound(self, name: str, loops: int = 0) -> bool:
        """Play a sound"""
        sound = self.get_sound(name)
        if sound:
            sound.play(loops)
            return True
        return False
    
    def create_ship_sprites(self):
        """Create sample ship sprites from basic shapes"""
        # Create small ship sprite
        ship_surface = pygame.Surface((32, 24), pygame.SRCALPHA)
        
        # Draw ship body (rectangle)
        pygame.draw.rect(ship_surface, (100, 100, 100), (8, 8, 16, 8))
        
        # Draw ship nose (triangle)
        pygame.draw.polygon(ship_surface, (120, 120, 120), [(24, 12), (30, 10), (30, 14)])
        
        # Draw engines
        pygame.draw.rect(ship_surface, (80, 80, 200), (4, 6, 4, 4))
        pygame.draw.rect(ship_surface, (80, 80, 200), (4, 14, 4, 4))
        
        # Store ship
        self.images['small_ship'] = ship_surface
        
        # Create larger ship
        big_ship = pygame.Surface((48, 32), pygame.SRCALPHA)
        pygame.draw.rect(big_ship, (80, 80, 80), (12, 12, 24, 8))
        pygame.draw.polygon(big_ship, (100, 100, 100), [(36, 16), (44, 12), (44, 20)])
        pygame.draw.rect(big_ship, (200, 80, 80), (6, 10, 6, 4))
        pygame.draw.rect(big_ship, (200, 80, 80), (6, 18, 6, 4))
        
        self.images['big_ship'] = big_ship
        
        print("✅ Created sample ship sprites")
    
    def scan_assets_folder(self) -> Dict[str, List[str]]:
        """Scan assets folder and return available files"""
        available_assets = {
            'images': [],
            'sounds': [],
            'fonts': [],
            'animations': []
        }
        
        # Scan images
        if self.images_path.exists():
            for ext in self.image_formats:
                files = list(self.images_path.glob(f"*{ext}"))
                available_assets['images'].extend([f.name for f in files])
        
        # Scan sounds
        if self.sounds_path.exists():
            for ext in self.sound_formats:
                files = list(self.sounds_path.glob(f"*{ext}"))
                available_assets['sounds'].extend([f.name for f in files])
        
        # Scan fonts
        if self.fonts_path.exists():
            for ext in self.font_formats:
                files = list(self.fonts_path.glob(f"*{ext}"))
                available_assets['fonts'].extend([f.name for f in files])
        
        # Scan animation folders
        if self.animations_path.exists():
            for folder in self.animations_path.iterdir():
                if folder.is_dir():
                    available_assets['animations'].append(folder.name)
        
        return available_assets
    
    def load_all_assets(self):
        """Automatically load all assets from folders"""
        available = self.scan_assets_folder()
        
        # Load images
        for image_file in available['images']:
            name = Path(image_file).stem
            file_path = self.images_path / image_file
            self.load_image(name, str(file_path))
        
        # Load sounds
        for sound_file in available['sounds']:
            name = Path(sound_file).stem
            file_path = self.sounds_path / sound_file
            self.load_sound(name, str(file_path))
        
        # Load animations
        for anim_folder in available['animations']:
            folder_path = self.animations_path / anim_folder
            self.load_animation(anim_folder, str(folder_path))
        
        # Load GIFs
        gif_files = []
        if self.images_path.exists():
            gif_files = list(self.images_path.glob("*.gif"))
        
        for gif_file in gif_files:
            name = gif_file.stem
            self.load_gif(name, str(gif_file))
        
        # Create sample sprites
        self.create_ship_sprites()
        
        print(f"✅ Auto-loaded {len(self.images)} images, {len(self.sounds)} sounds, {len(self.animations)} animations")
    
    def get_asset_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about an asset"""
        return self.asset_info.get(name)
    
    def list_assets(self) -> Dict[str, List[str]]:
        """List all loaded assets"""
        return {
            'images': list(self.images.keys()),
            'sounds': list(self.sounds.keys()),
            'animations': list(self.animations.keys()),
            'gifs': list(self.gifs.keys()),
            'fonts': list(self.fonts.keys())
        }
    
    def cleanup(self):
        """Clean up asset manager"""
        self.images.clear()
        self.sounds.clear()
        self.animations.clear()
        self.fonts.clear()
        self.asset_info.clear()

# Global asset manager instance
asset_manager = AssetManager()
