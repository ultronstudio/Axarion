"""
Axarion Engine File Manager
Utility functions for file operations and project management
"""

import os
import json
import shutil
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

class FileManagerError(Exception):
    """Custom exception for file manager errors"""
    pass

class FileManager:
    """Utility class for file operations in Axarion Engine"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.project_extensions = [".axp", ".json"]
        self.script_extensions = [".py", ".txt"]
        self.supported_formats = {
            "project": [".axp", ".json"],
            "script": [".py", ".txt"],
            "image": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
            "audio": [".wav", ".mp3", ".ogg", ".m4a"]
        }
    
    def create_directory(self, path: str) -> bool:
        """Create directory if it doesn't exist"""
        try:
            full_path = self.base_path / path
            full_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to create directory '{path}': {e}")
    
    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """Delete directory"""
        try:
            full_path = self.base_path / path
            if not full_path.exists():
                return True
            
            if recursive:
                shutil.rmtree(full_path)
            else:
                full_path.rmdir()
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to delete directory '{path}': {e}")
    
    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read text file content"""
        try:
            full_path = self.base_path / file_path
            with open(full_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise FileManagerError(f"Failed to read file '{file_path}': {e}")
    
    def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """Write content to text file"""
        try:
            full_path = self.base_path / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to write file '{file_path}': {e}")
    
    def read_json(self, file_path: str) -> Dict[str, Any]:
        """Read JSON file"""
        try:
            content = self.read_file(file_path)
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise FileManagerError(f"Invalid JSON in file '{file_path}': {e}")
        except Exception as e:
            raise FileManagerError(f"Failed to read JSON file '{file_path}': {e}")
    
    def write_json(self, file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """Write data to JSON file"""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return self.write_file(file_path, content)
        except Exception as e:
            raise FileManagerError(f"Failed to write JSON file '{file_path}': {e}")
    
    def copy_file(self, source: str, destination: str) -> bool:
        """Copy file from source to destination"""
        try:
            src_path = self.base_path / source
            dst_path = self.base_path / destination
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to copy file '{source}' to '{destination}': {e}")
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move file from source to destination"""
        try:
            src_path = self.base_path / source
            dst_path = self.base_path / destination
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to move file '{source}' to '{destination}': {e}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to delete file '{file_path}': {e}")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = self.base_path / file_path
        return full_path.exists() and full_path.is_file()
    
    def directory_exists(self, dir_path: str) -> bool:
        """Check if directory exists"""
        full_path = self.base_path / dir_path
        return full_path.exists() and full_path.is_dir()
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            full_path = self.base_path / file_path
            return full_path.stat().st_size
        except Exception as e:
            raise FileManagerError(f"Failed to get size of file '{file_path}': {e}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            full_path = self.base_path / file_path
            stat = full_path.stat()
            
            return {
                "name": full_path.name,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir(),
                "extension": full_path.suffix,
                "absolute_path": str(full_path)
            }
        except Exception as e:
            raise FileManagerError(f"Failed to get info for '{file_path}': {e}")
    
    def list_files(self, directory: str = ".", pattern: str = "*", 
                   recursive: bool = False) -> List[str]:
        """List files in directory"""
        try:
            dir_path = self.base_path / directory
            
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            # Convert to relative paths and filter files only
            result = []
            for file_path in files:
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_path)
                    result.append(str(relative_path))
            
            return sorted(result)
        except Exception as e:
            raise FileManagerError(f"Failed to list files in '{directory}': {e}")
    
    def list_directories(self, directory: str = ".") -> List[str]:
        """List directories"""
        try:
            dir_path = self.base_path / directory
            
            directories = [d for d in dir_path.iterdir() if d.is_dir()]
            result = []
            
            for dir_path in directories:
                relative_path = dir_path.relative_to(self.base_path)
                result.append(str(relative_path))
            
            return sorted(result)
        except Exception as e:
            raise FileManagerError(f"Failed to list directories in '{directory}': {e}")
    
    def find_files(self, pattern: str, directory: str = ".", 
                   file_type: Optional[str] = None) -> List[str]:
        """Find files matching pattern"""
        try:
            files = self.list_files(directory, pattern, recursive=True)
            
            if file_type and file_type in self.supported_formats:
                extensions = self.supported_formats[file_type]
                files = [f for f in files if any(f.endswith(ext) for ext in extensions)]
            
            return files
        except Exception as e:
            raise FileManagerError(f"Failed to find files with pattern '{pattern}': {e}")
    
    def get_file_hash(self, file_path: str, algorithm: str = "md5") -> str:
        """Calculate file hash"""
        try:
            full_path = self.base_path / file_path
            
            hash_func = getattr(hashlib, algorithm)()
            
            with open(full_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
        except Exception as e:
            raise FileManagerError(f"Failed to calculate hash for '{file_path}': {e}")
    
    def backup_file(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """Create backup of file"""
        try:
            backup_path = file_path + backup_suffix
            self.copy_file(file_path, backup_path)
            return backup_path
        except Exception as e:
            raise FileManagerError(f"Failed to backup file '{file_path}': {e}")
    
    def restore_backup(self, backup_path: str) -> str:
        """Restore file from backup"""
        try:
            if not backup_path.endswith(".backup"):
                raise ValueError("Not a backup file")
            
            original_path = backup_path[:-7]  # Remove .backup suffix
            self.copy_file(backup_path, original_path)
            return original_path
        except Exception as e:
            raise FileManagerError(f"Failed to restore backup '{backup_path}': {e}")
    
    def create_project_structure(self, project_name: str) -> str:
        """Create standard project directory structure"""
        try:
            project_dir = f"projects/{project_name}"
            
            # Create directories
            directories = [
                project_dir,
                f"{project_dir}/scenes",
                f"{project_dir}/scripts",
                f"{project_dir}/assets",
                f"{project_dir}/assets/images",
                f"{project_dir}/assets/audio"
            ]
            
            for directory in directories:
                self.create_directory(directory)
            
            # Create default project file
            project_data = {
                "name": project_name,
                "version": "1.0",
                "engine_version": "1.0",
                "scenes": {},
                "assets": [],
                "scripts": {}
            }
            
            project_file = f"{project_dir}/{project_name}.axp"
            self.write_json(project_file, project_data)
            
            return project_dir
        except Exception as e:
            raise FileManagerError(f"Failed to create project structure for '{project_name}': {e}")
    
    def validate_project_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate project file format"""
        errors = []
        
        try:
            if not self.file_exists(file_path):
                errors.append("Project file does not exist")
                return False, errors
            
            data = self.read_json(file_path)
            
            # Check required fields
            required_fields = ["name", "engine_version", "scenes"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
            
            # Validate scenes structure
            if "scenes" in data:
                if not isinstance(data["scenes"], dict):
                    errors.append("Scenes must be a dictionary")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Failed to validate project file: {e}")
            return False, errors
    
    def clean_temp_files(self, directory: str = ".", max_age_days: int = 7):
        """Clean up temporary files older than specified days"""
        try:
            import time
            
            temp_patterns = ["*.tmp", "*.temp", "*~", "*.backup"]
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            for pattern in temp_patterns:
                files = self.list_files(directory, pattern, recursive=True)
                
                for file_path in files:
                    full_path = self.base_path / file_path
                    file_age = current_time - full_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        self.delete_file(file_path)
                        print(f"Cleaned up old temporary file: {file_path}")
            
        except Exception as e:
            print(f"Warning: Failed to clean temp files: {e}")
    
    def get_project_files(self, directory: str = ".") -> List[str]:
        """Get all project files in directory"""
        project_files = []
        for ext in self.project_extensions:
            files = self.find_files(f"*{ext}", directory)
            project_files.extend(files)
        return project_files
    
    def get_script_files(self, directory: str = ".") -> List[str]:
        """Get all script files in directory"""
        script_files = []
        for ext in self.script_extensions:
            files = self.find_files(f"*{ext}", directory)
            script_files.extend(files)
        return script_files
    
    def export_project_archive(self, project_path: str, output_path: str) -> bool:
        """Export project as archive"""
        try:
            import zipfile
            
            project_dir = self.base_path / project_path
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_dir)
                        zipf.write(file_path, arcname)
            
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to export project archive: {e}")
    
    def import_project_archive(self, archive_path: str, destination: str) -> bool:
        """Import project from archive"""
        try:
            import zipfile
            
            dest_path = self.base_path / destination
            dest_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(dest_path)
            
            return True
        except Exception as e:
            raise FileManagerError(f"Failed to import project archive: {e}")
