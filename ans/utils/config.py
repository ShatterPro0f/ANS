"""
Configuration and logging utilities for the ANS application.

This module provides functions for:
- Application configuration initialization
- Settings persistence (load/save)
- Rotating log system
"""
import os
import datetime
from typing import Dict, Any, Optional

from ans.utils.constants import (
    CONFIG_DIR,
    APP_SETTINGS_FILE,
    LOG_FILE_PREFIX,
    MAX_LOG_FILES,
    FILE_ENCODING,
    TIMESTAMP_FORMAT,
    # Settings keys
    SETTING_DARK_MODE,
    SETTING_MODEL,
    SETTING_TEMPERATURE,
    SETTING_AUTO_SAVE,
    SETTING_NOTIFICATIONS,
    SETTING_AUTO_APPROVAL,
    SETTING_MAX_RETRIES,
    SETTING_DETAIL_LEVEL,
    SETTING_CHARACTER_DEPTH,
    SETTING_WORLD_DEPTH,
    SETTING_QUALITY_CHECK,
    SETTING_SECTIONS_PER_CHAPTER
)


class ConfigManager:
    """Manages application configuration and logging."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.current_app_log = None
        self._initialize_app_config()
    
    def _initialize_app_config(self):
        """Create app-level settings and config directory if they don't exist."""
        # Create app config folder for application-wide settings
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Create app settings file
        app_settings_path = os.path.join(CONFIG_DIR, APP_SETTINGS_FILE)
        if not os.path.exists(app_settings_path):
            with open(app_settings_path, 'w', encoding=FILE_ENCODING) as f:
                pass
        
        # Initialize rotating log system (log1.txt through log5.txt)
        self._rotate_app_logs()
    
    def _rotate_app_logs(self):
        """Rotate application logs using a 5-file system (log1.txt through log5.txt).
        
        On each startup, this method:
        1. Determines which log file to use next (oldest/least recently modified)
        2. Clears that log file (effectively reusing it)
        3. Stores the current log file number for this session
        
        This keeps the log directory clean and prevents needing to scroll through
        months/years of history when debugging current issues.
        """
        log_files = [os.path.join(CONFIG_DIR, f'{LOG_FILE_PREFIX}{i}.txt') 
                     for i in range(1, MAX_LOG_FILES + 1)]
        
        # Create all log files if they don't exist
        for log_file in log_files:
            if not os.path.exists(log_file):
                with open(log_file, 'w', encoding=FILE_ENCODING) as f:
                    pass
        
        # Find the oldest log file (least recently modified)
        oldest_log = min(log_files, key=lambda f: os.path.getmtime(f))
        
        # Clear the oldest log file for fresh session logging
        with open(oldest_log, 'w', encoding=FILE_ENCODING) as f:
            pass
        
        # Store current log file path for this session
        self.current_app_log = oldest_log
        
        # Touch the file to update modification time for next rotation
        os.utime(oldest_log, None)
    
    def write_app_log(self, message: str):
        """Write message to current rotating app log file.
        
        Args:
            message: Log message to write
        """
        try:
            if self.current_app_log:
                log_entry = f"{datetime.datetime.now().strftime(TIMESTAMP_FORMAT)} - {message}\n"
                with open(self.current_app_log, 'a', encoding=FILE_ENCODING) as f:
                    f.write(log_entry)
        except Exception as e:
            print(f"Failed to write to app log: {str(e)}")
    
    def load_settings(self) -> Dict[str, Any]:
        """Load application settings from config file.
        
        Returns:
            Dict containing all settings with their values
        """
        settings = {}
        try:
            config_path = os.path.join(CONFIG_DIR, APP_SETTINGS_FILE)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding=FILE_ENCODING) as f:
                    lines = f.readlines()
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Convert values to appropriate types
                            if key == SETTING_DARK_MODE or key == SETTING_NOTIFICATIONS or key == SETTING_AUTO_APPROVAL:
                                settings[key] = value == 'True'
                            elif key == SETTING_TEMPERATURE:
                                settings[key] = float(value)
                            elif key == SETTING_AUTO_SAVE or key == SETTING_MAX_RETRIES or key == SETTING_SECTIONS_PER_CHAPTER:
                                settings[key] = int(value)
                            else:
                                settings[key] = value
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return settings
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save application settings to config file.
        
        Args:
            settings: Dictionary of settings to save
        """
        try:
            # Create Config directory if it doesn't exist
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            config_path = os.path.join(CONFIG_DIR, APP_SETTINGS_FILE)
            
            # Format settings for writing
            lines = []
            for key, value in settings.items():
                lines.append(f"{key}: {value}\n")
            
            with open(config_path, 'w', encoding=FILE_ENCODING) as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error saving settings: {e}")


# Singleton instance for easy access
_config_manager_instance: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the singleton ConfigManager instance.
    
    Returns:
        ConfigManager instance
    """
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance


def initialize_app_config():
    """Initialize application configuration (convenience function)."""
    get_config_manager()


def write_app_log(message: str):
    """Write to app log (convenience function).
    
    Args:
        message: Log message to write
    """
    get_config_manager().write_app_log(message)


def load_settings() -> Dict[str, Any]:
    """Load settings (convenience function).
    
    Returns:
        Dictionary of settings
    """
    return get_config_manager().load_settings()


def save_settings(settings: Dict[str, Any]):
    """Save settings (convenience function).
    
    Args:
        settings: Dictionary of settings to save
    """
    get_config_manager().save_settings(settings)
