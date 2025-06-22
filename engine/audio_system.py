
"""
Axarion Engine Audio System
Handles sound effects, music, and audio management
"""

import pygame
import os
from typing import Dict, Optional, List
from pathlib import Path

class AudioSystem:
    """Audio system for playing sounds and music"""
    
    def __init__(self):
        try:
            # Try to initialize audio with fallback options
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.audio_enabled = True
            print("Audio system initialized successfully")
        except (pygame.error, OSError) as e:
            print(f"Audio system disabled: {e}")
            self.audio_enabled = False
            # Ensure pygame mixer is properly cleaned up
            try:
                pygame.mixer.quit()
            except:
                pass
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.current_music = None
        
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
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio_enabled:
            try:
                pygame.mixer.quit()
            except:
                pass

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
