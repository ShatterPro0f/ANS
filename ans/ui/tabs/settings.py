"""
Settings Tab module for the ANS application.

This tab handles application configuration and LLM settings.
"""
from PyQt5 import QtWidgets, QtCore


def create_settings_tab(main_window, signal_broker):
    """
    Create the Settings tab for application configuration.
    
    Args:
        main_window: Reference to ANSWindow instance
        signal_broker: SignalBroker for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """

    """Create settings tab with application-wide configuration options."""
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    
    # ===== Theme Settings Group =====
    theme_group = QtWidgets.QGroupBox("Theme Settings")
    theme_layout = QtWidgets.QVBoxLayout()
    
    # Dark mode toggle
    dark_mode_layout = QtWidgets.QHBoxLayout()
    dark_mode_label = QtWidgets.QLabel("Dark Mode:")
    dark_mode_checkbox = QtWidgets.QCheckBox()
    dark_mode_checkbox.setChecked(False)
    dark_mode_checkbox.stateChanged.connect(_on_dark_mode_toggled)
    dark_mode_layout.addWidget(dark_mode_label)
    dark_mode_layout.addWidget(dark_mode_checkbox)
    dark_mode_layout.addStretch()
    theme_layout.addLayout(dark_mode_layout)
    
    theme_group.setLayout(theme_layout)
    layout.addWidget(theme_group)
    
    # ===== LLM Settings Group =====
    llm_group = QtWidgets.QGroupBox("LLM Configuration")
    llm_layout = QtWidgets.QVBoxLayout()
    
    # Model selection
    model_layout = QtWidgets.QHBoxLayout()
    model_label = QtWidgets.QLabel("Model:")
    model_combo = QtWidgets.QComboBox()
    
    # Auto-detect installed models from Ollama
    _populate_ollama_models()
    
    # Set default model if available
    if model_combo.findText("gemma3:12b") >= 0:
        model_combo.setCurrentText("gemma3:12b")
    elif model_combo.count() > 0:
        model_combo.setCurrentIndex(0)
    
    model_layout.addWidget(model_label)
    model_layout.addWidget(model_combo)
    
    # Add refresh button to re-scan Ollama models
    refresh_models_btn = QtWidgets.QPushButton("Refresh Models")
    refresh_models_btn.setMaximumWidth(120)
    refresh_models_btn.clicked.connect(_refresh_ollama_models)
    model_layout.addWidget(refresh_models_btn)
    
    model_layout.addStretch()
    llm_layout.addLayout(model_layout)
    
    # Temperature slider
    temp_layout = QtWidgets.QHBoxLayout()
    temp_label = QtWidgets.QLabel("Temperature:")
    temperature_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
    temperature_slider.setMinimum(0)
    temperature_slider.setMaximum(100)
    temperature_slider.setValue(70)
    temperature_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
    temperature_slider.setTickInterval(10)
    temperature_value_label = QtWidgets.QLabel("0.70")
    temperature_slider.sliderMoved.connect(_on_temperature_changed)
    temp_layout.addWidget(temp_label)
    temp_layout.addWidget(temperature_slider)
    temp_layout.addWidget(temperature_value_label)
    temp_layout.addWidget(QtWidgets.QLabel("(0.0-1.0)"), 0, QtCore.Qt.AlignmentFlag.AlignRight)
    llm_layout.addLayout(temp_layout)
    
    llm_group.setLayout(llm_layout)
    layout.addWidget(llm_group)
    
    # ===== Application Settings Group =====
    app_group = QtWidgets.QGroupBox("Application")
    app_layout = QtWidgets.QVBoxLayout()
    
    # Auto-save interval
    autosave_layout = QtWidgets.QHBoxLayout()
    autosave_label = QtWidgets.QLabel("Auto-save Interval (minutes):")
    autosave_spinbox = QtWidgets.QSpinBox()
    autosave_spinbox.setMinimum(1)
    autosave_spinbox.setMaximum(60)
    autosave_spinbox.setValue(15)
    autosave_layout.addWidget(autosave_label)
    autosave_layout.addWidget(autosave_spinbox)
    autosave_layout.addStretch()
    app_layout.addLayout(autosave_layout)
    
    # Enable notifications
    notifications_layout = QtWidgets.QHBoxLayout()
    notifications_label = QtWidgets.QLabel("Enable Notifications:")
    notifications_checkbox = QtWidgets.QCheckBox()
    notifications_checkbox.setChecked(True)
    notifications_layout.addWidget(notifications_label)
    notifications_layout.addWidget(notifications_checkbox)
    notifications_layout.addStretch()
    app_layout.addLayout(notifications_layout)
    
    # Auto-approval setting
    autoapproval_layout = QtWidgets.QHBoxLayout()
    autoapproval_label = QtWidgets.QLabel("Auto-approve Content:")
    autoapproval_checkbox = QtWidgets.QCheckBox()
    autoapproval_checkbox.setChecked(False)
    autoapproval_info = QtWidgets.QLabel("(Auto-approves synopsis, outline, sections)")
    autoapproval_info.setStyleSheet("font-style: italic; color: #666;")
    autoapproval_layout.addWidget(autoapproval_label)
    autoapproval_layout.addWidget(autoapproval_checkbox)
    autoapproval_layout.addStretch()
    app_layout.addLayout(autoapproval_layout)
    app_layout.addWidget(autoapproval_info)
    
    app_group.setLayout(app_layout)
    layout.addWidget(app_group)
    
    # ===== Generation Parameters Group =====
    gen_group = QtWidgets.QGroupBox("Generation Parameters")
    gen_layout = QtWidgets.QVBoxLayout()
    
    # Max retries
    retries_layout = QtWidgets.QHBoxLayout()
    retries_label = QtWidgets.QLabel("Max LLM Retries:")
    max_retries_spinbox = QtWidgets.QSpinBox()
    max_retries_spinbox.setMinimum(1)
    max_retries_spinbox.setMaximum(10)
    max_retries_spinbox.setValue(3)
    retries_layout.addWidget(retries_label)
    retries_layout.addWidget(max_retries_spinbox)
    retries_layout.addStretch()
    gen_layout.addLayout(retries_layout)
    
    # Detail level
    detail_layout = QtWidgets.QHBoxLayout()
    detail_label = QtWidgets.QLabel("Detail Level:")
    detail_combo = QtWidgets.QComboBox()
    detail_combo.addItems(["Concise", "Balanced", "Detailed"])
    detail_combo.setCurrentText("Balanced")
    detail_layout.addWidget(detail_label)
    detail_layout.addWidget(detail_combo)
    detail_layout.addStretch()
    gen_layout.addLayout(detail_layout)
    
    # Character depth
    char_layout = QtWidgets.QHBoxLayout()
    char_label = QtWidgets.QLabel("Character Depth:")
    char_depth_combo = QtWidgets.QComboBox()
    char_depth_combo.addItems(["Shallow", "Standard", "Deep"])
    char_depth_combo.setCurrentText("Standard")
    char_layout.addWidget(char_label)
    char_layout.addWidget(char_depth_combo)
    char_layout.addStretch()
    gen_layout.addLayout(char_layout)
    
    # World depth
    world_layout = QtWidgets.QHBoxLayout()
    world_label = QtWidgets.QLabel("World-building Depth:")
    world_depth_combo = QtWidgets.QComboBox()
    world_depth_combo.addItems(["Minimal", "Standard", "Comprehensive"])
    world_depth_combo.setCurrentText("Standard")
    world_layout.addWidget(world_label)
    world_layout.addWidget(world_depth_combo)
    world_layout.addStretch()
    gen_layout.addLayout(world_layout)
    
    # Quality check
    quality_layout = QtWidgets.QHBoxLayout()
    quality_label = QtWidgets.QLabel("Quality Check Level:")
    quality_combo = QtWidgets.QComboBox()
    quality_combo.addItems(["Strict", "Moderate", "Lenient"])
    quality_combo.setCurrentText("Moderate")
    quality_layout.addWidget(quality_label)
    quality_layout.addWidget(quality_combo)
    quality_layout.addStretch()
    gen_layout.addLayout(quality_layout)
    
    # Sections per chapter
    sections_layout = QtWidgets.QHBoxLayout()
    sections_label = QtWidgets.QLabel("Sections Per Chapter:")
    sections_spinbox = QtWidgets.QSpinBox()
    sections_spinbox.setMinimum(1)
    sections_spinbox.setMaximum(10)
    sections_spinbox.setValue(3)
    sections_layout.addWidget(sections_label)
    sections_layout.addWidget(sections_spinbox)
    sections_layout.addStretch()
    gen_layout.addLayout(sections_layout)
    
    gen_group.setLayout(gen_layout)
    layout.addWidget(gen_group)
    
    # ===== Info Group =====
    info_group = QtWidgets.QGroupBox("Application Info")
    info_layout = QtWidgets.QVBoxLayout()
    
    # Version info
    version_label = QtWidgets.QLabel("Version: 1.0.0")
    info_layout.addWidget(version_label)
    
    # About button
    about_button = QtWidgets.QPushButton("About ANS")
    about_button.clicked.connect(_on_about_clicked)
    info_layout.addWidget(about_button)
    
    info_group.setLayout(info_layout)
    layout.addWidget(info_group)
    
    # Add stretch to fill remaining space
    layout.addStretch()
    
    # Load settings from config
    _load_settings()
    
    # Connect change signals to save settings
    model_combo.currentTextChanged.connect(_save_settings)
    autosave_spinbox.valueChanged.connect(_save_settings)
    notifications_checkbox.stateChanged.connect(_save_settings)
    autoapproval_checkbox.stateChanged.connect(_save_settings)
    max_retries_spinbox.valueChanged.connect(_save_settings)
    detail_combo.currentTextChanged.connect(_save_settings)
    char_depth_combo.currentTextChanged.connect(_save_settings)
    world_depth_combo.currentTextChanged.connect(_save_settings)
    quality_combo.currentTextChanged.connect(_save_settings)
    sections_spinbox.valueChanged.connect(_save_settings)
    
    return tab

    references = {
        'dark_mode_checkbox': dark_mode_checkbox,
        'model_combo': model_combo,
        'temperature_slider': temperature_slider,
        'max_retries_spinbox': max_retries_spinbox,
    }

    return tab, references
