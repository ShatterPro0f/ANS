"""
Constants used throughout the ANS application.

This module centralizes all magic strings, configuration constants, and
default values used in the application.
"""

# Directory paths
PROJECTS_DIR = "projects"
CONFIG_DIR = "Config"
ASSETS_DIR = "assets"
DRAFTS_DIR = "drafts"

# Configuration files
APP_SETTINGS_FILE = "app_settings.txt"
LOG_FILE_PREFIX = "log"

# Project files
PROJECT_FILES = {
    'story': 'story.txt',
    'log': 'log.txt',
    'config': 'config.txt',
    'context': 'context.txt',
    'characters': 'characters.txt',
    'world': 'world.txt',
    'synopsis': 'synopsis.txt',
    'refined_synopsis': 'refined_synopsis.txt',
    'summaries': 'summaries.txt',
    'outline': 'outline.txt',
    'timeline': 'timeline.txt',
    'buffer_backup': 'buffer_backup.txt'
}

# Asset files
LOGO_FILE = "logo.png"
LOGO_LIGHT_FILE = "logo_light.png"
LOGO_DARK_FILE = "logo_dark.png"

# LLM defaults
DEFAULT_LLM_MODEL = "gemma3:12b"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_RETRIES = 3

# Generation defaults
DEFAULT_DETAIL_LEVEL = "balanced"
DEFAULT_CHARACTER_DEPTH = "standard"
DEFAULT_WORLD_DEPTH = "standard"
DEFAULT_QUALITY_CHECK = "moderate"
DEFAULT_SECTIONS_PER_CHAPTER = 3
DEFAULT_SOFT_TARGET_WORDS = 250000
DEFAULT_TOTAL_CHAPTERS = 25

# Option values
DETAIL_LEVELS = ["concise", "balanced", "detailed"]
CHARACTER_DEPTHS = ["shallow", "standard", "deep"]
WORLD_DEPTHS = ["minimal", "standard", "comprehensive"]
QUALITY_CHECKS = ["strict", "moderate", "lenient"]

# UI constants
WINDOW_TITLE = "Automated Novel System"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
TITLE_BAR_HEIGHT = 32
LOGO_HEIGHT = 80
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 32

# Tab names
TAB_INITIALIZATION = "Initialization"
TAB_NOVEL_IDEA = "Novel Idea"
TAB_PLANNING = "Planning"
TAB_WRITING = "Writing"
TAB_LOGS = "Logs"
TAB_DASHBOARD = "Dashboard"
TAB_SETTINGS = "Settings"

# Progress thresholds
MILESTONE_THRESHOLD = 80  # Percentage
EXTENSION_CHAPTERS = 5
WRAP_UP_CHAPTERS = 2

# Export formats
EXPORT_FORMAT_DOCX = "docx"
EXPORT_FORMAT_PDF = "pdf"

# Settings keys
SETTING_DARK_MODE = "DarkMode"
SETTING_MODEL = "Model"
SETTING_TEMPERATURE = "Temperature"
SETTING_AUTO_SAVE = "AutoSave"
SETTING_NOTIFICATIONS = "Notifications"
SETTING_AUTO_APPROVAL = "AutoApproval"
SETTING_MAX_RETRIES = "MaxRetries"
SETTING_DETAIL_LEVEL = "DetailLevel"
SETTING_CHARACTER_DEPTH = "CharacterDepth"
SETTING_WORLD_DEPTH = "WorldDepth"
SETTING_QUALITY_CHECK = "QualityCheck"
SETTING_SECTIONS_PER_CHAPTER = "SectionsPerChapter"

# Time formats
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Colors (for dark/light mode)
COLOR_DARK_BG = "#1e1e1e"
COLOR_DARK_TEXT = "#e0e0e0"
COLOR_DARK_BUTTON = "#2d2d2d"
COLOR_LIGHT_BG = "#ffffff"
COLOR_LIGHT_TEXT = "#000000"
COLOR_LIGHT_BUTTON = "#f0f0f0"
COLOR_CLOSE_HOVER = "#e81123"
COLOR_CLOSE_PRESSED = "#c41410"

# Content types (for approve/adjust signals)
CONTENT_TYPE_SYNOPSIS = "synopsis"
CONTENT_TYPE_OUTLINE = "outline"
CONTENT_TYPE_CHARACTERS = "characters"
CONTENT_TYPE_WORLD = "world"
CONTENT_TYPE_TIMELINE = "timeline"
CONTENT_TYPE_SECTION = "section"

# Log messages
LOG_PROJECT_CREATED = "Project created: {}"
LOG_PROJECT_LOADED = "Project loaded: {}"
LOG_LLM_CONNECTION_SUCCESS = "LLM connection successful ({})"
LOG_LLM_CONNECTION_FAILED = "LLM connection failed: {}"
LOG_NOVEL_GENERATION_STARTED = "Novel generation started with config: {}"
LOG_GENERATION_COMPLETE = "Novel generation complete"
LOG_SECTION_APPROVED = "Section {} of Chapter {} approved and processed ({} words)"
LOG_CHAPTER_COMPLETE = "Chapter {} complete! Moving to Chapter {}"
LOG_NOVEL_COMPLETE = "=== NOVEL COMPLETE ==="

# File encoding
FILE_ENCODING = "utf-8"

# Backup settings
BACKUP_INTERVAL_HOURS = 1
MAX_LOG_FILES = 5
MAX_LOG_SIZE_MB = 10
