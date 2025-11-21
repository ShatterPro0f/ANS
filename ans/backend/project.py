"""
Project management for the ANS application.

This module provides the ProjectManager class for handling all project-related
file I/O operations, including creation, loading, and persistence.
"""
import os
import json
import datetime
import threading
from typing import Dict, Any, Optional, List

from ans.utils.constants import (
    PROJECTS_DIR,
    PROJECT_FILES,
    DRAFTS_DIR,
    FILE_ENCODING,
    TIMESTAMP_FORMAT
)


class ProjectManager:
    """Manages project file operations with thread-safe locking."""
    
    def __init__(self):
        """Initialize project manager."""
        self._file_locks: Dict[str, threading.Lock] = {}
        self._lock_registry_lock = threading.Lock()
    
    def _get_file_lock(self, filepath: str) -> threading.Lock:
        """Get or create a lock for a specific file.
        
        Args:
            filepath: Absolute path to file
            
        Returns:
            threading.Lock for the file
        """
        with self._lock_registry_lock:
            if filepath not in self._file_locks:
                self._file_locks[filepath] = threading.Lock()
            return self._file_locks[filepath]
    
    def read_file(self, filepath: str) -> str:
        """Read file content safely with locking.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content as string, or error message
        """
        try:
            lock = self._get_file_lock(filepath)
            with lock:
                with open(filepath, 'r', encoding=FILE_ENCODING) as f:
                    return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to file safely with locking.
        
        Args:
            filepath: Path to file
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            lock = self._get_file_lock(filepath)
            with lock:
                with open(filepath, 'w', encoding=FILE_ENCODING) as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False
    
    def append_file(self, filepath: str, content: str) -> bool:
        """Append content to file safely with locking.
        
        Args:
            filepath: Path to file
            content: Content to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            lock = self._get_file_lock(filepath)
            with lock:
                with open(filepath, 'a', encoding=FILE_ENCODING) as f:
                    f.write(content)
            return True
        except Exception as e:
            print(f"Error appending to file: {str(e)}")
            return False
    
    def create_project_structure(self, project_name: str) -> str:
        """Create project directory structure and files.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Full path to created project directory
        """
        # Create projects folder and project directory
        os.makedirs(PROJECTS_DIR, exist_ok=True)
        full_project_path = os.path.join(PROJECTS_DIR, project_name)
        os.makedirs(full_project_path, exist_ok=True)
        
        # Create drafts folder
        os.makedirs(os.path.join(full_project_path, DRAFTS_DIR), exist_ok=True)
        
        # List of project-specific files to create (empty)
        empty_files = [
            PROJECT_FILES['story'],
            PROJECT_FILES['config'],
            PROJECT_FILES['context'],
            PROJECT_FILES['buffer_backup']
        ]
        
        # Create empty text files
        for filename in empty_files:
            filepath = os.path.join(full_project_path, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding=FILE_ENCODING) as f:
                    pass
        
        # Create empty JSON files
        json_files = [PROJECT_FILES['characters'], PROJECT_FILES['world']]
        for filename in json_files:
            filepath = os.path.join(full_project_path, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding=FILE_ENCODING) as f:
                    pass
        
        # Create progress tracking file
        progress_file = os.path.join(full_project_path, 'progress.json')
        if not os.path.exists(progress_file):
            with open(progress_file, 'w', encoding=FILE_ENCODING) as f:
                json.dump({}, f, indent=2)
        
        # Create summaries.txt (empty)
        summaries_file = os.path.join(full_project_path, PROJECT_FILES['summaries'])
        if not os.path.exists(summaries_file):
            with open(summaries_file, 'w', encoding=FILE_ENCODING) as f:
                pass
        
        return full_project_path
    
    def load_project(self, project_name: str) -> Dict[str, Any]:
        """Load an existing project into memory.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary containing project data
            
        Raises:
            FileNotFoundError: If project or required files don't exist
        """
        project_path = os.path.join(PROJECTS_DIR, project_name)
        
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project '{project_name}' not found at {project_path}")
        
        # Verify all required project files exist
        required_files = [
            PROJECT_FILES['story'],
            PROJECT_FILES['config'],
            PROJECT_FILES['context'],
            PROJECT_FILES['characters'],
            PROJECT_FILES['world'],
            PROJECT_FILES['summaries'],
            PROJECT_FILES['buffer_backup']
        ]
        
        for filename in required_files:
            filepath = os.path.join(project_path, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Project file missing: {filename}")
        
        # Load and store project data in memory
        project_data = {
            'name': project_name,
            'path': project_path,
            'story': self.read_file(os.path.join(project_path, PROJECT_FILES['story'])),
            'config': self.read_file(os.path.join(project_path, PROJECT_FILES['config'])),
            'context': self.read_file(os.path.join(project_path, PROJECT_FILES['context'])),
            'characters': self.read_file(os.path.join(project_path, PROJECT_FILES['characters'])),
            'world': self.read_file(os.path.join(project_path, PROJECT_FILES['world'])),
            'summaries': self.read_file(os.path.join(project_path, PROJECT_FILES['summaries'])),
            'buffer_backup': self.read_file(os.path.join(project_path, PROJECT_FILES['buffer_backup']))
        }
        
        # Load progress tracking if it exists
        progress_file = os.path.join(project_path, 'progress.json')
        try:
            with open(progress_file, 'r', encoding=FILE_ENCODING) as f:
                project_data['progress'] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            project_data['progress'] = {}
        
        return project_data
    
    def get_project_list(self) -> List[str]:
        """Get list of all existing projects.
        
        Returns:
            Sorted list of project names
        """
        if not os.path.exists(PROJECTS_DIR):
            return []
        
        projects = []
        for item in os.listdir(PROJECTS_DIR):
            item_path = os.path.join(PROJECTS_DIR, item)
            if os.path.isdir(item_path):
                projects.append(item)
        
        return sorted(projects)
    
    def save_progress(self, project_path: str, stage: str, status: str) -> bool:
        """Save progress tracking to project.
        
        Args:
            project_path: Path to project directory
            stage: Stage name ('synopsis', 'outline', etc.)
            status: Status string ('completed', 'approved', etc.)
            
        Returns:
            True if successful, False otherwise
        """
        progress_file = os.path.join(project_path, 'progress.json')
        
        # Load existing progress or create new
        try:
            with open(progress_file, 'r', encoding=FILE_ENCODING) as f:
                progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            progress = {}
        
        # Update stage status
        progress[stage] = {
            'status': status,
            'timestamp': datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        }
        
        # Save progress file
        try:
            with open(progress_file, 'w', encoding=FILE_ENCODING) as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Warning: Could not save progress: {str(e)}")
            return False
    
    def load_progress(self, project_path: str) -> Dict[str, Any]:
        """Load progress tracking from project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Progress dictionary
        """
        progress_file = os.path.join(project_path, 'progress.json')
        
        try:
            with open(progress_file, 'r', encoding=FILE_ENCODING) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


# Singleton instance for easy access
_project_manager_instance: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    """Get or create the singleton ProjectManager instance.
    
    Returns:
        ProjectManager instance
    """
    global _project_manager_instance
    if _project_manager_instance is None:
        _project_manager_instance = ProjectManager()
    return _project_manager_instance
