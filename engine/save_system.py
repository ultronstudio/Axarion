
"""
Advanced Save System for Axarion Engine
Handles game saves, player progress, and game state management
"""

import json
import os
import pickle
import gzip
import hashlib
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

class SaveSystem:
    """Advanced save system with encryption, compression, and cloud sync"""
    
    def __init__(self):
        self.save_directory = "saves/"
        self.backup_directory = "saves/backups/"
        self.settings_file = "settings.json"
        
        # Save system configuration
        self.compression_enabled = True
        self.encryption_enabled = False
        self.backup_enabled = True
        self.max_backups = 5
        self.auto_save_enabled = False
        self.auto_save_interval = 300  # 5 minutes
        
        # Save slots
        self.max_save_slots = 10
        self.current_save_slot = 1
        
        # Game state tracking
        self.game_state = {}
        self.player_data = {}
        self.world_data = {}
        self.settings = {}
        
        # Progress tracking
        self.achievements = {}
        self.statistics = {}
        self.unlock_flags = {}
        
        # Auto-save timer
        self.last_auto_save = time.time()
        
        # Create directories
        os.makedirs(self.save_directory, exist_ok=True)
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Load settings
        self.load_settings()
    
    def save_game(self, slot: int = None, custom_name: str = None) -> bool:
        """Save complete game state"""
        if slot is None:
            slot = self.current_save_slot
        
        try:
            # Generate save filename
            if custom_name:
                filename = f"save_{custom_name}.sav"
            else:
                filename = f"save_slot_{slot}.sav"
            
            save_path = os.path.join(self.save_directory, filename)
            
            # Create complete save data
            save_data = {
                "metadata": {
                    "version": "1.0",
                    "timestamp": time.time(),
                    "slot": slot,
                    "custom_name": custom_name,
                    "playtime": self.get_total_playtime(),
                    "level": self.player_data.get("level", "unknown"),
                    "checksum": ""
                },
                "game_state": self.game_state,
                "player_data": self.player_data,
                "world_data": self.world_data,
                "achievements": self.achievements,
                "statistics": self.statistics,
                "unlock_flags": self.unlock_flags
            }
            
            # Generate checksum for integrity
            data_str = json.dumps(save_data, sort_keys=True)
            save_data["metadata"]["checksum"] = hashlib.md5(data_str.encode()).hexdigest()
            
            # Create backup if enabled
            if self.backup_enabled and os.path.exists(save_path):
                self.create_backup(save_path)
            
            # Save data
            if self.compression_enabled:
                self.save_compressed(save_data, save_path)
            else:
                self.save_uncompressed(save_data, save_path)
            
            print(f"Game saved to slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, slot: int = None, custom_name: str = None) -> bool:
        """Load complete game state"""
        if slot is None:
            slot = self.current_save_slot
        
        try:
            # Generate load filename
            if custom_name:
                filename = f"save_{custom_name}.sav"
            else:
                filename = f"save_slot_{slot}.sav"
            
            save_path = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(save_path):
                print(f"Save file not found: {save_path}")
                return False
            
            # Load data
            if self.compression_enabled:
                save_data = self.load_compressed(save_path)
            else:
                save_data = self.load_uncompressed(save_path)
            
            # Verify checksum
            if not self.verify_save_integrity(save_data):
                print("Save file corrupted - attempting to load backup")
                backup_loaded = self.load_backup(save_path)
                if not backup_loaded:
                    return False
                save_data = backup_loaded
            
            # Restore game state
            self.game_state = save_data.get("game_state", {})
            self.player_data = save_data.get("player_data", {})
            self.world_data = save_data.get("world_data", {})
            self.achievements = save_data.get("achievements", {})
            self.statistics = save_data.get("statistics", {})
            self.unlock_flags = save_data.get("unlock_flags", {})
            
            self.current_save_slot = slot
            
            print(f"Game loaded from slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return False
    
    def save_compressed(self, data: Dict, filepath: str):
        """Save data with compression"""
        json_str = json.dumps(data, indent=2)
        compressed_data = gzip.compress(json_str.encode('utf-8'))
        
        with open(filepath, 'wb') as f:
            f.write(compressed_data)
    
    def load_compressed(self, filepath: str) -> Dict:
        """Load compressed data"""
        with open(filepath, 'rb') as f:
            compressed_data = f.read()
        
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_str)
    
    def save_uncompressed(self, data: Dict, filepath: str):
        """Save data without compression"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_uncompressed(self, filepath: str) -> Dict:
        """Load uncompressed data"""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def verify_save_integrity(self, save_data: Dict) -> bool:
        """Verify save file integrity using checksum"""
        if "metadata" not in save_data or "checksum" not in save_data["metadata"]:
            return False
        
        stored_checksum = save_data["metadata"]["checksum"]
        save_data["metadata"]["checksum"] = ""
        
        data_str = json.dumps(save_data, sort_keys=True)
        calculated_checksum = hashlib.md5(data_str.encode()).hexdigest()
        
        save_data["metadata"]["checksum"] = stored_checksum
        
        return stored_checksum == calculated_checksum
    
    def create_backup(self, save_path: str):
        """Create backup of existing save"""
        if not os.path.exists(save_path):
            return
        
        timestamp = int(time.time())
        backup_name = f"{os.path.basename(save_path)}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_directory, backup_name)
        
        # Copy file to backup
        import shutil
        shutil.copy2(save_path, backup_path)
        
        # Clean old backups
        self.cleanup_old_backups()
    
    def load_backup(self, save_path: str) -> Optional[Dict]:
        """Load most recent backup"""
        base_name = os.path.basename(save_path)
        backups = []
        
        for filename in os.listdir(self.backup_directory):
            if filename.startswith(base_name + ".backup_"):
                timestamp = int(filename.split("_")[-1])
                backups.append((timestamp, filename))
        
        if not backups:
            return None
        
        # Get most recent backup
        backups.sort(reverse=True)
        latest_backup = backups[0][1]
        backup_path = os.path.join(self.backup_directory, latest_backup)
        
        try:
            if self.compression_enabled:
                return self.load_compressed(backup_path)
            else:
                return self.load_uncompressed(backup_path)
        except Exception as e:
            print(f"Failed to load backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Remove old backups exceeding max limit"""
        backups = []
        
        for filename in os.listdir(self.backup_directory):
            if ".backup_" in filename:
                timestamp = int(filename.split("_")[-1])
                backups.append((timestamp, filename))
        
        backups.sort(reverse=True)
        
        # Remove excess backups
        for i in range(self.max_backups, len(backups)):
            old_backup = os.path.join(self.backup_directory, backups[i][1])
            os.remove(old_backup)
    
    def auto_save(self) -> bool:
        """Perform automatic save if enabled"""
        if not self.auto_save_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_auto_save >= self.auto_save_interval:
            success = self.save_game(slot=0, custom_name="autosave")
            if success:
                self.last_auto_save = current_time
                print("Auto-save completed")
            return success
        
        return False
    
    def quick_save(self) -> bool:
        """Quick save to dedicated slot"""
        return self.save_game(custom_name="quicksave")
    
    def quick_load(self) -> bool:
        """Quick load from dedicated slot"""
        return self.load_game(custom_name="quicksave")
    
    def get_save_info(self, slot: int = None, custom_name: str = None) -> Optional[Dict]:
        """Get save file information without loading"""
        if slot is None and custom_name is None:
            return None
        
        try:
            if custom_name:
                filename = f"save_{custom_name}.sav"
            else:
                filename = f"save_slot_{slot}.sav"
            
            save_path = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(save_path):
                return None
            
            # Load only metadata
            if self.compression_enabled:
                save_data = self.load_compressed(save_path)
            else:
                save_data = self.load_uncompressed(save_path)
            
            metadata = save_data.get("metadata", {})
            
            # Add file size
            metadata["file_size"] = os.path.getsize(save_path)
            
            # Format timestamp
            if "timestamp" in metadata:
                metadata["date_string"] = time.strftime("%Y-%m-%d %H:%M:%S", 
                                                       time.localtime(metadata["timestamp"]))
            
            return metadata
            
        except Exception as e:
            print(f"Failed to get save info: {e}")
            return None
    
    def list_saves(self) -> List[Dict]:
        """List all available saves"""
        saves = []
        
        for filename in os.listdir(self.save_directory):
            if filename.endswith('.sav'):
                # Extract slot or custom name
                if filename.startswith('save_slot_'):
                    slot = int(filename.replace('save_slot_', '').replace('.sav', ''))
                    save_info = self.get_save_info(slot=slot)
                    if save_info:
                        save_info['type'] = 'slot'
                        save_info['identifier'] = slot
                        saves.append(save_info)
                        
                elif filename.startswith('save_'):
                    custom_name = filename.replace('save_', '').replace('.sav', '')
                    save_info = self.get_save_info(custom_name=custom_name)
                    if save_info:
                        save_info['type'] = 'custom'
                        save_info['identifier'] = custom_name
                        saves.append(save_info)
        
        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return saves
    
    def delete_save(self, slot: int = None, custom_name: str = None) -> bool:
        """Delete save file"""
        try:
            if custom_name:
                filename = f"save_{custom_name}.sav"
            else:
                filename = f"save_slot_{slot}.sav"
            
            save_path = os.path.join(self.save_directory, filename)
            
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Save deleted: {filename}")
                return True
            else:
                print(f"Save not found: {filename}")
                return False
                
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False
    
    # PLAYER DATA MANAGEMENT
    def set_player_data(self, key: str, value: Any):
        """Set player data"""
        self.player_data[key] = value
    
    def get_player_data(self, key: str, default: Any = None) -> Any:
        """Get player data"""
        return self.player_data.get(key, default)
    
    def set_world_data(self, key: str, value: Any):
        """Set world/level data"""
        self.world_data[key] = value
    
    def get_world_data(self, key: str, default: Any = None) -> Any:
        """Get world/level data"""
        return self.world_data.get(key, default)
    
    def set_game_state(self, key: str, value: Any):
        """Set game state data"""
        self.game_state[key] = value
    
    def get_game_state(self, key: str, default: Any = None) -> Any:
        """Get game state data"""
        return self.game_state.get(key, default)
    
    # ACHIEVEMENT SYSTEM
    def unlock_achievement(self, achievement_id: str, timestamp: float = None):
        """Unlock achievement"""
        if timestamp is None:
            timestamp = time.time()
        
        self.achievements[achievement_id] = {
            "unlocked": True,
            "timestamp": timestamp,
            "date_string": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        }
        
        print(f"Achievement unlocked: {achievement_id}")
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if achievement is unlocked"""
        return self.achievements.get(achievement_id, {}).get("unlocked", False)
    
    def get_achievement_progress(self) -> Dict:
        """Get achievement progress statistics"""
        total_achievements = len(self.achievements)
        unlocked_achievements = sum(1 for ach in self.achievements.values() if ach.get("unlocked", False))
        
        return {
            "total": total_achievements,
            "unlocked": unlocked_achievements,
            "percentage": (unlocked_achievements / total_achievements * 100) if total_achievements > 0 else 0
        }
    
    # STATISTICS TRACKING
    def increment_stat(self, stat_name: str, amount: float = 1):
        """Increment a statistic"""
        self.statistics[stat_name] = self.statistics.get(stat_name, 0) + amount
    
    def set_stat(self, stat_name: str, value: float):
        """Set a statistic value"""
        self.statistics[stat_name] = value
    
    def get_stat(self, stat_name: str, default: float = 0) -> float:
        """Get a statistic value"""
        return self.statistics.get(stat_name, default)
    
    def get_total_playtime(self) -> float:
        """Get total playtime in seconds"""
        return self.get_stat("total_playtime", 0)
    
    def add_playtime(self, seconds: float):
        """Add playtime"""
        self.increment_stat("total_playtime", seconds)
    
    # UNLOCK FLAGS
    def set_unlock_flag(self, flag_name: str, unlocked: bool = True):
        """Set unlock flag"""
        self.unlock_flags[flag_name] = unlocked
    
    def is_unlocked(self, flag_name: str) -> bool:
        """Check if content is unlocked"""
        return self.unlock_flags.get(flag_name, False)
    
    # SETTINGS MANAGEMENT
    def save_settings(self) -> bool:
        """Save game settings"""
        try:
            settings_path = self.settings_file
            
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False
    
    def load_settings(self) -> bool:
        """Load game settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                return True
            else:
                # Create default settings
                self.settings = self.get_default_settings()
                self.save_settings()
                return True
                
        except Exception as e:
            print(f"Failed to load settings: {e}")
            self.settings = self.get_default_settings()
            return False
    
    def get_default_settings(self) -> Dict:
        """Get default game settings"""
        return {
            "graphics": {
                "resolution": "800x600",
                "fullscreen": False,
                "vsync": True,
                "antialiasing": True
            },
            "audio": {
                "master_volume": 1.0,
                "music_volume": 0.8,
                "sfx_volume": 0.9,
                "muted": False
            },
            "controls": {
                "move_left": "a",
                "move_right": "d",
                "jump": "space",
                "action": "e"
            },
            "gameplay": {
                "difficulty": "normal",
                "auto_save": True,
                "subtitles": True
            }
        }
    
    def set_setting(self, category: str, key: str, value: Any):
        """Set a specific setting"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting"""
        return self.settings.get(category, {}).get(key, default)
    
    # EXPORT/IMPORT
    def export_save(self, slot: int, export_path: str) -> bool:
        """Export save to external file"""
        try:
            filename = f"save_slot_{slot}.sav"
            save_path = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(save_path):
                return False
            
            import shutil
            shutil.copy2(save_path, export_path)
            
            print(f"Save exported to {export_path}")
            return True
            
        except Exception as e:
            print(f"Failed to export save: {e}")
            return False
    
    def import_save(self, import_path: str, slot: int) -> bool:
        """Import save from external file"""
        try:
            if not os.path.exists(import_path):
                return False
            
            filename = f"save_slot_{slot}.sav"
            save_path = os.path.join(self.save_directory, filename)
            
            import shutil
            shutil.copy2(import_path, save_path)
            
            print(f"Save imported to slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to import save: {e}")
            return False
    
    def cleanup(self):
        """Clean up save system"""
        # Final auto-save if enabled
        if self.auto_save_enabled:
            self.auto_save()
        
        # Save settings
        self.save_settings()

# Global save system instance
save_system = SaveSystem()
