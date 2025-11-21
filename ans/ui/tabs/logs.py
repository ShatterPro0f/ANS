"""
Logs Tab for the ANS application.

This module provides the Logs tab where users can view application and project logs.
"""
from PyQt5 import QtWidgets


def create_logs_tab(main_window, signal_broker):
    """Create and configure the Logs tab.
    
    This tab displays:
    - Application logs when no project is loaded
    - Project-specific logs when a project is active
    
    Args:
        main_window: Reference to the main ANSWindow instance
        signal_broker: SignalBroker instance for signal connections
        
    Returns:
        tuple: (tab_widget, references_dict) where references_dict contains:
            - 'logs_text_edit': QTextEdit for displaying logs
    """
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    
    # Create logs text edit
    logs_text_edit = QtWidgets.QTextEdit()
    logs_text_edit.setReadOnly(True)
    logs_text_edit.setPlaceholderText("Application logs will appear here...")
    
    # Initial message
    logs_text_edit.setText("No project loaded. Application logs:\n\n")
    logs_text_edit.append("ANS (Automated Novel System) initialized.")
    logs_text_edit.append("Load or create a project to begin.")
    
    layout.addWidget(logs_text_edit)
    
    # Return tab and widget references
    references = {
        'logs_text_edit': logs_text_edit
    }
    
    return tab, references


def update_logs(logs_text_edit, log_message):
    """Update logs display with new message.
    
    Args:
        logs_text_edit: QTextEdit widget to update
        log_message: Log message to append
    """
    if logs_text_edit:
        logs_text_edit.append(log_message)
        # Auto-scroll to bottom
        cursor = logs_text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        logs_text_edit.setTextCursor(cursor)
