"""
Dashboard Tab module for the ANS application.

This tab provides project overview and export functionality.
"""
from PyQt5 import QtWidgets, QtCore


def create_dashboard_tab(main_window, signal_broker):
    """
    Create the Dashboard tab for project status and exports.
    
    Args:
        main_window: Reference to ANSWindow instance
        signal_broker: SignalBroker for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """

        """Create dashboard tab with status and progress indicators."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        
        # Create status group
        status_group = QtWidgets.QGroupBox("Project Status")
        status_layout = QtWidgets.QVBoxLayout()
        
        # Status label
        dashboard_status_label = QtWidgets.QLabel("Status: Not Initialized")
        dashboard_status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(dashboard_status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Create progress group
        progress_group = QtWidgets.QGroupBox("Generation Progress")
        progress_layout = QtWidgets.QVBoxLayout()
        
        # Progress label
        dashboard_progress_label = QtWidgets.QLabel("Progress: 0%")
        dashboard_progress_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        progress_layout.addWidget(dashboard_progress_label)
        
        # Progress bar
        dashboard_progress_bar = QtWidgets.QProgressBar()
        dashboard_progress_bar.setValue(0)
        progress_layout.addWidget(dashboard_progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Create export group
        export_group = QtWidgets.QGroupBox("Export Novel")
        export_layout = QtWidgets.QVBoxLayout()
        
        # Export info label
        export_info = QtWidgets.QLabel("Export your completed novel to document formats:")
        export_layout.addWidget(export_info)
        
        # Button layout for export options
        button_layout = QtWidgets.QHBoxLayout()
        
        # Export to DOCX button
        export_docx_button = QtWidgets.QPushButton("Export to .docx")
        export_docx_button.clicked.connect(_on_export_docx)
        button_layout.addWidget(export_docx_button)
        
        # Export to PDF button
        export_pdf_button = QtWidgets.QPushButton("Export to .pdf")
        export_pdf_button.clicked.connect(_on_export_pdf)
        button_layout.addWidget(export_pdf_button)
        
        export_layout.addLayout(button_layout)
        
        # Export status label
        export_status_label = QtWidgets.QLabel("")
        export_status_label.setStyleSheet("color: #666; font-style: italic;")
        export_layout.addWidget(export_status_label)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Add stretch to fill space
        layout.addStretch()
        
        return tab
    
    
    references = {
        'dashboard_status_label': dashboard_status_label,
        'dashboard_progress_label': dashboard_progress_label,
        'dashboard_progress_bar': dashboard_progress_bar,
        'export_status_label': export_status_label,
    }
    
    return tab, references
