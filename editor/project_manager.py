"""
Axarion Engine Project Manager
Handles project creation, loading, and saving
"""

import json
import os
from tkinter import messagebox

class ProjectManager:
    """Manages Axarion Engine projects"""
    
    def __init__(self, main_editor):
        self.main_editor = main_editor
        self.project_template = {
            "name": "New Project",
            "version": "1.0",
            "engine_version": "1.0",
            "created": "",
            "modified": "",
            "settings": {
                "resolution": [800, 600],
                "fullscreen": False,
                "vsync": True,
                "physics_enabled": True,
                "gravity": [0, 981]
            },
            "scenes": {},
            "assets": [],
            "scripts": {}
        }
    
    def create_new_project(self, name="New Project"):
        """Create a new project"""
        try:
            # Clear current project
            self.main_editor.engine.scenes.clear()
            
            # Create default scene
            default_scene = self.main_editor.engine.create_scene("Main")
            self.main_editor.engine.current_scene = default_scene
            
            # Reset project state
            self.main_editor.current_project_path = None
            self.main_editor.project_modified = False
            
            # Update UI
            self.main_editor.refresh_hierarchy()
            self.main_editor.update_status(f"New project '{name}' created")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Project Error", f"Failed to create new project: {e}")
            return False
    
    def save_project(self, file_path, project_data=None):
        """Save project to file"""
        try:
            if project_data is None:
                project_data = self.get_project_data()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save project file
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {e}")
            return False
    
    def load_project(self, file_path):
        """Load project from file"""
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            
            # Validate project data
            if not self.validate_project_data(project_data):
                raise ValueError("Invalid project file format")
            
            # Load project into engine
            self.load_project_data(project_data)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")
            return False
    
    def get_project_data(self):
        """Get current project data"""
        project_data = self.project_template.copy()
        
        # Update with current engine state
        project_data["scenes"] = {}
        for scene_name, scene in self.main_editor.engine.scenes.items():
            project_data["scenes"][scene_name] = scene.serialize()
        
        # Add current scripts
        if hasattr(self.main_editor, 'script_editor'):
            script_content = self.main_editor.script_editor.get_script_content()
            if script_content.strip():
                project_data["scripts"]["main"] = script_content
        
        return project_data
    
    def load_project_data(self, project_data):
        """Load project data into engine"""
        # Clear current state
        self.main_editor.engine.scenes.clear()
        
        # Load scenes
        scenes_data = project_data.get("scenes", {})
        for scene_name, scene_data in scenes_data.items():
            scene = self.main_editor.engine.create_scene(scene_name)
            scene.deserialize(scene_data)
        
        # Set first scene as current
        if self.main_editor.engine.scenes:
            first_scene_name = next(iter(self.main_editor.engine.scenes.keys()))
            self.main_editor.engine.current_scene = self.main_editor.engine.scenes[first_scene_name]
        
        # Load scripts
        scripts_data = project_data.get("scripts", {})
        if "main" in scripts_data and hasattr(self.main_editor, 'script_editor'):
            self.main_editor.script_editor.set_script_content(scripts_data["main"])
        
        # Apply settings
        settings = project_data.get("settings", {})
        if "physics_enabled" in settings:
            self.main_editor.engine.physics.enable_physics(settings["physics_enabled"])
        
        if "gravity" in settings:
            gravity = settings["gravity"]
            self.main_editor.engine.physics.set_gravity(gravity[0], gravity[1])
        
        # Update UI
        self.main_editor.refresh_hierarchy()
        self.main_editor.project_modified = False
    
    def validate_project_data(self, project_data):
        """Validate project data structure"""
        required_fields = ["engine_version", "scenes"]
        
        for field in required_fields:
            if field not in project_data:
                return False
        
        # Check engine version compatibility
        engine_version = project_data.get("engine_version", "0.0")
        if not self.is_version_compatible(engine_version):
            return False
        
        return True
    
    def is_version_compatible(self, version):
        """Check if project version is compatible with current engine"""
        # Simple version check - for now, accept any version
        return True
    
    def export_project(self, file_path, format="json"):
        """Export project in specified format"""
        try:
            project_data = self.get_project_data()
            
            if format.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export project: {e}")
            return False
    
    def import_project(self, file_path, format="json"):
        """Import project from specified format"""
        try:
            if format.lower() == "json":
                return self.load_project(file_path)
            else:
                raise ValueError(f"Unsupported import format: {format}")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import project: {e}")
            return False
    
    def get_recent_projects(self):
        """Get list of recently opened projects"""
        # TODO: Implement recent projects tracking
        return []
    
    def add_to_recent_projects(self, file_path):
        """Add project to recent projects list"""
        # TODO: Implement recent projects tracking
        pass
    
    def create_project_backup(self, project_path):
        """Create a backup of the current project"""
        try:
            backup_path = project_path + ".backup"
            project_data = self.get_project_data()
            
            with open(backup_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to create backup: {e}")
            return False
    
    def get_project_info(self, file_path):
        """Get basic information about a project file"""
        try:
            with open(file_path, 'r') as f:
                project_data = json.load(f)
            
            return {
                "name": project_data.get("name", "Unknown"),
                "version": project_data.get("version", "Unknown"),
                "engine_version": project_data.get("engine_version", "Unknown"),
                "scene_count": len(project_data.get("scenes", {})),
                "created": project_data.get("created", "Unknown"),
                "modified": project_data.get("modified", "Unknown")
            }
            
        except Exception as e:
            return None
    
    def cleanup_project_temp_files(self, project_path):
        """Clean up temporary files for a project"""
        try:
            # Remove backup files older than 7 days
            backup_path = project_path + ".backup"
            if os.path.exists(backup_path):
                stat = os.stat(backup_path)
                age_days = (time.time() - stat.st_mtime) / (24 * 3600)
                if age_days > 7:
                    os.remove(backup_path)
            
            return True
            
        except Exception as e:
            print(f"Failed to cleanup temp files: {e}")
            return False
