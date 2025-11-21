"""
Initialization Tab module for the ANS application.

This tab handles project creation and loading functionality.
"""
from PyQt5 import QtWidgets, QtCore
from ans.utils.constants import PROJECTS_DIR


def create_initialization_tab(main_window, signal_broker):
    """
    Create the Initialization tab.
    
    Args:
        main_window: Reference to ANSWindow instance
        signal_broker: SignalBroker for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    
    # Add logo at top if available
    try:
        import os
        logo_path = os.path.join('assets', 'logo.png')
        if os.path.exists(logo_path):
            logo_layout = QtWidgets.QVBoxLayout()
            logo_label = QtWidgets.QLabel()
            pixmap = QtWidgets.QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToHeight(80, QtCore.Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(QtCore.Qt.AlignCenter)
            logo_layout.addWidget(logo_label)
            
            # Add title and subtitle
            title_label = QtWidgets.QLabel("Automated Novel System")
            title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #1a2f4d;")
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            logo_layout.addWidget(title_label)
            
            subtitle_label = QtWidgets.QLabel("AI-Powered Creative Writing Assistant")
            subtitle_label.setStyleSheet("font-size: 11pt; color: #666;")
            subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
            logo_layout.addWidget(subtitle_label)
            
            # Add separator
            separator = QtWidgets.QFrame()
            separator.setFrameShape(QtWidgets.QFrame.HLine)
            separator.setFrameShadow(QtWidgets.QFrame.Sunken)
            logo_layout.addWidget(separator)
            
            layout.addLayout(logo_layout)
    except Exception as e:
        pass  # Logo display is optional
    
    # Project Creation Group
    create_group = QtWidgets.QGroupBox("Create New Project")
    create_layout = QtWidgets.QVBoxLayout()
    
    project_name_label = QtWidgets.QLabel("Project Name:")
    create_layout.addWidget(project_name_label)
    
    project_name_input = QtWidgets.QLineEdit()
    project_name_input.setPlaceholderText("Enter project name (e.g., MyNovel)")
    create_layout.addWidget(project_name_input)
    
    create_button = QtWidgets.QPushButton("Create Project")
    create_layout.addWidget(create_button)
    
    create_group.setLayout(create_layout)
    layout.addWidget(create_group)
    
    # Project Loading Group
    load_group = QtWidgets.QGroupBox("Load Existing Project")
    load_layout = QtWidgets.QVBoxLayout()
    
    project_list_label = QtWidgets.QLabel("Select Project:")
    load_layout.addWidget(project_list_label)
    
    project_combo = QtWidgets.QComboBox()
    load_layout.addWidget(project_combo)
    
    refresh_button = QtWidgets.QPushButton("Refresh Project List")
    load_layout.addWidget(refresh_button)
    
    load_button = QtWidgets.QPushButton("Load Project")
    load_layout.addWidget(load_button)
    
    load_group.setLayout(load_layout)
    layout.addWidget(load_group)
    
    # Status Label
    status_label = QtWidgets.QLabel("No project loaded")
    status_label.setWordWrap(True)
    layout.addWidget(status_label)
    
    layout.addStretch()
    tab.setLayout(layout)
    
    # Connect signals
    def _on_create_project():
        project_name = project_name_input.text().strip()
        if not project_name:
            QtWidgets.QMessageBox.warning(tab, "Input Required", "Please enter a project name.")
            return
        
        # Call main window's create project method
        if hasattr(main_window, 'create_project_structure'):
            import os
            project_path = os.path.join(PROJECTS_DIR, project_name)
            if os.path.exists(project_path):
                QtWidgets.QMessageBox.warning(tab, "Project Exists", 
                                             f"Project '{project_name}' already exists.")
                return
            
            success = main_window.create_project_structure(project_path)
            if success:
                project_name_input.clear()
                status_label.setText(f"Project '{project_name}' created successfully!")
                _refresh_project_list()
            else:
                QtWidgets.QMessageBox.critical(tab, "Error", "Failed to create project.")
    
    def _on_load_project():
        project_name = project_combo.currentText()
        if not project_name:
            QtWidgets.QMessageBox.warning(tab, "No Selection", "Please select a project to load.")
            return
        
        # Call main window's load project method
        if hasattr(main_window, 'load_project'):
            success = main_window.load_project(project_name)
            if success:
                status_label.setText(f"Project '{project_name}' loaded successfully!")
            else:
                QtWidgets.QMessageBox.critical(tab, "Error", f"Failed to load project '{project_name}'.")
    
    def _refresh_project_list():
        project_combo.clear()
        if hasattr(main_window, 'get_project_list'):
            projects = main_window.get_project_list()
            project_combo.addItems(projects)
    
    # Connect button clicks
    create_button.clicked.connect(_on_create_project)
    load_button.clicked.connect(_on_load_project)
    refresh_button.clicked.connect(_refresh_project_list)
    
    # Initial population of project list
    _refresh_project_list()
    
    # References for external access
    references = {
        'project_name_input': project_name_input,
        'project_combo': project_combo,
        'status_label': status_label,
        'refresh_list': _refresh_project_list
    }
    
    return tab, references
