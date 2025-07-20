import os
from pathlib import Path
import json
import hashlib
from PIL import Image, ImageTk
import tkinter as tk

class AssetUtils:
    """Utility class for asset management operations"""
    
    def __init__(self):
        # File type mappings
        self.file_types = {
            # Images
            '.png': 'images', '.jpg': 'images', '.jpeg': 'images',
            '.gif': 'images', '.bmp': 'images', '.webp': 'images', '.svg': 'images',
            
            # Audio
            '.mp3': 'sounds', '.wav': 'sounds', '.ogg': 'sounds', 
            '.m4a': 'sounds', '.flac': 'sounds', '.aac': 'sounds',
            
            # Fonts
            '.ttf': 'fonts', '.otf': 'fonts', '.woff': 'fonts', '.woff2': 'fonts',
            
            # Python files
            '.py': 'python',
            
            # Text files
            '.txt': 'text',
            
            # Data/Other
            '.json': 'other', '.md': 'other', 
            '.yml': 'other', '.yaml': 'other', '.xml': 'other'
        }
        
        # File type icons
        self.file_icons = {
            'images': '🖼️',
            'sounds': '🎵',
            'fonts': '🔤',
            'other': '📄',
            'python': '🐍',
            'text': '📝',
            'unknown': '❓'
        }
        
    def get_file_type(self, file_extension):
        """Get file type based on extension"""
        return self.file_types.get(file_extension.lower(), 'other')
        
    def get_file_type_icon(self, file_type):
        """Get icon for file type"""
        return self.file_icons.get(file_type, self.file_icons['unknown'])
        
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def get_file_hash(self, file_path):
        """Generate MD5 hash of file for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error generating hash for {file_path}: {e}")
            return None
            
    def create_image_thumbnail(self, image_path, size=(100, 100)):
        """Create thumbnail for image file"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                    
                img.thumbnail(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            return None
            
    def is_supported_file(self, file_path):
        """Check if file type is supported"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.file_types
        
    def get_asset_info(self, file_path):
        """Get comprehensive info about an asset file"""
        path = Path(file_path)
        
        if not path.exists():
            return None
            
        try:
            stat = path.stat()
            file_type = self.get_file_type(path.suffix)
            
            info = {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'size_formatted': self.format_file_size(stat.st_size),
                'type': file_type,
                'extension': path.suffix,
                'modified': stat.st_mtime,
                'icon': self.get_file_type_icon(file_type)
            }
            
            # Add type-specific info
            if file_type == 'images':
                info.update(self.get_image_info(path))
            elif file_type == 'sounds':
                info.update(self.get_audio_info(path))
                
            return info
            
        except Exception as e:
            print(f"Error getting info for {file_path}: {e}")
            return None
            
    def get_image_info(self, image_path):
        """Get additional info for image files"""
        try:
            with Image.open(image_path) as img:
                return {
                    'dimensions': img.size,
                    'mode': img.mode,
                    'format': img.format
                }
        except Exception as e:
            print(f"Error getting image info for {image_path}: {e}")
            return {}
            
    def get_audio_info(self, audio_path):
        """Get additional info for audio files (basic implementation)"""
        try:
            # This could be extended with proper audio metadata libraries
            # For now, just return basic info
            return {
                'format': Path(audio_path).suffix.upper()[1:]
            }
        except Exception as e:
            print(f"Error getting audio info for {audio_path}: {e}")
            return {}
            
    def validate_asset_name(self, name):
        """Validate asset name for filesystem compatibility"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
            
        # Remove leading/trailing spaces and dots
        name = name.strip(' .')
        
        # Ensure it's not empty
        if not name:
            name = "unnamed_asset"
            
        return name
        
    def create_asset_metadata(self, file_path, additional_info=None):
        """Create metadata entry for an asset"""
        info = self.get_asset_info(file_path)
        if not info:
            return None
            
        metadata = {
            'name': info['name'],
            'type': info['type'],
            'size': info['size'],
            'hash': self.get_file_hash(file_path),
            'imported_at': info['modified'],
            'tags': [],
            'description': ''
        }
        
        if additional_info:
            metadata.update(additional_info)
            
        return metadata
        
    def search_assets(self, assets, query, search_in=['name', 'tags', 'description']):
        """Search assets based on query"""
        if not query:
            return assets
            
        query_lower = query.lower()
        filtered_assets = []
        
        for asset in assets:
            match_found = False
            
            for field in search_in:
                if field == 'name' and query_lower in asset.get('name', '').lower():
                    match_found = True
                    break
                elif field == 'tags':
                    tags = asset.get('tags', [])
                    if any(query_lower in tag.lower() for tag in tags):
                        match_found = True
                        break
                elif field == 'description' and query_lower in asset.get('description', '').lower():
                    match_found = True
                    break
                    
            if match_found:
                filtered_assets.append(asset)
                
        return filtered_assets
        
    def get_supported_extensions(self):
        """Get list of all supported file extensions"""
        return list(self.file_types.keys())
        
    def get_extensions_by_type(self, file_type):
        """Get extensions for a specific file type"""
        return [ext for ext, ftype in self.file_types.items() if ftype == file_type]
        
    def organize_assets_by_type(self, assets):
        """Organize assets by their type"""
        organized = {
            'images': [],
            'sounds': [],
            'fonts': [],
            'other': []
        }
        
        for asset in assets:
            asset_type = asset.get('type', 'other')
            organized[asset_type].append(asset)
            
        return organized
        
    def generate_unique_filename(self, directory, filename):
        """Generate a unique filename in the given directory"""
        path = Path(directory) / filename
        
        if not path.exists():
            return filename
            
        # Split name and extension
        stem = path.stem
        suffix = path.suffix
        
        counter = 1
        while path.exists():
            new_name = f"{stem}_{counter}{suffix}"
            path = Path(directory) / new_name
            counter += 1
            
        return path.name
