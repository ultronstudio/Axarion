
"""
Axarion Engine Hot Reload System
Enables hot reloading of scripts without restarting the engine
"""

import os
import time
import hashlib
from typing import Dict, Set, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ScriptWatcher(FileSystemEventHandler):
    """Watches for script file changes"""
    
    def __init__(self, reload_system):
        self.reload_system = reload_system
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.ax'):
            self.reload_system.mark_for_reload(event.src_path)

class HotReloadSystem:
    """Hot reload system for AXScript files"""
    
    def __init__(self):
        self.watched_files: Dict[str, float] = {}  # file_path -> last_modified
        self.file_hashes: Dict[str, str] = {}  # file_path -> hash
        self.reload_callbacks: Dict[str, Callable] = {}  # file_path -> callback
        self.pending_reloads: Set[str] = set()
        
        # File system watcher
        self.observer = Observer()
        self.watcher = ScriptWatcher(self)
        self.enabled = True
        
        # Error tracking
        self.reload_errors: Dict[str, str] = {}
    
    def start_watching(self, directory: str = "."):
        """Start watching directory for changes"""
        if self.enabled:
            self.observer.schedule(self.watcher, directory, recursive=True)
            self.observer.start()
    
    def stop_watching(self):
        """Stop watching for changes"""
        self.observer.stop()
        self.observer.join()
    
    def register_script(self, file_path: str, reload_callback: Callable):
        """Register script for hot reloading"""
        if os.path.exists(file_path):
            self.watched_files[file_path] = os.path.getmtime(file_path)
            self.file_hashes[file_path] = self._get_file_hash(file_path)
            self.reload_callbacks[file_path] = reload_callback
    
    def mark_for_reload(self, file_path: str):
        """Mark file for reload on next update"""
        if file_path in self.watched_files:
            self.pending_reloads.add(file_path)
    
    def update(self):
        """Check for file changes and reload if needed"""
        if not self.enabled:
            return
        
        # Process pending reloads
        for file_path in list(self.pending_reloads):
            if self._should_reload(file_path):
                self._reload_script(file_path)
            self.pending_reloads.discard(file_path)
        
        # Check watched files
        for file_path in list(self.watched_files.keys()):
            if self._should_reload(file_path):
                self._reload_script(file_path)
    
    def _should_reload(self, file_path: str) -> bool:
        """Check if file should be reloaded"""
        if not os.path.exists(file_path):
            return False
        
        current_mtime = os.path.getmtime(file_path)
        current_hash = self._get_file_hash(file_path)
        
        # Check if file was modified
        if (current_mtime > self.watched_files[file_path] or 
            current_hash != self.file_hashes[file_path]):
            return True
        
        return False
    
    def _reload_script(self, file_path: str):
        """Reload script file"""
        try:
            # Update tracking info
            self.watched_files[file_path] = os.path.getmtime(file_path)
            self.file_hashes[file_path] = self._get_file_hash(file_path)
            
            # Call reload callback
            if file_path in self.reload_callbacks:
                self.reload_callbacks[file_path](file_path)
                print(f"🔄 Hot reloaded: {file_path}")
                
                # Clear previous errors
                if file_path in self.reload_errors:
                    del self.reload_errors[file_path]
        
        except Exception as e:
            error_msg = f"Hot reload failed for {file_path}: {str(e)}"
            self.reload_errors[file_path] = error_msg
            print(f"❌ {error_msg}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get file content hash"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def get_reload_errors(self) -> Dict[str, str]:
        """Get current reload errors"""
        return self.reload_errors.copy()
    
    def enable(self, enabled: bool):
        """Enable or disable hot reloading"""
        self.enabled = enabled

# Global instance
hot_reload_system = HotReloadSystem()
