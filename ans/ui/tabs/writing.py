"""
Writing Tab module for the ANS application.

This tab handles draft generation and section approval workflow.
"""
from PyQt5 import QtWidgets, QtCore


def create_writing_tab(main_window, signal_broker):
    """
    Create the Writing tab for draft review and section management.
    
    Args:
        main_window: Reference to ANSWindow instance
        signal_broker: SignalBroker for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """

        """Create Writing tab with draft display and section approval/adjustment controls."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # ===== Draft Display Section =====
        draft_group = QtWidgets.QGroupBox("Current Section Draft")
        draft_layout = QtWidgets.QVBoxLayout()
        
        # Expand button for draft
        draft_expand_btn = QtWidgets.QPushButton("Expand")
        draft_expand_btn.setMaximumWidth(100)
        draft_expand_btn.clicked.connect(lambda: _expand_text_window("draft_display"))
        draft_layout.addWidget(draft_expand_btn)
        
        draft_display = QtWidgets.QTextEdit()
        draft_display.setReadOnly(True)
        draft_display.setPlaceholderText("Draft sections will appear here as they are generated...")
        draft_display.setMinimumHeight(300)
        draft_layout.addWidget(draft_display)
        
        draft_group.setLayout(draft_layout)
        layout.addWidget(draft_group)
        
        # ===== Section Action Buttons =====
        section_buttons_layout = QtWidgets.QHBoxLayout()
        
        section_label = QtWidgets.QLabel("Section Actions:")
        section_buttons_layout.addWidget(section_label)
        
        approve_section_button = QtWidgets.QPushButton("Approve Section")
        approve_section_button.setMinimumHeight(40)
        approve_section_button.setMaximumWidth(150)
        approve_section_button.setEnabled(False)
        approve_section_button.clicked.connect(_on_approve_section)
        section_buttons_layout.addWidget(approve_section_button)
        
        adjust_section_button = QtWidgets.QPushButton("Adjust Section")
        adjust_section_button.setMinimumHeight(40)
        adjust_section_button.setMaximumWidth(150)
        adjust_section_button.setEnabled(False)
        adjust_section_button.clicked.connect(_on_adjust_section)
        section_buttons_layout.addWidget(adjust_section_button)
        
        pause_button = QtWidgets.QPushButton("Pause")
        pause_button.setMinimumHeight(40)
        pause_button.setMaximumWidth(100)
        pause_button.setEnabled(False)
        pause_button.clicked.connect(_on_pause_generation)
        section_buttons_layout.addWidget(pause_button)
        
        resume_button = QtWidgets.QPushButton("Resume")
        resume_button.setMinimumHeight(40)
        resume_button.setMaximumWidth(100)
        resume_button.setEnabled(False)
        resume_button.setVisible(False)
        resume_button.clicked.connect(_on_resume_generation)
        section_buttons_layout.addWidget(resume_button)
        
        section_buttons_layout.addStretch()
        layout.addLayout(section_buttons_layout)
        
        layout.addStretch()
        
        return tab
    
    
    references = {
        'draft_display': draft_display,
        'approve_section_button': approve_section_button,
        'adjust_section_button': adjust_section_button,
        'pause_button': pause_button,
        'resume_button': resume_button,
    }
    
    return tab, references
