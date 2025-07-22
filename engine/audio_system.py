
"""
Axarion Engine Audio System
Handles sound effects, music, and audio management
"""

import pygame
import os
import math
from typing import Dict, Optional, List, Tuple, Set
from pathlib import Path

class AudioSystem:
    """Audio system for playing sounds and music"""
    
    def __init__(self):
        try:
            # Enhanced audio initialization with better settings
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
            pygame.mixer.init()
            self.audio_enabled = True
            print("🔊 Enhanced Audio system initialized successfully")
        except (pygame.error, OSError) as e:
            print(f"Audio system disabled: {e}")
            self.audio_enabled = False
            try:
                pygame.mixer.quit()
            except:
                pass
        
        # Enhanced audio management
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_channels: Dict[str, pygame.mixer.Channel] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music = None
        
        # Advanced features
        self.audio_groups: Dict[str, List[str]] = {}
        self.fading_sounds: Dict[str, Dict] = {}
        self.looping_sounds: Set[str] = set()
        self.sound_priorities: Dict[str, int] = {}
        
        # Performance tracking
        self.max_channels = 32
        self.active_channels = 0
        
        # 3D audio simulation
        self.listener_position = (0, 0)
        self.enable_3d_audio = False
        self.max_audio_distance = 1000.0
        
    def load_sound(self, name: str, file_path: str) -> bool:
        """Load a sound effect"""
        try:
            if os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
                return True
        except Exception as e:
            print(f"Failed to load sound {name}: {e}")
        return False
    
    def play_sound(self, name: str, loops: int = 0) -> bool:
        """Play a sound effect"""
        if not self.audio_enabled or name not in self.sounds:
            return False
        
        try:
            self.sounds[name].play(loops)
            return True
        except Exception as e:
            print(f"Failed to play sound {name}: {e}")
        return False
    
    def stop_sound(self, name: str):
        """Stop a specific sound"""
        if name in self.sounds:
            self.sounds[name].stop()
    
    def load_music(self, file_path: str) -> bool:
        """Load background music"""
        try:
            if os.path.exists(file_path):
                pygame.mixer.music.load(file_path)
                self.current_music = file_path
                return True
        except Exception as e:
            print(f"Failed to load music: {e}")
        return False
    
    def play_music(self, loops: int = -1, fade_in: int = 0) -> bool:
        """Play background music"""
        if not self.audio_enabled:
            return False
        
        try:
            if fade_in > 0:
                pygame.mixer.music.fadeout(fade_in)
            pygame.mixer.music.play(loops)
            pygame.mixer.music.set_volume(self.music_volume)
            return True
        except Exception as e:
            print(f"Failed to play music: {e}")
        return False
    
    def stop_music(self, fade_out: int = 0):
        """Stop background music"""
        if fade_out > 0:
            pygame.mixer.music.fadeout(fade_out)
        else:
            pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pause music"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause music"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def update(self, delta_time):
        """Update audio system - required for engine compatibility"""
        pass  # Audio system doesn't need per-frame updates
    
    def play_sound_3d(self, name: str, position: Tuple[float, float], 
                      max_distance: float = None, loops: int = 0) -> bool:
        """Play sound with 3D positioning"""
        if not self.audio_enabled or name not in self.sounds or not self.enable_3d_audio:
            return self.play_sound(name, loops)
        
        max_dist = max_distance or self.max_audio_distance
        
        # Calculate distance and volume
        lx, ly = self.listener_position
        sx, sy = position
        distance = math.sqrt((sx - lx) ** 2 + (sy - ly) ** 2)
        
        if distance > max_dist:
            return False
        
        # Calculate volume based on distance
        volume_factor = 1.0 - (distance / max_dist)
        volume = self.sfx_volume * volume_factor
        
        # Calculate stereo panning
        angle = math.atan2(sy - ly, sx - lx)
        pan = (math.sin(angle) + 1.0) / 2.0  # 0.0 = left, 1.0 = right
        
        try:
            channel = self.sounds[name].play(loops)
            if channel:
                channel.set_volume(volume * (1.0 - pan), volume * pan)
                return True
        except Exception as e:
            print(f"Failed to play 3D sound {name}: {e}")
        
        return False

    def set_listener_position(self, x: float, y: float):
        """Set 3D audio listener position"""
        self.listener_position = (x, y)

    def enable_3d_audio_system(self, enabled: bool = True):
        """Enable or disable 3D audio"""
        self.enable_3d_audio = enabled

    def create_audio_group(self, group_name: str, sound_names: List[str]):
        """Create audio group for batch operations"""
        self.audio_groups[group_name] = sound_names

    def play_audio_group(self, group_name: str, loops: int = 0) -> bool:
        """Play all sounds in audio group"""
        if group_name not in self.audio_groups:
            return False
        
        success = True
        for sound_name in self.audio_groups[group_name]:
            if not self.play_sound(sound_name, loops):
                success = False
        
        return success

    def stop_audio_group(self, group_name: str):
        """Stop all sounds in audio group"""
        if group_name not in self.audio_groups:
            return
        
        for sound_name in self.audio_groups[group_name]:
            self.stop_sound(sound_name)

    def set_audio_group_volume(self, group_name: str, volume: float):
        """Set volume for audio group"""
        if group_name not in self.audio_groups:
            return
        
        for sound_name in self.audio_groups[group_name]:
            if sound_name in self.sounds:
                self.sounds[sound_name].set_volume(volume)

    def fade_in_sound(self, name: str, duration: float, loops: int = 0) -> bool:
        """Fade in sound over duration"""
        if not self.audio_enabled or name not in self.sounds:
            return False
        
        try:
            channel = self.sounds[name].play(loops, fade_ms=int(duration * 1000))
            if channel:
                self.sound_channels[name] = channel
                return True
        except Exception as e:
            print(f"Failed to fade in sound {name}: {e}")
        
        return False

    def fade_out_sound(self, name: str, duration: float):
        """Fade out sound over duration"""
        if name in self.sound_channels and self.sound_channels[name]:
            try:
                self.sound_channels[name].fadeout(int(duration * 1000))
            except Exception as e:
                print(f"Failed to fade out sound {name}: {e}")

    def set_sound_priority(self, name: str, priority: int):
        """Set sound priority for channel management"""
        self.sound_priorities[name] = priority

    def play_sound_with_priority(self, name: str, priority: int = 0, loops: int = 0) -> bool:
        """Play sound with priority system"""
        if not self.audio_enabled or name not in self.sounds:
            return False
        
        # Check if we have available channels
        if self.active_channels >= self.max_channels:
            # Find lowest priority sound to stop
            lowest_priority = float('inf')
            lowest_channel = None
            
            for sound_name, channel in self.sound_channels.items():
                if channel and channel.get_busy():
                    sound_priority = self.sound_priorities.get(sound_name, 0)
                    if sound_priority < priority and sound_priority < lowest_priority:
                        lowest_priority = sound_priority
                        lowest_channel = sound_name
            
            # Stop lowest priority sound if found
            if lowest_channel:
                self.stop_sound(lowest_channel)
        
        # Play the sound
        self.sound_priorities[name] = priority
        return self.play_sound(name, loops)

    def get_audio_stats(self) -> Dict:
        """Get audio system statistics"""
        active_sounds = sum(1 for channel in self.sound_channels.values() 
                          if channel and channel.get_busy())
        
        return {
            'audio_enabled': self.audio_enabled,
            'total_sounds': len(self.sounds),
            'active_sounds': active_sounds,
            'max_channels': self.max_channels,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            '3d_audio_enabled': self.enable_3d_audio
        }

    def update(self, delta_time):
        """Enhanced audio system update"""
        if not self.audio_enabled:
            return
        
        # Update active channel count
        self.active_channels = sum(1 for channel in self.sound_channels.values() 
                                 if channel and channel.get_busy())
        
        # Clean up finished channels
        finished_channels = []
        for sound_name, channel in self.sound_channels.items():
            if channel and not channel.get_busy():
                finished_channels.append(sound_name)
        
        for sound_name in finished_channels:
            del self.sound_channels[sound_name]
            if sound_name in self.looping_sounds:
                self.looping_sounds.remove(sound_name)

    def cleanup(self):
        """Enhanced cleanup with proper resource management"""
        if self.audio_enabled:
            try:
                # Check if mixer is still initialized before cleanup
                if pygame.mixer.get_init():
                    # Stop all sounds
                    for channel in self.sound_channels.values():
                        if channel:
                            try:
                                channel.stop()
                            except:
                                pass
                    
                    # Stop music
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    
                    # Quit mixer
                    pygame.mixer.quit()
                    print("🔇 Audio system cleaned up successfully")
                else:
                    print("🔇 Audio system already cleaned up")
                
                # Clear data structures regardless
                self.sounds.clear()
                self.sound_channels.clear()
                self.audio_groups.clear()
                self.fading_sounds.clear()
                self.looping_sounds.clear()
                self.sound_priorities.clear()
                
            except Exception as e:
                print(f"Warning during audio cleanup: {e}")
                # Don't let audio cleanup errors crash the engine

# Enhanced global functions
def play_sound_3d(name: str, position: Tuple[float, float], max_distance: float = None, loops: int = 0) -> bool:
    """Play 3D positioned sound"""
    return audio_system.play_sound_3d(name, position, max_distance, loops)

def set_listener_position(x: float, y: float):
    """Set 3D audio listener position"""
    audio_system.set_listener_position(x, y)

def fade_in_sound(name: str, duration: float, loops: int = 0) -> bool:
    """Fade in sound"""
    return audio_system.fade_in_sound(name, duration, loops)

def fade_out_sound(name: str, duration: float):
    """Fade out sound"""
    audio_system.fade_out_sound(name, duration)

# Global audio system instance
audio_system = AudioSystem()

# Convenience functions for scripts
def play_sound(name: str, loops: int = 0) -> bool:
    """Play a sound effect"""
    return audio_system.play_sound(name, loops)

def play_music(file_path: str, loops: int = -1) -> bool:
    """Play background music"""
    if audio_system.load_music(file_path):
        return audio_system.play_music(loops)
    return False

def stop_music():
    """Stop background music"""
    audio_system.stop_music()

def set_volume(music_vol: float, sfx_vol: float):
    """Set audio volumes"""
    audio_system.set_music_volume(music_vol)
    audio_system.set_sfx_volume(sfx_vol)
