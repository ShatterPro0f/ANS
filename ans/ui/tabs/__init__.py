"""
Tab modules for the ANS application.

Each module exports a create_<name>_tab(main_window, signal_broker) function
that returns (tab_widget, references_dict).
"""

# Import all tab creation functions for easy access
from ans.ui.tabs.initialization import create_initialization_tab
from ans.ui.tabs.novel_idea import create_novel_idea_tab
from ans.ui.tabs.planning import create_planning_tab
from ans.ui.tabs.writing import create_writing_tab
from ans.ui.tabs.logs import create_logs_tab
from ans.ui.tabs.dashboard import create_dashboard_tab
from ans.ui.tabs.settings import create_settings_tab

__all__ = [
    'create_initialization_tab',
    'create_novel_idea_tab',
    'create_planning_tab',
    'create_writing_tab',
    'create_logs_tab',
    'create_dashboard_tab',
    'create_settings_tab',
]
