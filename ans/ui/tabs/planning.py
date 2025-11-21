"""
Planning Tab module for the ANS application.

This tab handles synopsis, outline, characters, world-building, and timeline management.
Extracted from ans.py _create_planning_tab method.
"""
from PyQt5 import QtWidgets, QtCore


def create_planning_tab(main_window, signal_broker):
    """
    Create the Planning tab with synopsis, outline, characters, world, and timeline displays.
    
    Args:
        main_window: Reference to ANSWindow instance
        signal_broker: SignalBroker for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict)
    """
    """Create Planning tab with initial and refined synopsis displays, outline, and Approve/Adjust buttons."""
    tab = QtWidgets.QWidget()
    main_layout = QtWidgets.QVBoxLayout(tab)
    
    # Create scroll area for content
    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidgetResizable(True)
    
    # Create inner widget for scroll area
    inner_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(inner_widget)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(8)
    
    # Store reference to main layout for expand/collapse
    self.planning_main_layout = layout
    
    # ===== Initial Synopsis Section =====
    initial_synopsis_group = QtWidgets.QGroupBox("Initial Synopsis")
    initial_synopsis_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for initial synopsis
    initial_expand_btn = QtWidgets.QPushButton("Expand")
    initial_expand_btn.setMaximumWidth(100)
    initial_expand_btn.clicked.connect(lambda: self._expand_text_window("synopsis_display"))
    initial_synopsis_layout.addWidget(initial_expand_btn)
    
    self.synopsis_display = QtWidgets.QTextEdit()
    self.synopsis_display.setReadOnly(True)
    self.synopsis_display.setPlaceholderText("Initial generated synopsis will appear here...")
    self.synopsis_display.setMinimumHeight(120)
    self.synopsis_display.setMaximumHeight(200)
    initial_synopsis_layout.addWidget(self.synopsis_display)
    
    # Buttons for initial synopsis (initially disabled - enabled when synopsis is generated)
    initial_synopsis_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.initial_approve_button = QtWidgets.QPushButton("Approve")
    self.initial_approve_button.setMinimumHeight(35)
    self.initial_approve_button.setMaximumWidth(100)
    self.initial_approve_button.setEnabled(False)
    self.initial_approve_button.clicked.connect(self._on_approve_initial_synopsis)
    initial_synopsis_buttons_layout.addWidget(self.initial_approve_button)
    
    self.initial_adjust_button = QtWidgets.QPushButton("Adjust")
    self.initial_adjust_button.setMinimumHeight(35)
    self.initial_adjust_button.setMaximumWidth(100)
    self.initial_adjust_button.setEnabled(False)
    self.initial_adjust_button.clicked.connect(self._on_adjust_initial_synopsis)
    initial_synopsis_buttons_layout.addWidget(self.initial_adjust_button)
    
    initial_synopsis_buttons_layout.addStretch()
    initial_synopsis_layout.addLayout(initial_synopsis_buttons_layout)
    
    initial_synopsis_group.setLayout(initial_synopsis_layout)
    self.initial_synopsis_group = initial_synopsis_group
    layout.addWidget(initial_synopsis_group)
    
    # ===== Refined Synopsis Section =====
    synopsis_group = QtWidgets.QGroupBox("Refined Synopsis")
    synopsis_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for refined synopsis
    refined_expand_btn = QtWidgets.QPushButton("Expand")
    refined_expand_btn.setMaximumWidth(100)
    refined_expand_btn.clicked.connect(lambda: self._expand_text_window("planning_synopsis_display"))
    synopsis_layout.addWidget(refined_expand_btn)
    
    self.planning_synopsis_display = QtWidgets.QTextEdit()
    self.planning_synopsis_display.setReadOnly(True)
    self.planning_synopsis_display.setPlaceholderText("Refined synopsis will appear here...")
    self.planning_synopsis_display.setMinimumHeight(120)
    self.planning_synopsis_display.setMaximumHeight(200)
    synopsis_layout.addWidget(self.planning_synopsis_display)
    
    # Buttons for refined synopsis
    synopsis_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.approve_button = QtWidgets.QPushButton("Approve")
    self.approve_button.setMinimumHeight(35)
    self.approve_button.setMaximumWidth(100)
    self.approve_button.setEnabled(False)
    self.approve_button.clicked.connect(self._on_approve_synopsis)
    synopsis_buttons_layout.addWidget(self.approve_button)
    
    self.adjust_button = QtWidgets.QPushButton("Adjust")
    self.adjust_button.setMinimumHeight(35)
    self.adjust_button.setMaximumWidth(100)
    self.adjust_button.setEnabled(False)
    self.adjust_button.clicked.connect(self._on_adjust_synopsis)
    synopsis_buttons_layout.addWidget(self.adjust_button)
    
    synopsis_buttons_layout.addStretch()
    synopsis_layout.addLayout(synopsis_buttons_layout)
    
    synopsis_group.setLayout(synopsis_layout)
    self.refined_synopsis_group = synopsis_group
    layout.addWidget(synopsis_group)
    
    # ===== Outline Section =====
    outline_group = QtWidgets.QGroupBox("Generated Outline (25 Chapters)")
    outline_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for outline
    outline_expand_btn = QtWidgets.QPushButton("Expand")
    outline_expand_btn.setMaximumWidth(100)
    outline_expand_btn.clicked.connect(lambda: self._expand_text_window("outline_display"))
    outline_layout.addWidget(outline_expand_btn)
    
    self.outline_display = QtWidgets.QTextEdit()
    self.outline_display.setReadOnly(True)
    self.outline_display.setPlaceholderText("Novel outline will appear here after synopsis approval...")
    self.outline_display.setMinimumHeight(120)
    self.outline_display.setMaximumHeight(200)
    outline_layout.addWidget(self.outline_display)
    
    # Buttons for outline
    outline_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.approve_outline_button = QtWidgets.QPushButton("Approve")
    self.approve_outline_button.setMinimumHeight(35)
    self.approve_outline_button.setMaximumWidth(100)
    self.approve_outline_button.setEnabled(False)
    self.approve_outline_button.clicked.connect(self._on_approve_outline)
    outline_buttons_layout.addWidget(self.approve_outline_button)
    
    self.adjust_outline_button = QtWidgets.QPushButton("Adjust")
    self.adjust_outline_button.setMinimumHeight(35)
    self.adjust_outline_button.setMaximumWidth(100)
    self.adjust_outline_button.setEnabled(False)
    self.adjust_outline_button.clicked.connect(self._on_adjust_outline)
    outline_buttons_layout.addWidget(self.adjust_outline_button)
    
    outline_buttons_layout.addStretch()
    outline_layout.addLayout(outline_buttons_layout)
    
    outline_group.setLayout(outline_layout)
    self.outline_group = outline_group
    layout.addWidget(outline_group)
    
    # ===== Characters Section =====
    characters_group = QtWidgets.QGroupBox("Generated Characters")
    characters_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for characters
    characters_expand_btn = QtWidgets.QPushButton("Expand")
    characters_expand_btn.setMaximumWidth(100)
    characters_expand_btn.clicked.connect(lambda: self._expand_text_window("characters_display"))
    characters_layout.addWidget(characters_expand_btn)
    
    self.characters_display = QtWidgets.QTextEdit()
    self.characters_display.setReadOnly(True)
    self.characters_display.setPlaceholderText("Character profiles will appear here after outline approval...")
    self.characters_display.setMinimumHeight(120)
    self.characters_display.setMaximumHeight(200)
    characters_layout.addWidget(self.characters_display)
    
    # Buttons for characters
    characters_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.approve_characters_button = QtWidgets.QPushButton("Approve")
    self.approve_characters_button.setMinimumHeight(35)
    self.approve_characters_button.setMaximumWidth(100)
    self.approve_characters_button.setEnabled(False)
    self.approve_characters_button.clicked.connect(self._on_approve_characters)
    characters_buttons_layout.addWidget(self.approve_characters_button)
    
    self.adjust_characters_button = QtWidgets.QPushButton("Adjust")
    self.adjust_characters_button.setMinimumHeight(35)
    self.adjust_characters_button.setMaximumWidth(100)
    self.adjust_characters_button.setEnabled(False)
    self.adjust_characters_button.clicked.connect(self._on_adjust_characters)
    characters_buttons_layout.addWidget(self.adjust_characters_button)
    
    characters_buttons_layout.addStretch()
    characters_layout.addLayout(characters_buttons_layout)
    
    characters_group.setLayout(characters_layout)
    self.characters_group = characters_group
    layout.addWidget(characters_group)
    
    # ===== World Section =====
    world_group = QtWidgets.QGroupBox("Generated World")
    world_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for world
    world_expand_btn = QtWidgets.QPushButton("Expand")
    world_expand_btn.setMaximumWidth(100)
    world_expand_btn.clicked.connect(lambda: self._expand_text_window("world_display"))
    world_layout.addWidget(world_expand_btn)
    
    self.world_display = QtWidgets.QTextEdit()
    self.world_display.setReadOnly(True)
    self.world_display.setPlaceholderText("World details will appear here after characters approval...")
    self.world_display.setMinimumHeight(120)
    self.world_display.setMaximumHeight(200)
    world_layout.addWidget(self.world_display)
    
    # Buttons for world
    world_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.approve_world_button = QtWidgets.QPushButton("Approve")
    self.approve_world_button.setMinimumHeight(35)
    self.approve_world_button.setMaximumWidth(100)
    self.approve_world_button.setEnabled(False)
    self.approve_world_button.clicked.connect(self._on_approve_world)
    world_buttons_layout.addWidget(self.approve_world_button)
    
    self.adjust_world_button = QtWidgets.QPushButton("Adjust")
    self.adjust_world_button.setMinimumHeight(35)
    self.adjust_world_button.setMaximumWidth(100)
    self.adjust_world_button.setEnabled(False)
    self.adjust_world_button.clicked.connect(self._on_adjust_world)
    world_buttons_layout.addWidget(self.adjust_world_button)
    
    world_buttons_layout.addStretch()
    world_layout.addLayout(world_buttons_layout)
    
    world_group.setLayout(world_layout)
    self.world_group = world_group
    layout.addWidget(world_group)
    
    # ===== Timeline Section =====
    timeline_group = QtWidgets.QGroupBox("Generated Timeline")
    timeline_layout = QtWidgets.QVBoxLayout()
    
    # Expand button for timeline
    timeline_expand_btn = QtWidgets.QPushButton("Expand")
    timeline_expand_btn.setMaximumWidth(100)
    timeline_expand_btn.clicked.connect(lambda: self._expand_text_window("timeline_display"))
    timeline_layout.addWidget(timeline_expand_btn)
    
    self.timeline_display = QtWidgets.QTextEdit()
    self.timeline_display.setReadOnly(True)
    self.timeline_display.setPlaceholderText("Timeline with dates, locations, and events will appear here after world approval...")
    self.timeline_display.setMinimumHeight(120)
    self.timeline_display.setMaximumHeight(200)
    timeline_layout.addWidget(self.timeline_display)
    
    # Buttons for timeline
    timeline_buttons_layout = QtWidgets.QHBoxLayout()
    
    self.approve_timeline_button = QtWidgets.QPushButton("Approve")
    self.approve_timeline_button.setMinimumHeight(35)
    self.approve_timeline_button.setMaximumWidth(100)
    self.approve_timeline_button.setEnabled(False)
    self.approve_timeline_button.clicked.connect(self._on_approve_timeline)
    timeline_buttons_layout.addWidget(self.approve_timeline_button)
    
    self.adjust_timeline_button = QtWidgets.QPushButton("Adjust")
    self.adjust_timeline_button.setMinimumHeight(35)
    self.adjust_timeline_button.setMaximumWidth(100)
    self.adjust_timeline_button.setEnabled(False)
    self.adjust_timeline_button.clicked.connect(self._on_adjust_timeline)
    timeline_buttons_layout.addWidget(self.adjust_timeline_button)
    
    timeline_buttons_layout.addStretch()
    timeline_layout.addLayout(timeline_buttons_layout)
    
    timeline_group.setLayout(timeline_layout)
    self.timeline_group = timeline_group
    layout.addWidget(timeline_group)
    
    layout.addStretch()
    
    # Add inner widget to scroll area
    scroll_area.setWidget(inner_widget)
    main_layout.addWidget(scroll_area)
    
    return tab
    
    
    # Create references dict for widgets that need external access
    references = {
    'synopsis_display': synopsis_display,
    'planning_synopsis_display': planning_synopsis_display,
    'outline_display': outline_display,
    'characters_display': characters_display,
    'world_display': world_display,
    'timeline_display': timeline_display,
    }
    
    return tab, references
