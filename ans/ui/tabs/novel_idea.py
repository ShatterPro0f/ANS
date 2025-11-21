"""
Novel Idea Tab for the ANS application.

This module provides the Novel Idea tab where users input their novel concept,
desired tone, and target word count to begin the generation process.
"""
from PyQt5 import QtWidgets


def create_novel_idea_tab(main_window, signal_broker):
    """Create and configure the Novel Idea tab.
    
    This tab allows users to:
    - Enter their novel idea/plot outline
    - Specify the desired tone
    - Set target word count
    - Start the novel generation process
    
    Args:
        main_window: Reference to the main ANSWindow instance
        signal_broker: SignalBroker instance for emitting signals
        
    Returns:
        tuple: (tab_widget, references_dict) where references_dict contains:
            - 'novel_idea_input': QTextEdit for idea input
            - 'tone_input': QTextEdit for tone input
            - 'word_count_spinbox': QSpinBox for word count
    """
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    
    # ===== Novel Idea Section =====
    idea_group = QtWidgets.QGroupBox("Novel Idea")
    idea_layout = QtWidgets.QVBoxLayout()
    
    idea_label = QtWidgets.QLabel("Describe your novel idea:")
    novel_idea_input = QtWidgets.QTextEdit()
    novel_idea_input.setPlaceholderText("Enter your novel idea, plot outline, or inspiration...")
    novel_idea_input.setMinimumHeight(100)
    
    idea_layout.addWidget(idea_label)
    idea_layout.addWidget(novel_idea_input)
    idea_group.setLayout(idea_layout)
    layout.addWidget(idea_group)
    
    # ===== Tone Section =====
    tone_group = QtWidgets.QGroupBox("Tone")
    tone_layout = QtWidgets.QVBoxLayout()
    
    tone_label = QtWidgets.QLabel("Describe the desired tone:")
    tone_input = QtWidgets.QTextEdit()
    tone_input.setPlaceholderText("e.g., 'Dark and mysterious', 'Light-hearted and humorous', 'Epic and grand'...")
    tone_input.setMinimumHeight(80)
    
    tone_layout.addWidget(tone_label)
    tone_layout.addWidget(tone_input)
    tone_group.setLayout(tone_layout)
    layout.addWidget(tone_group)
    
    # ===== Word Count Target Section =====
    wordcount_group = QtWidgets.QGroupBox("Target Word Count")
    wordcount_layout = QtWidgets.QHBoxLayout()
    
    wordcount_label = QtWidgets.QLabel("Soft Target Word Count:")
    word_count_spinbox = QtWidgets.QSpinBox()
    word_count_spinbox.setMinimum(10000)
    word_count_spinbox.setMaximum(1000000)
    word_count_spinbox.setValue(250000)
    word_count_spinbox.setSingleStep(10000)
    
    wordcount_layout.addWidget(wordcount_label)
    wordcount_layout.addWidget(word_count_spinbox)
    wordcount_layout.addStretch()
    wordcount_group.setLayout(wordcount_layout)
    layout.addWidget(wordcount_group)
    
    # ===== Start Button =====
    def _on_start_novel():
        """Handle start button click - emit start signal with configuration."""
        idea = novel_idea_input.toPlainText().strip()
        tone = tone_input.toPlainText().strip()
        word_count = word_count_spinbox.value()
        
        if not idea:
            # Show error if no idea provided
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(tab, "Input Required", "Please enter a novel idea to continue.")
            return
        
        if not tone:
            QMessageBox.warning(tab, "Input Required", "Please describe the desired tone.")
            return
        
        # Format config string for thread
        config_str = f"Idea: {idea}, Tone: {tone}, Soft Target: {word_count}"
        
        # Emit start signal through signal broker
        signal_broker.start_signal.emit(config_str)
    
    start_button = QtWidgets.QPushButton("Start")
    start_button.setMinimumHeight(40)
    start_button.clicked.connect(_on_start_novel)
    layout.addWidget(start_button)
    
    layout.addStretch()
    
    # Return tab and widget references
    references = {
        'novel_idea_input': novel_idea_input,
        'tone_input': tone_input,
        'word_count_spinbox': word_count_spinbox,
        'start_button': start_button
    }
    
    return tab, references
