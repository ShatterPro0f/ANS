"""
ANS (Automated Novel System) - AI-Powered Creative Writing Assistant

A PyQt5-based desktop application for automated novel generation and management.
"""

__version__ = '1.0.0'
__author__ = 'ANS Development Team'
__description__ = 'Automated Novel System - AI-Powered Creative Writing Assistant'

# Package imports for easy access
from ans.signals import SignalBroker

# Utility imports
from ans.utils.constants import (
    DEFAULT_LLM_MODEL,
    WINDOW_TITLE,
    PROJECT_FILES
)

from ans.utils.config import (
    get_config_manager,
    initialize_app_config,
    write_app_log,
    load_settings,
    save_settings
)

from ans.backend.project import get_project_manager
from ans.backend.llm import generate_with_retry, test_llm_connection

__all__ = [
    '__version__',
    '__author__',
    '__description__',
    'SignalBroker',
    'get_config_manager',
    'get_project_manager',
    'generate_with_retry',
    'test_llm_connection',
]
